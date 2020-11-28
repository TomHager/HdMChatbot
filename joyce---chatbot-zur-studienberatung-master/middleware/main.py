import time
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
import logging.config
import dialogflow_v2 as df
import redis
from flask import Flask
from flask_cors import CORS
from flask import request
import json
from definitions import GCLOUD_KEY_FILE, PROJECT_ID, LANG, CAP_REACHED_MESSAGE, REDIS_HOST, REDIS_PORT, REDIS_DB, \
    MONTHLY_COST_CAP
from webapp_middleware.cost_cap_middleware import CostCapMiddleware

application = Flask(__name__)
application.wsgi_app = CostCapMiddleware(application, application.wsgi_app)
CORS(application)


def create_session_client():
    return df.SessionsClient.from_service_account_json(GCLOUD_KEY_FILE)


def get_accumulated_cost():
    r = create_redis_client()
    return float(r.get('accumulated_cost'))


def create_redis_client():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


def get_fulfillment_message_array(fulfillment_messages):
    messages = []

    for i in range(len(fulfillment_messages)):

        message = fulfillment_messages[i].text.text[0]

        if len(message.strip('"')) > 0:
            messages.append(message)

    return messages


@application.route('/query', methods=['POST'])
def text_query():
    """
    Text Query mit der Dialogflow v2 API.
    Request muss mit Header: application/x-www-form-urlencoded gesendet werden.
    Benoetigte Parameter: session_id, text
    """

    session_client = create_session_client()

    if get_accumulated_cost() < MONTHLY_COST_CAP:

        request_data = request.form

        session = session_client.session_path(PROJECT_ID, request_data['session_id'])
        text_input = df.types.TextInput(text=request_data['text'], language_code=LANG)
        query_input = df.types.QueryInput(text=text_input)
        response = session_client.detect_intent(
            session=session, query_input=query_input)

        answer = {'timestamp': time.time(),
                  'fulfillment': get_fulfillment_message_array(response.query_result.fulfillment_messages)}

        return application.response_class(response=json.dumps(answer), mimetype='application/json')
    else:
        message = [str(CAP_REACHED_MESSAGE)]
        answer = {'timestamp': time.time(), 'fulfillment': message}
        return application.response_class(response=json.dumps(answer), mimetype='application/json')


if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    application.logger.handlers = gunicorn_logger.handlers
    application.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5000)

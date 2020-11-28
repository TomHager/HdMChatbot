import os


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, 'config/config.json')
GCLOUD_KEY_FILE = os.path.join(ROOT_DIR, 'config/joyce-16948-75b914ea1adf.json')
PROJECT_ID = "joyce-16948"
LANG = "en"
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
MONTHLY_COST_CAP = 10
COST_PER_TEXT_REQUEST = 0.002
CAP_REACHED_MESSAGE = "Ich kann dir jetzt nicht antworten."
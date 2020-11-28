## Middleware

* Webserver zum weiterleiten von HTTP-Requests vom Frontend
* Benutzt die Dialogflow v2 API
* Filtert Anfragen, um hohe Lizenzkosten zu verhindern



#### Start

```shell
 pip install Flask
 python main.py
 * Running on http://localhost:5000/
```


#### Tests

Environment kann im config/config.json festgelegt werden.
Um Tests ausführen zu können ist das notwendig.
Weitere Config-Möglichkeiten:

```json
{
  "project_id": "test-agent-c6043",
  "lang": "en",
  "env_name": "chatbot"
}

```



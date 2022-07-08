import json
import os
from datetime import datetime

from flask import Flask, request  # , Response

app = Flask(__name__)

# Run the Flask application as below
# export FLASK_APP=webhook_listener.py
# python -m flask run


@app.route("/webhook", methods=["POST"])
def respond():
    print(request.json)
    if not os.path.exists("output"):
        os.mkdir("output")
    reportfile = f'output/Webhook-{format(datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))}.json'
    fileout = open(reportfile, "w")
    fileout.write(json.dumps(request.json, indent=4))
    fileout.close
    return "Webhooks POST with Python was successful "  # Response(status=200)


@app.route("/web", methods=["GET"])
def hello():
    return "Webhooks with Python"


if __name__ == "__main__":
    app.run(debug=True)

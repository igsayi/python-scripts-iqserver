from flask import Flask, request  # , Response

app = Flask(__name__)

# Run the Flask application as below
# export FLASK_APP=main.py
# python -m flask run


@app.route("/webhook", methods=["POST"])
def respond():
    print(request.json)
    return "Webhooks POST with Python was successful "  # Response(status=200)


@app.route("/web", methods=["GET"])
def hello():
    return "Webhooks with Python"


if __name__ == "__main__":
    app.run(debug=True)

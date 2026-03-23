# Sample Flask app
from flask import Flask

app = Flask(__name__)

@app.route("/users/<int:user_id>", methods=["GET", "POST"])
def user_profile(user_id):
    pass

app.add_url_rule("/health", "health", lambda: "OK", methods=["GET"])

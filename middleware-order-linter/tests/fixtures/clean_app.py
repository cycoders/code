from flask import Flask
app = Flask(__name__)
@app.before_request
def auth(): pass
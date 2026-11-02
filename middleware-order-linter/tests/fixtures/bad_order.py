from flask import Flask
app = Flask(__name__)
@app.after_request
def cors(): pass
@app.before_request
def auth(): pass
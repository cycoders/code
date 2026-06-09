from flask import request
import os

def serve():
    filename = request.args.get('file')
    return open(filename).read()  # vulnerable
import ast
import pytest
from route_extractor_cli.extractors.fastapi import FastAPIExtractor
from route_extractor_cli.extractors.flask import FlaskExtractor
from route_extractor_cli.extractors.django import DjangoExtractor
from route_extractor_cli.utils import parse_path_params
from route_extractor_cli.models import Parameter


def test_fastapi_simple():
    code = """
from fastapi import FastAPI
app = FastAPI()
@app.get("/users/{user_id}")
def read_user(user_id: int):
    pass
    """
    tree = ast.parse(code)
    ext = FastAPIExtractor()
    ext.visit(tree)
    assert len(ext.routes) == 1
    route = ext.routes[0]
    assert route.methods == ["GET"]
    assert "/users/{user_id}" in route.path
    assert "read_user" in route.handler


def test_flask_simple():
    code = """
from flask import Flask
app = Flask(__name__)
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    pass
    """
    tree = ast.parse(code)
    ext = FlaskExtractor()
    ext.visit(tree)
    assert len(ext.routes) >= 1  # Decorator handling basic


def test_django_simple():
    code = """
from django.urls import path
from . import views
urlpatterns = [path('users/<int:pk>/', views.UserView.as_view(), name='user-detail')]
    """
    tree = ast.parse(code)
    ext = DjangoExtractor()
    ext.visit(tree)
    assert len(ext.routes) == 1
    route = ext.routes[0]
    assert 'user-detail' in route.handler


def test_parse_path_params():
    params = parse_path_params("/users/{user_id:int}/{name}")
    assert len(params) == 2
    assert params[0]["name"] == "user_id"
    assert params[0]["type_hint"] == "int"
    assert params[1]["name"] == "name"


def test_no_routes():
    code = "print('hello')"
    tree = ast.parse(code)
    ext = FastAPIExtractor()
    ext.visit(tree)
    assert len(ext.routes) == 0

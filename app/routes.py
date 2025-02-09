from flask import Blueprint, Response, jsonify

main = Blueprint("main", __name__)


@main.route("/")
def home() -> Response:
    return jsonify({"message": "Welcome to Timetraveler!"})

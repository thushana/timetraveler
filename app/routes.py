from flask import Blueprint, Response, make_response, render_template

main = Blueprint("main", __name__)


@main.route("/")
def home() -> Response:
    # Explicitly wrap the rendered template in a Response object
    return make_response(render_template("index.html"))

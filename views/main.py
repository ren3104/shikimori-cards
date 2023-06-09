from flask import Blueprint, redirect


bp_main = Blueprint("main", __name__)


@bp_main.route("/")
def index():
    return redirect("https://github.com/ren3104")

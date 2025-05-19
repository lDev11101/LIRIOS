from flask import render_template, Blueprint, session, redirect, url_for

bp_main = Blueprint("main", __name__, url_prefix="/")


@bp_main.route("/")
def index():
    if not "username" in session:
        return redirect(url_for("auth.login"))
    return render_template("index.html")
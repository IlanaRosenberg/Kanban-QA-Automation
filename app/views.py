from flask import Blueprint, render_template, redirect, url_for

views_bp = Blueprint("views", __name__)


@views_bp.route("/")
def index():
    return render_template("index.html")


@views_bp.route("/login")
def login():
    return render_template("login.html")


@views_bp.route("/register")
def register():
    return render_template("register.html")


@views_bp.route("/boards")
def boards():
    return render_template("boards.html")


@views_bp.route("/boards/<int:board_id>")
def board_detail(board_id):
    return render_template("board_detail.html", board_id=board_id)


@views_bp.route("/logout")
def logout():
    return redirect(url_for("views.login"))

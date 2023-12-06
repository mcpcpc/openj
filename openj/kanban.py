#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from openj.db import get_db
from openj.api.card import create_card as create_card_api
from openj.api.card import read_card as read_card_api
from openj.api.card import update_card as update_card_api
from openj.api.card import delete_card as delete_card_api
from openj.api.user import create_user as create_user_api
from openj.api.user import read_user as read_user_api
from openj.api.user import update_user as update_user_api
from openj.api.user import delete_user as delete_user_api

kanban = Blueprint("kanban", __name__)


@kanban.route("/kanban")
def index():
    options = request.args.copy().to_dict()
    lanes = get_db().execute("SELECT * FROM lane").fetchall()
    cards = (
        get_db()
        .execute(
            """
        SELECT
            card.id AS id,
            card.created_at AS created_at,
            card.updated_at AS updated_at,
            card.title AS title,
            card.lane_id AS lane_id,
            user.firstname AS firstname,
            user.lastname AS lastname
        FROM card
            INNER JOIN user ON user.id = card.user_id
        """
        )
        .fetchall()
    )
    groups = {l["title"]: [c for c in cards if c["lane_id"] == l["id"]] for l in lanes}
    return render_template("kanban.html", options=options, groups=groups)


@kanban.route("/kanban/card/create", methods=("GET", "POST"))
def create_card():
    if request.method == "POST":
        response = create_card_api()
        if response[1] < 300:
            return redirect(url_for("kanban.index"))
        flash(response[0], "error")
    users = get_db().execute("SELECT * FROM user").fetchall()
    lanes = get_db().execute("SELECT * FROM lane").fetchall()
    return render_template("create_card.html", users=users, lanes=lanes)


@kanban.route("/kanban/card/update/<int:id>", methods=("GET", "POST"))
def update_card(id: int):
    if request.method == "POST":
        response = update_card_api(id)
        if response[1] < 300:
            return redirect(url_for("kanban.index"))
        flash(response[0], "error")
    card = read_card_api(id)[0]
    users = get_db().execute("SELECT * FROM user").fetchall()
    lanes = get_db().execute("SELECT * FROM lane").fetchall()
    return render_template("update_card.html", users=users, lanes=lanes, card=card)


@kanban.get("/kanban/card/delete/<int:id>")
def delete_card(id: int):
    delete_card_api(id)
    return redirect(url_for("kanban.index"))


@kanban.route("/kanban/user/create", methods=("GET", "POST"))
def create_user():
    if request.method == "POST":
        response = create_user_api()
        if response[1] < 300:
            return redirect(url_for("kanban.index"))
        flash(response[0], "error")
    return render_template("create_user.html")


@kanban.route("/kanban/user/update/<int:id>", methods=("GET", "POST"))
def update_user(id: int):
    if request.method == "POST":
        response = update_user_api(id)
        if response[1] < 300:
            return redirect(url_for("kanban.index"))
        flash(response[0], "error")
    user = read_user_api(id)[0]
    return render_template("update_user.html", user=user)


@kanban.get("/kanban/user/delete/<int:id>")
def delete_user(id: int):
    delete_user_api(id)
    return redirect(url_for("kanban.index"))

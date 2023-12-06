#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request

from openj.db import get_db

user = Blueprint("user", __name__, url_prefix="/api")


@user.post("/user")
def create_user():
    """Create user."""

    form = request.form.copy().to_dict()
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            INSERT INTO user (
                firstname,
                lastname
            ) VALUES (
                :firstname,
                :lastname
            )
            """,
            form,
        )
        db.commit()
    except db.ProgrammingError:
        return "Missing parameter(s).", 400
    except db.IntegrityError:
        return "Invalid parameter(s).", 400
    return "User successfully created.", 201


@user.get("/user/<int:id>")
def read_user(id: int):
    """Read user."""

    row = (
        get_db()
        .execute(
            "SELECT * FROM user WHERE id = ?",
            (id,),
        )
        .fetchone()
    )
    if not row:
        return "User does not exist.", 404
    return dict(row), 200


@user.put("/user/<int:id>")
def update_user(id: int):
    """Update user."""

    form = request.form.copy().to_dict()
    form["id"] = id
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            UPDATE user SET
                updated_at = CURRENT_TIMESTAMP,
                firstname = :firstname,
                lastname = :lastname
            WHERE id = :id
            """,
            form,
        )
        db.commit()
    except db.ProgrammingError:
        return "Missing parameter(s).", 400
    except db.IntegrityError:
        return "Invalid parameter(s).", 400
    return "User successfully updated.", 201


@user.delete("/user/<int:id>")
def delete_user(id: int):
    """Delete user."""

    db = get_db()
    db.execute("DELETE FROM user WHERE id = ?", (id,))
    db.commit()
    return "User successfully deleted.", 200


@user.get("/user")
def list_users():
    """List users."""

    rows = get_db().execute("SELECT * FROM user").fetchall()
    if not rows:
        return "Users do not exist.", 404
    return list(map(dict, rows)), 200

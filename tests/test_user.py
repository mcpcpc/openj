#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from pathlib import Path
from sqlite3 import connect
from unittest import main
from unittest import TestCase

from openj import create_app


class UserTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls._resources = Path(__file__).parent
        path = cls._resources / "preload.sql"
        with open(path, mode="r", encoding="utf-8") as f:
            cls._preload = f.read()

    def setUp(self):
        self.db = "file::memory:?cache=shared"
        self.app = create_app(
            {"TESTING": True, "DATABASE": self.db, "SECRET_KEY": "dev"},
        )
        self.client = self.app.test_client()
        self.runner = self.app.test_cli_runner()
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.app.test_cli_runner().invoke(args=["init-db"])

    def tearDown(self):
        self.ctx.pop()

    def test_create_user(self):
        db = connect(self.db)
        db.executescript(self._preload)
        response = self.client.post(
            "/api/user",
            data={
                "firstname": "firstname_two",
                "lastname": "lastname_two",
            },
        )
        self.assertEqual(response.status_code, 201)

    def test_read_user(self):
        db = connect(self.db)
        db.executescript(self._preload)
        response = self.client.get("/api/user/1")
        self.assertEqual(response.status_code, 200)

    def test_update_user(self):
        db = connect(self.db)
        db.executescript(self._preload)
        response = self.client.put(
            "/api/user/1",
            data={
                "firstname": "firstname_one_",
                "lastname": "lastname_one_",
            },
        )
        self.assertEqual(response.status_code, 201)

    def test_delete_user(self):
        db = connect(self.db)
        db.executescript(self._preload)
        response = self.client.delete("/api/user/1")
        self.assertEqual(response.status_code, 200)

    def test_list_users(self):
        db = connect(self.db)
        db.executescript(self._preload)
        response = self.client.get("/api/user")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    main()

"""Offline regression tests; never connect to the production database."""
import asyncio
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi import FastAPI, HTTPException, Request
from fastapi.security import HTTPBasicCredentials
from jinja2 import Environment, FileSystemLoader

from app import auth
from app.routes_auth import safe_admin_redirect
from app.routes_health import register_health_routes


class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {
            "ADMIN_LOGIN": "test-admin", "ADMIN_PASSWORD": "test-only-password",
            "ADMIN_PASS": "", "ADMIN_SESSION_SECRET": "test-only-session-secret",
        })
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_signed_session_and_tampering(self):
        token = auth.make_admin_token("test-admin")
        self.assertEqual(auth.verify_admin_token(token), "test-admin")
        self.assertIsNone(auth.verify_admin_token(token + "tampered"))
        self.assertIsNone(auth.verify_admin_token("malformed"))

    def test_expired_session(self):
        with patch("app.auth.time.time", return_value=1):
            token = auth.make_admin_token("test-admin")
        self.assertIsNone(auth.verify_admin_token(token))

    def test_secret_is_required(self):
        with patch.dict(os.environ, {"ADMIN_SESSION_SECRET": ""}):
            with self.assertRaises(RuntimeError):
                auth.get_admin_session_secret()

    def test_empty_basic_password_rejected(self):
        request = Request({"type": "http", "path": "/admin", "headers": [],
                           "query_string": b"", "scheme": "http", "server": ("localhost", 8000)})
        credentials = HTTPBasicCredentials(username="test-admin", password="")
        with patch.dict(os.environ, {"ADMIN_PASSWORD": ""}):
            with self.assertRaises(HTTPException) as result:
                asyncio.run(auth.verify_admin(request, credentials))
        self.assertEqual(result.exception.status_code, 303)

    def test_redirects_stay_local(self):
        for value in ("https://example.com", "//example.com", "/administrator", "/admin\\evil", None):
            self.assertEqual(safe_admin_redirect(value), "/admin")
        self.assertEqual(safe_admin_redirect("/admin/leads?page=2"), "/admin/leads?page=2")

    def test_db_health_hides_internal_errors(self):
        app = FastAPI()
        connection_factory = MagicMock(side_effect=RuntimeError("PRIVATE connection detail"))
        register_health_routes(app, connection_factory)
        endpoint = next(route.endpoint for route in app.routes if route.path == "/health/db")
        response = asyncio.run(endpoint())
        self.assertEqual(response.status_code, 503)
        self.assertNotIn(b"PRIVATE", response.body)

    def test_db_health_success_and_cleanup(self):
        app = FastAPI()
        factory = MagicMock()
        register_health_routes(app, factory)
        endpoint = next(route.endpoint for route in app.routes if route.path == "/health/db")
        self.assertEqual(asyncio.run(endpoint()), {"status": "ok"})
        factory.return_value.close.assert_called_once()
        factory.return_value.cursor.return_value.close.assert_called_once()

    def test_templates_compile(self):
        directory = Path(__file__).resolve().parents[1] / "app" / "templates"
        environment = Environment(loader=FileSystemLoader(directory))
        for template in directory.rglob("*.html"):
            with self.subTest(template=template.name):
                environment.get_template(template.relative_to(directory).as_posix())

    def test_client_tokens_are_not_tracked(self):
        from app.routes_stats import should_track_request
        request = Request({"type": "http", "method": "GET", "path": "/client/test-token/files/1", "headers": []})
        self.assertFalse(should_track_request(request))

    def test_statistics_require_independent_secret(self):
        from app.routes_stats import hash_ip
        with patch.dict(os.environ, {"STATS_IP_HASH_SECRET": ""}):
            with self.assertRaises(RuntimeError):
                hash_ip("127.0.0.1")


if __name__ == "__main__":
    unittest.main()

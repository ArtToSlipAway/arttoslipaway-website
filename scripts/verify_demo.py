"""End-to-end checks against an already running LOCAL synthetic demo.

Run after seed_demo. Creates only test leads; removes those exact rows afterwards.
No HTTPX, browser or live customer records required.
"""
import hashlib
import http.cookiejar
import json
import os
import re
import unittest
import urllib.error
import urllib.parse
import urllib.request
import uuid

from app.db import get_db_connection

BASE = os.getenv("TEST_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, newurl):
        return None


def client():
    return urllib.request.build_opener(NoRedirect(), urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def request(opener, path, fields=None, files=None, origin=True):
    headers = {}
    body = None
    if fields is not None:
        if files:
            boundary = "portfolio-test-" + uuid.uuid4().hex
            chunks = []
            for key, value in fields.items():
                chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode())
            for name, data in files:
                chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="reference_files"; filename="{name}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode() + data + b"\r\n")
            chunks.append(f'--{boundary}--\r\n'.encode())
            body = b"".join(chunks)
            headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        else:
            body = urllib.parse.urlencode(fields).encode()
        if origin:
            headers["Origin"] = BASE if origin is True else origin
    try:
        response = opener.open(urllib.request.Request(BASE + path, data=body, headers=headers), timeout=30)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        return response.code, response.headers, response.read()


class DemoIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if urllib.parse.urlparse(BASE).hostname not in {"localhost", "127.0.0.1"}:
            raise RuntimeError("Only a local test server is allowed")
        if os.getenv("DEMO_MODE", "").lower() != "true":
            raise RuntimeError("DEMO_MODE=true is required")
        cls.db = get_db_connection()
        with cls.db.cursor() as cur:
            cur.execute("SELECT setting_value FROM site_settings WHERE setting_key='demo_seed_version'")
            if not cur.fetchone():
                raise RuntimeError("Seed a separate synthetic demo first")
        cls.created_ids = []
        cls.public = client()
        cls.admin = client()
        status, _, _ = request(cls.admin, "/admin/login", {
            "username": os.environ["ADMIN_LOGIN"], "password": os.environ["ADMIN_PASSWORD"],
        })
        if status != 303:
            raise RuntimeError(f"Demo administrator login failed: {status}")

    @classmethod
    def tearDownClass(cls):
        from app.paths import PRIVATE_UPLOADS_DIR
        try:
            with cls.db, cls.db.cursor() as cur:
                for lead_id in cls.created_ids:
                    cur.execute("SELECT file_path FROM lead_files WHERE lead_id=%s", (lead_id,))
                    for (key,) in cur.fetchall():
                        if re.fullmatch(r"private/[a-f0-9]{32}\.(?:pdf|png|jpg|jpeg|webp)", key):
                            (PRIVATE_UPLOADS_DIR / key.split("/", 1)[1]).unlink(missing_ok=True)
                    cur.execute("DELETE FROM client_access_tokens WHERE lead_id=%s", (lead_id,))
                    cur.execute("DELETE FROM lead_files WHERE lead_id=%s", (lead_id,))
                    cur.execute("DELETE FROM leads WHERE id=%s", (lead_id,))
        finally:
            cls.db.close()

    def new_lead(self, files=None):
        tag = "integration-" + uuid.uuid4().hex
        status, _, _ = request(self.public, "/request", {
            "name": tag, "contact": "integration@example.com", "personal_data_agreement": "on",
            "idea": "Synthetic integration test", "city": "Санкт-Петербург",
        }, files=files)
        self.assertEqual(status, 303)
        with self.db.cursor() as cur:
            cur.execute("SELECT id FROM leads WHERE name=%s", (tag,))
            lead_id = cur.fetchone()[0]
        self.created_ids.append(lead_id)
        return lead_id

    def token_for(self, lead_id):
        status, _, body = request(self.admin, f"/admin/leads/{lead_id}/client-link", {})
        self.assertEqual(status, 200)
        match = re.search(rb"/client/([A-Za-z0-9_-]{20,128})", body)
        self.assertIsNotNone(match)
        return match.group(1).decode()

    def test_public_and_administrative_pages(self):
        for path in ["/", "/projects", "/categories/tattoo", "/categories/tattoo-graphics",
                     "/projects/demo-mountains", "/request", "/health", "/health/db",
                     "/api/city-slots", "/api/home-carousel", "/api/announcement", "/privacy"]:
            with self.subTest(path=path):
                self.assertEqual(request(self.public, path)[0], 200)
        for path in ["/admin", "/admin/leads", "/admin/projects", "/admin/categories", "/admin/media", "/admin/visual"]:
            with self.subTest(path=path):
                self.assertEqual(request(self.public, path)[0], 303)
                self.assertEqual(request(self.admin, path)[0], 200)

    def test_login_requires_origin(self):
        # Browsers need this policy to preserve Origin on same-origin form POSTs.
        self.assertEqual(request(self.public, "/admin/login")[1]["Referrer-Policy"], "same-origin")
        self.assertEqual(request(self.public, "/admin/login", {"username": "x", "password": "x"}, origin=False)[0], 403)
        self.assertEqual(request(self.public, "/admin/login", {"username": "x", "password": "x"}, origin="https://untrusted.example")[0], 403)

    def test_invalid_attachment_rolls_back(self):
        with self.db.cursor() as cur:
            cur.execute("SELECT count(*) FROM leads")
            before = cur.fetchone()[0]
        status, _, _ = request(self.public, "/request", {
            "name": "invalid-file-demo", "contact": "invalid@example.com", "personal_data_agreement": "on",
        }, files=[("fake.png", b"not a PNG")])
        self.assertEqual(status, 400)
        with self.db.cursor() as cur:
            cur.execute("SELECT count(*) FROM leads")
            self.assertEqual(cur.fetchone()[0], before)

    def test_private_attachment_authorization_and_revocation(self):
        data = b"%PDF-1.4\nSynthetic portfolio test attachment\n%%EOF\n"
        lead_id = self.new_lead([("demo-reference.pdf", data)])
        other_id = self.new_lead()
        token, other_token = self.token_for(lead_id), self.token_for(other_id)
        with self.db.cursor() as cur:
            cur.execute("SELECT id,file_path FROM lead_files WHERE lead_id=%s", (lead_id,))
            file_id, key = cur.fetchone()
        for path in [f"/uploads/{key.split('/')[1]}", f"/private_files/{key.split('/')[1]}",
                     f"/client/{other_token}/files/{file_id}", f"/client/{'x'*40}/files/{file_id}"]:
            self.assertEqual(request(self.public, path)[0], 404)
        self.assertEqual(request(self.public, f"/admin/lead-files/{file_id}")[0], 303)
        for opener, path in [(self.admin, f"/admin/lead-files/{file_id}"),
                             (self.public, f"/client/{token}/files/{file_id}")]:
            status, headers, body = request(opener, path)
            self.assertEqual(status, 200)
            self.assertEqual(body, data)
            self.assertEqual(headers["Cache-Control"], "no-store")
            self.assertEqual(headers["Referrer-Policy"], "no-referrer")
            self.assertTrue(headers["Content-Disposition"].startswith("attachment"))
        self.assertEqual(request(self.public, f"/client/{token}")[0], 200)
        with self.db, self.db.cursor() as cur:
            cur.execute("UPDATE client_access_tokens SET expires_at=NOW()-interval '1 second' WHERE token_hash=%s", (hashlib.sha256(token.encode()).hexdigest(),))
        self.assertEqual(request(self.public, f"/client/{token}/files/{file_id}")[0], 404)
        with self.db, self.db.cursor() as cur:
            cur.execute("UPDATE client_access_tokens SET expires_at=NULL, is_active=FALSE WHERE token_hash=%s", (hashlib.sha256(token.encode()).hexdigest(),))
        self.assertEqual(request(self.public, f"/client/{token}/files/{file_id}")[0], 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)

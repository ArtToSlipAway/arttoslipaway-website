import asyncio
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException, UploadFile
from app import upload_core
from app.routes_private_files import private_file_response


class UploadTests(unittest.TestCase):
    def test_private_storage_outside_public_uploads(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(upload_core, "PRIVATE_UPLOADS_DIR", Path(directory)):
            key = asyncio.run(upload_core.save_upload_file(
                UploadFile(filename="reference.pdf", file=io.BytesIO(b"%PDF-1.4\ntest")),
                allowed_extensions=upload_core.REFERENCE_UPLOAD_EXTENSIONS, private=True,
            ))
            self.assertTrue(key.startswith("private/"))
            self.assertEqual(len(list(Path(directory).iterdir())), 1)

    def test_invalid_signature_and_empty_file_leave_no_artifacts(self):
        for payload in (b"not an image", b""):
            with tempfile.TemporaryDirectory() as directory, patch.object(upload_core, "PRIVATE_UPLOADS_DIR", Path(directory)):
                with self.assertRaises(HTTPException):
                    asyncio.run(upload_core.save_upload_file(UploadFile(filename="bad.png", file=io.BytesIO(payload)), private=True))
                self.assertEqual(list(Path(directory).iterdir()), [])

    def test_oversized_upload_is_removed(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(upload_core, "PRIVATE_UPLOADS_DIR", Path(directory)), patch.object(upload_core, "MAX_UPLOAD_SIZE", 8):
            with self.assertRaises(HTTPException):
                asyncio.run(upload_core.save_upload_file(UploadFile(filename="big.png", file=io.BytesIO(b"\x89PNG\r\n\x1a\nlarge")), private=True))
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_legacy_external_and_traversal_paths_rejected(self):
        for path in ["/uploads/old.pdf", "https://example.com/test.pdf", "private/../../.env", "private/fake.pdf"]:
            with self.subTest(path=path), self.assertRaises(HTTPException):
                private_file_response({"file_path": path})

    def test_private_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            target = base / "sensitive.txt"
            target.write_text("not downloadable")
            (base / ("a"*32 + ".pdf")).symlink_to(target)
            with patch("app.routes_private_files.PRIVATE_UPLOADS_DIR", base), self.assertRaises(HTTPException):
                private_file_response({"file_path": "private/" + "a"*32 + ".pdf"})


if __name__ == "__main__":
    unittest.main()

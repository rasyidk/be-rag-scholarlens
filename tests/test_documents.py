import io
from types import SimpleNamespace
from pathlib import Path

from fastapi.testclient import TestClient
from bson import ObjectId

from app.main import app
from app.core.security import create_access_token
import app.services.document_service as document_service


client = TestClient(app)


def test_upload_pdf_success(tmp_path, monkeypatch):
    # Use temp dir for uploads
    monkeypatch.setattr(document_service, "UPLOAD_DIR", tmp_path / "uploads")

    # Stub collection that returns an ObjectId
    class StubColl:
        def insert_one(self, doc):
            return SimpleNamespace(inserted_id=ObjectId())

    monkeypatch.setattr(document_service, "get_documents_collection", lambda: StubColl())

    token, _ = create_access_token("user123")
    headers = {"Authorization": f"Bearer {token}"}

    file_content = b"%PDF-1.4 fake pdf content"
    files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {"name": "Test Doc"}

    resp = client.post("/api/v1/documents", headers=headers, data=data, files=files)
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "success"
    d = body["data"]
    assert d["name"] == "Test Doc"
    assert d["original_filename"] == "test.pdf"

    saved_path = Path(d["saved_filename"])
    assert saved_path.exists()


def test_upload_wrong_content_type(monkeypatch):
    # Ensure real UPLOAD_DIR isn't used in this test
    monkeypatch.setattr(document_service, "get_documents_collection", lambda: SimpleNamespace(insert_one=lambda doc: SimpleNamespace(inserted_id=ObjectId())))

    token, _ = create_access_token("user123")
    headers = {"Authorization": f"Bearer {token}"}

    files = {"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")}
    data = {"name": "Bad Doc"}

    resp = client.post("/api/v1/documents", headers=headers, data=data, files=files)
    assert resp.status_code == 400
    body = resp.json()
    assert body["status"] == "error"


def test_upload_missing_auth():
    file_content = b"%PDF-1.4 fake pdf content"
    files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {"name": "Test Doc"}

    resp = client.post("/api/v1/documents", data=data, files=files)
    assert resp.status_code == 401


def test_delete_document_success(tmp_path, monkeypatch):
    # create a fake saved file
    saved_dir = tmp_path / "uploads" / "user123"
    saved_dir.mkdir(parents=True)
    saved_file = saved_dir / "file.pdf"
    saved_file.write_bytes(b"pdf")

    # stub collection behavior
    class StubColl:
        def find_one(self, q):
            return {"_id": ObjectId(), "user_id": "user123", "saved_filename": str(saved_file)}

        def delete_one(self, q):
            return SimpleNamespace(deleted_count=1)

    monkeypatch.setattr(document_service, "get_documents_collection", lambda: StubColl())
    monkeypatch.setattr(document_service, "UPLOAD_DIR", tmp_path / "uploads")

    token, _ = create_access_token("user123")
    headers = {"Authorization": f"Bearer {token}"}

    # use the id from stubbed find_one
    fake_id = "507f1f77bcf86cd799439011"
    resp = client.delete(f"/api/v1/documents/{fake_id}", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "success"
    assert not saved_file.exists()


def test_delete_document_not_found(monkeypatch):
    class StubColl:
        def find_one(self, q):
            return None

        def delete_one(self, q):
            return SimpleNamespace(deleted_count=0)

    monkeypatch.setattr(document_service, "get_documents_collection", lambda: StubColl())

    token, _ = create_access_token("user123")
    headers = {"Authorization": f"Bearer {token}"}

    fake_id = "507f1f77bcf86cd799439011"
    resp = client.delete(f"/api/v1/documents/{fake_id}", headers=headers)
    assert resp.status_code == 404
    body = resp.json()
    assert body["status"] == "error"

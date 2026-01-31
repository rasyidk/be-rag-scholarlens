from types import SimpleNamespace
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.utils.response import success_response

client = TestClient(app)


def test_get_documents_by_project_success(monkeypatch):
    # stub service to return two documents
    def stub_get_docs(user_id, project_id):
        return success_response(message="ok", data=[{"_id": "1", "name": "doc1"}, {"_id": "2", "name": "doc2"}], code=200)

    monkeypatch.setattr("app.services.document_service.get_documents_by_project", stub_get_docs)

    token, _ = create_access_token("user123")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/v1/projects/abc123/documents", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "success"
    assert len(body["data"]) == 2


def test_get_documents_by_project_unauthorized():
    resp = client.get("/api/v1/projects/abc123/documents")
    assert resp.status_code == 401

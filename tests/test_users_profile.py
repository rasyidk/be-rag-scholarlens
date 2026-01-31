from types import SimpleNamespace
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.services.user_service import get_user
from app.utils.response import success_response
import app.services.user_service as user_service

client = TestClient(app)


def test_profile_success(monkeypatch):
    # stub the service to return a known user
    def stub_get_user(uid):
        return success_response(message="User fetched", data={"_id": uid, "name": "Alice", "email": "a@example.com", "email_verified": True, "created_at": "2026-01-01T00:00:00"}, code=200)

    monkeypatch.setattr(user_service, "get_user", stub_get_user)

    token, _ = create_access_token("507f1f77bcf86cd799439011")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/v1/users/profile", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "success"
    assert body["data"]["name"] == "Alice"


def test_profile_unauthorized():
    resp = client.get("/api/v1/users/profile")
    assert resp.status_code == 401

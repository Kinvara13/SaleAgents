import pytest

def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_settings_ai_configs(client):
    # 1. Create AI Config
    response = client.post("/api/v1/settings/ai-configs", json={
        "name": "Smoke Test AI",
        "provider": "openai",
        "api_key": "test_key",
        "base_url": "http://localhost:8000",
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1024
    })
    assert response.status_code == 201
    cfg = response.json()
    assert cfg["name"] == "Smoke Test AI"
    cfg_id = cfg["id"]

    # 2. Get AI Configs
    response = client.get("/api/v1/settings/ai-configs")
    assert response.status_code == 200
    configs = response.json()
    assert len(configs) >= 1
    assert any(c["id"] == cfg_id for c in configs)

    # 3. Activate Config
    response = client.post(f"/api/v1/settings/ai-configs/{cfg_id}/activate")
    assert response.status_code == 200
    assert response.json()["is_active"] is True

    # 4. Patch Config
    response = client.patch(f"/api/v1/settings/ai-configs/{cfg_id}", json={
        "model": "gpt-4-turbo"
    })
    assert response.status_code == 200
    assert response.json()["model"] == "gpt-4-turbo"

    # 5. Delete Config
    response = client.delete(f"/api/v1/settings/ai-configs/{cfg_id}")
    assert response.status_code == 204

def test_users_roles(client):
    # 1. Get roles
    response = client.get("/api/v1/users/roles/list")
    assert response.status_code == 200
    roles = response.json()
    assert isinstance(roles, list)
    assert len(roles) > 0

    # 2. Create User
    response = client.post("/api/v1/users", json={
        "username": "smoke_user",
        "password": "password123",
        "name": "Smoke User",
        "role": "executor"
    })
    assert response.status_code == 201
    user = response.json()
    assert user["username"] == "smoke_user"
    user_id = user["id"]

    # 3. List Users
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    users = response.json()
    assert any(u["id"] == user_id for u in users)

    # 4. Delete User
    response = client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 204

def test_tenders(client):
    # 1. Create Tender
    response = client.post("/api/v1/tenders", json={
        "title": "Smoke Tender",
        "source_url": "http://example.com",
        "publish_date": "2026-04-22",
        "deadline": "2026-05-22",
        "amount": "100万",
        "margin": "5万",
        "project_type": "IT",
        "description": "Smoke test description"
    })
    assert response.status_code == 201
    tender = response.json()
    assert tender["title"] == "Smoke Tender"
    tender_id = tender["id"]

    # 2. List Tenders
    response = client.get("/api/v1/tenders")
    assert response.status_code == 200
    tenders = response.json()
    assert any(t["id"] == tender_id for t in tenders)

    # 3. Tender Decision
    response = client.post(f"/api/v1/tenders/{tender_id}/decision", json={
        "decision": "bid",
        "margin": "10万",
        "project_type": "Software"
    })
    assert response.status_code == 200
    updated = response.json()
    assert updated["decision"] == "bid"
    assert updated["margin"] == "10万"
    assert updated["project_type"] == "Software"

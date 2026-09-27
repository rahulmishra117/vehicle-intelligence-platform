def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


def test_create_and_fetch_inspection(client):
    payload = {
        "vehicle_id": "car-2001",
        "make": "Toyota",
        "model": "Innova",
        "year": 2023,
        "odometer_km": 10000,
        "inspector": "Test Inspector",
        "decision": "approved",
        "notes": "Clean vehicle",
        "issues": [],
    }
    created = client.post("/api/v1/inspections", json=payload)
    assert created.status_code == 201
    assert created.json()["vehicle_id"] == "CAR-2001"
    fetched = client.get(f'/api/v1/inspections/{created.json()["id"]}')
    assert fetched.status_code == 200
    assert fetched.json() == created.json()


def test_unknown_inspection_is_404(client):
    response = client.get("/api/v1/inspections/99999")
    assert response.status_code == 404


def test_explains_rejection(client):
    response = client.post("/api/v1/query", json={"query": "Why was vehicle CAR-1002 rejected?"})
    body = response.json()
    assert response.status_code == 200
    assert body["interpretation"]["intent"] == "explain_decision"
    assert body["interpretation"]["filters"]["vehicle_id"] == "CAR-1002"
    assert "head-gasket" in body["answer"]
    assert body["count"] == 1


def test_searches_engine_issues(client):
    response = client.post("/api/v1/query", json={"query": "Show all cars with engine issues"})
    body = response.json()
    assert response.status_code == 200
    assert body["interpretation"]["filters"] == {"category": "engine"}
    assert [item["vehicle_id"] for item in body["results"]] == ["CAR-1002"]


def test_summarizes_inspection(client):
    response = client.post("/api/v1/query", json={"query": "Summarize inspection for CAR-1004"})
    body = response.json()
    assert body["count"] == 1
    assert "INR 125,000" in body["answer"]


def test_validation_rejects_bad_payload(client):
    response = client.post("/api/v1/inspections", json={"vehicle_id": "x"})
    assert response.status_code == 422


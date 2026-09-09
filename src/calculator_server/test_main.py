from urllib import response

from fastapi.testclient import TestClient
from calculator_server.main import app  # or whatever your app module is

client = TestClient(app)

def test_basic_division():
    r = client.post("/calculate", params={"expr": "30/4"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 7.5) < 1e-9

def test_percent_subtraction():
    r = client.post("/calculate", params={"expr": "100 - 6%"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 94.0) < 1e-9

def test_standalone_percent():
    r = client.post("/calculate", params={"expr": "6%"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 0.06) < 1e-9

def test_invalid_expr_returns_ok_false():
    r = client.post("/calculate", params={"expr": "2**(3"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is False
    assert "error" in data and data["error"] != ""

def test_get_history_is_empty():
    client.delete("/history")

    response = client.get("/history")

    assert response.status_code == 200
    assert response.json() == []


def test_get_history_contains_calculation():
    client.delete("/history")

    client.post("/calculate", params={"expr": "10+5"})
    client.post("/calculate", params={"expr": "30/4"})

    response = client.get("/history")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["expr"] == "10+5"
    assert data[0]["result"] == 15
    assert data[1]["expr"] == "30/4"
    assert data[1]["result"] == 7.5
    assert "timestamp" in data[0]


def test_get_history_with_limit():
    client.delete("/history")

    client.post("/calculate", params={"expr": "1+1"})
    client.post("/calculate", params={"expr": "2+2"})
    client.post("/calculate", params={"expr": "3+3"})

    response = client.get(
        "/history",
        params={"limit": 2},
    )
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["expr"] == "2+2"
    assert data[1]["expr"] == "3+3"


def test_delete_empty_history():
    client.delete("/history")

    response = client.delete("/history")
    data = response.json()

    assert response.status_code == 200
    assert data["ok"] is True
    assert data["deleted"] == 0
    assert data["message"] == "History cleared"


def test_delete_history_returns_deleted_count():
    client.delete("/history")

    client.post("/calculate", params={"expr": "10+10"})
    client.post("/calculate", params={"expr": "20+20"})
    client.post("/calculate", params={"expr": "30+30"})

    response = client.delete("/history")
    data = response.json()

    assert response.status_code == 200
    assert data["ok"] is True
    assert data["deleted"] == 3


def test_delete_history_removes_all_records():
    client.delete("/history")

    client.post("/calculate", params={"expr": "100-25"})
    client.post("/calculate", params={"expr": "5*5"})

    delete_response = client.delete("/history")
    assert delete_response.status_code == 200

    history_response = client.get("/history")

    assert history_response.status_code == 200
    assert history_response.json() == []
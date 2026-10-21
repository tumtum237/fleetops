
import os

# Cette variable doit être définie AVANT les imports de l'application.
os.environ["DATABASE_URL"] = "sqlite:///./test_fleetops.db"

from fastapi.testclient import TestClient

from app.main import app
from app.models.database import Base, engine


def setup_function():
    # Réinitialise uniquement la base SQLite de test.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_create_and_list_vehicle():
    with TestClient(app) as client:
        payload = {
            "registration": "TEST-001",
            "brand": "Renault",
            "model": "Zoe",
            "status": "available",
        }

        create_response = client.post("/vehicles", json=payload)

        assert create_response.status_code == 201

        created_vehicle = create_response.json()
        assert created_vehicle["registration"] == "TEST-001"

        list_response = client.get("/vehicles")

        assert list_response.status_code == 200
        assert len(list_response.json()) == 1
        assert list_response.json()[0]["id"] == created_vehicle["id"]


def test_unknown_vehicle_returns_404():
    with TestClient(app) as client:
        response = client.get("/vehicles/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Vehicle not found"

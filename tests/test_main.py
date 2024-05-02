import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mongomock import MongoClient
from app.main import app  

client = TestClient(app)

def test_create_user():
    response = client.post("/users/", json={"name": "John", "email": "john@example.com"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "John", "email": "john@example.com"}

def test_get_user():
    response = client.get("/users/6631c0af6f0ce70070c8cfe0")
    print(response.content)
    assert response.status_code == 200
def test_update_user():
    response = client.put("/users/1", json={"name": "John Updated", "email": "johnupdated@example.com"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "John Updated", "email": "johnupdated@example.com"}
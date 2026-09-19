from fastapi.testclient import TestClient

from chief_of_staff.app import app
from chief_of_staff.generate import HeuristicGenerator
from chief_of_staff.prompts import StartupBrief


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_generate_does_not_invent_numbers():
    payload = {
        "brief": "We help independent clinics reduce missed appointments with automated reminders and patient follow-up.",
        "industry": "Healthcare",
        "stage": "Seed",
        "fundraising_goal": "Expand the product and sales team.",
    }
    response = client.post("/generate", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "clinics" in body["pitch_copy"].lower()
    assert body["evaluation"]["numeric_error"] is False
    assert body["evaluation"]["plain_text_compliant"] is True
    assert "{" not in body["pitch_copy"]


def test_plain_text_endpoint():
    response = client.post(
        "/generate.txt",
        json={"brief": "We coordinate CSA packing lists for weekly shares."},
    )
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "CSA" in response.text or "packing" in response.text.lower()


def test_homepage_renders():
    response = client.get("/")
    assert response.status_code == 200
    assert "Chief of Staff" in response.text


def test_heuristic_preserves_source_facts():
    brief = StartupBrief(
        brief="Tidebench lets chefs place wholesale seafood orders against what the dock actually landed that morning.",
        industry="Wholesale food",
        stage="Seed",
        fundraising_goal="Add more regional docks and invoice export.",
    )
    text = HeuristicGenerator().generate(brief)
    assert "Tidebench" in text or "seafood" in text.lower()
    assert "Seed" in text or "seed" in text

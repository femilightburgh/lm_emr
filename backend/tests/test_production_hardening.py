import importlib

from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_exists():
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_production_mode_disables_debug(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://lm_admin:lm_password@localhost:5432/lm_emr",
    )
    monkeypatch.setenv(
        "JWT_SECRET_KEY",
        "this-is-a-valid-production-secret-key-long-enough",
    )

    import app.core.config as config_module

    importlib.reload(config_module)
    settings = config_module.Settings()

    assert settings.app_env == "production"
    assert settings.debug is False

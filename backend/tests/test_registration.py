import pytest
import pandas as pd
from types import SimpleNamespace
from fastapi import HTTPException
from services.registration import lookup_registration  

@pytest.fixture
def fake_app():
    """Fake FastAPI app with rego_data"""
    class App:
        state = SimpleNamespace()
    return App()

# Test behavior when registration data is not loaded: ensures proper error if dataset is empty
def test_rego_data_empty(fake_app):
    """Should raise 500 if rego_data is empty"""
    fake_app.state.rego_data = pd.DataFrame()
    with pytest.raises(HTTPException) as exc:
        lookup_registration(fake_app, "ABC123")
    assert exc.value.status_code == 500
    assert "not loaded" in exc.value.detail

# Test lookup for registration that does not exist: ensures proper 404 error is raised
def test_registration_not_found(fake_app):
    """Should raise 404 if registration is not in the dataset"""
    df = pd.DataFrame({"Registration": ["XYZ999"], "Make": ["Toyota"]})
    fake_app.state.rego_data = df
    with pytest.raises(HTTPException) as exc:
        lookup_registration(fake_app, "ABC123")
    assert exc.value.status_code == 404
    assert "not found" in exc.value.detail

# Test successful registration lookup: ensures correct record is returned when registration exists
def test_registration_found(fake_app):
    """Should return record dict if registration exists"""
    df = pd.DataFrame({
        "Registration": ["ABC123", "XYZ999"],
        "Make": ["Toyota", "Honda"],
        "Model": ["Corolla", "Civic"]
    })
    fake_app.state.rego_data = df

    result = lookup_registration(fake_app, "ABC123")
    assert result["Registration"] == "ABC123"
    assert result["Make"] == "Toyota"
    assert result["Model"] == "Corolla"

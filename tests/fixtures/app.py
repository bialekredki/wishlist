import pytest
from fastapi.testclient import TestClient

from wishlist import initialize_application


@pytest.fixture(scope="session")
def client():
    yield TestClient(app=initialize_application())

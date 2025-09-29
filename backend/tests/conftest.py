import pytest
from httpx import AsyncClient
from server import create_app

@pytest.fixture(scope="session")
def app():
    return create_app()

@pytest.fixture(scope="session")
async def client(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

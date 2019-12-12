import pytest

from coin.app import app

"""
This client fixture will be called by each individual test.
"""


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_empty_db(client):
    pass
class TestNodes:
    def test_register_node(self):
        assert False

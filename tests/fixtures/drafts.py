import copy

import pytest


@pytest.fixture(name="list_draft_input_data")
def fixture_list_draft_input_data():
    return {
        "name": "Test List Draft",
        "draft": {
            "thumbnail": "test",
            "description": "no",
            "draft_items": [
                {
                    "thumbnail": "test",
                    "description": "none",
                    "price": None,
                    "name": "Test Item Draft",
                    "count": 5,
                    "min_price": 0
                    "max_price": 150
                }
            ]
        }
    }


@pytest.fixture
def list_draft_data_factory(list_draft_input_data):
    def _factory(input_data):
        data = copy.deepcopy(list_draft_input_data)
        data.update(input_data)
        return data
    return _factory

@pytest.fixture
def list_draft_factory(list_draft_input_data):
    def _factory(data):
        data = data or list_draft_input_data
        
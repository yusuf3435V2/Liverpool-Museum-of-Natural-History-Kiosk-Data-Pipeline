# pylint: skip-file
from Kafka_pipeline import (
    dict_message,
    validate_message,
    transform_message,
)


# dict_message tests

def test_dict_message_valid_json():
    raw_message = '{"at": "2026-04-27T15:00:03.502624+01:00", "site": "4", "val": 2}'

    result = dict_message(raw_message)

    assert result == {
        "at": "2026-04-27T15:00:03.502624+01:00",
        "site": "4",
        "val": 2,
    }


def test_dict_message_invalid_json_returns_none():
    raw_message = "this is not valid json"

    result = dict_message(raw_message)

    assert result is None

# validate_message tests


def test_validate_message_accepts_valid_rating_message():
    message = {
        "at": "2026-04-27T15:00:03.502624+01:00",
        "site": "4",
        "val": 2,
    }

    result = validate_message(message)

    assert result is True


def test_validate_message_rejects_invalid_rating_value():
    message = {
        "at": "2026-04-27T15:00:03.502624+01:00",
        "site": "4",
        "val": 9,
    }

    result = validate_message(message)

    assert result is False

# transform_message tests


def test_transform_message_valid_rating_message():
    message = {
        "at": "2026-04-27T15:00:03.502624+01:00",
        "site": "4",
        "val": 2,
    }

    result = transform_message(message)

    assert result == {
        "exhibition_id": 4,
        "rating_value": 2,
        "type": None,
        "at": "27/04/26",
    }


def test_transform_message_valid_alert_message():
    message = {
        "at": "2026-04-27T15:00:03.502624+01:00",
        "site": "4",
        "val": -1,
        "type": 1,
    }

    result = transform_message(message)

    assert result == {
        "exhibition_id": 4,
        "rating_value": -1,
        "type": 1,
        "at": "27/04/26",
    }

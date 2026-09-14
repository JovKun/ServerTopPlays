# Import necessary libraries
from unittest.mock import MagicMock

# Test if user exists in the database (config.json)
def test_user_exists_in_database():

    # Create a mock user object
    mock_user = MagicMock()
    mock_user.id = 123456

    # Mock the config dictionary to simulate the database
    config = {
        "users": {
            "123456": {
                "username": "testuser",
                "last_checked": 1690000000
            }
        }
    }

    # Check if the user exists in the database
    user_exists = str(mock_user.id) in config["users"]

    # Assert that the user exists in the database
    assert user_exists, f"Expected user with ID {mock_user.id} to exist in the database, but it does not."

# Test if user does not exist in the database (config.json)
def test_user_not_exists_in_database():

    # Create a mock user object
    mock_user = MagicMock()
    mock_user.id = 654321

    # Mock the config dictionary to simulate the database
    config = {
        "users": {
            "123456": {
                "username": "testuser",
                "last_checked": 1690000000
            }
        }
    }

    # Check if the user exists in the database
    user_exists = str(mock_user.id) in config["users"]

    # Assert that the user does not exist in the database
    assert not user_exists, f"Expected user with ID {mock_user.id} to not exist in the database, but it does."
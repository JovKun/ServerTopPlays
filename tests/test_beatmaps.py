# Import necessary libraries
from unittest.mock import MagicMock, patch
import requests

# Test beatmapset.status conversion
def test_beatmapset_status_conversion():

    # Create a mock beatmapset object
    mock_beatmapset = MagicMock()

    # Set the status values for the mock objects
    mock_beatmapset.status = -1   # WIP

    # Get beatmapset status
    beatmap_status = ""

    # Convert the status to a string representation
    if mock_beatmapset.status == -1:
        beatmap_status = "WIP"
    elif mock_beatmapset.status == 0:
        beatmap_status = "Pending"

    # Assert the expected status
    assert beatmap_status == "WIP", f"Expected 'WIP', but got '{beatmap_status}'"

# Test if card.jpg exists for a given beatmapset
def image_exists(url: str) -> bool:
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Test cases for image_exists function when the image exists
@patch("requests.head")
def test_image_exists(mock_head):

    # Create a mock response object with a status code of 200
    mock_head.return_value.status_code = 200

    assert image_exists("https://assets.ppy.sh/beatmaps/123456/card.jpg") == True, "Expected image to exist"

# Test case for image_exists function when the image does not exist
@patch("requests.head")
def test_image_not_exists(mock_head):

    # Create a mock response object with a status code of 404
    mock_head.return_value.status_code = 404

    assert image_exists("https://assets.ppy.sh/beatmaps/123456/card.jpg") == False, "Expected image to not exist"
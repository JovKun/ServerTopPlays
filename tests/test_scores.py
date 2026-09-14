# Import necessary libraries
from unittest.mock import MagicMock

# Test score mods conversion for multiple mods
def test_score_mods_conversion_multiple_mods():

    # current_user.mods = [LazerMod(mod = "HD", settings = None), LazerMod(mod = "HR", settings = None)]

    # Create the mock current_user object with mods
    current_user = MagicMock()
    mod_1 = MagicMock()
    mod_2 = MagicMock()

    mod_1.mod.value = "HD"
    mod_2.mod.value = "HR"

    current_user.mods = [mod_1, mod_2]

    # Convert the mods to a string representation
    user_mods = "".join([lazermod.mod.value for lazermod in current_user.mods])
    user_mods = user_mods if user_mods != "" else "NM"

    # Assert the expected mods string
    assert user_mods == "HDHR", f"Expected 'HDHR', but got '{user_mods}'"

# Test score mods conversion for no mods
def test_score_mods_conversion_no_mods():

    # Create the mock current_user object with no mods
    current_user = MagicMock()
    current_user.mods = []

    # Convert the mods to a string representation
    user_mods = "".join([lazermod.mod.value for lazermod in current_user.mods])
    user_mods = user_mods if user_mods != "" else "NM"

    # Assert the expected mods string
    assert user_mods == "NM", f"Expected 'NM', but got '{user_mods}'"

# Test score mods conversion for a single mod
def test_score_mods_conversion_single_mod():

    # Create the mock current_user object with a single mod
    current_user = MagicMock()
    mod_1 = MagicMock()
    mod_1.mod.value = "DT"

    current_user.mods = [mod_1]

    # Convert the mods to a string representation
    user_mods = "".join([lazermod.mod.value for lazermod in current_user.mods])
    user_mods = user_mods if user_mods != "" else "NM"

    # Assert the expected mods string
    assert user_mods == "DT", f"Expected 'DT', but got '{user_mods}'"

# Test score rank conversion
def test_score_rank_conversion():

    # Create the mock score object with a rank
    mock_score = MagicMock()
    mock_score.rank = "A"
    user_rank = mock_score.rank

    # Convert the rank to a string representation
    if user_rank == "D":
        user_rank = "<:D_nn:1330334959222788236>"
    elif user_rank == "C":
        user_rank = "<:C_nn:1330334958027538513>"
    elif user_rank == "B":
        user_rank = "<:B_nn:1330334956961923143>"
    elif user_rank == "A":
        user_rank = "<:A_nn:1330334955418681345>"
    elif user_rank == "S":
        user_rank = "<:S_nn:1330334960460103722>"
    elif user_rank == "SH":
        user_rank = "<:SH_nn:1330334960460103722>"
    elif user_rank == "X":
        user_rank = "<:SS_nn:1330334962972364873>"
    elif user_rank == "XH":
        user_rank = "<:SSH_nn:1330334962972364873>"

    # Assert the expected rank
    assert user_rank == "<:A_nn:1330334955418681345>", f"Expected 'A', but got '{user_rank}'"

# Test score miss conversion
def test_score_miss_conversion():

    # Create the mock score object with a miss count
    mock_score = MagicMock()
    mock_score.statistics.miss = 5

    # Convert the miss count to a string representation
    count_miss = "" if mock_score.statistics.miss is None else str(mock_score.statistics.miss) + "<:miss_nn:1330340826492047481>"

    # Assert the expected miss count
    assert count_miss == "5<:miss_nn:1330340826492047481>", f"Expected '5', but got '{count_miss}'"
from unittest.mock import MagicMock, mock_open, patch

import pytest

from steam_vdf import users


class TestUsers:
    @pytest.fixture
    def mock_loginusers_vdf_data(self):
        return {
            "users": {
                "76561197960287930": {  # Example Steam64 ID
                    "AccountName": "testuser",
                    "PersonaName": "Test User",
                },
                "76561197960287931": {  # Example Steam64 ID
                    "AccountName": "testuser2",
                    "PersonaName": "Test User 2",
                },
            }
        }

    @pytest.fixture
    def mock_config_vdf_data(self):
        return {
            "InstallConfigStore": {
                "Software": {
                    "Valve": {
                        "Steam": {
                            "Accounts": {
                                "testuser": {
                                    "PersonaName": "Test User",
                                    "AccountName": "testuser",
                                }
                            }
                        }
                    }
                }
            }
        }

    @pytest.fixture
    def mock_shortcuts_vdf_data(self):
        return {
            "shortcuts": {
                0: {
                    "AppName": "Custom Game 1",
                    "Exe": '"/path/to/game1.exe"',
                    "StartDir": '"/path/to/game1"',
                    "appid": 123456,
                },
                1: {
                    "AppName": "Custom Game 2",
                    "Exe": '"/path/to/game2.exe"',
                    "StartDir": '"/path/to/game2"',
                    "appid": 234567,
                },
            }
        }

    def test_get_steam_user_names(
        self, mock_loginusers_vdf_data, mock_config_vdf_data
    ):
        with patch("os.path.exists", return_value=True), patch(
            "vdf.load"
        ) as mock_vdf_load, patch("builtins.open", mock_open()):

            # Set up the mock to return different values for different files
            mock_vdf_load.side_effect = [
                mock_loginusers_vdf_data,
                mock_config_vdf_data,
            ]

            args = MagicMock()
            result = users.get_steam_user_names(args, "/fake/steam/path")

            expected = {
                "76561197960287930": {
                    "PersonaName": "Test User",
                    "AccountName": "testuser",
                    "Steam32ID": "22202",
                },
                "76561197960287931": {
                    "PersonaName": "Test User 2",
                    "AccountName": "testuser2",
                    "Steam32ID": "22203",
                },
                "22202": {
                    "PersonaName": "Test User",
                    "AccountName": "testuser",
                    "Steam64ID": "76561197960287930",
                },
                "22203": {
                    "PersonaName": "Test User 2",
                    "AccountName": "testuser2",
                    "Steam64ID": "76561197960287931",
                },
                "testuser": {
                    "PersonaName": "Test User",
                    "AccountName": "testuser",
                    "Steam64ID": None,
                },
            }
            assert result == expected

    @pytest.mark.parametrize("userdata_exists", [True, False])
    def test_list_shortcuts(self, userdata_exists, mock_shortcuts_vdf_data):
        with patch("os.path.exists") as mock_exists, patch(
            "os.listdir"
        ) as mock_listdir, patch("os.path.isdir") as mock_isdir, patch(
            "vdf.binary_load", return_value=mock_shortcuts_vdf_data
        ), patch(
            "steam_vdf.users.get_steam_user_names",
            return_value={
                "12345": {
                    "PersonaName": "Test User",
                    "AccountName": "testuser",
                }
            },
        ):

            mock_exists.return_value = userdata_exists
            mock_listdir.return_value = ["12345"]
            mock_isdir.return_value = True

            args = MagicMock()
            args.user = None

            result = users.list_shortcuts(args, "/fake/steam/path")

            if userdata_exists:
                assert result is True
            else:
                assert result is False

    def test_list_shortcuts_specific_user(self, mock_shortcuts_vdf_data):
        with patch("os.path.exists") as mock_exists, patch(
            "os.listdir"
        ) as mock_listdir, patch("os.path.isdir") as mock_isdir, patch(
            "vdf.binary_load", return_value=mock_shortcuts_vdf_data
        ), patch(
            "steam_vdf.users.get_steam_user_names",
            return_value={
                "12345": {
                    "PersonaName": "Test User",
                    "AccountName": "testuser",
                }
            },
        ):

            mock_exists.return_value = True
            mock_listdir.return_value = ["12345"]
            mock_isdir.return_value = True

            args = MagicMock()
            args.user = "12345"

            result = users.list_shortcuts(args, "/fake/steam/path")
            assert result is True

    def test_list_shortcuts_no_userdata(self):
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = False

            args = MagicMock()
            result = users.list_shortcuts(args, "/fake/steam/path")
            assert result is False

    @pytest.mark.parametrize("shortcuts_file_exists", [True, False])
    def test_list_shortcuts_with_shortcuts_file(
        self, shortcuts_file_exists, mock_shortcuts_vdf_data
    ):
        with patch("os.path.exists") as mock_exists, patch(
            "os.listdir"
        ) as mock_listdir, patch("os.path.isdir") as mock_isdir, patch(
            "vdf.binary_load", return_value=mock_shortcuts_vdf_data
        ), patch(
            "steam_vdf.users.get_steam_user_names",
            return_value={
                "12345": {
                    "PersonaName": "Test User",
                    "AccountName": "testuser",
                }
            },
        ):

            mock_exists.side_effect = lambda x: (
                not x.endswith("shortcuts.vdf")
                if not shortcuts_file_exists
                else True
            )
            mock_listdir.return_value = ["12345"]
            mock_isdir.return_value = True

            args = MagicMock()
            args.user = "12345"

            result = users.list_shortcuts(args, "/fake/steam/path")

            if shortcuts_file_exists:
                assert result is True
            else:
                assert (
                    result is True
                )  # Because the function continues even if shortcuts.vdf doesn't exist

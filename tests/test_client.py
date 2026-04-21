from unittest.mock import MagicMock, patch

import pytest

import pynormanshutters
from pynormanshutters import Client, login, FULLY_OPEN_POSITION


class TestClient:
    def setup_method(self):
        self.client = Client("192.168.1.100", "test-session-token")

    def _mock_post(self, return_value):
        mock_response = MagicMock()
        mock_response.json.return_value = return_value
        self.client.session.post = MagicMock(return_value=mock_response)
        return mock_response

    def test_get_window_info(self):
        expected = {"data": [{"id": 1, "name": "Living Room"}]}
        self._mock_post(expected)

        result = self.client.get_window_info()

        self.client.session.post.assert_called_once_with(
            "http://192.168.1.100/cgi-bin/cgi/getWindowInfo",
            headers=pynormanshutters.HEADERS,
        )
        assert result == expected

    def test_get_room_info(self):
        expected = {"data": [{"id": 2, "name": "Bedroom"}]}
        self._mock_post(expected)

        result = self.client.get_room_info()

        self.client.session.post.assert_called_once_with(
            "http://192.168.1.100/cgi-bin/cgi/getRoomInfo",
            headers=pynormanshutters.HEADERS,
        )
        assert result == expected

    def test_get_scene_info(self):
        expected = {"data": []}
        self._mock_post(expected)

        result = self.client.get_scene_info()

        self.client.session.post.assert_called_once_with(
            "http://192.168.1.100/cgi-bin/cgi/getSceneInfo",
            headers=pynormanshutters.HEADERS,
        )
        assert result == expected

    def test_get_schedule_info(self):
        expected = {"data": []}
        self._mock_post(expected)

        result = self.client.get_schedule_info()

        self.client.session.post.assert_called_once_with(
            "http://192.168.1.100/cgi-bin/cgi/getScheduleInfo",
            headers=pynormanshutters.HEADERS,
        )
        assert result == expected

    def test_remote_control_posts_body(self):
        expected = {"result": "ok"}
        self._mock_post(expected)
        body = {"type": "fullclose", "action": 1}

        result = self.client._remote_control(body)

        self.client.session.post.assert_called_once_with(
            "http://192.168.1.100/cgi-bin/cgi/RemoteControl",
            headers=pynormanshutters.HEADERS,
            json=body,
        )
        assert result == expected

    def test_fullclose(self):
        with patch.object(self.client, "_remote_control", return_value={"result": "ok"}) as mock_rc:
            result = self.client.fullclose()
            mock_rc.assert_called_once_with({"type": "fullclose", "action": 1})
            assert result == {"result": "ok"}

    def test_fullopen(self):
        with patch.object(self.client, "_remote_control", return_value={"result": "ok"}) as mock_rc:
            self.client.fullopen()
            mock_rc.assert_called_once_with({"type": "fullopen", "action": 1})

    def test_open_window(self):
        with patch.object(self.client, "_remote_control", return_value={}) as mock_rc:
            self.client.open_window(42)
            mock_rc.assert_called_once_with(
                {"type": "fullopen", "action": 4, "id": 42}
            )

    def test_close_window(self):
        with patch.object(self.client, "_remote_control", return_value={}) as mock_rc:
            self.client.close_window(42)
            mock_rc.assert_called_once_with(
                {"type": "fullclose", "action": 4, "id": 42}
            )

    def test_set_window_position(self):
        with patch.object(self.client, "_remote_control", return_value={}) as mock_rc:
            self.client.set_window_position(42, 20)
            mock_rc.assert_called_once_with(
                {"type": "window", "action": 1, "id": 42, "position": 20}
            )

    def test_set_window_position_fully_open(self):
        with patch.object(self.client, "_remote_control", return_value={}) as mock_rc:
            self.client.set_window_position(5, FULLY_OPEN_POSITION)
            mock_rc.assert_called_once_with(
                {"type": "window", "action": 1, "id": 5, "position": FULLY_OPEN_POSITION}
            )

    def test_client_sets_session_cookie(self):
        client = Client("10.0.0.1", "my-cookie")
        assert client.session.cookies.get("Session") == "my-cookie"
        assert client.addr == "10.0.0.1"


class TestLogin:
    def test_login_posts_correct_url_and_password(self):
        mock_response = MagicMock()
        mock_response.cookies.get.return_value = "returned-session"

        with patch("requests.post", return_value=mock_response) as mock_post:
            login("192.168.1.50")

            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert "192.168.1.50" in call_args[0][0]
            assert call_args[1]["json"]["password"] == pynormanshutters.DEFAULT_PASSWORD

    def test_login_returns_client_with_session(self):
        mock_response = MagicMock()
        mock_response.cookies.get.return_value = "session-abc"

        with patch("requests.post", return_value=mock_response):
            client = login("192.168.1.50")

        assert isinstance(client, Client)
        assert client.addr == "192.168.1.50"
        assert client.session.cookies.get("Session") == "session-abc"

    @pytest.mark.parametrize("addr", ["192.168.1.1", "10.0.0.5", "172.16.0.100"])
    def test_login_uses_provided_address(self, addr):
        mock_response = MagicMock()
        mock_response.cookies.get.return_value = "tok"

        with patch("requests.post", return_value=mock_response) as mock_post:
            login(addr)

        assert addr in mock_post.call_args[0][0]

import argparse
import json
import queue
import requests
import zeroconf

HEADERS = {
    "Content-Type": "application/json"
}
DEFAULT_PASSWORD = "123456789"
SERVICE_NAME_PREFIX = "NORMANHUB_"

# The hub reports this position value when shutters are fully open.
# Confirmed empirically: fullopen() drives all shutters to position 37.
FULLY_OPEN_POSITION = 37
FULLY_CLOSED_POSITION = 100


def discover(wait_secs=1):
    addrs = queue.Queue(maxsize=0)

    class Listener:
        def add_service(self, zeroconf, type, name):
            if not name.startswith(SERVICE_NAME_PREFIX):
                return

            info = zeroconf.get_service_info(type, name)
            if not info:
                return

            addrs.put(info.parsed_addresses()[0])

        def remove_service(self, zeroconf, type, name):
            pass

        def update_service(self, zc, type_, name):
            pass

    session = zeroconf.Zeroconf()
    listener = Listener()
    zeroconf.ServiceBrowser(session, "_http._tcp.local.", listener)

    try:
        addr = addrs.get(timeout=wait_secs)
    finally:
        session.close()

    return addr


def login(addr):
    body = {
        "password": DEFAULT_PASSWORD,
        "app_version": "2.11.21",
    }
    r = requests.post("http://%s/cgi-bin/cgi/GatewayLogin" % addr, headers=HEADERS, json=body)
    return Client(addr, r.cookies.get("Session"))


class Client:
    def __init__(self, addr, session):
        self.addr = addr
        self.session = requests.Session()
        self.session.cookies.set("Session", session)

    def get_window_info(self):
        url = "http://%s/cgi-bin/cgi/getWindowInfo" % self.addr
        response = self.session.post(url, headers=HEADERS)
        return response.json()

    def get_room_info(self):
        url = "http://%s/cgi-bin/cgi/getRoomInfo" % self.addr
        response = self.session.post(url, headers=HEADERS)
        return response.json()

    def get_scene_info(self):
        url = "http://%s/cgi-bin/cgi/getSceneInfo" % self.addr
        response = self.session.post(url, headers=HEADERS)
        return response.json()

    def get_schedule_info(self):
        url = "http://%s/cgi-bin/cgi/getScheduleInfo" % self.addr
        response = self.session.post(url, headers=HEADERS)
        return response.json()

    def _remote_control(self, body: dict):
        url = "http://%s/cgi-bin/cgi/RemoteControl" % self.addr
        response = self.session.post(url, headers=HEADERS, json=body)
        return response.json()

    def fullclose(self):
        return self._remote_control({"type": "fullclose", "action": 1})

    def fullopen(self):
        return self._remote_control({"type": "fullopen", "action": 1})

    def open_window(self, window_id: int):
        """Open a single window by its Id (from get_window_info)."""
        return self._remote_control({"type": "window", "action": 1, "id": window_id, "position": FULLY_OPEN_POSITION})

    def close_window(self, window_id: int):
        """Close a single window by its Id (from get_window_info)."""
        return self._remote_control({"type": "window", "action": 1, "id": window_id, "position": FULLY_CLOSED_POSITION})

    def set_window_position(self, window_id: int, position: int):
        """Set slat position (0-FULLY_OPEN_POSITION) for a single window by its Id."""
        return self._remote_control({"type": "window", "action": 1, "id": window_id, "position": position})


# CLI implementation
def main():
    parser = argparse.ArgumentParser(description="Motorized Shutters CLI")
    parser.add_argument(
        "command",
        choices=[
            "get_window_info", "get_room_info", "get_scene_info", "get_schedule_info",
            "fullclose", "fullopen",
            "open_window", "close_window", "set_window_position",
        ],
        help="Command to execute",
    )
    parser.add_argument("--id", type=int, help="Window Id for per-window commands (see get_window_info)")
    parser.add_argument("--position", type=int, help="Position value for set_window_position")
    args = parser.parse_args()

    addr = discover()
    if addr is None:
        print("no norman hubs found")
        return

    client = login(addr)

    if args.command == "get_window_info":
        result = client.get_window_info()
    elif args.command == "get_room_info":
        result = client.get_room_info()
    elif args.command == "get_scene_info":
        result = client.get_scene_info()
    elif args.command == "get_schedule_info":
        result = client.get_schedule_info()
    elif args.command == "fullclose":
        result = client.fullclose()
    elif args.command == "fullopen":
        result = client.fullopen()
    elif args.command == "open_window":
        if args.id is None:
            parser.error("--id required for open_window")
        result = client.open_window(args.id)
    elif args.command == "close_window":
        if args.id is None:
            parser.error("--id required for close_window")
        result = client.close_window(args.id)
    elif args.command == "set_window_position":
        if args.id is None or args.position is None:
            parser.error("--id and --position required for set_window_position")
        result = client.set_window_position(args.id, args.position)
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()

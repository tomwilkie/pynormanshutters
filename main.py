import argparse
import json
import queue
import requests
import time
import zeroconf

HEADERS = {
    "Content-Type": "application/json"
}
DEFAULT_PASSWORD = "123456789"
SERVICE_NAME_PREFIX = "NORMANHUB_"

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
    r = requests.post(f"http://%s/cgi-bin/cgi/GatewayLogin" % addr, headers=HEADERS, json=body)
    return Client(addr, r.cookies.get("Session"))

class Client:
    def __init__(self, addr, session):
        self.addr = addr
        self.session = requests.Session()
        self.session.cookies.set("Session", session)

    def get_window_info(self):
        url = f"http://%s/cgi-bin/cgi/getWindowInfo" % self.addr
        response = self.session.post(url, headers=HEADERS)
        return response.json()

    def get_room_info(self):
        url = f"http://%s/cgi-bin/cgi/getRoomInfo" % self.addr
        response = self.session.post(url, headers=HEADERS)
        return response.json()

    def get_scene_info(self):
        url = f"http://%s/cgi-bin/cgi/getSceneInfo" % self.addr
        response = self.session.post(url, headers=HEADERS)
        return response.json()

    def get_schedule_info(self):
        url = f"http://%s/cgi-bin/cgi/getScheduleInfo" % self.addr
        response = self.session.post(url, headers=HEADERS)
        return response.json()

    def fullclose(self):
        url = f"http://%s/cgi-bin/cgi/RemoteControl" % self.addr
        response = self.session.post(url, headers=HEADERS, json={
            "type": "fullclose",
            "action": 1,
        })
        return response.json()

    def fullopen(self):
        url = f"http://%s/cgi-bin/cgi/RemoteControl" % self.addr
        response = self.session.post(url, headers=HEADERS, json={
            "type": "fullopen",
            "action": 1,
        })
        return response.json()

# CLI implementation
def main():
    parser = argparse.ArgumentParser(description="Motorized Shutters CLI")
    parser.add_argument("command", choices=["get_window_info", "get_room_info", "get_scene_info", "get_schedule_info", "fullclose", "fullopen"], help="Command to execute")
    args = parser.parse_args()

    addr = discover()
    if addr is None:
        print("no norman hubs found")

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

    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
import argparse
import json
import requests

headers = {
    "Content-Type": "application/json"
}

def login(addr):
    body = {
        "password": "123456789",
        "app_version": "2.11.21",
    }
    r = requests.post(f"http://%s/cgi-bin/cgi/GatewayLogin" % addr, headers=headers, json=body)
    return Client(addr, r.cookies.get("Session"))

class Client:
    def __init__(self, addr, session):
        self.addr = addr
        self.session = requests.Session()
        self.session.cookies.set("Session", session)

    def get_window_info(self):
        url = f"http://%s/cgi-bin/cgi/getWindowInfo" % self.addr
        response = self.session.post(url, headers=headers)
        return response.json()

    def get_room_info(self):
        url = f"http://%s/cgi-bin/cgi/getRoomInfo" % self.addr
        response = self.session.post(url, headers=headers)
        return response.json()

    def get_scene_info(self):
        url = f"http://%s/cgi-bin/cgi/getSceneInfo" % self.addr
        response = self.session.post(url, headers=headers)
        return response.json()

    def get_schedule_info(self):
        url = f"http://%s/cgi-bin/cgi/getScheduleInfo" % self.addr
        response = self.session.post(url, headers=headers)
        return response.json()

    def fullclose(self):
        url = f"http://%s/cgi-bin/cgi/RemoteControl" % self.addr
        response = self.session.post(url, headers=headers, json={
            "type": "fullclose",
            "action": 1,
        })
        return response.json()

    def fullopen(self):
        url = f"http://%s/cgi-bin/cgi/RemoteControl" % self.addr
        response = self.session.post(url, headers=headers, json={
            "type": "fullopen",
            "action": 1,
        })
        return response.json()

# CLI implementation
def main():
    parser = argparse.ArgumentParser(description="Motorized Shutters CLI")
    parser.add_argument("address", help="Address of the motorized shutters system")
    parser.add_argument("command", choices=["get_window_info", "get_room_info", "get_scene_info", "get_schedule_info", "fullclose", "fullopen"], help="Command to execute")

    args = parser.parse_args()

    client = login(args.address)
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
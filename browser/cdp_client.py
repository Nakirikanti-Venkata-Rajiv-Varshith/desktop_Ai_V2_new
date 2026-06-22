import requests
import websocket
import json


class CDPClient:

    def __init__(self):

        self.ws = None
        self.msg_id = 0

    def connect(self):

        try:
            tabs = requests.get(
                "http://localhost:9222/json"
            ).json()
        except Exception:
            raise Exception("Could not reach Chromium debug port 9222. Is browser running?")

        if not tabs:
            raise Exception(
                "No Chromium tabs found"
            )

        target_tab = None

        # Prioritize connecting to a YouTube tab if one exists
        for tab in tabs:
            if (
                tab.get("type") == "page"
                and "youtube.com" in tab.get("url", "")
            ):
                target_tab = tab
                break

        # Fallback: Connect to any active webpage tab available
        if not target_tab:
            for tab in tabs:
                if tab.get("type") == "page":
                    target_tab = tab
                    break

        if not target_tab:
            raise Exception(
                "No valid browser target pages found to attach."
            )

        ws_url = target_tab[
            "webSocketDebuggerUrl"
        ]

        self.ws = websocket.create_connection(
            ws_url
        )

        print(
            f"[CDP] Connected to target tab: {target_tab.get('url')}"
        )

    def send(self, method, params=None):

        if params is None:
            params = {}

        self.msg_id += 1

        payload = {
            "id": self.msg_id,
            "method": method,
            "params": params
        }

        self.ws.send(
            json.dumps(payload)
        )

        while True:

            response = json.loads(
                self.ws.recv()
            )

            if response.get("id") == self.msg_id:
                return response

    def execute_js(self, script):

        response = self.send(
            "Runtime.evaluate",
            {
                "expression": script,
                "returnByValue": True
            }
        )

        try:

            return response[
                "result"
            ][
                "result"
            ][
                "value"
            ]

        except Exception:

            return response
        
    def run_js(self, script):

        response = self.send(
            "Runtime.evaluate",
            {
                "expression": script,
                "returnByValue": True
            }
        )

        try:
            return response[
                "result"
            ][
                "result"
            ][
                "value"
            ]

        except Exception:
            return response
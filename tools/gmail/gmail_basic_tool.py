import time
import json
import requests
import websocket
import sys

from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

from browser.focus import focus_chromium
from tools.browser.tool import BrowserTool
from utils.global_events import event_bus

class GmailBasicTool:

    def __init__(self, debug_port=9222):
        self.debug_url = f"http://localhost:{debug_port}/json"
        self.ws = None
        self.msg_id = 0

    def _connect_to_tab(self, mail_only=True):
        """Internal helper to connect websocket debugging protocol to the active Gmail tab."""
        try:
            tabs = requests.get(self.debug_url, timeout=2).json()
        except Exception:
            return False

        target_tab = None
        
        # Look specifically for an existing Gmail tab
        for tab in tabs:
            if tab.get("type") == "page" and "mail.google.com" in tab.get("url", ""):
                target_tab = tab
                break

        # Fallback to any active page if we aren't strictly enforcing mail_only
        if not target_tab and not mail_only:
            for tab in tabs:
                if tab.get("type") == "page" and "webSocketDebuggerUrl" in tab:
                    target_tab = tab
                    break

        if not target_tab:
            return False

        try:
            ws_url = target_tab["webSocketDebuggerUrl"]
            self.ws = websocket.create_connection(ws_url)
            return True
        except Exception:
            return False

    def send_cdp(self, method, params=None):
        if params is None:
            params = {}
        self.msg_id += 1
        payload = {"id": self.msg_id, "method": method, "params": params}
        self.ws.send(json.dumps(payload))
        
        # Block until the matching response ID is captured
        while True:
            response = json.loads(self.ws.recv())
            if response.get("id") == self.msg_id:
                return response

    def execute_js(self, script):
        response = self.send_cdp("Runtime.evaluate", {"expression": script, "returnByValue": True})
        try:
            return response["result"]["result"]["value"]
        except Exception:
            return response

    # @staticmethod
    # def open():
    #     """Fast-path command specifically just to open the UI."""
    #     from tools.browser.tool import BrowserTool
    #     BrowserTool.open_url("https://mail.google.com")
    #     return "Gmail Opened"

    @staticmethod
    def open():

        event_bus.emit(
            "Opening Gmail"
        )

        BrowserTool.open_url(
            "https://mail.google.com"
        )

        event_bus.emit(
            "Gmail opened"
        )

        return "Gmail Opened"

    def compose_email(self, recipient: str, subject: str | None = None, body: str | None = None):
        """
        Brings Chromium into focus, ensures Gmail is open, clicks compose,
        and cleanly populates the email recipient, subject, and message body.
        """
        focus_chromium()
        time.sleep(0.5)
        
        # =========================================================
        # CRITICAL FIX: Ensure Gmail is actually open and loaded!
        # =========================================================
        if not self._connect_to_tab(mail_only=True):
            from tools.browser.tool import BrowserTool
            # Force the browser to open Gmail using PyAutoGUI shortcut
            BrowserTool.open_url("https://mail.google.com")
            
            # Wait a generous amount of time for Gmail's heavy dashboard to fully load
            time.sleep(8.0) 
            
            # Try connecting again now that it is loaded
            if not self._connect_to_tab(mail_only=True):
                return {"status": "ERROR", "message": "Failed to hook into Gmail tab after navigating."}

        # Step 1: Trigger the Compose popup button
        compose_script = """
        (() => {
            // Check if a compose box is already open on screen to avoid double-clicking
            if (document.querySelector('[aria-label="Message Body"], .Am')) {
                return "ALREADY_OPEN";
            }
            const composeSelectors = ['.T-I-KE', '[role="button"][gh="cm"]', '.z0 > .T-I'];
            for (const selector of composeSelectors) {
                const btn = document.querySelector(selector);
                if (btn) {
                    btn.click();
                    return "SUCCESS_COMPOSE_CLICKED";
                }
            }
            return "ERROR_COMPOSE_NOT_FOUND";
        })()
        """
        compose_status = self.execute_js(compose_script)
        if "ERROR" in str(compose_status):
            return {"status": "ERROR", "message": f"Failed to locate compose element: {compose_status}"}

        # Give the compose popup window a moment to animate and render
        time.sleep(2.5)

        # Step 2: Write details cleanly into input targets
        write_script = f"""
        (() => {{
            // 1. Populate the "To" Recipient field
            const toField = document.querySelector('input[peoplekit-id], input[name="to"], input.agP');
            if (toField) {{
                toField.focus();
                document.execCommand('insertText', false, {json.dumps(recipient)});
                // Simulate hitting Enter to lock in the email address chip
                toField.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', keyCode: 13, bubbles: true }}));
            }} else {{
                return "ERROR_TO_FIELD_NOT_FOUND";
            }}

            // 2. Populate the "Subject" field
            const subjField = document.querySelector('input[name="subjectbox"], .aoT');
            if (subjField) {{
                subjField.focus();
                document.execCommand('insertText', false, {json.dumps(subject)});
            }} else {{
                return "ERROR_SUBJECT_FIELD_NOT_FOUND";
            }}

            // 3. Populate the "Message Body" textbox
            const bodyField = document.querySelector('[role="textbox"][aria-label="Message Body"], .Am');
            if (bodyField) {{
                bodyField.focus();
                document.execCommand('insertText', false, {json.dumps(body)});
            }} else {{
                return "ERROR_BODY_FIELD_NOT_FOUND";
            }}

            return "SUCCESS_EMAIL_COMPOSED";
        }})()
        """
        
        comp_status = self.execute_js(write_script)
        if comp_status != "SUCCESS_EMAIL_COMPOSED":
            return {"status": "ERROR", "message": f"Data entry injection failure: {comp_status}"}

        time.sleep(1.5) 

        # Step 3: Click the Send button
        transmit_script = """
        (() => {
            const sendSelectors = ['.T-I-atl', '.aoO', '[aria-label*="Send"]'];
            for (const s of sendSelectors) {
                const sendBtn = document.querySelector(s);
                if (sendBtn) {
                    sendBtn.click();
                    return "SUCCESS_EMAIL_SENT";
                }
            }
            return "ERROR_SEND_BUTTON_NOT_FOUND";
        })()
        """
        send_status = self.execute_js(transmit_script)
        if send_status != "SUCCESS_EMAIL_SENT":
            return {"status": "ERROR", "message": f"Send transmission action failed: {send_status}"}

        # Close the websocket cleanly when finished
        if self.ws:
            self.ws.close()

        return {"status": "SUCCESS", "message": "Email composed and transmitted successfully."}

    def schedule_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        time: str
    ):
        """
        Schedule an email using Gmail's native schedule-send.
        time format expected:
        14:00
        09:30
        18:45
        """

        try:

            now = datetime.now()

            target_time = datetime.strptime(
                time,
                "%H:%M"
            ).replace(
                year=now.year,
                month=now.month,
                day=now.day
            )

            if target_time <= now:
                target_time += timedelta(days=1)

            target_date_str = target_time.strftime(
                "%B %d, %Y"
            )

            target_hour_str = target_time.strftime(
                "%I:%M %p"
            )

            with sync_playwright() as p:

                browser = p.chromium.connect_over_cdp(
                    "http://localhost:9222"
                )

                context = browser.contexts[0]

                gmail_page = next(
                    (
                        page
                        for page in context.pages
                        if "mail.google.com" in page.url
                    ),
                    None
                )

                if not gmail_page:

                    gmail_page = context.new_page()

                    gmail_page.goto(
                        "https://mail.google.com"
                    )

                    gmail_page.wait_for_timeout(
                        5000
                    )

                # ==================================================
                # OPEN COMPOSE
                # ==================================================

                gmail_page.evaluate(
                    """
                    () => {
                        let composeBtn =
                            document.querySelector(
                                'div[role="button"][gh="cm"]'
                            ) ||
                            document.querySelector(
                                '.T-I.T-I-KE.L3'
                            );

                        if (composeBtn) {
                            composeBtn.focus();
                            composeBtn.click();
                        }
                    }
                    """
                )

                gmail_page.wait_for_timeout(
                    2000
                )

                # ==================================================
                # FILL EMAIL
                # ==================================================

                gmail_page.evaluate(
                    """
                    ([rec, sub, bod]) => {

                        let toField =
                            document.querySelector(
                                'input[peoplekit-id], textarea[aria-label="To"], input[aria-label="To"], textarea[name="to"]'
                            );

                        if (toField) {

                            toField.focus();

                            document.execCommand(
                                'insertText',
                                false,
                                rec
                            );

                            toField.dispatchEvent(
                                new KeyboardEvent(
                                    'keydown',
                                    {
                                        bubbles: true,
                                        cancelable: true,
                                        key: 'Enter',
                                        keyCode: 13
                                    }
                                )
                            );
                        }

                        let subjField =
                            document.querySelector(
                                'input[name="subjectbox"], input[aria-label="Subject"]'
                            );

                        if (subjField) {

                            subjField.focus();

                            document.execCommand(
                                'insertText',
                                false,
                                sub
                            );
                        }

                        let bodyField =
                            document.querySelector(
                                'div[role="textbox"][aria-label="Message Body"]'
                            );

                        if (bodyField) {

                            bodyField.focus();

                            document.execCommand(
                                'insertText',
                                false,
                                bod
                            );
                        }
                    }
                    """,
                    [
                        recipient,
                        subject,
                        body
                    ]
                )

                gmail_page.wait_for_timeout(
                    2000
                )

                # ==================================================
                # OPEN SCHEDULE SEND
                # ==================================================

                gmail_page.locator(
                    'div[role="button"][data-tooltip*="More send options"], .G-asf'
                ).first.click()

                gmail_page.wait_for_timeout(
                    1000
                )

                gmail_page.locator(
                    'div[role="menuitem"]:has-text("Schedule send")'
                ).first.click()

                gmail_page.wait_for_timeout(
                    1500
                )

                gmail_page.locator(
                    'text=Pick date & time'
                ).first.click()

                # ==================================================
                # PICK DATE/TIME
                # ==================================================

                schedule_dialog = gmail_page.get_by_role(
                    "dialog",
                    name="Pick date & time"
                )

                schedule_dialog.wait_for(
                    timeout=5000
                )

                dialog_inputs = schedule_dialog.locator(
                    "input"
                )

                date_input = dialog_inputs.nth(0)

                date_input.click()

                gmail_page.keyboard.press(
                    "Meta+A"
                    if sys.platform == "darwin"
                    else "Control+A"
                )

                gmail_page.keyboard.type(
                    target_date_str,
                    delay=100
                )

                gmail_page.keyboard.press(
                    "Tab"
                )

                gmail_page.wait_for_timeout(
                    500
                )

                time_input = dialog_inputs.nth(1)

                time_input.click()

                gmail_page.keyboard.press(
                    "Meta+A"
                    if sys.platform == "darwin"
                    else "Control+A"
                )

                time_input.fill(
                    target_hour_str
                )

                time_input.press(
                    "Tab"
                )

                gmail_page.wait_for_timeout(
                    1000
                )

                schedule_dialog.get_by_role(
                    "button",
                    name="Schedule send"
                ).click()

                gmail_page.wait_for_timeout(
                    3000
                )

                return {
                    "status": "SUCCESS",
                    "message": (
                        f"Email scheduled to "
                        f"{recipient} "
                        f"at "
                        f"{target_hour_str}"
                    )
                }

        except Exception as e:

            return {
                "status": "ERROR",
                "message": str(e)
            }    
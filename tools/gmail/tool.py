import time
import json
import requests
import websocket
from browser.focus import focus_chromium
import sys
from tools.browser.tool import BrowserTool
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from pathlib import Path
import ollama

class GmailTool:
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

    @staticmethod
    def open():
        """Fast-path command specifically just to open the UI."""
        from tools.browser_tools.browser_tool import BrowserTool
        BrowserTool.open_url("https://mail.google.com")
        return "Gmail Opened"

    def compose_email(self, recipient: str, subject: str, body: str):
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
            from tools.browser_tools.browser_tool import BrowserTool
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
        
    def fetch_emails_by_date(
        self,
        date_filter="today"
    ):
        """
        Fetch inbox emails matching a date filter and
        save them to data/gmail_transcript.txt
        """

        try:


            with sync_playwright() as p:

                browser = (
                    p.chromium.connect_over_cdp(
                        "http://localhost:9222"
                    )
                )

                context = browser.contexts[0]

                gmail_page = None

                for page in context.pages:

                    if (
                        "mail.google.com"
                        in page.url
                    ):
                        gmail_page = page
                        break

                if gmail_page is None:

                    gmail_page = (
                        context.new_page()
                    )

                    gmail_page.goto(
                        "https://mail.google.com"
                    )

                    gmail_page.wait_for_timeout(
                        8000
                    )

                gmail_page.bring_to_front()

                gmail_page.wait_for_timeout(
                    5000
                )

                emails = gmail_page.evaluate("""
                () => {

                    const rows =
                        Array.from(
                            document.querySelectorAll(
                                'tr[role="row"]'
                            )
                        );

                    const collected = [];

                    for (const row of rows) {

                        try {

                            const sender =
                                row.querySelector('.yP')
                                ?.innerText || '';

                            const subject =
                                row.querySelector('.bog')
                                ?.innerText || '';

                            const snippet =
                                row.querySelector('.y2')
                                ?.innerText || '';

                            const date =
                                row.querySelector(
                                    'td.xW span'
                                )?.getAttribute(
                                    'title'
                                )
                                ||
                                row.querySelector(
                                    'td.xW span'
                                )?.innerText
                                ||
                                '';

                            collected.push({
                                sender,
                                subject,
                                snippet,
                                date
                            });

                        } catch(err){}
                    }

                    return collected;
                }
                """)

                print("\n" + "="*100)
                print("RAW EMAILS FROM GMAIL")
                print("="*100)

                for e in emails:
                    print(
                        f"SUBJECT: {e['subject']}"
                    )
                    print(
                        f"DATE: {e['date']}"
                    )
                    print("-"*50)

                print("="*100)
            filtered_emails = []

            date_filter_lower = str(
                date_filter
            ).lower().strip()

            for email in emails:

                mail_date = str(
                    email.get(
                        "date",
                        ""
                    )
                ).lower()

                if date_filter_lower == "today":

                    # Gmail shows today's mails as:
                    # 11:23 AM
                    # 4:15 PM
                    from datetime import datetime

                    today_str = datetime.now().strftime(
                        "%a, %b %d, %Y"
                    ).lower()
                    print(
                        f"\nTODAY STRING: {today_str}\n"
                    )

                    if mail_date.startswith(today_str):
                        filtered_emails.append(email)

                elif date_filter_lower == "yesterday":

                    if "yesterday" in mail_date:

                        filtered_emails.append(
                            email
                        )

                else:

                    if date_filter_lower in mail_date:

                        filtered_emails.append(
                            email
                        )
            print("\nFILTERED EMAILS\n")

            for e in filtered_emails:
                print(
                    e["subject"],
                    " --> ",
                    e["date"]
                )
            print(
                f"\nTOTAL TODAY EMAILS: {len(filtered_emails)}\n"
            )

            return {
                "status":"SUCCESS",
                "message":f"{len(filtered_emails)} emails extracted",
                "emails": filtered_emails
            }

        except Exception as e:

            return {
                "status":"ERROR",
                "message":str(e)
            }
        
    def summarize_emails(
        self,
        date_filter="today"
    ):

        try:

            fetch_result = (
                self.fetch_emails_by_date(
                    date_filter
                )
            )

            if (
                fetch_result["status"]
                != "SUCCESS"
            ):
                return fetch_result
            
            emails = fetch_result["emails"]

            if not emails:
                return {
                    "status": "SUCCESS",
                    "summary": "No emails found for the requested date."
                }
            
            prompt = f"""
            You are a professional executive email summarization assistant.

            You will receive a JSON array called EMAIL JSON.

            Each email object contains:

            - sender
            - subject
            - snippet
            - date

            YOUR TASK:

            Read every email carefully and create a concise summary.

            IMPORTANT RULES:

            1. Process EVERY email in the JSON array.
            2. Never skip an email.
            3. Never merge multiple emails together.
            4. Preserve the original subject exactly as provided.
            5. Generate exactly ONE summary per email.
            6. Summary must be ONE sentence only.
            7. Maximum 25 words per summary.
            8. Do not invent information.
            9. Use only information present in the email.
            10. Maintain the same order as the input JSON.
            11. Do not add introductions, conclusions, or explanations.
            12. Do not output markdown code blocks.

            OUTPUT FORMAT:

            MAIL 1
            Subject: <original subject>

            Summary:
            <one sentence summary>

            Date & Time Received:
            <date>

            --------------------------------

            MAIL 2
            Subject: <original subject>

            Summary:
            <one sentence summary>

            Date & Time Received:
            <date>

            --------------------------------

            Continue until all emails have been processed.

            After processing all emails, create this section:

            HIGH PRIORITY EMAILS

            Include only emails related to:

            - Security alerts
            - Password resets
            - Verification codes
            - Banking notifications
            - Payment confirmations
            - Payment failures
            - Meeting invitations
            - Interview invitations
            - Job opportunities
            - Deadlines
            - Urgent requests
            - Account access warnings

            Format:

            1.
            Subject: <subject>

            Date & Time Received:
            <date>

            Reason:
            <why this email is important>

            If no high priority emails exist, output exactly:

            HIGH PRIORITY EMAILS

            None

            EMAIL JSON:

            {json.dumps(emails, indent=2)}
            """


            response = ollama.chat(
                model="qwen3:8b",
                messages=[
                    {
                        "role":"user",
                        "content":prompt
                    }
                ]
            )

            summary = (
                response["message"]
                ["content"]
            )

            Path("logs").mkdir(
                exist_ok=True
            )

            with open(
                "logs/gmail_summary.log",
                "w",
                encoding="utf-8"
            ) as f:

                f.write(summary)

            summary = response["message"]["content"]

            print("\n")
            print("="*80)
            print(summary)
            print("="*80)
            print("\n")
            return {
                "status":"SUCCESS",
                "summary":summary
            }

        except Exception as e:

            return {
                "status":"ERROR",
                "message":str(e)
            }
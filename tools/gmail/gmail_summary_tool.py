import json
import ollama

from pathlib import Path
from playwright.sync_api import sync_playwright

from utils.global_events import event_bus


class GmailSummaryTool:

    def fetch_emails_by_date(
        self,
        date_filter="today"
    ):
        """
        Fetch inbox emails matching a date filter and
        save them to data/gmail_transcript.txt
        """

        try:

            event_bus.emit(
                "Connecting to Gmail inbox"
            )


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

                event_bus.emit(
                    "Inbox opened"
                )

                gmail_page.wait_for_timeout(
                    5000
                )

                event_bus.emit(
                    "Reading email rows"
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
                
                event_bus.emit(
                    f"Found {len(emails)} emails"
                )
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

            event_bus.emit(
                f"Filtered {len(filtered_emails)} emails for {date_filter}"
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
            event_bus.emit(
                "Starting email summarization"
            )

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

            event_bus.emit(
                f"Loaded {len(emails)} emails"
            )

            if not emails:
                return {
                    "status": "SUCCESS",
                    "summary": "No emails found for the requested date."
                }
            
            event_bus.emit(
                "Building summary prompt"
            )

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

            event_bus.emit(
                "Generating summary using Qwen3"
            )

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

            event_bus.emit(
                "Summary generated"
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

            event_bus.emit(
                "Summary saved"
            )

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
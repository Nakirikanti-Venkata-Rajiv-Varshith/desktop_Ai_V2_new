TOOL_METADATA = {
    "name": "gmail",

    "description": (
        "Interact with Gmail to compose, send, "
        "schedule and summarize emails."
    ),

    "functions": {

        "open": {

            "description":
                "Open Gmail in the browser.",

            "arguments": {},

            "memory_resolution": {},

            "examples": [
                "open gmail",
                "launch gmail"
            ]
        },

        "compose_email": {

            "description":
                "Compose and immediately send an email.",

            "arguments": {

                "recipient": "string",

                "subject": "string",

                "body": "string"
            },

            "memory_resolution": {

                "recipient": "email",

                "subject": None,

                "body": None
            },

            "examples": [

                "email John",

                "send an email to balaya@gmail.com",

                "mail dad saying I will be late"
            ]
        },

        "schedule_email": {

            "description":
                "Compose an email and schedule it to be sent later.",

            "arguments": {

                "recipient": "string",

                "subject": "string",

                "body": "string",

                "time": "HH:MM"
            },

            "memory_resolution": {

                "recipient": "email",

                "subject": None,

                "body": None,

                "time": None
            },

            "examples": [

                "schedule an email for tomorrow at 9 AM",

                "send this email at 6 PM",

                "email Balaya tonight"
            ]
        },

        "fetch_emails_by_date": {

            "description":
                "Retrieve emails for a specific date.",

            "arguments": {

                "date_filter": "string"
            },

            "memory_resolution": {

                "date_filter": None
            },

            "examples": [

                "show today's emails",

                "fetch yesterday's emails",

                "emails from Monday"
            ]
        },

        "summarize_emails": {

            "description":
                "Summarize emails from a specific date.",

            "arguments": {

                "date_filter": "string"
            },

            "memory_resolution": {

                "date_filter": None
            },

            "examples": [

                "summarize today's emails",

                "summarize yesterday's emails",

                "email summary"
            ]
        }
    }
}
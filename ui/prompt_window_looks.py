"""
UI Stylesheet configuration repository matching Gemini visual hierarchy and typography.
Exposes a clean string module to safely isolate look configurations from layout hooks.
"""

AESTHETIC_DARK_QSS = """
    /* Main Window Core */
    QMainWindow {
        background-color: #08080a; 
    }

    /* Section Header */
    QLabel#HeaderLabel {
        color: #a1a1b3; 
        font-size: 11px;
        font-weight: bold;
        letter-spacing: 1.5px; 
        font-family: 'Google Sans', 'Inter', 'Segoe UI', sans-serif;
    }

    /* Main Text Area Monitor Block */
    QTextEdit {
        background-color: #111115; 
        border: 1px solid #22222e; 
        border-radius: 10px;
        color: #f8f8f2; 
        padding: 14px;
        font-size: 13px;
        font-family: 'JetBrains Mono', 'Roboto Mono', 'Consolas', monospace;
    }

    /* --- Dynamic State Status Bar Rules --- */
    
    /* Green Glow Variant (State: ready) */
    QLabel#StatusBar[state="ready"] {
        color: #00ff87; 
        font-weight: bold;
        font-size: 11px;
        letter-spacing: 0.5px;
        padding-left: 2px;
        font-family: 'Google Sans', 'Inter', 'Segoe UI', sans-serif;
    }
    
    /* Orange Glow Variant (State: processing) */
    QLabel#StatusBar[state="processing"] {
        color: #ff9100; 
        font-weight: bold;
        font-size: 11px;
        letter-spacing: 0.5px;
        padding-left: 2px;
        font-family: 'Google Sans', 'Inter', 'Segoe UI', sans-serif;
    }

    /* Command Input Field Box */
    QLineEdit {
        background-color: #111115;
        border: 1px solid #22222e;
        border-radius: 8px;
        color: #ffffff; 
        padding: 11px 14px;
        font-size: 13px;
        font-family: 'Google Sans', 'Inter', 'Segoe UI', sans-serif;
    }
    QLineEdit:focus {
        border: 1px solid #b388ff; 
    }

    /* Run Trigger Button Layout */
    QPushButton {
        background-color: #b388ff; 
        color: #08080a; 
        border: none;
        border-radius: 8px;
        font-weight: bold;
        font-size: 11px;
        letter-spacing: 1.2px;
        padding: 11px 20px;
        font-family: 'Google Sans', 'Inter', 'Segoe UI', sans-serif;
    }
    QPushButton:hover {
        background-color: #d1b3ff; 
    }
    QPushButton:pressed {
        background-color: #9055ff; 
    }
"""
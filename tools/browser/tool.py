import webbrowser
import urllib.parse
import pyautogui
import time
from browser.focus import focus_chromium

class BrowserTool:

    @staticmethod
    def open_new_tab():

        pyautogui.hotkey(
            "ctrl",
            "t"
        )

        return "New tab opened"
    
    @staticmethod
    def search(query):

        focus_chromium()

        time.sleep(0.5)

        pyautogui.hotkey(
            "ctrl",
            "l"
        )

        time.sleep(0.2)

        pyautogui.write(query)

        pyautogui.press("enter")

        return f"Searched {query}"
    
    @staticmethod
    def open_website(url):

        focus_chromium()

        time.sleep(0.5)

        pyautogui.hotkey(
            "ctrl",
            "l"
        )

        time.sleep(0.2)

        pyautogui.write(url)

        pyautogui.press("enter")

        return f"Opened {url}"
    
    @staticmethod
    def open_url(url):

        return BrowserTool.open_website(url)

    @staticmethod
    def close_tab():

        focus_chromium()

        pyautogui.hotkey(
            "ctrl",
            "w"
        )

        return "Closed tab"
    
    @staticmethod
    def open_new_tab():

        focus_chromium()

        pyautogui.hotkey(
            "ctrl",
            "t"
        )

        return "New tab opened"
    
    @staticmethod
    def refresh():

        focus_chromium()

        pyautogui.hotkey(
            "ctrl",
            "r"
        )

        return "Page refreshed"
    
    @staticmethod
    def go_back():

        focus_chromium()

        pyautogui.hotkey(
            "alt",
            "left"
        )

        return "Went back"
    
    @staticmethod
    def go_forward():

        focus_chromium()

        pyautogui.hotkey(
            "alt",
            "right"
        )

        return "Went forward"
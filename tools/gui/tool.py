import pyautogui
import time

class GUITool:

    @staticmethod
    def move_mouse(x, y):

        pyautogui.moveTo(
            x,
            y,
            duration=0.5
        )

        return f"Moved mouse to {x},{y}"

    @staticmethod
    def click():

        pyautogui.click()

        return "Clicked"

    @staticmethod
    def double_click():

        pyautogui.doubleClick()

        return "Double Clicked"

    @staticmethod
    def type_text(text):

        pyautogui.write(
            text,
            interval=0.03
        )

        return f"Typed: {text}"

    @staticmethod
    def hotkey(keys):

        pyautogui.hotkey(*keys)

        return f"Pressed {keys}"

    @staticmethod
    def press(key):

        pyautogui.press(key)

        return f"Pressed {key}"
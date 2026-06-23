from tools.system.tool import SystemTool
from tools.gmail.tool import GmailTool
from tools.browser.tool import BrowserTool
from tools.youtube.tool import YouTubeTool
from tools.file.tool import FileTool
from tools.app.tool import AppTool
from tools.chat.tool import ChatTool

TOOLS = {
    "system": SystemTool,
    "gmail": GmailTool,
    "browser": BrowserTool,
    "youtube": YouTubeTool,
    "file": FileTool,
    "app": AppTool,
    "chat": ChatTool
}
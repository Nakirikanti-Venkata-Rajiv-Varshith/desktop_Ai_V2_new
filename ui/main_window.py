# ui/main_window.py
import os
import subprocess
import time
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtCore import QThread, pyqtSignal

from ui.prompt_bar import PromptBar
from ui.command_splitter import split_commands
from ui.prompt_window_looks import AESTHETIC_DARK_QSS

# Core Framework Bridging Imports
from agent.orchestrator import Orchestrator
from tools.logger import agent_logger

class AgentWorker(QThread):
    """Background computation runner safeguarding UI components from locking up."""
    status_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)

    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def run(self):
        try:
            # Crucial: Instantiate the framework runner entirely INSIDE the run loop 
            # to guarantee that OllamaClient initialization stays on this background thread.
            orchestrator = Orchestrator()

            # Handle user text parsing
            if "summarize" in self.text.lower() and "explain" in self.text.lower():
                commands = [self.text]
            else:
                commands = split_commands(self.text)

            overall_success = True

            for idx, command in enumerate(commands, start=1):
                self.status_signal.emit(f"Processing execution step {idx}/{len(commands)}: <b>'{command}'</b>")
                
                # Feed command step into the current routing/planning loop
                # results = orchestrator.run(command)
                
                # self.status_signal.emit(f"<b>AI Agent:</b> Successfully ran step. Result: {str(results)}")

                results = orchestrator.run(command)

                if (
                    isinstance(results, list)
                    and len(results) > 0
                    and isinstance(results[0], dict)
                    and "summary" in results[0]
                ):
                    self.status_signal.emit(
                        f"<b>AI Agent:</b>\n{results[0]['summary']}"
                    )
                else:
                    self.status_signal.emit(
                        f"<b>AI Agent:</b> Successfully ran step. Result: {str(results)}"
                    )


            self.finished_signal.emit(overall_success)
        except Exception as e:
            agent_logger.error(f"GUI Thread session failed: {str(e)}")
            self.status_signal.emit(f"<b><font color='#ff5555'>[Error]</font></b> {str(e)}")
            self.finished_signal.emit(False)


class MainWindow(QMainWindow):
    """Core Dashboard interface window."""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Ubuntu AI Desktop Agent V2")
        self.resize(700, 500)
        self.setStyleSheet(AESTHETIC_DARK_QSS)

        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Monitor Header Panel
        self.header_label = QLabel("SYSTEM LIVE FEED TRACKER")
        self.header_label.setObjectName("HeaderLabel")
        layout.addWidget(self.header_label)

        # Text Console Output Area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # Status Monitor Glow Bar
        self.status_bar = QLabel("System Status: Operational")
        self.status_bar.setObjectName("StatusBar")
        self.status_bar.setProperty("state", "ready")
        layout.addWidget(self.status_bar)

        # Command Text Input Component
        self.prompt_bar = PromptBar()
        self.prompt_bar.command_submitted.connect(self._handle_command_submission)
        layout.addWidget(self.prompt_bar)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        self.chat_display.append("<b><font color='#b388ff'>[System]</font></b> Dashboard engine active. Awaiting instructions...")

    def _handle_command_submission(self, text: str):
        self.prompt_bar.set_running_state(True)
        self.set_ui_processing_state(True)
        
        # Fire up the worker background thread safely
        self.worker = AgentWorker(text)
        self.worker.status_signal.connect(self._update_chat_display)
        self.worker.finished_signal.connect(self._handle_worker_completion)
        self.worker.start()

    def set_ui_processing_state(self, is_processing: bool):
        if is_processing:
            self.status_bar.setText("System Status: Thinking & Executing Plan...")
            self.status_bar.setProperty("state", "processing")
        else:
            self.status_bar.setText("System Status: Operational")
            self.status_bar.setProperty("state", "ready")
        
        # Force stylesheet recalculation for dynamic properties
        self.status_bar.style().unpolish(self.status_bar)
        self.status_bar.style().polish(self.status_bar)

    def _update_chat_display(self, status: str):
        if "<b>AI Agent:</b>" in status or len(status) > 150:
            header = "<b><font color='#b388ff'>[System] AI Agent:</font></b><br>"
            body = status.replace("<b>AI Agent:</b>", "").strip()
            if "MAIL 1" in body:

                formatted_body = (
                    body
                    .replace("\n", "<br>")
                    .replace(
                        "MAIL ",
                        "<br><br><b>MAIL "
                    )
                    .replace(
                        "Subject:",
                        "</b><br><b>Subject:</b>"
                    )
                    .replace(
                        "Summary:",
                        "<br><b>Summary:</b>"
                    )
                    .replace(
                        "Date & Time Received:",
                        "<br><b>Date & Time Received:</b>"
                    )
                    .replace(
                        "HIGH PRIORITY EMAILS",
                        "<br><br><hr><b>HIGH PRIORITY EMAILS</b>"
                    )
                )

            else:

                formatted_body = body.replace(
                    "\n",
                    "<br>"
                )
            self.chat_display.append(f"{header}<font color='#f8f8f2'>{formatted_body}</font><br>")
        else:
            self.chat_display.append(f"<font color='#b388ff'>[System]</font> <font color='#a1a1b3'>{status}</font>")

    def _handle_worker_completion(self, success: bool):
        self.prompt_bar.set_running_state(False)
        self.set_ui_processing_state(False)
        if not success:
            self.chat_display.append("<font color='#ff5555'>[Warning] Sequence cycle terminated early due to processing faults.</font>")

    def _cleanup_session(self):
        """Restores background worker state cleanly before exit."""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()

    def closeEvent(self, event):
        """Triggers automatically when the window layout is closed."""
        self._cleanup_session()
        try:
            # Terminate the local Ollama runner process smoothly
            subprocess.run(["ollama", "stop", "qwen3:8b"], timeout=5)
        except Exception:
            pass
        event.accept()
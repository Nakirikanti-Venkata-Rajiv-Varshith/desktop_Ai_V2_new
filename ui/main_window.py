# ui/main_window.py
import os
import subprocess
import time
import traceback
from PyQt6.QtWidgets import (QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QTextEdit,QLabel)
from PyQt6.QtCore import QThread, pyqtSignal
from ui.event_worker import EventWorker
from ui.prompt_bar import PromptBar
from ui.command_splitter import split_commands
from ui.prompt_window_looks import AESTHETIC_DARK_QSS
from models.execution_queue import ExecutionQueue
from agent.queue_builder import QueueBuilder
from ui.queue_panel import QueuePanel
from ui.queue_execution_worker import QueueExecutionWorker
# Core Framework Bridging Imports
from agent.orchestrator import Orchestrator
from tools.logger import agent_logger


class MainWindow(QMainWindow):
    """Core Dashboard interface window."""
    
    # def __init__(self):
    #     super().__init__()
    #     self.worker = None
    #     self._init_ui()

    def __init__(self):
        super().__init__()

        self.worker = None
        self.execution_queue = ExecutionQueue()

        self.queue_builder = QueueBuilder()

        self._init_ui()

        # SSE/EventBus Listener
        self.event_worker = EventWorker()

        self.event_worker.event_received.connect(
            self._handle_agent_event
        )

        self.event_worker.start()

        

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

        top_layout = QHBoxLayout()
        

       

        # Text Console Output Area
        # ==================================================
        # CHAT DISPLAY
        # ==================================================

        self.chat_display = QTextEdit()

        self.chat_display.setReadOnly(True)

        # ==================================================
        # QUEUE PANEL
        # ==================================================

        self.queue_panel = QueuePanel()

        self.queue_panel.add_requested.connect(
            self._handle_add_to_queue
        )

        self.queue_panel.delete_requested.connect(
            self._handle_delete_queue_item
        )

        self.queue_panel.execute_requested.connect(
            self._execute_queue
        )
        # ==================================================
        # TOP LAYOUT
        # ==================================================

        top_layout = QHBoxLayout()

        top_layout.addWidget(
            self.chat_display,
            stretch=3
        )

        top_layout.addWidget(
            self.queue_panel,
            stretch=1
        )

        layout.addLayout(
            top_layout
        )

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


    def _queue_updated(
        self
    ):

        self._refresh_queue_panel()

    def _refresh_queue_panel(
        self
    ):

        self.queue_panel.clear_queue()
        print("\nCURRENT QUEUE:")
        for item in self.execution_queue.items:

            self.queue_panel.add_queue_item(
                item
            )
            print(item.description)
        pending_count = len(
            [
                item
                for item in self.execution_queue.items
                if not item.executed
            ]
        )
        self.queue_panel.title.setText(
            f"Execution Queue ({pending_count})"
        )

    def _handle_add_to_queue(
        self,
        text: str
    ):

        print(
            f"\nQUEUE APPEND REQUEST: {text}"
        )

        self.queue_builder.append_to_queue(
            self.execution_queue,
            text
        )

        self._refresh_queue_panel()

    def _handle_delete_queue_item(
        self,
        item_id: int
    ):

        self.execution_queue.remove_item(
            item_id
        )

        self._refresh_queue_panel()

    def _execute_queue(
        self
    ):

        if (
            self.worker
            and self.worker.isRunning()
        ):
            return
        
        if not self.execution_queue.items:

            self.chat_display.append(
                "<font color='#ff5555'>[Queue]</font> Queue is empty"
            )

            return

        self.prompt_bar.set_running_state(
            True
        )

        self.set_ui_processing_state(
            True
        )

        self.worker = QueueExecutionWorker(
            self.execution_queue
        )

        self.worker.status_signal.connect(
            self._update_chat_display
        )

        self.worker.queue_updated.connect(
            self._queue_updated
        )

        self.worker.finished_signal.connect(
            self._handle_worker_completion
        )

        self.queue_panel.set_execution_state(
            True
        )

        self.worker.start()

    # def _handle_command_submission(self, text: str):
    #     self.prompt_bar.set_running_state(True)
    #     self.set_ui_processing_state(True)
        
    #     # Fire up the worker background thread safely
    #     self.worker = AgentWorker(text)
    #     self.worker.status_signal.connect(self._update_chat_display)
    #     self.worker.finished_signal.connect(self._handle_worker_completion)
    #     self.worker.start()
    def _handle_command_submission(
        self,
        text: str
    ):

        queue = self.queue_builder.build(
            text
        )

        print("\nQUEUE GENERATED:")
        for item in queue.items:
            print(item.description)

        for item in queue.items:

            self.execution_queue.add_item(
                item
            )

        self._refresh_queue_panel()

        self.chat_display.append(
            f"<font color='#b388ff'>[Queue]</font> "
            f"Added {len(queue.items)} task(s)"
        )

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

    def _handle_agent_event(
        self,
        message
    ):

        self.chat_display.append(
            f"<font color='#8be9fd'>[Agent Event]</font> "
            f"<font color='#f8f8f2'>{message}</font>"
        )

    def _handle_worker_completion(
        self,
        success: bool
    ):

        self.prompt_bar.set_running_state(False)

        self.set_ui_processing_state(False)

        self.queue_panel.set_execution_state(False)

        if success:

            self.chat_display.append(
                "<font color='#50fa7b'>[Queue]</font> "
                "All tasks completed successfully."
            )

            self.execution_queue.remove_completed_items()

            self._refresh_queue_panel()

        else:

            self.chat_display.append(
                "<font color='#ff5555'>[Warning]</font> "
                "Queue execution completed with errors."
            )

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
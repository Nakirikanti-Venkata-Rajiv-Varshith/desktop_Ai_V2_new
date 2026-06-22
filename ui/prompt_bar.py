from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt

class PromptBar(QWidget):
    """Encapsulates input validation collection mechanics."""
    command_submitted = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter desktop command here... (e.g., 'Open Chrome and search GitHub')")
        self.input_field.returnPressed.connect(self._handle_submit)

        self.submit_btn = QPushButton("Execute")
        self.submit_btn.clicked.connect(self._handle_submit)

        layout.addWidget(self.input_field)
        layout.addWidget(self.submit_btn)
        self.setLayout(layout)

    def _handle_submit(self):
        text = self.input_field.text().strip()
        if text:
            self.command_submitted.emit(text)
            self.input_field.clear()
            
    def set_running_state(self, is_running: bool):
        """Toggles interface interactability states during worker background operations."""
        self.input_field.setEnabled(not is_running)
        self.submit_btn.setEnabled(not is_running)
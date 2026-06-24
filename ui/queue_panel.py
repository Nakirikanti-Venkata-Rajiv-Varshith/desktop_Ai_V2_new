from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QPushButton
)

from PyQt6.QtCore import pyqtSignal

from models.queue_item import QueueItem

from ui.queue_item_widget import (
    QueueItemWidget
)


class QueuePanel(QWidget):

    add_requested = pyqtSignal(str)

    execute_requested = pyqtSignal()

    delete_requested = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self._init_ui()

    def _init_ui(self):

        layout = QVBoxLayout()

        # ---------------------------------
        # Title
        # ---------------------------------

        self.title = QLabel(
            "Execution Queue"
        )

        layout.addWidget(
            self.title
        )

        # ---------------------------------
        # Queue List
        # ---------------------------------

        self.queue_list = QListWidget()

        layout.addWidget(
            self.queue_list,
            stretch=1
        )

        # ---------------------------------
        # Add Task Input
        # ---------------------------------

        self.add_input = QLineEdit()

        self.add_input.setPlaceholderText(
            "Add task to queue..."
        )

        self.add_input.returnPressed.connect(
            self._handle_add
        )

        layout.addWidget(
            self.add_input
        )

        # ---------------------------------
        # Add Button
        # ---------------------------------

        self.add_button = QPushButton(
            "Add"
        )

        self.add_button.clicked.connect(
            self._handle_add
        )

        layout.addWidget(
            self.add_button
        )

        # ---------------------------------
        # Execute Queue Button
        # ---------------------------------

        self.execute_button = QPushButton(
            "Execute Queue"
        )

        self.execute_button.clicked.connect(
            self.execute_requested.emit
        )

        layout.addWidget(
            self.execute_button
        )

        self.setLayout(
            layout
        )

    def _handle_add(
        self
    ):

        print("ADD BUTTON CLICKED")
        text = (
            self.add_input.text()
            .strip()
        )

        if not text:
            return

        self.add_requested.emit(
            text
        )

        self.add_input.clear()

    def add_queue_item(
        self,
        queue_item: QueueItem
    ):

        list_item = QListWidgetItem()

        widget = QueueItemWidget(
            queue_item
        )

        widget.refresh_status()

        widget.delete_requested.connect(
            self.delete_requested.emit
        )

        list_item.setSizeHint(
            widget.sizeHint()
        )

        self.queue_list.addItem(
            list_item
        )

        self.queue_list.setItemWidget(
            list_item,
            widget
        )

    def clear_queue(
        self
    ):

        self.queue_list.clear()

    def set_execution_state(
        self,
        running: bool
    ):

        # Allow adding tasks while running

        self.add_input.setEnabled(
            True
        )

        self.add_button.setEnabled(
            True
        )

        # Prevent duplicate execution

        self.execute_button.setEnabled(
            not running
        )
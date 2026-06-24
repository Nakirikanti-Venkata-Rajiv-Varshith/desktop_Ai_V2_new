from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QCheckBox,
    QLabel,
    QPushButton
)

from PyQt6.QtCore import pyqtSignal

from models.queue_item import QueueItem


class QueueItemWidget(QWidget):

    delete_requested = pyqtSignal(int)

    def __init__(
        self,
        queue_item: QueueItem
    ):
        super().__init__()

        self.queue_item = queue_item

        self._init_ui()

    def _init_ui(self):

        layout = QHBoxLayout()

        layout.setContentsMargins(
            4,
            2,
            4,
            2
        )

        self.checkbox = QCheckBox()

        self.checkbox.setChecked(
            self.queue_item.enabled
        )

        self.checkbox.stateChanged.connect(
            self._on_checkbox_changed
        )

        self.description_label = QLabel(
            self.queue_item.description
        )

        self.delete_button = QPushButton(
            "✕"
        )

        if self.queue_item.status == "RUNNING":
            self.delete_button.setEnabled(False)

        self.delete_button.setFixedWidth(
            28
        )

        self.delete_button.clicked.connect(
            self._delete_clicked
        )

        layout.addWidget(
            self.checkbox
        )

        layout.addWidget(
            self.description_label,
            stretch=1
        )

        layout.addWidget(
            self.delete_button
        )

        self.setLayout(
            layout
        )

        self.refresh_status()

    def _on_checkbox_changed(
        self
    ):

        self.queue_item.enabled = (
            self.checkbox.isChecked()
        )

    def _delete_clicked(
        self
    ):

        self.delete_requested.emit(
            self.queue_item.id
        )

    def refresh_status(
        self
    ):

        status = self.queue_item.status

        color_map = {
            "PENDING": "#9e9e9e",
            "RUNNING": "#ffb300",
            "SUCCESS": "#00c853",
            "FAILED": "#ff1744",
            "SKIPPED": "#40c4ff"
        }

        color = color_map.get(
            status,
            "#9e9e9e"
        )

        self.description_label.setStyleSheet(
            f"color: {color};"
        )
from PyQt6.QtCore import (
    QThread,
    pyqtSignal
)

from agent.orchestrator import Orchestrator
from models.execution_queue import ExecutionQueue
from models.queue_item import QueueStatus

from tools.logger import agent_logger


class QueueExecutionWorker(QThread):

    status_signal = pyqtSignal(str)

    queue_updated = pyqtSignal()

    finished_signal = pyqtSignal(bool)

    def __init__(
        self,
        execution_queue: ExecutionQueue
    ):
        super().__init__()

        self.execution_queue = execution_queue

    def run(self):

        try:

            orchestrator = Orchestrator()

            overall_success = True

            current_step = 0

            while True:

                next_item = None

                for item in self.execution_queue.items:

                    if (
                        item.enabled
                        and not item.executed
                    ):
                        next_item = item
                        break

                    if (
                        not item.enabled
                        and not item.executed
                    ):

                        item.status = (
                            QueueStatus.SKIPPED
                        )

                        item.executed = True

                        self.queue_updated.emit()

                if next_item is None:
                    break

                item = next_item

                current_step += 1

                item.status = (
                    QueueStatus.RUNNING
                )

                self.queue_updated.emit()

                self.status_signal.emit(
                    f"Executing Step "
                    f"{current_step}: "
                    f"{item.description}"
                )

                try:

                    results = orchestrator.run(
                        item.description
                    )

                    item.status = (
                        QueueStatus.SUCCESS
                    )

                    item.executed = True

                    self.queue_updated.emit()

                    self.status_signal.emit(
                        f"Completed: "
                        f"{item.description}"
                    )

                    if (
                        isinstance(results, list)
                        and len(results) > 0
                    ):
                        self.status_signal.emit(
                            str(results)
                        )

                except Exception as e:

                    item.status = (
                        QueueStatus.FAILED
                    )

                    item.executed = True

                    self.queue_updated.emit()

                    overall_success = False

                    self.status_signal.emit(
                        f"Failed: "
                        f"{item.description}"
                    )

                    self.status_signal.emit(
                        str(e)
                    )

                    agent_logger.error(
                        str(e)
                    )

            self.finished_signal.emit(
                overall_success
            )

        except Exception as e:

            agent_logger.error(
                str(e)
            )

            self.finished_signal.emit(
                False
            )
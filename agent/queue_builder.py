from models.queue_item import QueueItem
from models.execution_queue import ExecutionQueue

from ui.command_splitter import split_commands


class QueueBuilder:

    def build(
        self,
        user_text: str
    ) -> ExecutionQueue:

        queue = ExecutionQueue()

        commands = split_commands(
            user_text
        )

        for index, command in enumerate(
            commands,
            start=1
        ):

            queue.add_item(
                QueueItem(
                    id=index,
                    description=command
                )
            )

        return queue

    def append_to_queue(
        self,
        queue: ExecutionQueue,
        user_text: str
    ) -> ExecutionQueue:

        commands = split_commands(
            user_text
        )

        next_id = queue.next_id()

        for command in commands:

            queue.add_item(
                QueueItem(
                    id=next_id,
                    description=command
                )
            )

            next_id += 1

        return queue
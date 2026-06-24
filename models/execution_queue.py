from pydantic import BaseModel, Field

from models.queue_item import QueueItem


class ExecutionQueue(BaseModel):

    items: list[QueueItem] = Field(
        default_factory=list
    )

    def add_item(
        self,
        item: QueueItem
    ):
        self.items.append(item)

    def remove_item(
        self,
        item_id: int
    ):
        self.items = [
            item
            for item in self.items
            if item.id != item_id
        ]

    def clear(self):
        self.items.clear()

    def get_item(
        self,
        item_id: int
    ) -> QueueItem | None:

        for item in self.items:

            if item.id == item_id:
                return item

        return None

    def get_enabled_items(
        self
    ) -> list[QueueItem]:

        return [
            item
            for item in self.items
            if item.enabled
        ]

    def get_pending_items(
        self
    ) -> list[QueueItem]:

        return [
            item
            for item in self.items
            if item.status == "PENDING"
        ]

    def next_id(
        self
    ) -> int:

        if not self.items:
            return 1

        return (
            max(
                item.id
                for item in self.items
            )
            + 1
        )

    def move_item(
        self,
        old_index: int,
        new_index: int
    ):

        if (
            old_index < 0
            or old_index >= len(self.items)
            or new_index < 0
            or new_index >= len(self.items)
        ):
            return

        item = self.items.pop(
            old_index
        )

        self.items.insert(
            new_index,
            item
        )

    def to_json(self):

        return self.model_dump()

    @classmethod
    def from_json(
        cls,
        data: dict
    ):

        return cls(**data)
    
    def remove_completed_items(self):

        self.items = [
            item
            for item in self.items
            if not item.executed
        ]
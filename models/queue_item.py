from pydantic import BaseModel, Field


class QueueStatus:
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class QueueItem(BaseModel):

    id: int

    description: str

    enabled: bool = True

    status: str = QueueStatus.PENDING

    executed: bool = False

    tool: str | None = None

    function: str | None = None

    arguments: dict = Field(
        default_factory=dict
    )
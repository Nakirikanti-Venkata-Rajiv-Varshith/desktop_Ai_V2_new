from fastapi import APIRouter

from agent.orchestrator import Orchestrator

from api.models.execute_request import ExecuteRequest
from api.models.execute_response import ExecuteResponse

router = APIRouter()

orchestrator = Orchestrator()


@router.post(
    "/execute",
    response_model=ExecuteResponse
)
def execute(request: ExecuteRequest):

    result = orchestrator.run(
        request.query
    )

    return {
        "result": result
    }
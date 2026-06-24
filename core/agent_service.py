from agent.orchestrator import Orchestrator

class AgentService:

    def __init__(self):
        self.orchestrator = Orchestrator()

    def execute(self, query: str):
        return self.orchestrator.run(query)
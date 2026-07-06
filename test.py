from memory.semantic_learning import SemanticLearning
from memory.semantic_memory import SemanticMemory
from models.execution_event import ExecutionEvent

# Start clean
SemanticMemory.clear()

event = ExecutionEvent(
    tool="browser",
    function="open_url",
    arguments={
        "url": "https://github.com/balaya/project"
    },
    success=True,
    experience=None
)

candidate = SemanticLearning.extract_candidate(
    event
)

document = SemanticLearning.build_document(
    candidate
)

SemanticMemory.add_document(
    document
)

print("Stored successfully")

print()

print(
    SemanticMemory.all_documents()
)
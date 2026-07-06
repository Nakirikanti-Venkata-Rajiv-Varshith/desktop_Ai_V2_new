from models.execution_event import ExecutionEvent
from models.semantic_document import SemanticDocument
from models.semantic_candidate import SemanticCandidate
class SemanticLearning:
    """
    Converts completed executions into
    semantic documents when appropriate.

    This class decides whether an execution
    represents reusable semantic knowledge.
    """
    @staticmethod
    def should_learn(
        event: ExecutionEvent
    ) -> bool:
        """
        Determine whether a completed execution
        represents reusable semantic knowledge.
        """

        semantic_targets = {

            ("browser", "open_url"),

            ("file", "open"),

            ("file", "download"),

            ("browser", "download_file")
        }

        return (
            event.tool,
            event.function
        ) in semantic_targets
    
    @staticmethod
    def extract_candidate(
        event: ExecutionEvent
    ) -> SemanticCandidate | None:
        """
        Extract reusable semantic information
        from a completed execution.

        Returns None if no reusable semantic
        information exists.
        """

        if not SemanticLearning.should_learn(
            event
        ):
            return None

        text = " ".join(
            str(value)
            for value in event.arguments.values()
            if value not in (
                None,
                "",
                [],
                {}
            )
        )

        if not text:
            return None

        return SemanticCandidate(
            text=text,
            metadata={
                "tool": event.tool,
                "function": event.function
            }
        )
    
    @staticmethod
    def build_document(
        candidate: SemanticCandidate
    ) -> SemanticDocument:
        """
        Convert a SemanticCandidate into a
        SemanticDocument.

        Embeddings are NOT generated here.
        SemanticMemory is responsible for that.
        """

        return SemanticDocument(

            id=candidate.text,

            text=candidate.text,

            metadata=candidate.metadata
        )
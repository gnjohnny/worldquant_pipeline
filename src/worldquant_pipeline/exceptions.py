"""Domain exceptions for worldquant_pipeline."""


class WorldQuantPipelineError(Exception):
    """Base exception for all worldquant_pipeline errors."""


class ASTSyntaxError(WorldQuantPipelineError):
    """Raised when an alpha expression fails syntactic parsing or tokenization."""

    def __init__(self, message: str, position: int | None = None, token: str | None = None) -> None:
        super().__init__(message)
        self.position = position
        self.token = token


class UnknownOperatorError(WorldQuantPipelineError):
    """Raised when an operator is not present in the whitelisted catalog."""


class OperatorArityError(WorldQuantPipelineError):
    """Raised when an operator receives an incorrect number of arguments."""

    def __init__(self, operator: str, expected: int, received: int) -> None:
        message = f"Operator '{operator}' requires {expected} arguments, but received {received}."
        super().__init__(message)
        self.operator = operator
        self.expected = expected
        self.received = received


class UnknownFieldError(WorldQuantPipelineError):
    """Raised when an expression references a field not in the approved data catalog."""

    def __init__(self, field_name: str) -> None:
        super().__init__(f"Field '{field_name}' is not in the approved data catalog.")
        self.field_name = field_name


class DuplicateCandidateError(WorldQuantPipelineError):
    """Raised when an expression is canonically identical to an existing candidate."""

    def __init__(self, expression_hash: str, existing_candidate_id: str) -> None:
        super().__init__(
            f"Candidate with hash '{expression_hash}' already exists (ID: {existing_candidate_id})."
        )
        self.expression_hash = expression_hash
        self.existing_candidate_id = existing_candidate_id


class GateValidationError(WorldQuantPipelineError):
    """Raised when a candidate or experiment fails a quality gate."""


class DatabaseConfigError(WorldQuantPipelineError):
    """Raised when database connection details are missing or unreachable."""

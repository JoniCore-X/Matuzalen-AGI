class AIGenerationError(RuntimeError):
    """Raised when the model cannot produce a usable response."""


class AITimeoutError(AIGenerationError):
    """Raised when a model request exceeds the configured timeout."""


class AIValidationError(AIGenerationError):
    """Raised when a model response is not valid JSON."""

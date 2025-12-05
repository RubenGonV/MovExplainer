"""
Unit tests for the Ollama LLM infrastructure component.
This module contains tests for the OllamaLLM class and the PromptBuilder helper,
verifying both mocked behavior and integration with a running Ollama service.
"""

from unittest.mock import patch, MagicMock
from ollama import ResponseError
import pytest

from infrastructure.llm.ollama_llm import OllamaLLM
from infrastructure.llm.prompt_builder import PromptBuilder


@pytest.mark.unit
class TestPromptBuilder:
    """Unit tests for PromptBuilder."""

    def test_empty_builder(self):
        """Test creating an empty builder."""
        builder = PromptBuilder()
        context = builder.get_context()
        assert not context

    def test_add_position(self):
        """Test adding position information."""
        builder = PromptBuilder()
        builder.add_position(
            fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            description="starting position",
        )

        context = builder.get_context()
        assert "position" in context
        assert (
            context["position"]["fen"]
            == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        )
        assert context["position"]["description"] == "starting position"

    def test_add_move(self):
        """Test adding move information."""
        builder = PromptBuilder()
        builder.add_move(uci="e2e4", san="e4")

        context = builder.get_context()
        assert "move" in context
        assert context["move"]["uci"] == "e2e4"
        assert context["move"]["san"] == "e4"

    def test_add_evaluation_centipawns(self):
        """Test adding centipawn evaluation."""
        builder = PromptBuilder()
        builder.add_evaluation(cp=25, depth=15, pv=["e4", "e5", "Nf3"])

        context = builder.get_context()
        assert "evaluation" in context
        assert context["evaluation"]["evaluation"] == "25 centipawns"
        assert context["evaluation"]["depth"] == 15
        assert context["evaluation"]["principal_variation"] == "e4 e5 Nf3"

    def test_add_evaluation_mate(self):
        """Test adding mate evaluation."""
        builder = PromptBuilder()
        builder.add_evaluation(mate=3, depth=20)

        context = builder.get_context()
        assert "evaluation" in context
        assert context["evaluation"]["evaluation"] == "Mate in 3"
        assert context["evaluation"]["depth"] == 20

    def test_fluent_api_chaining(self):
        """Test that methods can be chained."""
        prompt = (
            PromptBuilder()
            .add_position(
                fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
            )
            .add_move(uci="e2e4", san="e4")
            .add_evaluation(cp=25)
            .build()
        )

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "e4" in prompt

    def test_build_creates_prompt(self):
        """Test that build() creates a non-empty prompt."""
        builder = PromptBuilder()
        builder.add_position(
            fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        )
        builder.add_move(uci="e2e4", san="e4")

        prompt = builder.build()
        assert isinstance(prompt, str)
        assert "e4" in prompt
        assert "chess" in prompt.lower()

    def test_to_json(self):
        """Test JSON export."""
        builder = PromptBuilder()
        builder.add_move(uci="e2e4", san="e4")

        json_str = builder.to_json()
        assert isinstance(json_str, str)
        assert "e2e4" in json_str


@pytest.mark.unit
class TestOllamaLLMMocked:
    """Unit tests for OllamaLLM using mocks (no real Ollama connection)."""

    @pytest.fixture
    def mock_ollama_client(self):
        """Create a mock Ollama client."""
        with patch("infrastructure.llm.ollama_llm.ollama.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            yield mock_client

    def test_initialization(self):
        """Test LLM initialization."""
        llm = OllamaLLM(model="mistral", timeout=30)
        assert llm.model == "mistral"
        assert llm.timeout == 30

    def test_explain_success(self, mock_ollama_client):
        """Test successful explanation generation."""
        mock_ollama_client.generate.return_value = {
            "response": "This is a test explanation."
        }
        llm = OllamaLLM()
        context = {"position": "starting position", "move": "e4", "evaluation": "+0.25"}

        result = llm.explain(context)
        assert result == "This is a test explanation."
        assert mock_ollama_client.generate.called

    def test_explain_empty_context_raises(self):
        """Test that empty context raises ValueError."""
        llm = OllamaLLM()

        with pytest.raises(ValueError, match="Context cannot be empty"):
            llm.explain({})

    def test_is_available_success(self, mock_ollama_client):
        """Test availability check when service is available."""
        mock_ollama_client.list.return_value = []

        llm = OllamaLLM()
        assert llm.is_available() is True

    def test_is_available_failure(self, mock_ollama_client):
        """Test availability check when service is unavailable."""
        mock_ollama_client.list.side_effect = ConnectionError("Cannot connect")

        llm = OllamaLLM()
        assert llm.is_available() is False

    def test_retry_logic_on_server_error(self, mock_ollama_client):
        """Test retry logic on server errors."""
        # First two calls fail with server error, third succeeds
        mock_ollama_client.generate.side_effect = [
            ResponseError("Server error", status_code=500),
            ResponseError("Server error", status_code=500),
            {"response": "Success after retries"},
        ]

        llm = OllamaLLM(max_retries=3)
        context = {"move": "e4"}

        result = llm.explain(context)
        assert result == "Success after retries"
        assert mock_ollama_client.generate.call_count == 3

    def test_no_retry_on_client_error(self, mock_ollama_client):
        """Test that client errors don't trigger retries."""

        mock_ollama_client.generate.side_effect = ResponseError(
            "Bad request", status_code=400
        )

        llm = OllamaLLM(max_retries=3)
        context = {"move": "e4"}

        with pytest.raises(RuntimeError, match="Ollama API error"):
            llm.explain(context)

        # Should only be called once (no retries for client errors)
        assert mock_ollama_client.generate.call_count == 1


@pytest.mark.llm
@pytest.mark.integration
class TestOllamaLLMIntegration:
    """Integration tests for OllamaLLM (requires running Ollama instance)."""

    def test_real_ollama_connection(self):
        """Test real connection to Ollama (skipped if not available)."""
        llm = OllamaLLM(model="mistral")

        if not llm.is_available():
            pytest.skip("Ollama service not available")

        context = {"position": "starting position", "move": "e4", "evaluation": "+0.25"}

        result = llm.explain(context)
        assert isinstance(result, str)
        assert len(result) > 0

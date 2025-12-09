"""
Unit tests for the Groq LLM infrastructure component.
This module contains tests for the GroqLLM class,
verifying both mocked behavior and integration patterns.
"""

from unittest.mock import patch, MagicMock
import pytest

from infrastructure.llm.groq_llm import GroqLLM


@pytest.mark.unit
class TestGroqLLMMocked:
    """Unit tests for GroqLLM using mocks (no real Groq connection)."""

    @pytest.fixture
    def mock_groq_client(self):
        """Create a mock Groq client."""
        with patch("infrastructure.llm.groq_llm.Groq") as mock_groq_class:
            mock_client = MagicMock()
            mock_groq_class.return_value = mock_client
            yield mock_client

    def test_initialization(self):
        """Test LLM initialization with API key."""
        with patch(
            "infrastructure.llm.groq_llm.os.getenv", return_value="test-api-key"
        ):
            llm = GroqLLM(model="llama-3.1-8b-instant", timeout=30)
            assert llm.model == "llama-3.1-8b-instant"
            assert llm.timeout == 30

    def test_initialization_without_api_key(self):
        """Test LLM initialization without API key."""
        with patch("infrastructure.llm.groq_llm.os.getenv", return_value=None):
            llm = GroqLLM()
            assert llm.client is None

    def test_explain_success(self, mock_groq_client):
        """Test successful explanation generation."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is a test explanation."
        mock_groq_client.chat.completions.create.return_value = mock_response

        with patch("infrastructure.llm.groq_llm.os.getenv", return_value="test-key"):
            llm = GroqLLM()

        context = {"position": "starting position", "move": "e4", "evaluation": "+0.25"}

        result = llm.explain(context)
        assert result == "This is a test explanation."
        assert mock_groq_client.chat.completions.create.called

    def test_explain_empty_context_raises(self):
        """Test that empty context raises ValueError."""
        with patch("infrastructure.llm.groq_llm.os.getenv", return_value="test-key"):
            llm = GroqLLM()

        with pytest.raises(ValueError, match="Context cannot be empty"):
            llm.explain({})

    def test_explain_no_api_key_raises(self):
        """Test that missing API key raises RuntimeError."""
        with patch("infrastructure.llm.groq_llm.os.getenv", return_value=None):
            llm = GroqLLM()

        with pytest.raises(RuntimeError, match="Groq API key not configured"):
            llm.explain({"move": "e4"})

    def test_is_available_success(self, mock_groq_client):
        """Test availability check when service is available."""
        mock_groq_client.models.list.return_value = []

        with patch("infrastructure.llm.groq_llm.os.getenv", return_value="test-key"):
            llm = GroqLLM()
        assert llm.is_available() is True

    def test_is_available_failure_no_client(self):
        """Test availability check when no client configured."""
        with patch("infrastructure.llm.groq_llm.os.getenv", return_value=None):
            llm = GroqLLM()
        assert llm.is_available() is False

    def test_is_available_failure_connection_error(self, mock_groq_client):
        """Test availability check when service is unavailable."""
        from groq import APIConnectionError

        mock_groq_client.models.list.side_effect = APIConnectionError(
            request=MagicMock()
        )

        with patch("infrastructure.llm.groq_llm.os.getenv", return_value="test-key"):
            llm = GroqLLM()
        assert llm.is_available() is False

    def test_retry_logic_on_server_error(self, mock_groq_client):
        """Test retry logic on server errors."""
        from groq import APIError

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Success after retries"

        # First two calls fail with server error, third succeeds
        error = APIError(
            message="Server error", request=MagicMock(), body={"error": "server error"}
        )
        error.status_code = 500

        mock_groq_client.chat.completions.create.side_effect = [
            error,
            error,
            mock_response,
        ]

        with patch("infrastructure.llm.groq_llm.os.getenv", return_value="test-key"):
            with patch("infrastructure.llm.groq_llm.time.sleep"):  # Skip actual sleep
                llm = GroqLLM(max_retries=3)
                context = {"move": "e4"}

                result = llm.explain(context)
                assert result == "Success after retries"
                assert mock_groq_client.chat.completions.create.call_count == 3

    def test_no_retry_on_client_error(self, mock_groq_client):
        """Test that client errors don't trigger retries."""
        from groq import APIError

        error = APIError(
            message="Bad request", request=MagicMock(), body={"error": "bad request"}
        )
        error.status_code = 400

        mock_groq_client.chat.completions.create.side_effect = error

        with patch("infrastructure.llm.groq_llm.os.getenv", return_value="test-key"):
            llm = GroqLLM(max_retries=3)
            context = {"move": "e4"}

            with pytest.raises(RuntimeError, match="Groq API error"):
                llm.explain(context)

            # Should only be called once (no retries for client errors)
            assert mock_groq_client.chat.completions.create.call_count == 1


@pytest.mark.llm
@pytest.mark.integration
class TestGroqLLMIntegration:
    """Integration tests for GroqLLM (requires GROQ_API_KEY)."""

    def test_real_groq_connection(self):
        """Test real connection to Groq (skipped if not available)."""
        llm = GroqLLM(model="llama-3.1-8b-instant")

        if not llm.is_available():
            pytest.skip("Groq service not available (no API key or connection)")

        context = {"position": "starting position", "move": "e4", "evaluation": "+0.25"}

        result = llm.explain(context)
        assert isinstance(result, str)
        assert len(result) > 0

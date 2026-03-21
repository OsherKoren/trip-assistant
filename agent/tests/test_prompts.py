"""Tests for prompt utilities."""

from src.prompts import format_history
from src.schemas import HistoryEntry


class TestFormatHistory:
    """Tests for format_history utility."""

    def test_empty_history_returns_empty_string(self) -> None:
        """format_history returns empty string for empty list."""
        assert format_history([]) == ""

    def test_single_entry(self) -> None:
        """format_history formats a single entry correctly."""
        history: list[HistoryEntry] = [
            {"role": "user", "content": "What time is the flight?"},
        ]
        result = format_history(history)
        assert "User: What time is the flight?" in result
        assert result.startswith("Previous conversation:\n")

    def test_user_and_assistant_entries(self) -> None:
        """format_history formats both roles correctly."""
        history: list[HistoryEntry] = [
            {"role": "user", "content": "What time is the flight?"},
            {"role": "assistant", "content": "The flight departs at 10:00 AM."},
        ]
        result = format_history(history)
        assert "User: What time is the flight?" in result
        assert "Assistant: The flight departs at 10:00 AM." in result

    def test_truncation_to_max_turns(self) -> None:
        """format_history truncates to max_turns most recent entries."""
        history: list[HistoryEntry] = [
            {"role": "user", "content": f"Question {i}"} for i in range(15)
        ]
        result = format_history(history, max_turns=5)
        # Should only contain the last 5 entries (10-14)
        assert "Question 10" in result
        assert "Question 14" in result
        assert "Question 9" not in result

    def test_default_max_turns_is_ten(self) -> None:
        """format_history defaults to 10 max turns."""
        history: list[HistoryEntry] = [{"role": "user", "content": f"Q{i}"} for i in range(20)]
        result = format_history(history)
        assert "Q10" in result
        assert "Q19" in result
        assert "Q9" not in result

    def test_trailing_newlines_for_prompt_insertion(self) -> None:
        """format_history ends with double newline for clean prompt insertion."""
        history: list[HistoryEntry] = [
            {"role": "user", "content": "hello"},
        ]
        result = format_history(history)
        assert result.endswith("\n\n")

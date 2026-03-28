"""Tests for question normalization and hashing."""

import re

from app.cache import hash_question, normalize_question


class TestNormalizeQuestion:
    """Tests for normalize_question function."""

    def test_lowercase(self) -> None:
        assert normalize_question("HELLO") == "hello"

    def test_strip_whitespace(self) -> None:
        assert normalize_question("  hello  ") == "hello"

    def test_collapse_internal_whitespace(self) -> None:
        assert normalize_question("hello   world") == "hello world"

    def test_remove_punctuation_except_question_mark(self) -> None:
        assert normalize_question("hello, world! right?") == "hello world right?"

    def test_combined(self) -> None:
        assert normalize_question("  What TIME  is our   flight?!  ") == "what time is our flight?"

    def test_preserves_numbers(self) -> None:
        assert normalize_question("Flight at 3:00 PM?") == "flight at 300 pm?"

    def test_empty_string(self) -> None:
        assert normalize_question("") == ""

    def test_only_whitespace(self) -> None:
        assert normalize_question("   ") == ""


class TestHashQuestion:
    """Tests for hash_question function."""

    def test_deterministic(self) -> None:
        assert hash_question("hello") == hash_question("hello")

    def test_different_inputs(self) -> None:
        assert hash_question("hello") != hash_question("world")

    def test_is_hex_string(self) -> None:
        result = hash_question("test")
        assert re.match(r"^[0-9a-f]{64}$", result)

    def test_sha256_length(self) -> None:
        assert len(hash_question("anything")) == 64

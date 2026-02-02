"""Tests for documents module."""

from pathlib import Path

import pytest

from src.documents import load_documents


def test_load_documents_all_files():
    """Test that load_documents loads all 6 txt files from data directory."""
    documents = load_documents()

    assert len(documents) == 6
    assert all(isinstance(content, str) for content in documents.values())
    assert all(len(content) > 0 for content in documents.values())


@pytest.mark.parametrize(
    "expected_key",
    [
        pytest.param("flight", id="flight_file"),
        pytest.param("car_rental", id="car_rental_file"),
        pytest.param("routes_to_aosta", id="routes_file"),
        pytest.param("aosta_valley", id="aosta_file"),
        pytest.param("chamonix", id="chamonix_file"),
        pytest.param("annecy_geneva", id="annecy_geneva_file"),
    ],
)
def test_load_documents_expected_keys(expected_key: str):
    """Test that load_documents returns dict with all expected keys."""
    documents = load_documents()

    assert expected_key in documents
    assert isinstance(documents[expected_key], str)
    assert len(documents[expected_key]) > 0


def test_load_documents_custom_data_dir(tmp_path: Path):
    """Test that load_documents can load from a custom directory."""
    # Create test files in temporary directory
    test_file1 = tmp_path / "test1.txt"
    test_file2 = tmp_path / "test2.txt"
    test_file1.write_text("Test content 1")
    test_file2.write_text("Test content 2")

    documents = load_documents(tmp_path)

    assert len(documents) == 2
    assert documents["test1"] == "Test content 1"
    assert documents["test2"] == "Test content 2"


def test_load_documents_missing_directory():
    """Test that load_documents handles missing directory gracefully."""
    non_existent_dir = Path("/non/existent/directory")

    with pytest.raises(FileNotFoundError):
        load_documents(non_existent_dir)


def test_load_documents_empty_directory(tmp_path: Path):
    """Test that load_documents returns empty dict for directory with no txt files."""
    documents = load_documents(tmp_path)

    assert documents == {}

"""Tests for error handling across all nodes."""

import pytest

from src.nodes import (
    classify_question,
    handle_annecy_geneva,
    handle_aosta,
    handle_car_rental,
    handle_chamonix,
    handle_flight,
    handle_general,
    handle_routes,
)
from src.schemas import TripAssistantState


@pytest.mark.parametrize(
    "node_function,expected_source",
    [
        pytest.param(
            classify_question,
            None,  # Classifier doesn't set source
            id="classifier_error_handling",
        ),
        pytest.param(
            handle_flight,
            "flight.txt",  # Source still set
            id="flight_specialist_error_handling",
        ),
        pytest.param(
            handle_car_rental,
            "car_rental.txt",
            id="car_rental_specialist_error_handling",
        ),
        pytest.param(
            handle_routes,
            "routes_to_aosta.txt",
            id="routes_specialist_error_handling",
        ),
        pytest.param(
            handle_aosta,
            "aosta_valley.txt",
            id="aosta_specialist_error_handling",
        ),
        pytest.param(
            handle_chamonix,
            "chamonix.txt",
            id="chamonix_specialist_error_handling",
        ),
        pytest.param(
            handle_annecy_geneva,
            "annecy_geneva.txt",
            id="annecy_geneva_specialist_error_handling",
        ),
        pytest.param(
            handle_general,
            None,
            id="general_specialist_error_handling",
        ),
    ],
)
def test_all_nodes_handle_llm_failures_gracefully(
    mocker,
    sample_state: TripAssistantState,
    node_function,
    expected_source: str | None,
):
    """Test that all nodes handle LLM failures gracefully with proper error messages.

    This comprehensive test verifies that:
    1. Classifier falls back to "general" category with 0.0 confidence on error
    2. All specialists return user-friendly error messages on LLM failure
    3. No exceptions propagate up (graceful degradation)
    4. Proper logging occurs (via logger.error)
    5. Source fields are still set correctly even on error
    """
    # Mock logger to verify error logging
    mock_logger = mocker.patch("src.nodes.classifier.logger")
    mocker.patch("src.nodes.specialist_factory.logger", mock_logger)
    mocker.patch("src.nodes.general.logger", mock_logger)

    # Simulate LLM failure for all modules
    mock_llm_error = Exception("Simulated OpenAI API failure")

    # Mock classifier LLM to raise exception
    mock_classifier = mocker.patch("src.nodes.classifier.ChatOpenAI")
    mock_classifier.return_value.with_structured_output.return_value.invoke.side_effect = (
        mock_llm_error
    )

    # Mock specialist factory LLM to raise exception
    mock_specialist = mocker.patch("src.nodes.specialist_factory.ChatOpenAI")
    mock_specialist.return_value.invoke.side_effect = mock_llm_error

    # Mock general specialist LLM to raise exception
    mock_general = mocker.patch("src.nodes.general.ChatOpenAI")
    mock_general.return_value.invoke.side_effect = mock_llm_error

    # Execute the node function
    result = node_function(sample_state)

    # Verify result structure is valid
    assert isinstance(result, dict)

    # Verify behavior based on node type
    if node_function == classify_question:
        # Classifier should fall back to general category
        assert result["category"] == "general"
        assert result["confidence"] == 0.0
        assert "current_context" in result

        # Verify error was logged
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Classifier failed" in error_call

    else:
        # Specialists should return error message
        assert "answer" in result
        assert "source" in result

        # Answer should be a user-friendly error message
        answer = result["answer"]
        assert isinstance(answer, str)
        assert len(answer) > 0
        assert "Sorry" in answer or "couldn't" in answer

        # Should NOT be a raw exception or empty
        assert "Exception" not in answer
        assert "Traceback" not in answer

        # Source should still be set correctly
        assert result["source"] == expected_source

        # Verify error was logged
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "failed" in error_call.lower()


def test_routing_handles_missing_category(sample_state: TripAssistantState, mocker):
    """Test that routing function handles missing/None category gracefully."""
    from src.graph import route_by_category

    # Mock logger to verify warning
    mock_logger = mocker.patch("src.graph.logger")

    # Create state with no category
    state_no_category = sample_state.copy()
    state_no_category["category"] = None  # type: ignore[typeddict-item]

    # Route should fall back to general
    route = route_by_category(state_no_category)

    assert route == "general"

    # Verify warning was logged
    mock_logger.warning.assert_called_once()
    warning_call = mock_logger.warning.call_args[0][0]
    assert "No category" in warning_call
    assert "general" in warning_call


def test_error_messages_are_user_friendly():
    """Test that error messages in error handling are user-friendly.

    This test verifies the actual error message strings used in the code
    to ensure they follow best practices:
    - Apologetic tone
    - No technical jargon
    - Clear call to action
    - No raw exception details
    """
    # Read the actual error messages from source files
    import re
    from pathlib import Path

    agent_dir = Path(__file__).parent.parent

    # Check classifier error message
    classifier_file = agent_dir / "src" / "nodes" / "classifier.py"
    classifier_content = classifier_file.read_text()

    # Should have fallback to general category
    assert 'TopicClassification(category="general", confidence=0.0)' in classifier_content

    # Check specialist factory error messages
    factory_file = agent_dir / "src" / "nodes" / "specialist_factory.py"
    factory_content = factory_file.read_text()

    # Should have user-friendly error message
    error_msg_pattern = r'answer = .*"Sorry.*couldn\'t.*Please try again'
    assert re.search(error_msg_pattern, factory_content, re.DOTALL)

    # Check general specialist error message
    general_file = agent_dir / "src" / "nodes" / "general.py"
    general_content = general_file.read_text()

    # Should have user-friendly error message
    assert "Sorry" in general_content
    assert "couldn't" in general_content or "could not" in general_content

    # Should NOT have technical error details
    assert "Exception" not in classifier_content.split("logger.error")[1]  # After logging
    assert "Traceback" not in factory_content.split("logger.error")[1]
    assert "API" not in general_content.split("answer =")[1].split("return")[0]


def test_graph_end_to_end_with_classifier_error(mocker, sample_state: TripAssistantState):
    """Test complete graph execution when classifier fails.

    Verifies that:
    1. Classifier error causes fallback to general category
    2. Graph still completes execution (routes to general specialist)
    3. User gets a valid answer (even if it's an error message)
    4. No exceptions propagate
    """
    from src.graph import graph

    # Mock logger
    mock_logger = mocker.patch("src.nodes.classifier.logger")
    mocker.patch("src.nodes.general.logger", mock_logger)

    # Simulate classifier failure
    mock_classifier = mocker.patch("src.nodes.classifier.ChatOpenAI")
    mock_classifier.return_value.with_structured_output.return_value.invoke.side_effect = Exception(
        "Simulated classifier failure"
    )

    # Mock general specialist to succeed
    mock_general = mocker.patch("src.nodes.general.ChatOpenAI")
    mock_general.return_value.invoke.return_value.content = "I can help with general questions"

    # Execute graph
    result = graph.invoke(sample_state)

    # Should route to general due to classifier failure
    assert result["category"] == "general"
    assert result["confidence"] == 0.0

    # Should still get an answer from general specialist
    assert "answer" in result
    assert len(result["answer"]) > 0

    # Should have logged the classifier error
    assert mock_logger.error.called


def test_graph_end_to_end_with_specialist_error(mocker, sample_state: TripAssistantState):
    """Test complete graph execution when specialist fails.

    Verifies that:
    1. Classifier succeeds and routes correctly
    2. Specialist error is handled gracefully
    3. User gets error message (not exception)
    4. Graph completes without crashing
    """
    from src.graph import graph
    from src.nodes.classifier import TopicClassification

    # Mock logger
    mock_logger = mocker.patch("src.nodes.specialist_factory.logger")

    # Mock classifier to succeed
    mock_classification = TopicClassification(category="flight", confidence=0.95)
    mock_classifier = mocker.patch("src.nodes.classifier.ChatOpenAI")
    mock_classifier.return_value.with_structured_output.return_value.invoke.return_value = (
        mock_classification
    )

    # Simulate specialist failure
    mock_specialist = mocker.patch("src.nodes.specialist_factory.ChatOpenAI")
    mock_specialist.return_value.invoke.side_effect = Exception("Simulated specialist failure")

    # Execute graph
    result = graph.invoke(sample_state)

    # Should have correct category from classifier
    assert result["category"] == "flight"
    assert result["confidence"] == 0.95

    # Should have error message from specialist
    assert "answer" in result
    assert "Sorry" in result["answer"]
    assert "couldn't" in result["answer"]

    # Should still have source set
    assert result["source"] == "flight.txt"

    # Should have logged the specialist error
    assert mock_logger.error.called

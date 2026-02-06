"""LangGraph nodes for the Trip Assistant agent."""

from src.nodes.classifier import classify_question
from src.nodes.general import handle_general
from src.nodes.specialist_factory import create_specialist

# Create all specialist nodes using factory
# This ensures consistent behavior and error handling across all specialists
handle_flight = create_specialist("flight", "flight.txt")
handle_car_rental = create_specialist("car_rental", "car_rental.txt")
handle_routes = create_specialist("routes", "routes_to_aosta.txt")
handle_aosta = create_specialist("aosta", "aosta_valley.txt")
handle_chamonix = create_specialist("chamonix", "chamonix.txt")
handle_annecy_geneva = create_specialist("annecy_geneva", "annecy_geneva.txt")

__all__ = [
    "classify_question",
    "handle_flight",
    "handle_car_rental",
    "handle_routes",
    "handle_aosta",
    "handle_chamonix",
    "handle_annecy_geneva",
    "handle_general",
]

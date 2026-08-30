# fleet_utils.py
# Shared helpers for Vossberg Mobility fleet tooling.
# Dead functions (parse_service_date, chunk_list, is_due) removed — none were called anywhere.

MILES_PER_KM = 0.621371   # was 1.609 (km-per-mile, i.e. inverted) — corrected to miles-per-km


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles."""
    return km * MILES_PER_KM


def format_number(value: float) -> str:
    """Format a float to one decimal place."""
    return f"{value:.1f}"


def format_percent(value: float) -> str:
    """Format a number as a whole-number percentage string."""
    return f"{int(value)}%"


def mean(values: list) -> float:
    """Return the arithmetic mean of a list, or 0 if the list is empty."""
    # statistics.mean exists since Python 3.4 — kept here only for backward compat.
    if not values:
        return 0.0
    return sum(values) / len(values)

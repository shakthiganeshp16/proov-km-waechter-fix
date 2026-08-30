# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.
SERVICE_INTERVAL_KM = 15000
WARN_AT_PERCENT = 80


def wear_percent(km_since_service: float, interval: float) -> float:
    """Return how much of the service interval has been used, as a percentage (0–100+)."""
    return (km_since_service / interval) * 100   # true division — was erroneously //


def needs_service(car: dict) -> bool:
    """Return True when a car has consumed >= WARN_AT_PERCENT of its service interval."""
    last = car.get("last_service_km")
    if last is None:
        # No service reading on file — cannot calculate wear; treat as fresh.
        return False
    km_since = car["odometer"] - last
    return wear_percent(km_since, SERVICE_INTERVAL_KM) >= WARN_AT_PERCENT


def check_fleet(fleet: list) -> list:
    """Flag every car that needs service and return a list of their IDs."""
    flagged = []
    for car in fleet:
        if needs_service(car):
            flagged.append(car["id"])
            print(f"SERVICE DUE: {car['id']}")
    return flagged

"""Shared labels and edge types for rebuildable KG projections."""

from __future__ import annotations


ATM = "https://data.nasa.gov/ontologies/atmonto/ATM#"
NAS = "https://data.nasa.gov/ontologies/atmonto/NAS#"
EQP = "https://data.nasa.gov/ontologies/atmonto/equipment#"
GEN = "https://data.nasa.gov/ontologies/atmonto/general#"

SEMANTIC_RELATION = "SEMANTIC_RELATION"

FORMAL_CLASS_LABELS = {
    f"{ATM}Flight": "Flight",
    f"{ATM}ActualFlightRoute": "FlightRoute",
    f"{ATM}AircraftTrackPoint": "TrackPoint",
    f"{ATM}NavigationFix": "NavigationFix",
    f"{NAS}Sector": "Sector",
    f"{NAS}Airport": "Facility",
    f"{NAS}AirCarrier": "AirCarrier",
    f"{EQP}Aircraft": "Aircraft",
    f"{EQP}AircraftModel": "AircraftModel",
}

FORMAL_RELATIONSHIP_TYPES = {
    f"{ATM}departureAirport": "DEPARTURE_AIRPORT",
    f"{ATM}arrivalAirport": "ARRIVAL_AIRPORT",
    f"{ATM}aircraftFlown": "AIRCRAFT_FLOWN",
    f"{ATM}operatedBy": "OPERATED_BY",
    f"{ATM}hasActualRoute": "HAS_ACTUAL_ROUTE",
    f"{GEN}hasSequencedItem": "HAS_SEQUENCED_ITEM",
    f"{ATM}aircraftFix": "AIRCRAFT_FIX",
    f"{ATM}locatedInSector": "LOCATED_IN_SECTOR",
    f"{NAS}withinARTCC": "WITHIN_ARTCC",
    f"{EQP}hasAircraftModel": "HAS_AIRCRAFT_MODEL",
}


__all__ = [
    "FORMAL_CLASS_LABELS",
    "FORMAL_RELATIONSHIP_TYPES",
    "SEMANTIC_RELATION",
]

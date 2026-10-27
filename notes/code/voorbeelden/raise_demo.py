"""Drie manieren om in een except een fout te vertalen. Draai met: bereik | from | zonder | none"""
import sys

class MeetFout(Exception):
    """Fout bij het uitlezen van een instrument."""

def controleer_bereik(waarde):
    if waarde > 1000:
        raise ValueError(f"Waarde {waarde} V buiten bereik (max 1000 V)")
    return waarde

def lees_met_from(tekst):
    try:
        return float(tekst)
    except ValueError as e:
        raise MeetFout(f"Geen getal: '{tekst}'") from e

def lees_zonder_from(tekst):
    try:
        return float(tekst)
    except ValueError:
        raise MeetFout(f"Geen getal: '{tekst}'")

def lees_from_none(tekst):
    try:
        return float(tekst)
    except ValueError:
        raise MeetFout(f"Geen getal: '{tekst}'") from None

keuze = sys.argv[1] if len(sys.argv) > 1 else "from"
if keuze == "bereik":
    print(controleer_bereik(230))
    print(controleer_bereik(1500))
elif keuze == "from":
    lees_met_from("OVLD")
elif keuze == "zonder":
    lees_zonder_from("OVLD")
elif keuze == "none":
    lees_from_none("OVLD")

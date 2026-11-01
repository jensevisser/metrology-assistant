"""Hoe komt er iets in een functie? Draai met: zonder argument, en met bijv. 1500"""
import sys

print("1. Het bestand begint te draaien.")


def controleer(waarde):
    print(f"   binnenin de functie is waarde = {waarde}")
    return waarde > 1000


print("2. De functie is nu beschreven, maar nog niet gebruikt.")

print("3. sys.argv is alles wat je op de opdrachtregel typte:")
print(f"   sys.argv = {sys.argv}")
print(f"   len(sys.argv) = {len(sys.argv)}")

getypt = sys.argv[1] if len(sys.argv) > 1 else "230"
print(f"4. keuze geworden: getypt = '{getypt}'")

print("5. Nu roepen we de functie aan; hier komt er iets in:")
te_hoog = controleer(float(getypt))
print(f"6. De functie gaf terug: {te_hoog}")

from dataclasses import dataclass

@dataclass(frozen=True)
class Meting:
    waarde: float
    eenheid: str

m = Meting(waarde=10.0003, eenheid="V")
print(m)
print(m.waarde, m.eenheid)
m.waarde = 9.9

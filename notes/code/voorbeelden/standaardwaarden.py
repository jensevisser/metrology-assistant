"""Voorbeelden uit deel A: de ster in de parameters, x or y, en een lijst als standaardwaarde."""

print("== de ster: na * alleen bij naam ==")
def meet(kanaal, bereik=10, *, nplc=1):
    return f"kanaal={kanaal} bereik={bereik} nplc={nplc}"

print(meet(1))
print(meet(1, 100, nplc=10))
try:
    meet(1, 100, 10)
except TypeError as e:
    print("TypeError:", e)

print("== x or y ==")
print(None or {})
print({"temperature": 0.2} or {})
print({} or "leeg")
print(0 or 120)

print("== lijst als standaardwaarde: valkuil ==")
def log_meting(waarde, log=[]):
    log.append(waarde)
    return log

print(log_meting(10.0))
print(log_meting(9.9))
print("bewaarde standaard:", log_meting.__defaults__)

print("== met None: goed ==")
def log_meting2(waarde, log=None):
    log = log or []
    log.append(waarde)
    return log

print(log_meting2(10.0))
print(log_meting2(9.9))
print("bewaarde standaard:", log_meting2.__defaults__)

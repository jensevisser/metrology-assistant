class Meetinstrument:
    def __init__(self, serienummer: str, calibratiedatum: str):
        self.serienummer = serienummer
        self.calibratiedatum = calibratiedatum

    def omschrijving(self) -> str:
        return f"instrument {self.serienummer}, gecalibreerd {self.calibratiedatum}"

class Multimeter(Meetinstrument):
    def __init__(self, serienummer: str, calibratiedatum: str, digits: float):
        super().__init__(serienummer, calibratiedatum)
        self.digits = digits

    def omschrijving(self) -> str:
        return f"{self.digits}-digit multimeter, " + super().omschrijving()

dmm = Multimeter("MY12345", "2026-03-01", 6.5)
print(dmm.serienummer)
print(dmm.omschrijving())
print(isinstance(dmm, Meetinstrument), isinstance(dmm, Multimeter))
print(issubclass(Multimeter, Meetinstrument), issubclass(Meetinstrument, Multimeter))

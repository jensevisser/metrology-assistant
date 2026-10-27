class MeetFout(Exception):
    pass

def lees(tekst):
    try:
        print("try: ik probeer om te zetten")
        return float(tekst)
    except ValueError as e:
        print("except ValueError: ik gooi een MeetFout")
        raise MeetFout(f"Geen getal: '{tekst}'") from e
    except MeetFout:
        print("except MeetFout: ben ik hier?")
    finally:
        print("finally: ik draai nog, vlak voordat de fout lees() verlaat")

def meetlat():
    try:
        lees("OVLD")
    except MeetFout as e:
        print("meetlat: MeetFout opgevangen ->", e)

meetlat()

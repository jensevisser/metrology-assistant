def niveau3():
    print("niveau3: ik ga delen door nul")
    return 1 / 0

def niveau2():
    print("niveau2: ik roep niveau3 aan")
    uitkomst = niveau3()
    print("niveau2: deze regel wordt nooit bereikt")
    return uitkomst

def niveau1():
    print("niveau1: ik roep niveau2 aan, met try")
    try:
        return niveau2()
    except ZeroDivisionError:
        return "opgevangen in niveau1"

print(niveau1())
print("--- en nu zonder try ---")
niveau2()

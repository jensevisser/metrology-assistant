"""Laat zien wat sys.argv is. Draai met verschillende woorden erachter."""
import sys

print(f"aantal:  {len(sys.argv)}")
for i, woord in enumerate(sys.argv):
    print(f"  argv[{i}] = {woord!r}")

"""The path options of the heavy entry points (#328), now inside the kit (original_match/fileopts.py) so that the kit
vendors as one folder, as its README says (goal2#483). This name stays for the scripts that import it from runtime/:
it is the same module object, so a test that patches one patches the other."""
import sys

from original_match import fileopts as _fileopts

sys.modules[__name__] = _fileopts

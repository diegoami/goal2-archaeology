# artifacts/

`known.json`: GOAL2's artifact sets, by hash: `goal2-a949da2f` and its successor `goal2-67cf27d6`,
which declares what the runtime writes (`*.GL`, `*.SUM`; F001, U21) over the same ten files. The ten
original files are assets of this repository's release `goal2-original` (U17), never committed.

`saves.json`: the owner's saved games (`*.GL`), assets of release `goal2-saves`, by hash, never
committed. `python3 tools/fetch_saves.py` downloads and verifies them into `.cache/saves/`
(`--refresh` downloads all again, `--check` verifies only); `--add FILE.GL [--as NAME.GL]` uploads
a new one and records its hash (commit `saves.json`). The recorder fetches them before every sitting.

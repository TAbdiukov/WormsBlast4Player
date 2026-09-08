# Worms Blast - experimental four-player bindings

`controls.txt` is a 48-record test preset. `generate_controls.py` writes a fixed P1-P4 keyboard preset.

> **Not a complete four-player fix.** These files supply keyboard bindings; they do not make `/4PLAYER` fully playable. Issues may include round-start failures and unresponsive in-game movement. The game's four-player path may be bugged or unfinished; the root cause remains unconfirmed. **Do report usage issues and bugs.**

## Preset

| Action | P1 | P2 | P3 | P4 |
|---|---|---|---|---|
| Move left | Left arrow | A | J | Numpad 4 |
| Move right | Right arrow | D | L | Numpad 6 |
| Aim up | Up arrow | W | I | Numpad 8 |
| Aim down | Down arrow | S | K | Numpad 2 |
| Fire | Space | Left Shift | U | Numpad + |
| Swap weapon | Enter | Left Ctrl | O | Numpad Enter |

P4 needs a numeric keypad.

## Generate the preset

Requires Python 3.9+, no dependencies.

```bat
python generate_controls.py --output "controls.generated.txt"
```

Normal generation always emits the fixed preset shown above.

To inspect the DAT without generating `controls.txt`, use:

```bat
python generate_controls.py -r
```

`--read` is the long form. This diagnostic mode uses `data\controls.dat` by default; if
needed, override that path with `--source`. Do not use `contrPS2.dat`.

This prints the parsed type-7 control records and writes the same diagnostic readout to a
timestamped file such as `controls.readout.20260908-095600.txt` in the current directory.

The generator writes exactly 48 fixed keyboard records for P1-P4 and does not inspect the
DAT for conflicts or existing mappings. `--read/-r` remains diagnostic only and rejects
malformed DAT structure while printing the parsed type-7 bindings for inspection.

## Install and test

Back up `controls.txt`, `data\controls.dat`, and `GameSave.dat`. Prefer a separate installation copy.

Rename the generated file to `controls.txt`, or use the preset. Place it beside `start.bat` in the game root:

```bat
@echo off
set "XEF=.\XEF"
set "XOM=.\XOM"
".\XOM\bin\WormsBlast.exe" /4PLAYER /NOLOGO /W [width] /H [height] /WIN
```

(adjust [width] and [height] per desired resolution)

WormsBlast.exe will compile `controls.txt` into `data\controls.dat`. 

**Save data can override bindings.** Startup subsequently loads `data\GameSave.dat`, falling back to `data\DfGmSv.dat`. Moving the main save aside may not remove overrides. Test on a copy rather than deleting progress.

Select human players. Leave debug keys and camera controls disabled. Test every action and key release separately, then simultaneous input. Try setting Player 3 or 4 to be human for the first time. Shared-keyboard rollover/ghosting limits still apply.

## File format

Exactly one skipped header line, followed by tab-separated records:

```text
record_id<TAB>ACTION<TAB>zero_based_player<TAB>group<TAB>decimal_keycode
```

The file format uses literal tabs, ASCII without a BOM, CRLF line endings without a final newline.

-------------------
Tim Abdiukov

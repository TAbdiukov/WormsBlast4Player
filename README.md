# Worms Blast - experimental four-player bindings

`controls.txt` is a 48-record test preset. `generate_controls.py` exports existing keyboard mappings from `controls.dat`, preserves P1/P2, and adds or replaces P3/P4.

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

P4 needs a numeric keypad. To retain your actual P1/P2 defaults, generate a file from the original DAT instead.

## Preserve existing mappings

Requires Python 3.9+, no dependencies.

```bat
python generate_controls.py --output "controls.from-defaults.txt"
```

The script expects `data\controls.dat` relative to the current directory and reports a
successful read/parse before generating output. If needed, override that path explicitly:

```bat
python generate_controls.py --source "D:\path\to\data\controls.dat" --output "controls.from-defaults.txt"
```

Do not use `contrPS2.dat`.

To inspect the DAT without generating `controls.txt`, use:

```bat
python generate_controls.py --read
```

This prints the parsed type-7 control records and writes the same diagnostic readout to a
timestamped file such as `controls.readout.20260908-095600.txt` in the current directory.

The generator preserves text-representable input records except P3/P4 replacement slots `7000–7011` and `8000–8011`. It validates the P1/P2 core mappings and selects non-overlapping P3/P4 keys, preferring the layouts above. Check its printed assignments; conflicts may select alternatives.

It leaves the source untouched, refuses output overwrites, and rejects malformed or unsupported bindings—including gamepad/axis records, unsupported actions, and nonzero extra/source fields. Non-input DAT sections are reported but not exported: this preserves input mappings, not the entire DAT.

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

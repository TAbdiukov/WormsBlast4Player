# Worms Blast /4PLAYER Fix

Fixes Worms Blast's `/4PLAYER` mode and provides four-player keyboard bindings.

[![buymeacoffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/tabdiukov)

**For almost all users:** download the [latest release](https://github.com/TAbdiukov/WormsBlast4PlayerFix/releases/latest).

The included `controls.txt` provides keyboard bindings for four local players. The optional `generate_controls.py` utility can instead create a controls file that preserves Player 1's bindings from your existing `data\controls.dat`.

Please report bugs or compatibility problems through [GitHub Issues](https://github.com/TAbdiukov/WormsBlast4PlayerFix/issues).

## Default controls

| Action      | P1          | P2           | P3 | P4 |
| ----------- | ----------- | ------------ | -- | -- |
| Move left   | Left arrow  | Numpad 4     | J  | A  |
| Move right  | Right arrow | Numpad 6     | L  | D  |
| Aim up      | Up arrow    | Numpad 8     | I  | W  |
| Aim down    | Down arrow  | Numpad 2     | K  | S  |
| Fire        | Space       | Numpad +     | U  | Q  |
| Swap weapon | Enter       | Numpad Enter | O  | E  |

P2 requires a numeric keypad.

## Installation

1. Download the [latest release](https://github.com/TAbdiukov/WormsBlast4PlayerFix/releases/latest).
2. Back up your existing game files, particularly `controls.txt`, `data\controls.dat`, and `data\GameSave.dat`.
3. Follow the instructions included with the release.
4. Start Worms Blast with the `/4PLAYER` option and select human players.

> **Save data can override bindings.** The game subsequently loads `data\GameSave.dat`, falling back to `data\DfGmSv.dat`. Test changes on a copy of the game rather than deleting existing progress.

Shared-keyboard rollover and ghosting limitations still apply.

## Optional: preserve your existing P1 mapping

Requires Python 3.9 or later and has no external dependencies.

Use this only if you want to generate a four-player `controls.txt` while retaining Player 1's existing keyboard mapping:

```bat
python generate_controls.py --output "controls.from-defaults.txt"
```

### Inspect an existing controls.dat

To parse and inspect the DAT without generating a new controls.txt, use:
```
python generate_controls.py --read
```

`--read` does not generate or modify controls.txt or the source DAT.

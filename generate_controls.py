#!/usr/bin/env python3
"""Generate Worms Blast PC controls.txt with fixed four-player keyboard rows.

Source: supplied WormsBlast.exe.c (Build 1.09 decompilation).
Binary reader: sub_498520 / sub_49B9B0.
Text format: sub_49B5C0. IDs: sub_45AB70. Groups: sub_428B40.

Uses only Python's standard library. Normal generation does not read controls.dat and
never overwrites an existing output. --read/-r remains available for DAT diagnostics.
Static/synthetic tests are not a substitute for testing the actual game.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import struct
import sys

# (action name, first ID offset, press action, release action)
ACTIONS = (
    ("FIRE", 0, 17008, 17009),
    ("LEFT", 2, 17002, 17003),
    ("RIGHT", 4, 17000, 17001),
    ("UP", 6, 17004, 17005),
    ("DOWN", 8, 17006, 17007),
    ("SWAP", 10, 17012, 17013),
)
TOKENS = {press: (name + "_P", 1) for name, _, press, _ in ACTIONS}
TOKENS.update({release: (name + "_R", 2) for name, _, _, release in ACTIONS})
TOKENS[17014] = ("START_P", 1)

# Fixed preset. Tuple order is FIRE, LEFT, RIGHT, UP, DOWN, SWAP. Numbers use
# the DirectInput-style scan-code convention.
LAYOUTS = (
    ("Arrows / Space / Enter",
     (("Space", 57), ("Left", 203), ("Right", 205), ("Up", 200),
      ("Down", 208), ("Enter", 28))),
    ("WASD / LeftShift / LeftCtrl",
     (("LeftShift", 42), ("A", 30), ("D", 32), ("W", 17),
      ("S", 31), ("LeftCtrl", 29))),
    ("IJKL / U / O",
     (("U", 22), ("J", 36), ("L", 38), ("I", 23), ("K", 37), ("O", 24))),
    ("Numeric keypad / Num+ / NumEnter",
     (("Num+", 78), ("Num4", 75), ("Num6", 77), ("Num8", 72),
      ("Num2", 80), ("NumEnter", 156))),
)
KEY_NAMES = {code: name for _, keys in LAYOUTS for name, code in keys}
KEY_NAMES.update({1: "Escape", 15: "Tab"})

class FormatError(ValueError):
    """Invalid or unsupported input; do not emit a lossy controls file."""

class Reader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.pos = 0

    def take(self, size: int) -> bytes:
        if size < 0 or size > len(self.data) - self.pos:
            raise FormatError("Truncated or invalid DAT at offset 0x%X." % self.pos)
        result = self.data[self.pos:self.pos + size]
        self.pos += size
        return result

    def u32(self) -> int:
        return struct.unpack("<I", self.take(4))[0]

    def string(self) -> None:
        self.take(self.u32())

@dataclass(frozen=True)
class Binding:
    record_id: int
    action: int
    group: int
    player: int
    extra: int
    source0: int
    source1: int
    source2: int
    edge: int
    key: int

    def check_text_representable(self) -> None:
        token = TOKENS.get(self.action)
        if token is None or self.edge != token[1]:
            raise FormatError("Record %d has an unsupported action/edge (%d/%d)."
                              % (self.record_id, self.action, self.edge))
        if (self.extra, self.source0, self.source1, self.source2) != (0, 0, 0, 0):
            raise FormatError(
                "Record %d is not a plain PC keyboard record. controls.txt cannot "
                "preserve its source/extra fields; no output was written."
                % self.record_id)
        if not 0 <= self.key <= 255:
            raise FormatError("Record %d has an unexpected key code %d."
                              % (self.record_id, self.key))

    def line(self) -> str:
        self.check_text_representable()
        return "%d\t%s\t%d\t%d\t%d" % (
            self.record_id, TOKENS[self.action][0], self.player, self.group, self.key)

def read_dat(data: bytes) -> tuple[list[Binding], tuple[int, ...]]:
    """Read seven section counts, then the variable/record sections in order."""
    if len(data) < 28:
        raise FormatError("DAT is too small for its seven-count header.")
    reader = Reader(data)
    counts = struct.unpack("<7I", reader.take(28))
    if sum(counts) > (len(data) - 28) // 4:
        raise FormatError("Implausible section counts; this may be another file format.")
    result: list[Binding] = []
    seen: set[int] = set()
    for kind, count in enumerate(counts, start=1):
        for _ in range(count):
            record_id = struct.unpack("<i", reader.take(4))[0]
            if record_id in seen:
                raise FormatError("Duplicate record ID %d." % record_id)
            seen.add(record_id)
            if kind == 7:
                result.append(Binding(record_id, *struct.unpack("<9i", reader.take(36))))
                continue
            if kind in (1, 2):
                reader.take(4)
            elif kind == 3:
                reader.string()
            elif kind == 4:
                reader.take(32)
            elif kind == 5:
                reader.take(156)
            else:  # type 6: one string, then three (string, 32-bit value) pairs
                reader.string()
                for _ in range(3):
                    reader.string()
                    reader.take(4)
    if reader.pos != len(data):
        raise FormatError("Unexpected trailing data at offset 0x%X." % reader.pos)
    if not result:
        raise FormatError("No type-7 control records found.")
    return result, counts

def verify_player(rows: list[Binding], player: int) -> None:
    by_id = {row.record_id: row for row in rows}
    base = 5000 + 1000 * player
    for name, offset, press, release in ACTIONS:
        pair = []
        for delta, action in enumerate((press, release)):
            row = by_id.get(base + offset + delta)
            if row is None:
                raise FormatError("Missing P%d %s record %d."
                                  % (player + 1, name, base + offset + delta))
            row.check_text_representable()
            if (row.action, row.group, row.player, row.edge) != (
                    action, player, player, delta + 1):
                raise FormatError("Unexpected P%d action/group/player in record %d."
                                  % (player + 1, row.record_id))
            pair.append(row)
        if pair[0].key != pair[1].key:
            raise FormatError("P%d %s press/release keys differ." % (player + 1, name))
    keys = [by_id[base + offset].key for _, offset, _, _ in ACTIONS]
    if len(set(keys)) != len(keys):
        raise FormatError("P%d uses the same key for multiple core actions." % (player + 1))

def make_player(player: int, keys: tuple[tuple[str, int], ...]) -> list[Binding]:
    rows = []
    base = 5000 + 1000 * player
    for (_, offset, press, release), (_, key) in zip(ACTIONS, keys):
        rows.append(Binding(base + offset, press, player, player, 0, 0, 0, 0, 1, key))
        rows.append(Binding(base + offset + 1, release, player, player, 0, 0, 0, 0, 2, key))
    return rows

def make_preset() -> tuple[list[Binding], dict[int, str]]:
    """Build the fixed P1-P4 keyboard preset without reading controls.dat."""
    result: list[Binding] = []
    descriptions: dict[int, str] = {}
    for player, (name, keys) in enumerate(LAYOUTS):
        result.extend(make_player(player, keys))
        descriptions[player] = name
    for player in range(4):
        verify_player(result, player)
    if len({row.record_id for row in result}) != len(result):
        raise FormatError("Duplicate IDs in fixed preset.")
    return result, descriptions

def render(rows: list[Binding], header: str) -> bytes:
    # One skipped header, literal tabs, ASCII, CRLF, and no final newline.
    if "\n" in header or "\r" in header:
        raise ValueError("Header must occupy one line.")
    return "\r\n".join([header] + [row.line() for row in rows]).encode("ascii")

def render_readout(source: Path, rows: list[Binding], counts: tuple[int, ...],
                   timestamp: datetime) -> str:
    lines = [
        "Source: %s" % source,
        "Read at: %s" % timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "Section counts: %s" % ", ".join(str(count) for count in counts),
        "Input mappings: %d" % len(rows),
        "",
        "ID\tACTION\tACTION_ID\tPLAYER\tGROUP\tEDGE\tKEY\tEXTRA\tSOURCE0\tSOURCE1\tSOURCE2",
    ]
    for row in rows:
        token = TOKENS.get(row.action)
        action_name = token[0] if token is not None else "UNKNOWN"
        lines.append("%d\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d" % (
            row.record_id, action_name, row.action, row.player, row.group, row.edge,
            row.key, row.extra, row.source0, row.source1, row.source2))
    return "\n".join(lines) + "\n"

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("data") / "controls.dat",
                        help="PC controls DAT used only by --read/-r (default: data\\controls.dat)")
    parser.add_argument("-o", "--output", type=Path, default=Path("controls.txt"),
                        help="New text file; must not already exist (default: controls.txt)")
    parser.add_argument("-r", "--read", action="store_true",
                        help="Read the DAT, print its input records, and save a timestamped readout")
    args = parser.parse_args()
    try:
        if args.read:
            if not args.source.exists():
                raise FormatError(
                    "Expected controls DAT was not found: %s\n"
                    "Run this script from the game root, or specify another DAT with --source PATH."
                    % args.source)
            if args.source.stat().st_size > 32 * 1024 * 1024:
                raise FormatError("Input exceeds the conservative 32 MiB size limit.")
            rows, counts = read_dat(args.source.read_bytes())
            print("Successfully read and parsed %s (%d input mappings)." %
                  (args.source, len(rows)))
            timestamp = datetime.now()
            readout_path = Path("%s.read.%s.txt" % (
                args.source.stem, timestamp.strftime("%Y%m%d-%H%M%S")))
            readout = render_readout(args.source, rows, counts, timestamp)
            sys.stdout.write(readout)
            with readout_path.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(readout)
            print("Saved readout to %s." % readout_path)
            return 0
        if args.output.exists():
            raise FormatError("Output already exists; choose another --output filename.")
        result, layouts = make_preset()
        payload = render(
            result, "ID\tACTION\tPLAYER\tGROUP\tKEYCODE | fixed P1-P4 preset")
        with args.output.open("xb") as stream:
            stream.write(payload)
        print("Created %s (%d mappings)." % (args.output, len(result)))
        print("controls.dat was not read or changed; all four players use the fixed preset.")
        by_id = {row.record_id: row for row in result}
        for player in range(4):
            values = []
            for name, offset, _, _ in ACTIONS:
                key = by_id[5000 + player * 1000 + offset].key
                values.append("%s=%s[%d]" % (name, KEY_NAMES.get(key, "scan code"), key))
            print("P%d (%s): %s" % (player + 1, layouts[player], ", ".join(values)))
        print("Back up game files before installation. Existing save data may override controls.")
        return 0
    except (OSError, ValueError, struct.error) as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())

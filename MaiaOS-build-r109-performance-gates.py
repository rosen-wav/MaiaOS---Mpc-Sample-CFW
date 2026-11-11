#!/usr/bin/env python3
"""Rebuild the MaiaOS r109 performance gates using verified local stock."""
import argparse
from hashlib import sha256
from pathlib import Path
import re
import struct
import subprocess

STOCK_SHA = "b6584cba76e416e432ad202509099d34373dc2c3d6a8fb625f5678bf0193b508"
REPLAY_SITES = {
    "missing_sample_gate": 0x1D61D4C,
    "missing_project_gate": 0x1D63A9C,
    "missing_program_gate": 0x1D6A3E4,
    "missing_file_a_gate": 0xF7900C,
    "missing_file_b_gate": 0xF796E8,
    "missing_file_c_gate": 0xF79A5C,
}
GATE_ADDRESS = 0x7435400


def stock_adrp(stock, site):
    instruction = struct.unpack_from("<I", stock, site)[0]
    if instruction & 0x9F000000 != 0x90000000:
        raise ValueError(f"Expected ADRP at stock offset {site:#x}")
    immediate = ((instruction >> 5) & 0x7FFFF) << 2 | (instruction >> 29) & 3
    if immediate & (1 << 20):
        immediate -= 1 << 21
    return instruction & 31, (site & ~0xFFF) + (immediate << 12)


def source_and_layout(stock, source):
    source, count = re.subn(r"^cmp w12,#20$", "cmp w12,#10", source, flags=re.M)
    if count != 1:
        raise ValueError("Unexpected sample voice limit in the source")
    for gate, site in REPLAY_SITES.items():
        start = source.index(f"\n{gate}:\n")
        end = source.index("\n.global ", start)
        register, page = stock_adrp(stock, site)
        block, count = re.subn(
            r"^adrp x[0-9]+,0x[0-9a-f]+(?=\nb 0x[0-9a-f]+$)",
            f"adrp x{register},{page:#x}",
            source[start:end],
            flags=re.M,
        )
        if count != 1:
            raise ValueError(f"Unexpected replay instruction for {gate}")
        source = source[:start] + block + source[end:]

    targets = set()

    def declare(match):
        target = int(match[2], 16)
        targets.add(target)
        return match[1] + f"gate_target_{target:x}"

    source = re.sub(
        r"^([ \t]*(?:b[ \t]+|adrp[ \t]+x[0-9]+,[ \t]*))0x([0-9a-fA-F]+)[ \t]*$",
        declare, source, flags=re.M,
    )
    layout = (
        "ENTRY(pad_pressure_gate)\n"
        f"SECTIONS {{ . = {GATE_ADDRESS:#x}; .text : {{ *(.text*) }} "
        "/DISCARD/ : { *(.note* .comment .eh_frame*) } }\n"
    )
    layout += "".join(f"gate_target_{target:x} = {target:#x};\n" for target in sorted(targets))
    return source, layout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True, help="Historical performance-gates.S")
    parser.add_argument("--output", type=Path, required=True, help="New build directory")
    parser.add_argument("--zig", default="zig")
    args = parser.parse_args()
    stock = args.stock.read_bytes()
    if sha256(stock).hexdigest() != STOCK_SHA:
        parser.error("Expected stock firmware 1.3.0.12")
    source, layout = source_and_layout(stock, args.source.read_text())
    args.output.mkdir()
    assembly = args.output / "performance.S"
    linker_script = args.output / "performance.ld"
    obj = args.output / "performance.o"
    elf = args.output / "performance.elf"
    assembly.write_text(source)
    linker_script.write_text(layout)
    subprocess.run([args.zig, "cc", "-target", "aarch64-linux-none", "-c", str(assembly),
                    "-o", str(obj)], check=True)
    subprocess.run([args.zig, "ld.lld", "-T", str(linker_script), str(obj), "-o", str(elf)],
                   check=True)
    print(elf)


if __name__ == "__main__":
    main()

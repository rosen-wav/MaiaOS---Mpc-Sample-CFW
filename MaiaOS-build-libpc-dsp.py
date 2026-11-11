"""Build libpc-dsp from the recovered MPC-audio-work-no-soundfont/dsp tree."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import re
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("dsp", type=Path, help="Extracted checkpoint dsp directory, with the sibling theme directory")
parser.add_argument("output", type=Path, help="New output directory")
parser.add_argument("--zig", type=Path, help="Zig 0.14.1 executable for ARM64. Omit for a native Linux test.")
args = parser.parse_args()
dsp = args.dsp.resolve()
out = args.output.resolve()
zig = str(args.zig.resolve()) if args.zig else None
out.mkdir(parents=True)
cc = [zig, "cc", "-target", "aarch64-linux-gnu.2.31"] if zig else ["cc"]
cxx = [zig, "c++", "-target", "aarch64-linux-gnu.2.31"] if zig else ["c++"]
fluid = dsp / "extra/fluidsynth"
headers = out / "include"
(headers / "fluidsynth").mkdir(parents=True, exist_ok=True)
(headers / "fluidsynth.h").write_text((fluid / "include/fluidsynth.cmake").read_text().replace(
    "#cmakedefine01 BUILD_SHARED_LIBS", "#define BUILD_SHARED_LIBS 0"))
version = (fluid / "include/fluidsynth/version.h.in").read_text()
for name, value in (("VERSION", "2.6.1"), ("VERSION_MAJOR", "2"), ("VERSION_MINOR", "6"), ("VERSION_MICRO", "1")):
    version = version.replace(f"@FLUIDSYNTH_{name}@", value)
(headers / "fluidsynth/version.h").write_text(version)
supported = set("""
HAVE_ARPA_INET_H HAVE_ERRNO_H HAVE_FCNTL_H HAVE_INTTYPES_H HAVE_LIMITS_H HAVE_MATH_H
HAVE_NETINET_IN_H HAVE_NETINET_TCP_H HAVE_PTHREAD_H HAVE_SIGNAL_H HAVE_STDARG_H HAVE_STDINT_H
HAVE_STDIO_H HAVE_STDLIB_H HAVE_STRINGS_H HAVE_STRING_H HAVE_SYS_MMAN_H HAVE_SYS_SOCKET_H
HAVE_SYS_STAT_H HAVE_SYS_TIME_H HAVE_SYS_TYPES_H HAVE_UNISTD_H HAVE_GETOPT_H HAVE_INETNTOP
STDC_HEADERS SUPPORTS_VLA HAVE_SINF HAVE_COSF HAVE_FABSF HAVE_POWF HAVE_SQRTF HAVE_LOGF
HAVE_SOCKLEN_T WITH_FLOAT HAVE_CXX_FILESYSTEM
""".split())
config = (fluid / "src/config.cmake").read_text().replace("@osal@", "cpp11")
config = re.sub(r"^#cmakedefine (\w+).*$",
                lambda m: f"#define {m[1]} 1" if m[1] in supported else "",
                config, flags=re.M)
(headers / "config.h").write_text(config)
cmake = (fluid / "src/CMakeLists.txt").read_text()
listing = re.search(r"set\s*\(\s*libfluidsynth_SOURCES\b(.*?)\)", cmake, re.S)[1]
fluid_sources = [fluid / "src" / n for n in listing.split() if n.endswith((".c", ".cpp"))]
fluid_sources += [fluid / "src/utils" / n for n in ("fluid_sys_cpp11.cpp", "fluid_file.cpp")]
extra = dsp / "extra"
extras = [extra / "extra.cpp", *sorted((extra / "dexed").glob("*.cc")), extra / "dexed/porta.cpp"]
extras = [f for f in extras if f.name != "tuning.cc"]
extras += [extra / "tunefish" / n for n in ("runtime/runtime.cpp", "runtime/array.cpp",
           "runtime/random.cpp", "synth/tf4.cpp", "synth/tf4fx.cpp")]
core = dsp / "source/adapter/synth_core.c"
sources = fluid_sources + extras + [core]
fluid_includes = [fluid / "src" / n for n in ("", "drivers", "synth", "rvoice", "midi", "utils", "sfloader", "bindings")]
includes = [headers, fluid / "include", fluid / "gcem/include", *fluid_includes]
common = ["-O2", "-fPIC", "-fvisibility=hidden", "-fwrapv", "-fno-strict-aliasing", "-fno-stack-protector"]

def build(item):
    index, source = item
    obj = out / f"{index:03d}-{source.stem}.o"
    if source == core:
        options = ["-ffreestanding", "-fno-builtin"]
        paths = [dsp / "source/include", dsp / "source/vendor/build/gen", dsp / "source/vendor/firmware/src", dsp / "source/adapter"]
    else:
        options = ["-std=c++17"] if source.suffix != ".c" else []
        if source in extras:
            options += ["-DeVSTI", "-Wno-deprecated-declarations"]
        paths = includes + [dsp / "source/adapter"]
    compiler = cc if source.suffix == ".c" else cxx
    result = subprocess.run([*compiler, *common, *options, *[f"-I{p}" for p in paths],
                             "-c", str(source), "-o", str(obj)], capture_output=True, text=True)
    if result.returncode:
        obj.unlink(missing_ok=True)
        raise RuntimeError(f"{source.name}: {result.stderr}")
    return obj

with ThreadPoolExecutor(max_workers=6) as pool:
    objects = list(pool.map(build, enumerate(sources)))
result = out / "libpc-dsp.so"
subprocess.run([*cxx, "-shared", "-Wl,-Bsymbolic", "-Wl,-z,defs",
                *map(str, objects), "-lm", "-pthread", "-o", str(result)], check=True)
print(result)

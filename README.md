# MaiaOS v1 — r109 public source preview

MaiaOS extends the Akai MPC Sample. This preview targets stock firmware **1.3.0.12** and includes the r109 host source, selected runtime sources, and the English installation and operating guides.

**Release status:** The first beta is out now in releases

## Get started

- [Installation guide](INSTALL.md) covers preparing a test microSD from a local r109 runtime, booting it, troubleshooting and returning to the previous setup.
- [User manual](MANUAL.md) covers DJ Mode, grooves, chords, Drumkit, Multisamples, AutoTune and effects. The controls describe r109, so use them with an installed r109 runtime.
- [Build notes](BUILD.md) cover Linux builds, tests and the remaining work for a stock-only release.

## Open-source credits

The notices and source headers record the authorship and license for individual files. Upstream projects can contain components beyond the portions used by MaiaOS.

| Project | Use and license | Notices |
| --- | --- | --- |
| Mixxx | DJ beat-grid fitting and lookup, analysis settings and filter mapping. GPL-2.0-or-later. | [Mixxx notice](SRC/host/LICENSES/dj-mixxx-NOTICE.txt) |
| Queen Mary DSP and Kiss FFT | Tempo, onset and beat tracking, spectral analysis and FFT. Queen Mary DSP is GPL-2.0-or-later. Kiss FFT carries its own BSD-style terms. | [QM DSP source and licenses](SRC/host/vendor/qm-dsp/) |
| Airwindows by Chris Johnson | Galactic3 reverb, Highpass2, Pressure6 compression and Mastering2. MIT. | [Airwindows notices](SRC/host/LICENSES/) and [Mastering2](SRC/host/src/LICENSE-Mastering2.txt) |
| More Chords, Melodee and Felucca | FM6 synthesis and upstream engine code. GPL-3.0-only. | [FM6 licensing](SRC/host/vendor/more-chords-fm6/LICENSING.md) |
| Dexed and Music Synthesizer for Android | FM6 lineage. Dexed is GPL-3.0-or-later and MSFA is Apache-2.0. | [Melodee licensing](SRC/host/dsp/new/MELODEE-LICENSING.md) |
| CS-1, Dinghy and SLOOP | Upstream synth code and its lineage. See the source-specific notices for GPL-3.0-only code and retained upstream credits. | [CS-1 licensing](SRC/host/dsp/new/CS1-LICENSING.md) and [Melodee licensing](SRC/host/dsp/new/MELODEE-LICENSING.md) |
| RS-01 / Schwung | Synth code by Charles Vestal, MIT. | [RS-01 license](SRC/host/dsp/new/rs01/LICENSE) |
| DaisySP, Rings, MAME uPD933, reSID and CrispyZebra | DSP lineage identified in the retained engine notices. DaisySP and Rings are MIT, uPD933 is BSD-3-Clause, reSID is GPL-2.0-or-later and CrispyZebra is GPL-3.0. | [Engine notices](SRC/host/dsp/new/MELODEE-LICENSING.md) |
| Flayr Tune | Pitch correction engine, AGPL-3.0. | [Tune license](SRC/runtime/SRC/autotune/vendor/LICENSE) |
| War Bells, Schwung module headers and Freeverb | War Bells send effect, AGPL-3.0-or-later. Schwung headers are MIT. War Bells credits the public-domain Freeverb design. | [War Bells third-party notices](SRC/runtime/SRC/fx/licenses/War-Bells-THIRD_PARTY.md) |
| IBM Plex Mono, Space Grotesk, Roboto and Titillium | Typeface files, glyphs or fallback credits. IBM Plex Mono, Space Grotesk and Titillium are SIL OFL 1.1. Roboto glyphs carry Apache-2.0 terms. | [Font notices](SRC/host/theme/fonts/) |
| DejaVu / Bitstream Vera, Rubik, Inter Tight, Terminus and Fukiai | Font credits in retained source and upstream notices. The font-specific terms are recorded there. | [Theme font license](SRC/host/theme/FONT-LICENSE.txt) and [upstream notices](SRC/host/dsp/new/LICENSES/) |

Source builds use Zig, Clang/LLD, Python and GNU C/C++ headers. Runtime tests also use Unicorn and pyelftools. GNU runtime notices are in the [AutoTune source](SRC/runtime/SRC/autotune/licenses/).

These credits cover the included sources and their documented lineage. The historical WT Lite runtime has Vital/JUCE lineage. The exact dependency and license inventory for that runtime and the remaining DSP modules still needs verification before a complete binary release. The Akai time-stretch and filter used by r109 belong to the firmware on the device.

MaiaOS is an independent project for the Akai MPC Sample.

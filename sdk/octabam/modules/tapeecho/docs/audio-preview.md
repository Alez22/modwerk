# Tape Echo audio preview provenance

This preview was rendered on 12 October 2026 through the unchanged 0.1.2-experimental fixed-point CPU engine. Editorial release 0.1.3-experimental retains that exact runtime and its historical test status. This is an offline computer render, with no new hardware or performance qualification.

`media/audio-preview.mp3` uses an original Modwerk woodblock transient created with deterministic additive synthesis. The original source sound and final render are copyright 2026 Modwerk contributors, licensed under the MIT terms in the module [LICENSE](../LICENSE). No third-party sample pack, firmware, extracted stock code/tables, card, memory dump or build image is included.

The following record preserves the actual rendered version, file/source hashes, settings, pass timing, recipe and decoded MP3 checks.

```json
{
  "file": "media/audio-preview.mp3",
  "sha256": "9a86595504eea84a5c6885955cf49a32beaa4cc1c72f475cc6055c71444225ce",
  "seconds": 12.400454,
  "encoding": {
    "format": "MP3",
    "sampleRateHz": 44100,
    "channels": 2,
    "bitrateKbps": 192,
    "decodedPeakDbfs": -1.564,
    "fadeInMs": 5,
    "passFadeOutMs": 200,
    "gapSeconds": 0.3,
    "loudnessMatch": "first-hit",
    "matchWindowSeconds": 0.02,
    "limiter": false
  },
  "passes": [
    {
      "label": "dry",
      "seconds": 1.2001814058956917,
      "settings": {
        "time": 80,
        "feedback": 0,
        "wow": 0,
        "age": 0,
        "sync": 1,
        "mix": 0,
        "tempoBpm": 120
      },
      "pcmSha256": "59f9997acb815659e05f09c8fbd86a2bf8f31fe50ab19a6c1b1015a768994dec",
      "dryBitExact": true,
      "start": 0.0,
      "duration": 1.200181,
      "matchGainDb": 0.0,
      "unmatchedPeakDbfs": -14.0
    },
    {
      "label": "clean eighth-note repeats",
      "seconds": 4.8,
      "settings": {
        "time": 80,
        "feedback": 64,
        "wow": 0,
        "age": 0,
        "sync": 1,
        "mix": 64,
        "tempoBpm": 120
      },
      "pcmSha256": "0d5d20d98f7748e3a23ee1d34f886080a1260b9f556f079740d96171739845b9",
      "dryBitExact": false,
      "start": 1.500181,
      "duration": 4.8,
      "matchGainDb": 6.089,
      "unmatchedPeakDbfs": -20.089
    },
    {
      "label": "worn dotted-eighth repeats",
      "seconds": 5.800272108843537,
      "settings": {
        "time": 101,
        "feedback": 82,
        "wow": 72,
        "age": 100,
        "sync": 1,
        "mix": 64,
        "tempoBpm": 120
      },
      "pcmSha256": "3ad72078760f31002d82f079b703e91e92a5246772b5a0f19a29f3ba8573c3d5",
      "dryBitExact": false,
      "start": 6.600181,
      "duration": 5.800272,
      "matchGainDb": 6.089,
      "unmatchedPeakDbfs": -20.089
    }
  ],
  "validation": {
    "nonzeroAudio": true,
    "decodedPeakBelowMinus1Dbfs": true,
    "final50msPeakDbfs": -90.309,
    "clippedSamples": 0
  },
  "schemaVersion": 2,
  "moduleId": "tapeecho",
  "moduleVersion": "0.1.2-experimental",
  "rendered": "2026-10-12",
  "sourceCommit": "32ac46b0c7e8c11e48ebc41674695e033142b46e",
  "limitations": [
    "Offline emulator/native render, not a physical Octatrack recording or new hardware/performance qualification."
  ],
  "sourceFilesSha256": {
    "cpu.c": "13c8ab1a6934bab2f679c40ad8096d2151326b06d1fcffaf261bde40d82c9814",
    "cpu.h": "d07d496a62b95f23f8c2cbd893a0125e8a67071e83bf2c642e14251e48e69ff3",
    "cpu.s": "1da9056c6a175fe91b09a03172e4ef516f085ee659cf7a9f9aff53836c368e64",
    "cpu_hooks.s": "d1d959af91fbd0759191c5e244b4396613d18c057c8e65281d76cb67beb73e34",
    "cpu_kernels.s": "5cd8a759642ee9f59b6fe44f1dbe82928dc1c5ead69f5ee3c92d76d6b5945327",
    "cpu_passthrough.asm": "68ef0beaa213de43e116d2feb367b437ef8c73c7f7b1c07328fde2d72edb3fdc",
    "cpu_tables.h": "1d2e3e062651f021ca94fd19339dde824bcf49c4d867da790c20957dd24db9b2",
    "generate_cpu.py": "09477f59af29dc6b68458454f818ec999339f4f4eefadb979cc13236ce431353",
    "generate_tables.py": "3461b659e2f22d7da776eb87755610094a4a3e72609c875e82902a8da9a8a69c",
    "manifest.py": "e83c639b3a6d51946b6cb5ae2af72d9376f2ff9cad75502396287c95c751927b",
    "time_fmt.s": "f50337532bbd802f67bb3c93d975405c2e386ec2a75bf525a814b9f9756f9d15"
  },
  "method": "Offline render of the module’s unchanged fixed-point cpu.c, compiled natively with cc -shared -fPIC -O2 -DTE_HOST=1 and called through te_process in 16-sample blocks using the existing verify_tapeecho_cpu.Engine ring-buffer harness. 300 silent blocks warm the controls. Direct onset RMS is matched over 20 ms; repeat levels and tails retain the module response. Not a hardware recording.",
  "sample": {
    "name": "Original Modwerk woodblock transient",
    "license": "MIT",
    "credit": "Modwerk contributors, 2026",
    "sourcePcmSha256": "f544ad6b81bb73c8fdc1f316d0a34f9e681f2c38aace73af8ab81929aba694af",
    "recipe": {
      "sampleRateHz": 44100,
      "durationSeconds": 0.18,
      "signal": "sum(sin(2*pi*f*t)*exp(-t/tau)) for (f,tau) = (620,0.032),(1040,0.023),(1760,0.014)",
      "envelope": "min(t/0.001,1) * clamp((0.18-t)/0.01,0,1)",
      "peakDbfs": -14,
      "channels": "identical left/right",
      "format": "interleaved stereo signed little-endian int32 containing Q23 words"
    }
  },
  "harness": {
    "name": "verify_tapeecho_cpu.Engine",
    "sourceSha256": "7e978248e9d6e00ff4cef19137ecc8044b376459ff6dab3ae87499f5ec2ee806",
    "abi": "Q31 stereo in/out; 176400-frame ring; tempo24=2880 at 120 BPM"
  }
}
```

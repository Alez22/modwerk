# Tape Echo audio preview provenance

Rendered on 12 October 2026 through the unchanged 0.1.2-experimental fixed-point CPU engine. Editorial release 0.1.3-experimental retains that exact runtime and historical test status.

Source: `106 Drums Lazer Snare.wav` from Legowelt's Roland JUNO 106 sample kit. Credit: Legowelt (Danny Wolfers), ©2012 Pacific Micro International Software. The included `106 SAMPLES README.txt` declares the kit free with unrestricted use. The source and this processed comparison are used under that pack permission (LicenseRef-Legowelt-Juno106-Sample-Permission); the module's MIT software licence does not relicense the source audio. The provenance below records the exact permission quote/file hash, original WAV/PCM hashes, excerpt, gain/fades and processed file hash. Only the comparison MP3 is bundled; the source WAV and sample pack stay on the developer's computer. No firmware, extracted stock code/tables, card, memory dump or build image is included. This is an offline computer render, with no new physical-hardware or performance qualification.

```json
{
  "file": "media/audio-preview.mp3",
  "sha256": "62321000c02d064db2a486c1f50edec19d737cea8c0c825492b6c7d903782566",
  "seconds": 4.05,
  "encoding": {
    "format": "MP3",
    "sampleRateHz": 44100,
    "channels": 2,
    "bitrateKbps": 192,
    "decodedPeakDbfs": -1.564,
    "fadeInMs": 5,
    "passFadeOutMs": 35,
    "gapSeconds": 0,
    "loudnessMatch": "first-hit",
    "matchWindowSeconds": 0.02,
    "limiter": false
  },
  "passes": [
    {
      "label": "dry",
      "seconds": 0.45024943310657595,
      "settings": {
        "time": 48,
        "feedback": 0,
        "wow": 0,
        "age": 0,
        "sync": 1,
        "mix": 0,
        "tempoBpm": 120
      },
      "pcmSha256": "96c1fe60512f761bbec4a935c94308116176b9fd701ef02e48f6bea050bf8902",
      "dryBitExact": true,
      "start": 0.0,
      "duration": 0.45,
      "renderedFrames": 19856,
      "trimStartFrame": 0,
      "trimEndFrame": 19845,
      "matchGainDb": 0.0,
      "unmatchedPeakDbfs": -14.0
    },
    {
      "label": "bright sixteenth-note repeats",
      "seconds": 1.6,
      "settings": {
        "time": 48,
        "feedback": 84,
        "wow": 0,
        "age": 0,
        "sync": 1,
        "mix": 85,
        "tempoBpm": 120
      },
      "pcmSha256": "6e9a53ee32a4f4d7fb89007cac3e709ce147f0d6662ebcf47b36fb094e6876d5",
      "dryBitExact": false,
      "start": 0.45,
      "duration": 1.6,
      "renderedFrames": 70560,
      "trimStartFrame": 0,
      "trimEndFrame": 70560,
      "matchGainDb": 9.609,
      "unmatchedPeakDbfs": -23.611
    },
    {
      "label": "worn eighth-note repeats",
      "seconds": 2.0001814058956917,
      "settings": {
        "time": 80,
        "feedback": 98,
        "wow": 105,
        "age": 110,
        "sync": 1,
        "mix": 85,
        "tempoBpm": 120
      },
      "pcmSha256": "06e09ee91173b3b95db3efeaa614fd0e5c0f1993561e66bced209e3736a234af",
      "dryBitExact": false,
      "start": 2.05,
      "duration": 2.0,
      "renderedFrames": 88208,
      "trimStartFrame": 0,
      "trimEndFrame": 88200,
      "matchGainDb": 9.611,
      "unmatchedPeakDbfs": -22.173
    }
  ],
  "validation": {
    "nonzeroAudio": true,
    "decodedPeakBelowMinus1Dbfs": true,
    "final50msPeakDbfs": -21.163,
    "clippedSamples": 0,
    "maximumQuietRunSecondsBelowMinus48Dbfs": 0.04
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
    "name": "106 Drums Lazer Snare.wav",
    "pack": "Legowelt Roland JUNO 106 sample kit",
    "pathWithinPack": "106 Drums Lazer Snare.wav",
    "credit": "Legowelt (Danny Wolfers), ©2012 Pacific Micro International Software",
    "license": "LicenseRef-Legowelt-Juno106-Sample-Permission",
    "permissionFile": "106 SAMPLES README.txt",
    "permissionFileSha256": "20398760fc080b8b53a8fff99b302d02a2ab73a420d90ee6333ee714ff47b2c3",
    "permissionQuote": "This sample kit is free, you can do whatever you want it",
    "originalFileSha256": "58047bd9dbd37de3b8c54c6b56c780af483a57ba7d2dcaa216575efee944c642",
    "originalPcmSha256": "23bb1412b59eedb793a1a793a911e519c58ffd5221d43628f7cf2e3d69f16d6a",
    "originalFormat": {
      "sampleRateHz": 44100,
      "channels": 2,
      "sampleBits": 16,
      "frames": 34304
    },
    "preparation": {
      "startFrame": 0,
      "frames": 18522,
      "fadeInMs": 0,
      "fadeOutMs": 20.0,
      "gainDb": -9.735022,
      "peakDbfs": -14,
      "resampled": false
    },
    "sourcePcmSha256": "ceb034dbe05d9da88f86f0589947a74b37c9ec4f9c9daefb9337f7f0c50a92e0",
    "sourceFormat": "interleaved stereo signed little-endian int32 containing Q23 words"
  },
  "harness": {
    "name": "verify_tapeecho_cpu.Engine",
    "sourceSha256": "7e978248e9d6e00ff4cef19137ecc8044b376459ff6dab3ae87499f5ec2ee806",
    "abi": "Q31 stereo in/out; 176400-frame ring; tempo24=2880 at 120 BPM"
  }
}
```

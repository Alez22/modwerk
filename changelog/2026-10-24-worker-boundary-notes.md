Document two sample-reader integration constraints from the Beat Slicer 1.40C emulator work: a newly wrapped queue call does not cover an already waiting receive, and a mutable map endpoint is not physical pool capacity. Require closed admission during bootstrap, unlocked queue waiting and a real arena reservation for injected test code. Checked against compiled stock-worker fixtures and the reserved-memory full-boot run; these results do not establish complete writer coverage or hardware timing.

Also document moving private arithmetic/decoding outside source ownership and revalidating before any later live read. Checked with nine lock-release interleavings and compiled instruction observation; physical timing remains unmeasured.

Document the emulator idle-boundary prerequisite for borrowed native calls and prohibit replay after uncertain execution. Checked with a full-boot loaded-source preview run and explicit retry/refusal regressions.

# SPDX-License-Identifier: GPL-3.0-or-later
"""Register the standalone adapter regressions in the SDK validation suite."""
import importlib.util
from pathlib import Path
import sys

adapter = Path(__file__).resolve().parents[1] / 'machines/octatrack/module-adapters'
sys.path.insert(0, str(adapter))
spec = importlib.util.spec_from_file_location('fm_runtime_adapter_tests', adapter / 'test_fm_runtime.py')
tests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests)
SourceTests = tests.SourceTests
LinkTests = tests.LinkTests

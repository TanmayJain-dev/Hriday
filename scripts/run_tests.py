#!/usr/bin/env python3
"""HRIDAY Zero-Dependency Test Runner.

Discovers and runs test files in tests/ using Python standard library.
"""
import importlib.util
import inspect
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def run_all_tests() -> int:
    test_files = sorted(ROOT.glob("tests/**/test_*.py"))
    passed = 0
    failed = 0
    errors: list[tuple[str, str, str]] = []

    print(f"=== HRIDAY Test Discovery ({len(test_files)} test files found) ===\n")
    start_total = time.time()

    for test_path in test_files:
        rel_path = test_path.relative_to(ROOT)
        module_name = f"test_module_{test_path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, test_path)
        if spec is None or spec.loader is None:
            print(f"[LOAD ERROR] {rel_path}")
            failed += 1
            continue

        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as ex:
            print(f"[IMPORT ERROR] {rel_path}: {ex}")
            errors.append((str(rel_path), "<module_import>", str(ex)))
            failed += 1
            continue

        test_funcs = [
            (name, func)
            for name, func in inspect.getmembers(mod, inspect.isfunction)
            if name.startswith("test_")
        ]

        for name, func in test_funcs:
            t0 = time.time()
            try:
                func()
                elapsed = (time.time() - t0) * 1000
                print(f"  OK   {rel_path}::{name} ({elapsed:.1f}ms)")
                passed += 1
            except AssertionError as ae:
                elapsed = (time.time() - t0) * 1000
                print(f"  FAIL {rel_path}::{name} ({elapsed:.1f}ms): {ae}")
                errors.append((str(rel_path), name, str(ae)))
                failed += 1
            except Exception as ex:
                elapsed = (time.time() - t0) * 1000
                print(f"  ERR  {rel_path}::{name} ({elapsed:.1f}ms): {ex}")
                errors.append((str(rel_path), name, f"{type(ex).__name__}: {ex}"))
                failed += 1

    total_time = time.time() - start_total
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed in {total_time:.2f}s")
    if errors:
        print("\nFailures:")
        for path, test_name, msg in errors:
            print(f"  - {path}::{test_name}: {msg}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())

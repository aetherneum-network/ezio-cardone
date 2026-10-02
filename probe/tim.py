"""Runner probe (diagnostic branch only): per-test wall time of the suite, no audit hook, optional CPU affinity (Windows), CPU topology.

usage: python probe/tim.py OUT.json [hexmask|-] [pattern|sweeps]   (EZIO_TEST_JOBS as usual)
"""
import json, os, sys, time, unittest, platform
sys.path.insert(0, os.getcwd())


def _k32():
    import ctypes, ctypes.wintypes as w
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.GetCurrentProcess.restype = w.HANDLE
    k.GetProcessAffinityMask.argtypes = [w.HANDLE, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t)]
    k.SetProcessAffinityMask.argtypes = [w.HANDLE, ctypes.c_size_t]
    return k


def topology():
    out = {"cpu_count": os.cpu_count(), "platform": platform.platform(), "machine": platform.processor()}
    if hasattr(os, "sched_getaffinity"):
        out["affinity"] = sorted(os.sched_getaffinity(0))
    if sys.platform == "win32":
        import ctypes, ctypes.wintypes as w
        k = _k32()
        n = w.DWORD(0); k.GetLogicalProcessorInformationEx(0, None, ctypes.byref(n))
        buf = ctypes.create_string_buffer(n.value); k.GetLogicalProcessorInformationEx(0, buf, ctypes.byref(n))
        off, cores = 0, []
        while off < n.value:
            size = ctypes.c_uint32.from_buffer(buf, off + 4).value
            mask = ctypes.c_uint64.from_buffer(buf, off + 32).value
            cores.append([i for i in range(64) if mask >> i & 1]); off += size
        out["cores"] = cores
        pm, sm = ctypes.c_size_t(), ctypes.c_size_t()
        k.GetProcessAffinityMask(k.GetCurrentProcess(), ctypes.byref(pm), ctypes.byref(sm))
        out["affinity"] = [i for i in range(64) if pm.value >> i & 1]
    else:
        try:
            cores = {}
            for cpu in sorted(os.listdir("/sys/devices/system/cpu")):
                p = f"/sys/devices/system/cpu/{cpu}/topology/thread_siblings_list"
                if cpu.startswith("cpu") and cpu[3:].isdigit() and os.path.exists(p):
                    cores.setdefault(open(p).read().strip(), []).append(int(cpu[3:]))
            out["cores"] = sorted(cores.values())
            out["model"] = next((l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")), "")
        except OSError as e:
            out["cores_error"] = str(e)
    return out


SWEEPS = ["tests.test_d30b_forms.S_UnreadScopeAdversarialSiblings.test_every_sibling_with_every_title_keeps_every_field",
          "tests.test_d34_forms.D34_RecognisedTypeSiblings.test_every_sibling_with_every_title_is_safe",
          "tests.test_d35_forms.D35_TypedSlotSiblings.test_every_sibling_is_safe",
          "tests.test_d36_forms.D36_TypedSlotSiblings.test_every_sibling_is_safe",
          "tests.test_d37_forms.D37_AddressSiblings.test_every_sibling_is_safe",
          "tests.test_d37_slots.D37_SlotSiblings.test_no_sibling_is_published_wrongly",
          "tests.test_d38_identification.D38_IdentificationSiblings.test_no_sibling_is_published_wrongly",
          "tests.test_d39_capital_count.D39_CountForm"]


def main():
    OUT = sys.argv[1]
    mask = sys.argv[2] if len(sys.argv) > 2 else "-"
    pattern = sys.argv[3] if len(sys.argv) > 3 else "test*.py"
    if mask != "-" and sys.platform == "win32":
        k = _k32()
        assert k.SetProcessAffinityMask(k.GetCurrentProcess(), int(mask, 16))
    topo = topology()

    class Result(unittest.TextTestResult):
        def __init__(self, *a, **k):
            super().__init__(*a, **k); self.rows = []; self._last = time.perf_counter()
        def startTest(self, test):
            now = time.perf_counter(); self._gap = now - self._last; self._t0 = now; super().startTest(test)
        def stopTest(self, test):
            super().stopTest(test); now = time.perf_counter()
            self.rows.append({"id": test.id(), "s": now - self._t0, "gap_before": self._gap}); self._last = now

    if pattern == "sweeps":
        suite = unittest.defaultTestLoader.loadTestsFromNames(SWEEPS)
    else:
        suite = unittest.defaultTestLoader.discover("tests", pattern=pattern, top_level_dir=".")
    t0 = time.perf_counter()
    res = unittest.TextTestRunner(resultclass=Result, verbosity=0, stream=open(os.devnull, "w")).run(suite)
    total = time.perf_counter() - t0
    record = {"total_s": total, "jobs": os.environ.get("EZIO_TEST_JOBS", ""), "mask": mask, "topology": topo,
               "tests": res.testsRun, "failures": len(res.failures), "errors": len(res.errors), "rows": res.rows,
               "fail_ids": [t.id() for t, _ in res.failures + res.errors]}
    json.dump(record, open(OUT, "w", encoding="utf-8"), indent=1)
    if os.environ.get("PROBE_PRINT"):
        print("PROBE-JSON", OUT, json.dumps(record, separators=(",", ":")))
    print(f"{OUT}: tests={res.testsRun} fail={len(res.failures)} err={len(res.errors)} total={total:.1f}s "
          f"jobs={os.environ.get('EZIO_TEST_JOBS', '')} mask={mask} affinity={topo.get('affinity')}")


if __name__ == "__main__":
    main()

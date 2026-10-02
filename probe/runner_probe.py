"""Runner probe (diagnostic branch only): the CPU topology the job sees, and the start-up cost of worker processes.

usage: python probe/runner_probe.py topology | spawn
"""
import concurrent.futures
import json
import multiprocessing
import os
import platform
import subprocess
import sys
import time

sys.path.insert(0, os.getcwd())


def _k32():
    import ctypes
    import ctypes.wintypes as w
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.GetCurrentProcess.restype = w.HANDLE
    k.GetProcessAffinityMask.argtypes = [w.HANDLE, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t)]
    return k


def topology() -> dict:
    out = {"python": sys.version.split()[0], "platform": platform.platform(), "cpu_count": os.cpu_count()}
    if sys.platform == "win32":
        import ctypes
        import ctypes.wintypes as w
        k = _k32()
        n = w.DWORD(0)
        k.GetLogicalProcessorInformationEx(0, None, ctypes.byref(n))
        buf = ctypes.create_string_buffer(n.value)
        k.GetLogicalProcessorInformationEx(0, buf, ctypes.byref(n))
        off, cores = 0, []
        while off < n.value:
            size = ctypes.c_uint32.from_buffer(buf, off + 4).value
            mask = ctypes.c_uint64.from_buffer(buf, off + 32).value
            cores.append([i for i in range(64) if mask >> i & 1])
            off += size
        pm, sm = ctypes.c_size_t(), ctypes.c_size_t()
        k.GetProcessAffinityMask(k.GetCurrentProcess(), ctypes.byref(pm), ctypes.byref(sm))
        out.update(cores=cores, affinity=[i for i in range(64) if pm.value >> i & 1])
        ps = ("Get-CimInstance Win32_Processor | ForEach-Object { $_.Name + ' | cores ' + $_.NumberOfCores + ' | logical '"
              " + $_.NumberOfLogicalProcessors + ' | max MHz ' + $_.MaxClockSpeed };"
              " (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory;"
              " Get-Volume | Where-Object DriveLetter | ForEach-Object { $_.DriveLetter + ': ' + $_.FileSystemType + ' '"
              " + [math]::Round($_.Size / 1GB) + ' GB' }")
        out["system"] = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True,
                                       text=True).stdout.strip().splitlines()
    else:
        out["affinity"] = sorted(os.sched_getaffinity(0))
        groups = {}
        base = "/sys/devices/system/cpu"
        for cpu in sorted(os.listdir(base)):
            p = f"{base}/{cpu}/topology/thread_siblings_list"
            if cpu.startswith("cpu") and cpu[3:].isdigit() and os.path.exists(p):
                groups.setdefault(open(p).read().strip(), []).append(int(cpu[3:]))
        out["cores"] = sorted(groups.values())
        keep = ("Model name", "Thread(s) per core", "Core(s) per socket", "Socket(s)", "Hypervisor vendor", "CPU(s)")
        out["system"] = [line for line in subprocess.run(["lscpu"], capture_output=True, text=True).stdout.splitlines()
                         if line.split(":")[0].strip() in keep]
        out["system"] += subprocess.run(["df", "-hT", os.environ.get("TMPDIR", "/tmp")], capture_output=True,
                                        text=True).stdout.strip().splitlines()
    out["temp"] = os.environ.get("TEMP") or os.environ.get("TMPDIR") or "/tmp"
    return out


def _start(t_submit: float) -> dict:
    """In a worker: when it began this task, and what importing a sweep's test module cost there."""
    began = time.time()
    t = time.perf_counter()
    import tests.test_d35_forms  # noqa: F401  (what a worker imports to unpickle a sweep's function)
    imported = time.perf_counter() - t
    time.sleep(1.0)               # keeps the task on this worker, so every worker starts one
    return {"pid": os.getpid(), "wait_s": began - t_submit, "import_s": imported}


def spawn() -> dict:
    out = {}
    for n in (1, 2, 4):
        t0 = time.perf_counter()
        ctx = multiprocessing.get_context("spawn")
        with concurrent.futures.ProcessPoolExecutor(n, mp_context=ctx) as pool:
            now = time.time()
            rows = [f.result() for f in [pool.submit(_start, now) for _ in range(n)]]
            ready = time.perf_counter() - t0
        out[f"workers_{n}"] = {"all_started_and_slept_1s": round(ready, 3),
                               "distinct_workers": len({r["pid"] for r in rows}),
                               "wait_s": [round(r["wait_s"], 3) for r in rows],
                               "import_s": [round(r["import_s"], 3) for r in rows],
                               "shutdown_s": round(time.perf_counter() - t0 - ready, 3)}
    return out


if __name__ == "__main__":
    what = sys.argv[1]
    result = topology() if what == "topology" else spawn()
    print(json.dumps(result, indent=1))
    print("PROBE-JSON", what, json.dumps(result, separators=(",", ":")))

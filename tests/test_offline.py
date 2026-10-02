"""The pack runs alone and offline: sockets are blocked, and the code has nothing to open one with."""
import ast
import socket
import unittest

from . import NetworkBlocked, ROOT
from . import support as s

NETWORK_MODULES = {"socket", "ssl", "urllib", "http", "requests", "httpx", "aiohttp", "anthropic", "openai",
                   "ftplib", "smtplib", "telnetlib", "xmlrpc", "websocket", "websockets", "asyncio", "subprocess"}
CODE_DIRS = ("dossier", "corpus", "eval", "scenarios", "tools")


def _sources():
    for d in CODE_DIRS:
        for p in sorted((ROOT / d).rglob("*.py")):
            yield p, ast.parse(p.read_text(encoding="utf-8"), filename=str(p))


def _imports(tree) -> set[str]:
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.add(node.module.split(".")[0])
    return found


class SocketsAreBlocked(unittest.TestCase):
    def test_in_this_process(self):
        with self.assertRaises(NetworkBlocked):
            socket.socket()
        with self.assertRaises(NetworkBlocked):
            socket.create_connection(("198.51.100.1", 80), timeout=1)
        with self.assertRaises(NetworkBlocked):
            socket.getaddrinfo("registry.example", 443)

    def test_in_child_processes(self):
        probe = s.tmp() / "probe.py"
        probe.write_text("import socket\ntry:\n    socket.socket()\nexcept Exception as exc:\n"
                         "    print(type(exc).__name__)\nelse:\n    print('OPEN')\n", encoding="utf-8")
        got = s.child([str(probe)])
        self.assertEqual(got.stdout.strip(), "NetworkBlocked", got.stderr)

    def test_a_full_run_in_a_child_process_needs_no_socket(self):
        work = s.tmp()
        got = s.child(["-m", "dossier.run", "--input", str(ROOT / "scenarios" / "S01" / "input"),
                       "--work", str(work)])
        self.assertEqual(got.returncode, 0, got.stdout + got.stderr)
        self.assertIn("RUN OK", got.stdout)


class CodeHasNoWayOut(unittest.TestCase):
    def test_no_network_or_process_module_is_imported(self):
        for path, tree in _sources():
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertEqual(_imports(tree) & NETWORK_MODULES, set())

    def test_the_pipeline_reads_no_clock_environment_or_randomness(self):
        """Inside dossier/: the date comes from the input (`as_of`), never from the machine."""
        banned_calls = {("datetime", "now"), ("datetime", "utcnow"), ("datetime", "today"), ("date", "today"),
                        ("time", "time"), ("time", "localtime"), ("time", "gmtime"), ("os", "getenv"),
                        ("os", "urandom"), ("uuid", "uuid4"), ("uuid", "uuid1")}
        for path in sorted((ROOT / "dossier").rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            rel = path.relative_to(ROOT).as_posix()
            with self.subTest(path=rel):
                self.assertEqual(_imports(tree) & {"random", "secrets", "uuid", "getpass", "platform"}, set())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                        self.assertNotIn((node.value.id, node.attr), banned_calls, f"{rel}:{node.lineno}")
                        self.assertNotEqual((node.value.id, node.attr), ("os", "environ"), f"{rel}:{node.lineno}")

    def test_the_model_hook_is_not_part_of_the_run(self):
        for name in ("run", "s1_extract", "s2_record", "s3_discrepancy", "s4_ownership", "s5_snapshot", "s6_build",
                     "s7_audit", "s8_shareable", "rules_engine"):
            text = (ROOT / "dossier" / f"{name}.py").read_text(encoding="utf-8")
            self.assertNotIn("model_hook", text, name)

    def test_only_declared_third_party_packages(self):
        import sys
        allowed = {"docx", "jsonschema"}
        local = {"dossier", "corpus", "eval", "scenarios", "tools", "_common", "make_inputs"}
        stdlib = set(sys.stdlib_module_names)
        for path, tree in _sources():
            extra = _imports(tree) - stdlib - local - allowed
            self.assertEqual(extra, set(), path.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    unittest.main()

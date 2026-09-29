import base64
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from config import Config  
from shell import Shell  


def make_csv(dir_path, rows, name="vfs.csv"):
    path = os.path.join(dir_path, name)
    lines = ["path,type,content"]
    for row in rows:
        lines.append(",".join(row))
    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")
    return path


class ShellVfsTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def test_default_vfs_when_no_path(self):
        shell = Shell()
        self.assertIsNone(shell.vfs_error)
        self.assertIn("home", shell.vfs.root.children)

    def test_vfs_info_reports_name_and_hash(self):
        content = base64.b64encode(b"hi").decode("ascii")
        path = make_csv(self.dir.name, [("/a.txt", "file", content)])
        shell = Shell(Config(vfs_path=path))
        out = shell.execute("vfs-info")
        self.assertTrue(out.startswith("vfs-info: "))
        self.assertIn(os.path.basename(path), out)
        self.assertIn(shell.vfs.sha256, out)

    def test_vfs_save_writes_file(self):
        shell = Shell()
        out_path = os.path.join(self.dir.name, "saved.csv")
        result = shell.execute(f"vfs-save {out_path}")
        self.assertIn("сохранено", result)
        self.assertTrue(os.path.exists(out_path))

    def test_vfs_save_without_path_is_error(self):
        shell = Shell()
        result = shell.execute("vfs-save")
        self.assertTrue(result.startswith("vfs-save:"))

    def test_missing_vfs_path_reports_error_and_falls_back(self):
        missing = os.path.join(self.dir.name, "nope.csv")
        shell = Shell(Config(vfs_path=missing))
        self.assertIsNotNone(shell.vfs_error)
        self.assertIn("home", shell.vfs.root.children)
        lines = shell.startup_output()
        self.assertTrue(any(line.startswith("vfs:") for line in lines))

    def test_bad_format_vfs_reports_error_and_falls_back(self):
        path = make_csv(self.dir.name, [("/a.txt", "weird", "")])
        shell = Shell(Config(vfs_path=path))
        self.assertIsNotNone(shell.vfs_error)
        self.assertIn("home", shell.vfs.root.children)


if __name__ == "__main__":
    unittest.main()

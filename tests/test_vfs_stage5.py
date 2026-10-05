import base64
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vfs import DEFAULT_OWNER, Vfs, VfsError  


def make_csv(dir_path, rows, columns="path,type,content,owner"):
    path = os.path.join(dir_path, "vfs.csv")
    lines = [columns]
    for row in rows:
        lines.append(",".join(row))
    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")
    return path


def b64(text):
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


class ChownTest(unittest.TestCase):
    def test_default_owner_is_root(self):
        vfs = Vfs.default()
        self.assertEqual(vfs.root.children["home"].owner, DEFAULT_OWNER)

    def test_chown_file_changes_owner(self):
        vfs = Vfs.default()
        vfs.root.add_file("a.txt", b"hi")
        vfs.chown([], "/a.txt", "mary")
        self.assertEqual(vfs.root.children["a.txt"].owner, "mary")

    def test_chown_dir_changes_owner(self):
        vfs = Vfs.default()
        vfs.chown([], "/home", "mary")
        self.assertEqual(vfs.root.children["home"].owner, "mary")

    def test_chown_root(self):
        vfs = Vfs.default()
        vfs.chown([], "/", "mary")
        self.assertEqual(vfs.root.owner, "mary")

    def test_chown_missing_path_raises(self):
        vfs = Vfs.default()
        with self.assertRaises(VfsError):
            vfs.chown([], "/nope", "mary")

    def test_chown_relative_to_cwd(self):
        vfs = Vfs.default()
        vfs.chown(["home"], ".", "mary")
        self.assertEqual(vfs.root.children["home"].owner, "mary")


class RmdirTest(unittest.TestCase):
    def test_rmdir_empty_dir_removes_it(self):
        vfs = Vfs.default()
        vfs.root.ensure_dir("empty")
        vfs.rmdir([], "/empty")
        self.assertNotIn("empty", vfs.root.children)

    def test_rmdir_nonempty_dir_raises(self):
        vfs = Vfs.default()
        vfs.root.children["home"].add_file("a.txt", b"hi")
        with self.assertRaises(VfsError):
            vfs.rmdir([], "/home")

    def test_rmdir_file_raises(self):
        vfs = Vfs.default()
        vfs.root.add_file("a.txt", b"hi")
        with self.assertRaises(VfsError):
            vfs.rmdir([], "/a.txt")

    def test_rmdir_missing_path_raises(self):
        vfs = Vfs.default()
        with self.assertRaises(VfsError):
            vfs.rmdir([], "/nope")

    def test_rmdir_root_raises(self):
        vfs = Vfs.default()
        with self.assertRaises(VfsError):
            vfs.rmdir([], "/")

    def test_rmdir_returns_segments(self):
        vfs = Vfs.default()
        vfs.root.ensure_dir("empty")
        segments = vfs.rmdir([], "/empty")
        self.assertEqual(segments, ["empty"])


class CsvFormatCompatTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def test_legacy_three_column_file_defaults_owner(self):
        path = make_csv(
            self.dir.name,
            [("/a.txt", "file", b64("hi"))],
            columns="path,type,content",
        )
        vfs = Vfs.load(path)
        self.assertEqual(vfs.root.children["a.txt"].owner, DEFAULT_OWNER)

    def test_four_column_file_reads_owner(self):
        path = make_csv(self.dir.name, [
            ("/a.txt", "file", b64("hi"), "mary"),
        ])
        vfs = Vfs.load(path)
        self.assertEqual(vfs.root.children["a.txt"].owner, "mary")

    def test_save_roundtrips_owner(self):
        path = make_csv(self.dir.name, [
            ("/a.txt", "file", b64("hi"), "mary"),
        ])
        vfs = Vfs.load(path)
        out = os.path.join(self.dir.name, "out.csv")
        vfs.save(out)
        reloaded = Vfs.load(out)
        self.assertEqual(reloaded.root.children["a.txt"].owner, "mary")

    def test_chown_then_save_persists(self):
        vfs = Vfs.default()
        vfs.chown([], "/home", "mary")
        out = os.path.join(self.dir.name, "out.csv")
        vfs.save(out)
        reloaded = Vfs.load(out)
        self.assertEqual(reloaded.root.children["home"].owner, "mary")

    def test_bad_columns_still_rejected(self):
        path = make_csv(self.dir.name, [("x", "y")], columns="foo,bar")
        with self.assertRaises(VfsError):
            Vfs.load(path)


if __name__ == "__main__":
    unittest.main()

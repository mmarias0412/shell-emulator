import base64
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vfs import Vfs, VfsError  


def make_csv(dir_path, rows, name="vfs.csv"):
    path = os.path.join(dir_path, name)
    lines = ["path,type,content"]
    for row in rows:
        lines.append(",".join(row))
    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")
    return path


def b64(text):
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


class DefaultVfsTest(unittest.TestCase):
    def test_default_has_home(self):
        vfs = Vfs.default()
        self.assertIn("home", vfs.root.children)
        self.assertTrue(vfs.root.children["home"].is_dir)

    def test_default_hash_is_stable(self):
        first = Vfs.default().sha256
        second = Vfs.default().sha256
        self.assertEqual(first, second)


class LoadVfsTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def test_minimal_one_file(self):
        path = make_csv(self.dir.name, [
            (f"/readme.txt", "file", b64("hi")),
        ])
        vfs = Vfs.load(path)
        node = vfs.root.children["readme.txt"]
        self.assertFalse(node.is_dir)
        self.assertEqual(node.content, b"hi")

    def test_several_files_flat(self):
        path = make_csv(self.dir.name, [
            ("/a.txt", "file", b64("A")),
            ("/b.txt", "file", b64("B")),
        ])
        vfs = Vfs.load(path)
        self.assertEqual(set(vfs.root.children), {"a.txt", "b.txt"})

    def test_nested_three_levels_implicit_dirs(self):
        path = make_csv(self.dir.name, [
            ("/docs/2024/report.txt", "file", b64("R")),
        ])
        vfs = Vfs.load(path)
        docs = vfs.root.children["docs"]
        year = docs.children["2024"]
        report = year.children["report.txt"]
        self.assertTrue(docs.is_dir)
        self.assertTrue(year.is_dir)
        self.assertEqual(report.content, b"R")

    def test_explicit_dir_rows(self):
        path = make_csv(self.dir.name, [
            ("/a", "dir", ""),
            ("/a/b", "dir", ""),
        ])
        vfs = Vfs.load(path)
        self.assertTrue(vfs.root.children["a"].children["b"].is_dir)

    def test_binary_content_roundtrips(self):
        blob = bytes(range(256))
        path = make_csv(self.dir.name, [
            ("/x.bin", "file", base64.b64encode(blob).decode("ascii")),
        ])
        vfs = Vfs.load(path)
        self.assertEqual(vfs.root.children["x.bin"].content, blob)

    def test_name_is_file_basename(self):
        path = make_csv(self.dir.name, [("/a.txt", "file", b64("A"))])
        vfs = Vfs.load(path)
        self.assertEqual(vfs.name, os.path.basename(path))

    def test_hash_matches_file_bytes(self):
        import hashlib
        path = make_csv(self.dir.name, [("/a.txt", "file", b64("A"))])
        with open(path, "rb") as file:
            expected = hashlib.sha256(file.read()).hexdigest()
        vfs = Vfs.load(path)
        self.assertEqual(vfs.sha256, expected)


class LoadErrorsTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def test_missing_file(self):
        missing = os.path.join(self.dir.name, "nope.csv")
        with self.assertRaises(VfsError):
            Vfs.load(missing)

    def test_bad_columns(self):
        path = os.path.join(self.dir.name, "bad.csv")
        with open(path, "w", encoding="utf-8") as file:
            file.write("foo,bar\n1,2\n")
        with self.assertRaises(VfsError):
            Vfs.load(path)

    def test_bad_type(self):
        path = make_csv(self.dir.name, [("/x.txt", "weird", b64("x"))])
        with self.assertRaises(VfsError):
            Vfs.load(path)

    def test_bad_base64(self):
        path = make_csv(self.dir.name, [("/x.txt", "file", "not base64!!")])
        with self.assertRaises(VfsError):
            Vfs.load(path)

    def test_duplicate_path(self):
        path = make_csv(self.dir.name, [
            ("/x.txt", "file", b64("a")),
            ("/x.txt", "file", b64("b")),
        ])
        with self.assertRaises(VfsError):
            Vfs.load(path)

    def test_file_then_dir_conflict(self):
        path = make_csv(self.dir.name, [
            ("/x", "file", b64("a")),
            ("/x/y.txt", "file", b64("b")),
        ])
        with self.assertRaises(VfsError):
            Vfs.load(path)


class SaveVfsTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def test_save_default_then_reload(self):
        vfs = Vfs.default()
        out = os.path.join(self.dir.name, "out.csv")
        vfs.save(out)
        reloaded = Vfs.load(out)
        self.assertIn("home", reloaded.root.children)

    def test_save_updates_hash_to_saved_bytes(self):
        import hashlib
        vfs = Vfs.default()
        out = os.path.join(self.dir.name, "out.csv")
        vfs.save(out)
        with open(out, "rb") as file:
            expected = hashlib.sha256(file.read()).hexdigest()
        self.assertEqual(vfs.sha256, expected)

    def test_save_roundtrips_nested_and_binary(self):
        blob = bytes([0, 1, 2, 255])
        src = make_csv(self.dir.name, [
            ("/docs/2024/r.txt", "file", b64("R")),
            ("/img.bin", "file", base64.b64encode(blob).decode("ascii")),
        ])
        vfs = Vfs.load(src)
        out = os.path.join(self.dir.name, "out.csv")
        vfs.save(out)
        reloaded = Vfs.load(out)
        report = reloaded.root.children["docs"].children["2024"].children[
            "r.txt"
        ]
        self.assertEqual(report.content, b"R")
        self.assertEqual(reloaded.root.children["img.bin"].content, blob)

    def test_save_to_bad_path_raises(self):
        vfs = Vfs.default()
        bad = os.path.join(self.dir.name, "no_such_dir", "out.csv")
        with self.assertRaises(VfsError):
            vfs.save(bad)


if __name__ == "__main__":
    unittest.main()

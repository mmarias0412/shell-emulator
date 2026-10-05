import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from config import Config  
from shell import Shell  

NESTED_VFS = os.path.join(
    os.path.dirname(__file__), "..", "data", "vfs_nested.csv"
)


class ChownCommandTest(unittest.TestCase):
    def test_chown_success_message(self):
        shell = Shell(Config(vfs_path=NESTED_VFS))
        out = shell.execute("chown mary /images/logo.png")
        self.assertEqual(
            out, "chown: владелец '/images/logo.png' изменён на 'mary'"
        )
        node = shell.vfs.root.children["images"].children["logo.png"]
        self.assertEqual(node.owner, "mary")

    def test_chown_missing_path_is_error(self):
        shell = Shell(Config(vfs_path=NESTED_VFS))
        out = shell.execute("chown mary /nope")
        self.assertEqual(
            out, "chown: нет такого файла или каталога: '/nope'"
        )

    def test_chown_wrong_arity_is_error(self):
        shell = Shell()
        out = shell.execute("chown onlyowner")
        self.assertEqual(
            out, "chown: требуется два аргумента — владелец и путь"
        )

    def test_chown_relative_path(self):
        shell = Shell(Config(vfs_path=NESTED_VFS))
        shell.execute("cd docs")
        shell.execute("chown mary 2024")
        node = shell.vfs.root.children["docs"].children["2024"]
        self.assertEqual(node.owner, "mary")


class RmdirCommandTest(unittest.TestCase):
    def test_rmdir_empty_dir_success_message(self):
        shell = Shell(Config(vfs_path=NESTED_VFS))
        out = shell.execute("rmdir /empty")
        self.assertEqual(out, "rmdir: каталог '/empty' удалён")
        self.assertNotIn("empty", shell.vfs.root.children)

    def test_rmdir_nonempty_dir_is_error(self):
        shell = Shell(Config(vfs_path=NESTED_VFS))
        out = shell.execute("rmdir /docs")
        self.assertEqual(out, "rmdir: каталог не пуст: '/docs'")

    def test_rmdir_file_is_error(self):
        shell = Shell(Config(vfs_path=NESTED_VFS))
        out = shell.execute("rmdir /images/logo.png")
        self.assertEqual(out, "rmdir: не каталог: '/images/logo.png'")

    def test_rmdir_missing_path_is_error(self):
        shell = Shell(Config(vfs_path=NESTED_VFS))
        out = shell.execute("rmdir /nope")
        self.assertEqual(
            out, "rmdir: нет такого файла или каталога: '/nope'"
        )

    def test_rmdir_too_many_args_is_error(self):
        shell = Shell()
        out = shell.execute("rmdir a b")
        self.assertEqual(out, "rmdir: требуется один аргумент — путь")

    def test_rmdir_moves_cwd_up_when_inside_removed_dir(self):
        shell = Shell(Config(vfs_path=NESTED_VFS))
        shell.execute("cd /docs/2024/notes")
        shell.vfs.root.children["docs"].children["2024"].children[
            "notes"
        ].children.clear()
        shell.execute("rmdir /docs/2024/notes")
        self.assertEqual(shell.cwd, ["docs", "2024"])

    def test_rmdir_unrelated_cwd_is_unaffected(self):
        shell = Shell(Config(vfs_path=NESTED_VFS))
        shell.execute("cd /images")
        shell.execute("rmdir /empty")
        self.assertEqual(shell.cwd, ["images"])


if __name__ == "__main__":
    unittest.main()

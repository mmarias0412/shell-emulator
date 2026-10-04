import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from config import Config  
from shell import CLEAR_SENTINEL, Shell  

NESTED_VFS = os.path.join(
    os.path.dirname(__file__), "..", "data", "vfs_nested.csv"
)


class LsTest(unittest.TestCase):
    def test_ls_root_default_vfs(self):
        shell = Shell()
        self.assertEqual(shell.execute("ls"), "home/")

    def test_ls_empty_dir_is_blank(self):
        shell = Shell()
        shell.execute("cd home")
        self.assertEqual(shell.execute("ls"), "")

    def test_ls_nested_vfs_lists_dirs_and_files(self):
        shell = Shell(Config(vfs_path=NESTED_VFS))
        self.assertEqual(shell.execute("ls"), "docs/  images/")

    def test_ls_absolute_path(self):
        shell = Shell(Config(vfs_path=NESTED_VFS))
        out = shell.execute("ls /docs/2024")
        self.assertEqual(out, "notes/  report.txt")

    def test_ls_file_prints_its_name(self):
        shell = Shell(Config(vfs_path=NESTED_VFS))
        self.assertEqual(shell.execute("ls /images/logo.png"), "logo.png")

    def test_ls_missing_path_is_error(self):
        shell = Shell(Config(vfs_path=NESTED_VFS))
        out = shell.execute("ls /nope")
        self.assertEqual(out, "ls: нет такого файла или каталога: '/nope'")

    def test_ls_too_many_args_is_error(self):
        shell = Shell()
        out = shell.execute("ls a b")
        self.assertEqual(out, "ls: слишком много аргументов")


class CdTest(unittest.TestCase):
    def test_cd_no_args_goes_to_home(self):
        shell = Shell()
        shell.execute("cd")
        self.assertEqual(shell.cwd, ["home"])

    def test_cd_into_subdir_and_back(self):
        shell = Shell(Config(vfs_path=NESTED_VFS))
        shell.execute("cd docs")
        shell.execute("cd 2024")
        self.assertEqual(shell.cwd, ["docs", "2024"])
        shell.execute("cd ..")
        self.assertEqual(shell.cwd, ["docs"])

    def test_cd_absolute_path(self):
        shell = Shell(Config(vfs_path=NESTED_VFS))
        shell.execute("cd /docs/2024/notes")
        self.assertEqual(shell.cwd, ["docs", "2024", "notes"])

    def test_cd_dot_dot_above_root_stays_at_root(self):
        shell = Shell()
        shell.execute("cd ..")
        self.assertEqual(shell.cwd, [])

    def test_cd_missing_path_is_error_and_cwd_unchanged(self):
        shell = Shell(Config(vfs_path=NESTED_VFS))
        out = shell.execute("cd /nope")
        self.assertEqual(out, "cd: нет такого файла или каталога: '/nope'")
        self.assertEqual(shell.cwd, [])

    def test_cd_into_file_is_error(self):
        shell = Shell(Config(vfs_path=NESTED_VFS))
        out = shell.execute("cd /images/logo.png")
        self.assertEqual(out, "cd: не каталог: '/images/logo.png'")
        self.assertEqual(shell.cwd, [])

    def test_cd_too_many_args_is_error(self):
        shell = Shell()
        out = shell.execute("cd a b")
        self.assertEqual(out, "cd: слишком много аргументов")

    def test_prompt_shows_current_directory(self):
        shell = Shell(Config(vfs_path=NESTED_VFS))
        shell.execute("cd docs")
        self.assertIn("/docs$", shell.prompt())


class ClearTest(unittest.TestCase):
    def test_clear_returns_sentinel(self):
        shell = Shell()
        self.assertEqual(shell.execute("clear"), CLEAR_SENTINEL)


class EchoTest(unittest.TestCase):
    def test_echo_joins_args_with_space(self):
        shell = Shell()
        self.assertEqual(shell.execute("echo hello world"), "hello world")

    def test_echo_no_args_is_empty(self):
        shell = Shell()
        self.assertEqual(shell.execute("echo"), "")


class HistoryTest(unittest.TestCase):
    def test_history_empty_at_start(self):
        shell = Shell()
        self.assertEqual(shell.execute("history"), "1  history")

    def test_history_lists_previous_commands_in_order(self):
        shell = Shell()
        shell.execute("ls")
        shell.execute("echo hi")
        out = shell.execute("history")
        self.assertEqual(out, "1  ls\n2  echo hi\n3  history")

    def test_history_ignores_empty_lines(self):
        shell = Shell()
        shell.execute("")
        shell.execute("ls")
        out = shell.execute("history")
        self.assertEqual(out, "1  ls\n2  history")


if __name__ == "__main__":
    unittest.main()

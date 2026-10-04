import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cmd_parser import parse  
from shell import Shell  


class ParserTest(unittest.TestCase):
    def test_command_and_args(self):
        self.assertEqual(parse("ls -l /tmp"), ("ls", ["-l", "/tmp"]))

    def test_extra_spaces(self):
        self.assertEqual(parse("  cd    dir  "), ("cd", ["dir"]))

    def test_empty(self):
        self.assertEqual(parse("   "), (None, []))


class ShellTest(unittest.TestCase):
    def setUp(self):
        self.shell = Shell()

    def test_title_has_user_and_host(self):
        title = self.shell.title()
        self.assertIn(self.shell.user, title)
        self.assertIn(self.shell.host, title)

    def test_ls_default_vfs_shows_home(self):
        self.assertEqual(self.shell.execute("ls"), "home/")

    def test_cd_without_args_goes_home(self):
        self.assertEqual(self.shell.execute("cd"), "")
        self.assertEqual(self.shell.cwd, ["home"])

    def test_unknown_command(self):
        out = self.shell.execute("foo bar")
        self.assertEqual(out, "foo: command not found")

    def test_empty_line(self):
        self.assertEqual(self.shell.execute(""), "")
        self.assertTrue(self.shell.running)

    def test_exit(self):
        self.shell.execute("exit")
        self.assertFalse(self.shell.running)


if __name__ == "__main__":
    unittest.main()

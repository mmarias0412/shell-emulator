import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from config import Config  
from script import ScriptError, read_script, strip_comment  
from shell import Shell  


class StripCommentTest(unittest.TestCase):
    def test_full_line_comment(self):
        self.assertEqual(strip_comment("# hello"), "")

    def test_inline_comment(self):
        self.assertEqual(strip_comment("ls -l  # list"), "ls -l")

    def test_hash_inside_word_kept(self):
        self.assertEqual(strip_comment("cd a#b"), "cd a#b")


class ScriptFileTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def write(self, text):
        path = os.path.join(self.dir.name, "s.emu")
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)
        return path

    def test_read_skips_comments_and_blank(self):
        path = self.write("# c\n\nls\n  cd x # y\n")
        self.assertEqual(read_script(path), ["ls", "cd x"])

    def test_missing_file(self):
        with self.assertRaises(ScriptError):
            read_script(os.path.join(self.dir.name, "nope.emu"))

    def test_run_shows_input_and_output(self):
        path = self.write("ls nope\nfoo\n")
        shell = Shell()
        dialog = shell.run_script(path)
        self.assertEqual(dialog, [
            shell.prompt() + "ls nope",
            "ls: нет такого файла или каталога: 'nope'",
            shell.prompt() + "foo",
            "foo: command not found",
        ])

    def test_exit_stops_script(self):
        path = self.write("exit\nls\n")
        shell = Shell()
        dialog = shell.run_script(path)
        self.assertEqual(dialog, [shell.prompt() + "exit"])
        self.assertFalse(shell.running)

    def test_missing_script_reports_error(self):
        shell = Shell()
        lines = shell.run_script(os.path.join(self.dir.name, "x.emu"))
        self.assertTrue(lines[0].startswith("script:"))

    def test_startup_output_has_debug_and_dialog(self):
        path = self.write("ls\n")
        shell = Shell(Config(script_path=path))
        lines = shell.startup_output()
        self.assertIn(path, "\n".join(lines[:3]))
        self.assertEqual(lines[-1], "home/")


if __name__ == "__main__":
    unittest.main()

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from config import Config, NOT_SET, parse_args  


class ConfigTest(unittest.TestCase):
    def test_no_args(self):
        config = parse_args([])
        self.assertIsNone(config.vfs_path)
        self.assertIsNone(config.script_path)

    def test_all_args(self):
        config = parse_args(["--vfs", "a.csv", "--script", "s.emu"])
        self.assertEqual(config, Config("a.csv", "s.emu"))

    def test_unknown_arg_exits(self):
        with self.assertRaises(SystemExit):
            parse_args(["--bogus"])

    def test_debug_lines_show_values(self):
        text = "\n".join(Config("a.csv", "s.emu").debug_lines())
        self.assertIn("a.csv", text)
        self.assertIn("s.emu", text)

    def test_debug_lines_not_set(self):
        text = "\n".join(Config().debug_lines())
        self.assertEqual(text.count(NOT_SET), 2)


if __name__ == "__main__":
    unittest.main()

import pytest
import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import Command

class TestCommand(unittest.TestCase):
    def test_command_prop_payload(self):
        comm = Command("foo bar", "test")
        self.assertEqual(comm.name, "test")
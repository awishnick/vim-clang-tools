import unittest
from clang_tools import find_definition
import clang.cindex as ci


class TestFindDefinition(unittest.TestCase):
    def setUp(self):
        if not ci.Config.loaded:
            ci.Config.set_library_path('clang/lib')
        self.index = ci.Index.create()
        self.test_file = 'test/find-defn/test.cpp'
        self.test_tu = self.index.parse(self.test_file)
        self.print_file = 'test/find-defn/print.cpp'
        self.print_tu = self.index.parse(self.print_file)
        self.test_h_file = 'test/find-defn/test.h'

    def test_other_tu(self):
        """Find the definition of a symbol from another translation unit."""
        # Search for the definition of the function 'in_other_tu()'.
        defn = find_definition(self.test_tu,
                               self.test_file,
                               line=7,
                               col=2,
                               tus=[self.test_tu, self.print_tu])
        self.assertIsNotNone(defn)
        self.assertEqual(defn.displayname, 'in_other_tu()')
        self.assertTrue(defn.is_definition())
        self.assertEqual(defn.location.file.name, self.print_file)

    def test_same_tu(self):
        """Find the definition of a symbol from the same translation unit."""
        # Search for the definition of the function 'in_this_tu()'.
        defn = find_definition(self.test_tu,
                               self.test_file,
                               line=8,
                               col=2,
                               tus=[self.test_tu, self.print_tu])
        self.assertIsNotNone(defn)
        self.assertEqual(defn.displayname, 'in_this_tu()')
        self.assertTrue(defn.is_definition())
        self.assertEqual(defn.location.file.name, self.test_file)

    def test_inline_header(self):
        """Find the definition of an inline function from a header."""
        # Search for the definition of the function 'inline_header'.
        defn = find_definition(self.test_tu,
                               self.test_file,
                               line=9,
                               col=2,
                               tus=[self.test_tu, self.print_tu])
        self.assertIsNotNone(defn)
        self.assertEqual(defn.displayname, 'inline_header()')
        self.assertTrue(defn.is_definition())
        self.assertEqual(defn.location.file.name, self.test_h_file)

    def test_static_header(self):
        """Find the definition of a static function from a header."""
        # Search for the definition of the function 'inline_header'.
        defn = find_definition(self.test_tu,
                               self.test_file,
                               line=10,
                               col=2,
                               tus=[self.test_tu, self.print_tu])
        self.assertIsNotNone(defn)
        self.assertEqual(defn.displayname, 'static_header()')
        self.assertTrue(defn.is_definition())
        self.assertEqual(defn.location.file.name, self.test_h_file)

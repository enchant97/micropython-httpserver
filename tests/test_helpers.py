from collections import OrderedDict
from unittest import TestCase

from httpserver import helpers


class TestPercentDecode(TestCase):
    def test_valid(self):
        v = "Hello%20World%21"
        expected = b"Hello World!"
        actual = helpers.perc_decode(v)

        self.assertEqual(expected, actual)

    def test_valid_form(self):
        v = "Hello+World%21"
        expected = b"Hello World!"
        actual = helpers.perc_decode(v, from_form=True)

        self.assertEqual(expected, actual)


class TestProcessQueryString(TestCase):
    def test_valid(self):
        test_values = (
            ("q=", OrderedDict([("q", b"")])),
            ("name=Leo", OrderedDict([("name", b"Leo")])),
            ("name=Leo&admin=1", OrderedDict([("name", b"Leo"), ("admin", b"1")])),
        )
        for query_string, expected in test_values:
            with self.subTest(query_string=query_string, expected=expected):
                actual = helpers.process_query_string(query_string)
                self.assertEqual(expected, actual)


class TestSeperatePathAndQueries(TestCase):
    def test_valid(self):
        test_values = (
            ("/", ("/", OrderedDict([]))),
            ("/?", ("/", OrderedDict([]))),
            ("/?q=", ("/", OrderedDict([("q", b"")]))),
            ("/?name=Leo", ("/", OrderedDict([("name", b"Leo")]))),
            ("/hello-world?name=Leo&admin=1", ("/hello-world", OrderedDict([("name", b"Leo"), ("admin", b"1")]))),
        )
        for path, expected in test_values:
            with self.subTest(path=path, expected=expected):
                actual = helpers.seperate_path_and_query(path)
                self.assertEqual(expected, actual)

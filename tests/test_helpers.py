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

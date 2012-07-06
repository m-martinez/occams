import unittest2 as unittest

from hive.roster.factory import isValidOurNumber
from hive.roster.testing import OCCAMS_ROSTER_INTEGRATION_TESTING

class TestFactory(unittest.TestCase):
    """
    Checks that valid OUR numbers are being produced.
    """

    layer = OCCAMS_ROSTER_INTEGRATION_TESTING

    def testValidator(self):
        invalid_numbers = (
            # ambiguous characters
            '222-22l',
            '222-l22',
            '222-22o',
            '222-o22',
            '222-220',
            '222-022',
            '222-221',
            '222-122',
            # vowels
            '222-a22',
            '222-e22',
            '222-i22',
            '222-o22',
            '222-u22',
            '222-y22',
            '222-fag',
            )

        valid_numbers = (
            '222-22b',
            '222-22f',
            '222-22g',
            )

        for number in invalid_numbers:
            self.assertFalse(isValidOurNumber(number), '%s is unexpectedly valid' % number)

        for number in valid_numbers:
            self.assertTrue(isValidOurNumber(number), '%s is unexpectedly invalid' % number)

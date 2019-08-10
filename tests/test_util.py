#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)

from unittest import TestCase

from beward.util import normalize_fqdn, is_valid_fqdn


class TestUtil(TestCase):
    def test_normalize_fqdn(self):
        fqdn = 'google.com.'
        expect = 'google.com'
        self.assertEqual(expect, normalize_fqdn(fqdn))

        fqdn = 'домен.рф.'
        expect = 'xn--d1acufc.xn--p1ai'
        self.assertEqual(expect, normalize_fqdn(fqdn))

        fqdn = 'домен.рф.:80'
        expect = 'xn--d1acufc.xn--p1ai'
        self.assertEqual(expect, normalize_fqdn(fqdn))

    def test_is_valid_fqdn__label_too_long(self):
        self.assertValidFQDN('b' * 63, 'com')
        try:
            self.assertInvalidFQDN('A' * 64, 'com')
        except UnicodeError:
            pass
        try:
            self.assertInvalidFQDN('b' * 63, 'A' * 64, 'com')
        except UnicodeError:
            pass

    def test_is_valid_fqdn__name_too_long_254_octets(self):
        parts = [(chr(ord('A') + i % 26))
                 for i in range(int(254 / 2) - 1)]
        parts.append('co')
        fqdn = '.'.join(parts)
        assert len(fqdn) == 254
        self.assertInvalidFQDN(fqdn)

    def test_is_valid_fqdn__name_ok_253_octets(self):
        parts = [(chr(ord('A') + i % 26)) for i in range(int(254 / 2))]
        fqdn = '.'.join(parts)
        assert len(fqdn) == 253
        self.assertValidFQDN(fqdn)

    def test_rfc_1035_s_3_1__trailing_byte(self):
        parts = [(chr(ord('A') + i % 26)) for i in range(int(254 / 2))]
        fqdn = '.'.join(parts) + '.'
        assert len(fqdn) == 254
        self.assertValidFQDN(fqdn)

    def test_rfc_3696_s_2__label_invalid_starts_or_ends_with_hyphen(self):
        self.assertInvalidFQDN('-a', 'com')
        self.assertInvalidFQDN('a-', 'com')
        self.assertInvalidFQDN('-a-', 'com')
        self.assertInvalidFQDN('a', '-com')
        self.assertInvalidFQDN('a', 'com-')

    def test_rfc_3696_s_2__punycode(self):
        self.assertValidFQDN('є', 'com')
        self.assertValidFQDN('le-tour-est-joué', 'com')
        self.assertValidFQDN('invalid', 'cóm')
        self.assertValidFQDN('ich-hätte-gern-ein-Umlaut', 'de')

    def test_rfc_3696_s_2__preferred_form_invalid_chars(self):
        self.assertInvalidFQDN('\x01', 'com')
        self.assertInvalidFQDN('x', '\x01\x02\x01')

    def test_rfc_3696_s_2__valid(self):
        self.assertValidFQDN('shopping', 'on', 'the', 'net')
        self.assertValidFQDN('who', 'is')
        self.assertValidFQDN('bbc', 'co', 'uk')
        self.assertValidFQDN('example', 'io')

    def test_rfc_3696_s_2__invalid(self):
        self.assertFalse(is_valid_fqdn('192.168.0.1'))

    def assertValidFQDN(self, *seq):
        self.assertTrue(self.is_valid_fqdn_from_labels_sequence(seq))

    def assertInvalidFQDN(self, *seq):
        self.assertFalse(self.is_valid_fqdn_from_labels_sequence(seq))

    @staticmethod
    def is_valid_fqdn_from_labels_sequence(fqdn_labels_sequence):
        fqdn = '.'.join(fqdn_labels_sequence)
        return is_valid_fqdn(fqdn)

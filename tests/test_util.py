# pylint: disable=protected-access,redefined-outer-name
"""Test to verify that Beward library works."""

from unittest import TestCase

from beward.util import is_valid_fqdn, normalize_fqdn


class TestUtil(TestCase):
    """Test case for utility functions."""

    def test_normalize_fqdn(self):
        """Test that normalize FQDN."""
        fqdn = "google.com."
        expect = "google.com"
        self.assertEqual(expect, normalize_fqdn(fqdn))

        fqdn = "домен.рф."
        expect = "xn--d1acufc.xn--p1ai"
        self.assertEqual(expect, normalize_fqdn(fqdn))

        fqdn = "домен.рф.:80"
        expect = "xn--d1acufc.xn--p1ai"
        self.assertEqual(expect, normalize_fqdn(fqdn))

    def test_is_valid_fqdn__label_too_long(self):
        """Test FQDN validations."""
        self.assertValidFQDN("b" * 63, "com")
        try:
            self.assertInvalidFQDN("A" * 64, "com")
        except UnicodeError:
            pass
        try:
            self.assertInvalidFQDN("b" * 63, "A" * 64, "com")
        except UnicodeError:
            pass

    def test_is_valid_fqdn__name_too_long_254_octets(self):
        """Test FQDN validations."""
        parts = [(chr(ord("A") + i % 26)) for i in range(int(254 / 2) - 1)]
        parts.append("co")
        fqdn = ".".join(parts)
        assert len(fqdn) == 254
        self.assertInvalidFQDN(fqdn)

    def test_is_valid_fqdn__name_ok_253_octets(self):
        """Test FQDN validations."""
        parts = [(chr(ord("A") + i % 26)) for i in range(int(254 / 2))]
        fqdn = ".".join(parts)
        assert len(fqdn) == 253
        self.assertValidFQDN(fqdn)

    def test_rfc_1035_s_3_1__trailing_byte(self):
        """Test FQDN validations."""
        parts = [(chr(ord("A") + i % 26)) for i in range(int(254 / 2))]
        fqdn = ".".join(parts) + "."
        assert len(fqdn) == 254
        self.assertValidFQDN(fqdn)

    def test_rfc_3696_s_2__label_invalid_starts_or_ends_with_hyphen(self):
        """Test FQDN validations."""
        self.assertInvalidFQDN("-a", "com")
        self.assertInvalidFQDN("a-", "com")
        self.assertInvalidFQDN("-a-", "com")
        self.assertInvalidFQDN("a", "-com")
        self.assertInvalidFQDN("a", "com-")

    def test_rfc_3696_s_2__punycode(self):
        """Test FQDN validations."""
        self.assertValidFQDN("є", "com")
        self.assertValidFQDN("le-tour-est-joué", "com")
        self.assertValidFQDN("invalid", "cóm")
        self.assertValidFQDN("ich-hätte-gern-ein-Umlaut", "de")

    def test_rfc_3696_s_2__preferred_form_invalid_chars(self):
        """Test FQDN validations."""
        self.assertInvalidFQDN("\x01", "com")
        self.assertInvalidFQDN("x", "\x01\x02\x01")

    def test_rfc_3696_s_2__valid(self):
        """Test FQDN validations."""
        self.assertValidFQDN("shopping", "on", "the", "net")
        self.assertValidFQDN("who", "is")
        self.assertValidFQDN("bbc", "co", "uk")
        self.assertValidFQDN("example", "io")

    def test_rfc_3696_s_2__invalid(self):
        """Test FQDN validations."""
        self.assertFalse(is_valid_fqdn("192.168.0.1"))

    # pylint: disable=invalid-name
    def assertValidFQDN(self, *seq):
        """Positive assert function for FQDN validations."""
        self.assertTrue(self._is_valid_fqdn_from_labels_sequence(seq))

    # pylint: disable=invalid-name
    def assertInvalidFQDN(self, *seq):
        """Negative assert function for FQDN validations."""
        self.assertFalse(self._is_valid_fqdn_from_labels_sequence(seq))

    @staticmethod
    def _is_valid_fqdn_from_labels_sequence(fqdn_labels_sequence):
        fqdn = ".".join(fqdn_labels_sequence)
        return is_valid_fqdn(fqdn)

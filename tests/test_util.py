# pylint: disable=protected-access,redefined-outer-name
"""Test to verify that Beward library works."""

import contextlib
from typing import Any

from beward.util import is_valid_fqdn, normalize_fqdn


def test_normalize_fqdn():
    """Test that normalize FQDN."""
    fqdn = "google.com."
    expect = "google.com"
    assert normalize_fqdn(fqdn) == expect

    fqdn = "домен.рф."
    expect = "xn--d1acufc.xn--p1ai"
    assert normalize_fqdn(fqdn) == expect

    fqdn = "домен.рф.:80"
    expect = "xn--d1acufc.xn--p1ai"
    assert normalize_fqdn(fqdn) == expect


def test_is_valid_fqdn__label_too_long():
    """Test FQDN validations."""
    assertValidFQDN("b" * 63, "com")
    with contextlib.suppress(UnicodeError):
        assertInvalidFQDN("A" * 64, "com")
    with contextlib.suppress(UnicodeError):
        assertInvalidFQDN("b" * 63, "A" * 64, "com")


def test_is_valid_fqdn__name_too_long_254_octets():
    """Test FQDN validations."""
    parts = [(chr(ord("A") + i % 26)) for i in range(int(254 / 2) - 1)]
    parts.append("co")
    fqdn = ".".join(parts)
    assert len(fqdn) == 254
    assertInvalidFQDN(fqdn)


def test_is_valid_fqdn__name_ok_253_octets():
    """Test FQDN validations."""
    parts = [(chr(ord("A") + i % 26)) for i in range(int(254 / 2))]
    fqdn = ".".join(parts)
    assert len(fqdn) == 253
    assertValidFQDN(fqdn)


def test_rfc_1035_s_3_1__trailing_byte():
    """Test FQDN validations."""
    parts = [(chr(ord("A") + i % 26)) for i in range(int(254 / 2))]
    fqdn = ".".join(parts) + "."
    assert len(fqdn) == 254
    assertValidFQDN(fqdn)


def test_rfc_3696_s_2__label_invalid_starts_or_ends_with_hyphen():
    """Test FQDN validations."""
    assertInvalidFQDN("-a", "com")
    assertInvalidFQDN("a-", "com")
    assertInvalidFQDN("-a-", "com")
    assertInvalidFQDN("a", "-com")
    assertInvalidFQDN("a", "com-")


def test_rfc_3696_s_2__punycode():
    """Test FQDN validations."""
    assertValidFQDN("є", "com")
    assertValidFQDN("le-tour-est-joué", "com")
    assertValidFQDN("invalid", "cóm")
    assertValidFQDN("ich-hätte-gern-ein-Umlaut", "de")


def test_rfc_3696_s_2__preferred_form_invalid_chars():
    """Test FQDN validations."""
    assertInvalidFQDN("\x01", "com")
    assertInvalidFQDN("x", "\x01\x02\x01")


def test_rfc_3696_s_2__valid():
    """Test FQDN validations."""
    assertValidFQDN("shopping", "on", "the", "net")
    assertValidFQDN("who", "is")
    assertValidFQDN("bbc", "co", "uk")
    assertValidFQDN("example", "io")


def test_rfc_3696_s_2__invalid():
    """Test FQDN validations."""
    assert is_valid_fqdn("192.168.0.1") is False


def _is_valid_fqdn_from_labels_sequence(fqdn_labels_sequence) -> bool:
    fqdn = ".".join(fqdn_labels_sequence)
    return is_valid_fqdn(fqdn)


# pylint: disable=invalid-name
def assertValidFQDN(*seq: Any) -> None:  # noqa: N802
    """Positive assert function for FQDN validations."""
    assert _is_valid_fqdn_from_labels_sequence(seq) is True


# pylint: disable=invalid-name
def assertInvalidFQDN(*seq: Any) -> None:  # noqa: N802
    """Negative assert function for FQDN validations."""
    assert _is_valid_fqdn_from_labels_sequence(seq) is False

#!/usr/bin/env python3
# coding=utf-8
###############################################################################
"""
__author__ = "sunhn"

Description:

"""

import logging
from typing import Dict, Tuple
import math

logger = logging.getLogger(__name__)


def password_length_valid(password: str, min_len: int = 12, max_len: int = 32) -> Tuple[bool, str]:
    """Check if the password length is within the specified range."""
    if not password:
        return False, "Password cannot be empty."
    if len(password) < min_len:
        return False, f"Password is too short, must be at least {min_len} characters."
    if len(password) > max_len:
        return False, f"Password is too long, must be at most {max_len} characters."
    return True, "Password length is valid."


def password_has_min_types(password: str, min_types: int = 3) -> Tuple[bool, str]:
    """Check if the password contains at least min_types of character categories."""
    if not password:
        return False, "Password cannot be empty."
    checks = [
        any(c.islower() for c in password),  # Lowercase letters
        any(c.isupper() for c in password),  # Uppercase letters
        any(c.isdigit() for c in password),  # Digits
        any(not c.isalnum() for c in password),  # Special characters
    ]
    types_found = sum(checks)
    if types_found >= min_types:
        return True, "Password contains sufficient character variety."
    return False, f"Password must contain at least {min_types} types of characters, found {types_found}."


def contains_sequential_chars(password: str, length: int = 3) -> Tuple[bool, str]:
    """Check if the password contains sequential characters (ascending or descending)."""
    if len(password) < length:
        return False, "Password too short to check for sequential characters."
    pw = password.lower()
    for i in range(len(pw) - length + 1):
        substr = pw[i : i + length]
        if substr.isalpha() or substr.isdigit():
            is_seq = all(ord(substr[j + 1]) - ord(substr[j]) == 1 for j in range(length - 1))
            is_rev_seq = all(ord(substr[j]) - ord(substr[j + 1]) == 1 for j in range(length - 1))
            if is_seq or is_rev_seq:
                return False, f"Sequential character pattern detected: {substr}"
    return True, "No sequential character pattern detected."


def contains_sequential_keyboard(password: str, length: int = 3) -> Tuple[bool, str]:
    """Check if the password contains a keyboard layout sequence (like 'qwe' or 'asd')."""
    if len(password) < length:
        return False, "Password too short to check for keyboard sequences."
    pw = password.lower()
    keyboard_rows = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]

    for i in range(len(pw) - length + 1):
        substr = pw[i : i + length]
        rev_substr = substr[::-1]
        if any(substr in row or rev_substr in row for row in keyboard_rows):
            return False, f"Keyboard pattern detected: {substr}"
    return True, "No keyboard pattern detected."


def contains_repeated_chars(password: str, max_repeats: int = 2) -> Tuple[bool, str]:
    """Check if the password contains a sequence of repeated characters beyond allowed limit."""
    if not password:
        return False, "Password cannot be empty."
    count = 1
    for i in range(1, len(password)):
        if password[i] == password[i - 1]:
            count += 1
            if count > max_repeats:
                return False, f"Password contains more than {max_repeats} repeated characters: '{password[i] * count}'"
        else:
            count = 1
    return True, "No excessive repeated characters detected."


def calculate_entropy(password: str, charsets: Dict[str, bool], threshold: float = 60.0) -> Tuple[bool, str]:
    """Calculate entropy based on used character sets and check if it meets the threshold."""
    if not password:
        return False, "Password cannot be empty."
    charset_size = 0
    if charsets.get("lower"):
        charset_size += 26
    if charsets.get("upper"):
        charset_size += 26
    if charsets.get("digit"):
        charset_size += 10
    if charsets.get("special"):
        charset_size += 32  # Common special character count
    if charset_size == 0:
        return False, "No valid character set detected."
    entropy = len(password) * math.log2(charset_size)
    entropy = round(entropy, 2)
    if entropy >= threshold:
        return True, f"Password entropy is {entropy}, which meets the requirement."
    return False, f"Password entropy is {entropy}, which is below the threshold of {threshold}."


def check_password_complexity_with_reason(password: str) -> Tuple[bool, str]:
    """Validate password using multiple checks and return result with reason."""
    checks = [
        password_length_valid(password),
        password_has_min_types(password),
        contains_sequential_chars(password),
        contains_sequential_keyboard(password),
        contains_repeated_chars(password),
        calculate_entropy(
            password,
            {
                "lower": any(c.islower() for c in password),
                "upper": any(c.isupper() for c in password),
                "digit": any(c.isdigit() for c in password),
                "special": any(not c.isalnum() for c in password),
            },
        ),
    ]
    for passed, reason in checks:
        if not passed:
            return False, reason
    return True, "Password is strong and meets all complexity requirements."

package com.bittercode.util;

import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.Arrays;
import java.util.Base64;

import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;

/**
 * PBKDF2-HMAC-SHA-256 password encoding for the Java 8 application.
 * Format: pbkdf2-sha256$iterations$salt$derivedKey
 */
public final class PasswordUtil {

    private static final String PREFIX = "pbkdf2-sha256$";
    private static final int ITERATIONS = 120_000;
    private static final int SALT_BYTES = 16;
    private static final int KEY_BITS = 256;
    private static final SecureRandom RANDOM = new SecureRandom();

    private PasswordUtil() {
    }

    public static String hash(String password) {
        if (password == null || password.length() < 8) {
            throw new IllegalArgumentException("Password must contain at least 8 characters.");
        }

        byte[] salt = new byte[SALT_BYTES];
        RANDOM.nextBytes(salt);
        byte[] derived = derive(password, salt, ITERATIONS, KEY_BITS);

        try {
            return PREFIX + ITERATIONS + "$"
                    + Base64.getEncoder().encodeToString(salt) + "$"
                    + Base64.getEncoder().encodeToString(derived);
        } finally {
            Arrays.fill(derived, (byte) 0);
        }
    }

    /**
     * Supports legacy plaintext comparison only so a successful login can
     * upgrade the stored value. New registrations always use hash().
     */
    public static boolean matches(String candidate, String storedValue) {
        if (candidate == null || storedValue == null) {
            return false;
        }

        if (!isEncoded(storedValue)) {
            return MessageDigest.isEqual(
                    candidate.getBytes(StandardCharsets.UTF_8),
                    storedValue.getBytes(StandardCharsets.UTF_8));
        }

        try {
            String[] parts = storedValue.split("\\$");
            if (parts.length != 4) {
                return false;
            }
            int iterations = Integer.parseInt(parts[1]);
            if (iterations < 10_000 || iterations > 1_000_000) {
                return false;
            }

            byte[] salt = Base64.getDecoder().decode(parts[2]);
            byte[] expected = Base64.getDecoder().decode(parts[3]);
            if (salt.length != SALT_BYTES || expected.length != KEY_BITS / 8) {
                return false;
            }

            byte[] actual = derive(candidate, salt, iterations, KEY_BITS);
            try {
                return MessageDigest.isEqual(expected, actual);
            } finally {
                Arrays.fill(actual, (byte) 0);
            }
        } catch (IllegalArgumentException exception) {
            return false;
        }
    }

    public static boolean isEncoded(String value) {
        return value != null && value.startsWith(PREFIX);
    }

    private static byte[] derive(
            String password, byte[] salt, int iterations, int keyBits) {
        char[] chars = password.toCharArray();
        PBEKeySpec spec = new PBEKeySpec(chars, salt, iterations, keyBits);
        try {
            return SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
                    .generateSecret(spec).getEncoded();
        } catch (GeneralSecurityException exception) {
            throw new IllegalStateException("PBKDF2 password hashing is unavailable.", exception);
        } finally {
            spec.clearPassword();
            Arrays.fill(chars, (char) 0);
        }
    }
}

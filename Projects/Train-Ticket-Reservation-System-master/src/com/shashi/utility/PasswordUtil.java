package com.shashi.utility;

import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.Base64;

import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;

/**
 * Password hashing helper using PBKDF2-HMAC-SHA-256 with a unique random salt.
 * The encoded representation is: pbkdf2-sha256$iterations$salt$hash.
 */
public final class PasswordUtil {

    private static final String PREFIX = "pbkdf2-sha256$";
    private static final int ITERATIONS = 120_000;
    private static final int KEY_LENGTH_BITS = 256;
    private static final int SALT_LENGTH_BYTES = 16;
    private static final SecureRandom SECURE_RANDOM = new SecureRandom();

    private PasswordUtil() {
    }

    public static String hash(String password) {
        if (password == null || password.isEmpty()) {
            throw new IllegalArgumentException("Password cannot be empty.");
        }

        byte[] salt = new byte[SALT_LENGTH_BYTES];
        SECURE_RANDOM.nextBytes(salt);

        byte[] derived = derive(password, salt, ITERATIONS, KEY_LENGTH_BITS);
        return PREFIX
                + ITERATIONS + "$"
                + Base64.getEncoder().encodeToString(salt) + "$"
                + Base64.getEncoder().encodeToString(derived);
    }

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
            if (salt.length < SALT_LENGTH_BYTES || expected.length == 0) {
                return false;
            }

            byte[] actual = derive(candidate, salt, iterations, expected.length * 8);
            return MessageDigest.isEqual(expected, actual);
        } catch (IllegalArgumentException exception) {
            return false;
        }
    }

    public static boolean isEncoded(String value) {
        return value != null && value.startsWith(PREFIX);
    }

    private static byte[] derive(
            String password,
            byte[] salt,
            int iterations,
            int keyLengthBits) {

        char[] passwordChars = password.toCharArray();
        PBEKeySpec specification = new PBEKeySpec(
                passwordChars, salt, iterations, keyLengthBits);

        try {
            SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
            return factory.generateSecret(specification).getEncoded();
        } catch (GeneralSecurityException exception) {
            throw new IllegalStateException("PBKDF2 password hashing is unavailable.", exception);
        } finally {
            specification.clearPassword();
            java.util.Arrays.fill(passwordChars, '\0');
        }
    }
}

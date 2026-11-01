package com.bittercode.util;

import java.util.Base64;

public class PasswordUtilSmokeTest {

    public static void main(String[] args) {
        String password = "bookstore-local-test-password";
        String firstHash = PasswordUtil.hash(password);
        String secondHash = PasswordUtil.hash(password);

        require(firstHash.startsWith("pbkdf2-sha256$"), "The stored value must use the PBKDF2 format.");
        require(firstHash.length() <= 100, "The hash must fit the current SQL password column.");
        require(!firstHash.equals(secondHash), "Each password hash must use a unique random salt.");
        require(PasswordUtil.matches(password, firstHash), "The correct password must verify.");
        require(!PasswordUtil.matches("wrong-password", firstHash), "An incorrect password must not verify.");
        require(PasswordUtil.matches("legacy-pass", "legacy-pass"),
                "Legacy plaintext values must remain verifiable for one-time migration.");

        String[] parts = firstHash.split("\\$");
        byte[] derived = Base64.getDecoder().decode(parts[3]);
        derived[0] ^= 0x01;
        String modifiedHash = parts[0] + "$" + parts[1] + "$" + parts[2] + "$"
                + Base64.getEncoder().encodeToString(derived);
        require(!PasswordUtil.matches(password, modifiedHash),
                "Modified password hashes must not verify.");

        System.out.println("Bookstore PBKDF2 smoke checks passed.");
    }

    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }
}

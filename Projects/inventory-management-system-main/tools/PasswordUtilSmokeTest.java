package com.inventorymanagementsystem.security;

import java.util.Base64;

public class PasswordUtilSmokeTest {

    public static void main(String[] args) {
        String password = "inventory-local-test-password";
        String firstHash = PasswordUtil.hash(password);
        String secondHash = PasswordUtil.hash(password);

        require(firstHash.startsWith("pbkdf2-sha256$"), "Expected PBKDF2 format.");
        require(firstHash.length() <= 255, "Hash must fit the users.password column.");
        require(!firstHash.equals(secondHash), "Hashes must use different random salts.");
        require(PasswordUtil.matches(password, firstHash), "Correct password should match.");
        require(!PasswordUtil.matches("wrong-password", firstHash), "Wrong password must fail.");
        require(PasswordUtil.matches("legacy-pass", "legacy-pass"),
                "Legacy plaintext values must be verifiable for migration.");

        String[] parts = firstHash.split("\\$");
        byte[] key = Base64.getDecoder().decode(parts[3]);
        key[0] ^= 0x01;
        String altered = parts[0] + "$" + parts[1] + "$" + parts[2] + "$"
                + Base64.getEncoder().encodeToString(key);
        require(!PasswordUtil.matches(password, altered), "Altered hashes must fail.");

        System.out.println("Inventory password hashing smoke checks passed.");
    }

    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }
}

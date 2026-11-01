import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.util.Base64;

public class CryptoUtilSmokeTest {

    public static void main(String[] args) throws Exception {
        CryptoUtil crypto = new CryptoUtil();
        String secret = "local-test-secret-2026";
        String message = "Sensitive text with Unicode: café, ñ, and ✓";

        String encrypted = crypto.encrypt(secret, message);
        require(encrypted.startsWith("v2:"), "Ciphertext must carry the v2 format marker.");
        require(!encrypted.contains(message), "Ciphertext must not expose the plaintext.");
        require(message.equals(crypto.decrypt(secret, encrypted)),
                "Decryption must restore the original text.");

        String secondEncryption = crypto.encrypt(secret, message);
        require(!encrypted.equals(secondEncryption),
                "A new salt and nonce must produce a different ciphertext.");

        byte[] payload = Base64.getDecoder().decode(encrypted.substring(3));
        payload[payload.length - 1] ^= 0x01;
        String modified = "v2:" + Base64.getEncoder().encodeToString(payload);
        expectAuthenticationFailure(crypto, secret, modified);

        expectAuthenticationFailure(crypto, "a-different-secret-2026", encrypted);

        System.out.println("AES-GCM smoke checks passed.");
    }

    private static void expectAuthenticationFailure(
            CryptoUtil crypto, String secret, String ciphertext) throws Exception {
        try {
            crypto.decrypt(secret, ciphertext);
            throw new AssertionError("Tampered data or an incorrect key must not decrypt.");
        } catch (GeneralSecurityException expected) {
            // GCM authentication correctly rejected the ciphertext.
        }
    }

    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }
}

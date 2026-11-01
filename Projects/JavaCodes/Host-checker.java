import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Scanner;

class WebsiteStatusChecker {

    private static final int CONNECT_TIMEOUT_MS = 5000;
    private static final int READ_TIMEOUT_MS = 5000;

    private WebsiteStatusChecker() {
    }

    public static void main(String[] args) {
        try (Scanner scanner = new Scanner(System.in)) {
            System.out.print("Enter the website URL to check: ");
            String urlToCheck = scanner.nextLine().trim();

            if (urlToCheck.isEmpty()) {
                System.err.println("A website URL is required.");
                return;
            }

            int statusCode = checkWebsiteStatus(urlToCheck);
            if (statusCode >= 200 && statusCode < 600) {
                System.out.println("The server responded (HTTP Status Code: " + statusCode + ").");
            } else {
                System.out.println("Unexpected HTTP status code: " + statusCode);
            }
        } catch (IOException | IllegalArgumentException exception) {
            System.err.println("Unable to check website status: " + exception.getMessage());
        }
    }

    public static int checkWebsiteStatus(String address) throws IOException {
        String normalizedAddress = address.contains("://")
                ? address
                : "https://" + address;
        URL websiteUrl = new URL(normalizedAddress);

        String protocol = websiteUrl.getProtocol();
        if (!"http".equalsIgnoreCase(protocol) && !"https".equalsIgnoreCase(protocol)) {
            throw new IOException("Only HTTP and HTTPS URLs are supported.");
        }

        HttpURLConnection connection = null;
        try {
            connection = (HttpURLConnection) websiteUrl.openConnection();
            connection.setRequestMethod("HEAD");
            connection.setConnectTimeout(CONNECT_TIMEOUT_MS);
            connection.setReadTimeout(READ_TIMEOUT_MS);
            connection.setInstanceFollowRedirects(true);
            connection.setRequestProperty("User-Agent", "JavaCodes-WebsiteStatusChecker/1.0");

            int statusCode = connection.getResponseCode();
            if (statusCode == HttpURLConnection.HTTP_BAD_METHOD
                    || statusCode == HttpURLConnection.HTTP_NOT_IMPLEMENTED) {
                connection.disconnect();
                connection = (HttpURLConnection) websiteUrl.openConnection();
                connection.setRequestMethod("GET");
                connection.setConnectTimeout(CONNECT_TIMEOUT_MS);
                connection.setReadTimeout(READ_TIMEOUT_MS);
                connection.setInstanceFollowRedirects(true);
                connection.setRequestProperty("Range", "bytes=0-0");
                connection.setRequestProperty("User-Agent", "JavaCodes-WebsiteStatusChecker/1.0");
                statusCode = connection.getResponseCode();
            }
            return statusCode;
        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }
    }
}

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

public class OpenWeatherMap {

    private static final String API_ENDPOINT =
            "https://api.openweathermap.org/data/2.5/weather";
    private static final int CONNECT_TIMEOUT_MS = 5000;
    private static final int READ_TIMEOUT_MS = 5000;

    private OpenWeatherMap() {
    }

    public static void main(String[] args) {
        String apiKey = System.getenv("OPENWEATHER_API_KEY");
        if (apiKey == null || apiKey.trim().isEmpty()) {
            System.err.println(
                    "Missing OPENWEATHER_API_KEY. Set it as an environment variable before running.");
            return;
        }

        String city = args.length == 0 ? "London" : String.join(" ", args).trim();
        if (city.isEmpty()) {
            System.err.println("Provide a city name, for example: java OpenWeatherMap London");
            return;
        }

        HttpURLConnection connection = null;
        try {
            String encodedCity = URLEncoder.encode(city, "UTF-8");
            String requestUrl = API_ENDPOINT
                    + "?q=" + encodedCity
                    + "&units=metric"
                    + "&appid=" + URLEncoder.encode(apiKey, "UTF-8");

            connection = (HttpURLConnection) new URL(requestUrl).openConnection();
            connection.setRequestMethod("GET");
            connection.setConnectTimeout(CONNECT_TIMEOUT_MS);
            connection.setReadTimeout(READ_TIMEOUT_MS);
            connection.setRequestProperty("Accept", "application/json");
            connection.setRequestProperty("User-Agent", "JavaCodes-WeatherExample/1.0");

            int status = connection.getResponseCode();
            InputStream responseStream = status >= 200 && status < 400
                    ? connection.getInputStream()
                    : connection.getErrorStream();

            if (responseStream == null) {
                System.err.println("Weather API returned HTTP " + status + " without a response body.");
                return;
            }

            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(responseStream, StandardCharsets.UTF_8))) {
                StringBuilder response = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    response.append(line);
                }

                if (status >= 200 && status < 300) {
                    System.out.println("Weather response for " + city + " (HTTP " + status + "):");
                    System.out.println(response);
                } else {
                    System.err.println("Weather API request failed (HTTP " + status + "):");
                    System.err.println(response);
                }
            }
        } catch (IOException exception) {
            System.err.println("Unable to retrieve weather data: " + exception.getMessage());
        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }
    }
}

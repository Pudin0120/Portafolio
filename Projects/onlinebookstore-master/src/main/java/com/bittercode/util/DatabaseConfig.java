package com.bittercode.util;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

final class DatabaseConfig {

    private static final Properties PROPERTIES = loadProperties();

    public static final String DRIVER_NAME = setting("DB_DRIVER", "db.driver", "com.mysql.cj.jdbc.Driver");
    public static final String DB_URL = setting(
            "DB_URL", "db.url",
            PROPERTIES.getProperty("db.host", "jdbc:mysql://localhost")
                    + ":" + PROPERTIES.getProperty("db.port", "3306")
                    + "/" + PROPERTIES.getProperty("db.name", "onlinebookstore"));
    public static final String DB_USER_NAME = setting("DB_USERNAME", "db.username", "");
    public static final String DB_PASSWORD = setting("DB_PASSWORD", "db.password", "");

    private DatabaseConfig() {
    }

    private static Properties loadProperties() {
        Properties properties = new Properties();
        try (InputStream input = DatabaseConfig.class.getClassLoader()
                .getResourceAsStream("application.properties")) {
            if (input != null) {
                properties.load(input);
            }
        } catch (IOException exception) {
            throw new ExceptionInInitializerError(
                    "Unable to read bookstore database configuration: " + exception.getMessage());
        }
        return properties;
    }

    private static String setting(String environmentName, String propertyName, String fallback) {
        String environmentValue = System.getenv(environmentName);
        if (environmentValue != null && !environmentValue.trim().isEmpty()) {
            return environmentValue.trim();
        }
        String propertyValue = PROPERTIES.getProperty(propertyName);
        return propertyValue == null || propertyValue.trim().isEmpty()
                ? fallback
                : propertyValue.trim();
    }
}

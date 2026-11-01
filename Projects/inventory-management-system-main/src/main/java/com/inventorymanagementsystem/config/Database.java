package com.inventorymanagementsystem.config;

import java.io.IOException;
import java.io.InputStream;
import java.sql.Connection;
import java.sql.DriverManager;
import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;

public final class Database {

    private static final Logger LOGGER = Logger.getLogger(Database.class.getName());
    private static final String CONFIG_FILE = "application.properties";
    private static final Database INSTANCE = new Database();

    private Database() {
    }

    public static Database getInstance() {
        return INSTANCE;
    }

    public Connection connectDB() {
        Properties dbConfig = new Properties();

        try (InputStream input = getClass().getClassLoader().getResourceAsStream(CONFIG_FILE)) {
            if (input == null) {
                throw new IllegalStateException(
                        "Missing " + CONFIG_FILE + " on the application classpath.");
            }

            dbConfig.load(input);

            String driver = resolveSetting(dbConfig, "javafx.jdbc.driver", "DB_DRIVER");
            String url = resolveSetting(dbConfig, "javafx.datasource.url", "DB_URL");
            String username = resolveSetting(dbConfig, "javafx.datasource.username", "DB_USERNAME");
            String password = resolveSetting(dbConfig, "javafx.datasource.password", "DB_PASSWORD");

            Class.forName(driver);
            return DriverManager.getConnection(url, username, password);
        } catch (IOException | ClassNotFoundException | java.sql.SQLException | IllegalStateException exception) {
            LOGGER.log(Level.SEVERE,
                    "Database connection failed. Check application.properties and DB_* environment variables.",
                    exception);
            return null;
        }
    }

    private static String resolveSetting(
            Properties properties,
            String propertyName,
            String environmentName) {

        String environmentValue = System.getenv(environmentName);
        if (environmentValue != null && !environmentValue.isBlank()) {
            return environmentValue.trim();
        }

        String propertyValue = properties.getProperty(propertyName);
        if (propertyValue == null || propertyValue.isBlank()) {
            throw new IllegalStateException(
                    "Missing database setting: " + propertyName + " / " + environmentName);
        }

        return propertyValue.trim();
    }
}

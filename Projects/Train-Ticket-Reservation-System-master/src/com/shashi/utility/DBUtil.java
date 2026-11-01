package com.shashi.utility;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.ResourceBundle;
import java.util.logging.Level;
import java.util.logging.Logger;

import com.shashi.beans.TrainException;
import com.shashi.constant.ResponseCode;

public final class DBUtil {

    private static final Logger LOGGER = Logger.getLogger(DBUtil.class.getName());
    private static final Connection CONNECTION = initializeConnection();

    private DBUtil() {
    }

    private static Connection initializeConnection() {
        try {
            ResourceBundle properties = ResourceBundle.getBundle("application");

            String driverName = resolve(properties, "driverName", "DB_DRIVER");
            String connectionString = resolve(properties, "connectionString", "DB_URL");
            String username = resolve(properties, "username", "DB_USERNAME");
            String password = resolve(properties, "password", "DB_PASSWORD");

            if (driverName.isEmpty() || connectionString.isEmpty()
                    || username.isEmpty() || password.isEmpty()) {
                throw new IllegalStateException(
                        "Set DB_DRIVER, DB_URL, DB_USERNAME, and DB_PASSWORD before starting the application.");
            }

            Class.forName(driverName);
            return DriverManager.getConnection(connectionString, username, password);
        } catch (Exception exception) {
            // Never print JDBC URLs, usernames, or passwords to application logs.
            LOGGER.log(Level.SEVERE,
                    "Oracle database initialization failed. Check the local DB_* environment variables.",
                    exception);
            return null;
        }
    }

    private static String resolve(
            ResourceBundle properties,
            String propertyName,
            String environmentName) {

        String environmentValue = System.getenv(environmentName);
        if (environmentValue != null && !environmentValue.trim().isEmpty()) {
            return environmentValue.trim();
        }

        return properties.containsKey(propertyName)
                ? properties.getString(propertyName).trim()
                : "";
    }

    public static Connection getConnection() throws TrainException {
        if (CONNECTION == null) {
            throw new TrainException(ResponseCode.DATABASE_CONNECTION_FAILURE);
        }
        return CONNECTION;
    }
}

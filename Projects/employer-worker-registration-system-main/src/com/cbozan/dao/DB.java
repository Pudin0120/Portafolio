package com.cbozan.dao;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public final class DB {

    public static volatile String ERROR_MESSAGE = "";

    private static final String DEFAULT_URL =
            "jdbc:postgresql://localhost:5432/Hesap-eProject";

    private Connection connection;

    private DB() {
    }

    private static class DBHelper {
        private static final DB INSTANCE = new DB();
    }

    public static Connection getConnection() throws SQLException {
        return DBHelper.INSTANCE.connect();
    }

    public static void destroyConnection() {
        DBHelper.INSTANCE.disconnect();
    }

    private synchronized Connection connect() throws SQLException {
        if (connection != null && !connection.isClosed()) {
            return connection;
        }

        String url = setting("EMPLOYER_DB_URL", "employer.db.url", DEFAULT_URL);
        String username = setting("EMPLOYER_DB_USER", "employer.db.user", "");
        String password = setting("EMPLOYER_DB_PASSWORD", "employer.db.password", "");

        if (username.isEmpty() || password.isEmpty()) {
            ERROR_MESSAGE = "Database credentials are not configured. Set EMPLOYER_DB_USER and EMPLOYER_DB_PASSWORD.";
            throw new SQLException(ERROR_MESSAGE);
        }

        try {
            connection = DriverManager.getConnection(url, username, password);
            ERROR_MESSAGE = "";
            return connection;
        } catch (SQLException exception) {
            // Do not expose JDBC URLs, usernames, or passwords in UI messages.
            ERROR_MESSAGE = "Unable to connect to PostgreSQL. Check the database service and EMPLOYER_DB_* settings.";
            throw new SQLException(ERROR_MESSAGE, exception);
        }
    }

    private String setting(String environmentName, String propertyName, String fallback) {
        String value = System.getenv(environmentName);
        if (value == null || value.trim().isEmpty()) {
            value = System.getProperty(propertyName);
        }
        return value == null || value.trim().isEmpty() ? fallback : value.trim();
    }

    private synchronized void disconnect() {
        if (connection == null) {
            return;
        }
        try {
            connection.close();
        } catch (SQLException exception) {
            ERROR_MESSAGE = "Unable to close the PostgreSQL connection cleanly.";
        } finally {
            connection = null;
        }
    }
}

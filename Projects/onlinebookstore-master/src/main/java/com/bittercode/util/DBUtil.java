package com.bittercode.util;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.logging.Level;
import java.util.logging.Logger;

import com.bittercode.constant.ResponseCode;
import com.bittercode.model.StoreException;

public final class DBUtil {

    private static final Logger LOGGER = Logger.getLogger(DBUtil.class.getName());
    private static Connection connection;

    static {
        try {
            Class.forName(DatabaseConfig.DRIVER_NAME);
            connection = DriverManager.getConnection(
                    DatabaseConfig.DB_URL,
                    DatabaseConfig.DB_USER_NAME,
                    DatabaseConfig.DB_PASSWORD);
        } catch (SQLException | ClassNotFoundException exception) {
            // Do not log JDBC URLs, usernames, or passwords.
            LOGGER.log(Level.SEVERE,
                    "Bookstore database initialization failed. Check DB_* environment settings and JDBC availability.");
        }
    }

    private DBUtil() {
    }

    public static Connection getConnection() throws StoreException {
        try {
            if (connection == null || connection.isClosed()) {
                throw new StoreException(ResponseCode.DATABASE_CONNECTION_FAILURE);
            }
            return connection;
        } catch (SQLException exception) {
            throw new StoreException(ResponseCode.DATABASE_CONNECTION_FAILURE);
        }
    }
}

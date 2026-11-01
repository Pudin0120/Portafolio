package com.cbozan.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class LoginDAO {

    private static final String VERIFY_LOGIN_SQL =
            "SELECT id FROM auth WHERE username = ? AND pass = ?";

    public boolean verifyLogin(String username, String password) {
        if (username == null || username.trim().isEmpty()
                || password == null || password.isEmpty()) {
            DB.ERROR_MESSAGE = "Enter both username and password.";
            return false;
        }

        Connection connection = DB.getConnection();
        if (connection == null) {
            return false;
        }

        try (PreparedStatement statement = connection.prepareStatement(VERIFY_LOGIN_SQL)) {
            statement.setString(1, username.trim());
            statement.setString(2, password);

            try (ResultSet result = statement.executeQuery()) {
                boolean authenticated = result.next();
                DB.ERROR_MESSAGE = authenticated ? "" : "Invalid username or password.";
                return authenticated;
            }
        } catch (SQLException exception) {
            DB.ERROR_MESSAGE = "Unable to verify the account. Check the database configuration.";
            System.err.println(DB.ERROR_MESSAGE);
            return false;
        }
    }
}

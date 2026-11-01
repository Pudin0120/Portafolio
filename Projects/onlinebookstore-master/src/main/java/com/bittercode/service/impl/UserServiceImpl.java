package com.bittercode.service.impl;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.servlet.http.HttpSession;

import com.bittercode.constant.ResponseCode;
import com.bittercode.constant.db.UsersDBConstants;
import com.bittercode.model.StoreException;
import com.bittercode.model.User;
import com.bittercode.model.UserRole;
import com.bittercode.service.UserService;
import com.bittercode.util.DBUtil;
import com.bittercode.util.PasswordUtil;

public class UserServiceImpl implements UserService {

    private static final Logger LOGGER = Logger.getLogger(UserServiceImpl.class.getName());

    private static final String REGISTER_USER_QUERY =
            "INSERT INTO " + UsersDBConstants.TABLE_USERS
                    + " (username, password, firstname, lastname, address, phone, mailid, usertype)"
                    + " VALUES (?, ?, ?, ?, ?, ?, ?, ?)";

    private static final String LOGIN_USER_QUERY =
            "SELECT * FROM " + UsersDBConstants.TABLE_USERS
                    + " WHERE " + UsersDBConstants.COLUMN_USERNAME + "=? AND "
                    + UsersDBConstants.COLUMN_USERTYPE + "=?";

    private static final String UPGRADE_PASSWORD_QUERY =
            "UPDATE " + UsersDBConstants.TABLE_USERS
                    + " SET " + UsersDBConstants.COLUMN_PASSWORD + "=? WHERE "
                    + UsersDBConstants.COLUMN_USERNAME + "=? AND "
                    + UsersDBConstants.COLUMN_PASSWORD + "=?";

    @Override
    public User login(UserRole role, String email, String password) throws StoreException {
        if (email == null || email.trim().isEmpty() || password == null) {
            return null;
        }

        UserRole effectiveRole = role == null ? UserRole.CUSTOMER : role;
        String userType = UserRole.SELLER.equals(effectiveRole) ? "1" : "2";
        Connection connection = DBUtil.getConnection();
        String storedPassword;
        User user;

        try (PreparedStatement statement = connection.prepareStatement(LOGIN_USER_QUERY)) {
            statement.setString(1, email.trim());
            statement.setString(2, userType);

            try (ResultSet result = statement.executeQuery()) {
                if (!result.next()) {
                    return null;
                }

                storedPassword = result.getString(UsersDBConstants.COLUMN_PASSWORD);
                user = new User();
                user.setFirstName(result.getString(UsersDBConstants.COLUMN_FIRSTNAME));
                user.setLastName(result.getString(UsersDBConstants.COLUMN_LASTNAME));
                user.setPhone(result.getLong(UsersDBConstants.COLUMN_PHONE));
                user.setEmailId(result.getString(UsersDBConstants.COLUMN_USERNAME));
            }
        } catch (SQLException exception) {
            LOGGER.log(Level.WARNING, "Bookstore account lookup failed.", exception);
            throw new StoreException(ResponseCode.INTERNAL_SERVER_ERROR);
        }

        if (!PasswordUtil.matches(password, storedPassword)) {
            return null;
        }

        // Upgrade legacy plaintext values only after a successful authentication.
        // Short legacy passwords remain readable until the user changes them.
        if (!PasswordUtil.isEncoded(storedPassword) && password.length() >= 8) {
            String upgradedPassword = PasswordUtil.hash(password);
            try (PreparedStatement upgrade = connection.prepareStatement(UPGRADE_PASSWORD_QUERY)) {
                upgrade.setString(1, upgradedPassword);
                upgrade.setString(2, email.trim());
                upgrade.setString(3, storedPassword);
                upgrade.executeUpdate();
            } catch (SQLException exception) {
                LOGGER.log(Level.WARNING, "Legacy account password could not be upgraded.", exception);
            }
        }

        return user;
    }

    @Override
    public boolean isLoggedIn(UserRole role, HttpSession session) {
        UserRole effectiveRole = role == null ? UserRole.CUSTOMER : role;
        return session != null && session.getAttribute(effectiveRole.toString()) != null;
    }

    @Override
    public boolean logout(HttpSession session) {
        if (session == null) {
            return false;
        }
        session.invalidate();
        return true;
    }

    @Override
    public String register(UserRole role, User user) throws StoreException {
        if (user == null || user.getEmailId() == null || user.getEmailId().trim().isEmpty()
                || user.getPassword() == null || user.getPassword().length() < 8
                || user.getFirstName() == null || user.getFirstName().trim().isEmpty()
                || user.getLastName() == null || user.getLastName().trim().isEmpty()
                || user.getAddress() == null || user.getPhone() == null) {
            return "Please provide valid account details and a password of at least 8 characters.";
        }

        String encodedPassword;
        try {
            encodedPassword = PasswordUtil.hash(user.getPassword());
        } catch (IllegalArgumentException exception) {
            return "Password must contain at least 8 characters.";
        }

        UserRole effectiveRole = role == null ? UserRole.CUSTOMER : role;
        int userType = UserRole.SELLER.equals(effectiveRole) ? 1 : 2;
        Connection connection = DBUtil.getConnection();

        try (PreparedStatement statement = connection.prepareStatement(REGISTER_USER_QUERY)) {
            statement.setString(1, user.getEmailId().trim());
            statement.setString(2, encodedPassword);
            statement.setString(3, user.getFirstName().trim());
            statement.setString(4, user.getLastName().trim());
            statement.setString(5, user.getAddress().trim());
            statement.setLong(6, user.getPhone());
            statement.setString(7, user.getEmailId().trim());
            statement.setInt(8, userType);

            return statement.executeUpdate() == 1
                    ? ResponseCode.SUCCESS.name()
                    : ResponseCode.FAILURE.name();
        } catch (SQLException exception) {
            String sqlState = exception.getSQLState();
            if (sqlState != null && sqlState.startsWith("23")) {
                return "An account with this email already exists.";
            }
            LOGGER.log(Level.WARNING, "Bookstore account registration failed.", exception);
            return "Unable to register the account. Please try again.";
        }
    }
}

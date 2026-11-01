package com.shashi.service.impl;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

import com.shashi.beans.TrainException;
import com.shashi.beans.UserBean;
import com.shashi.constant.ResponseCode;
import com.shashi.constant.UserRole;
import com.shashi.service.UserService;
import com.shashi.utility.DBUtil;
import com.shashi.utility.PasswordUtil;

public class UserServiceImpl implements UserService {

    private static final Logger LOGGER = Logger.getLogger(UserServiceImpl.class.getName());
    private final String TABLE_NAME;

    public UserServiceImpl(UserRole userRole) {
        if (userRole == null) {
            userRole = UserRole.CUSTOMER;
        }
        this.TABLE_NAME = userRole.toString();
    }

    @Override
    public UserBean getUserByEmailId(String customerEmailId) throws TrainException {
        String query = "SELECT * FROM " + TABLE_NAME + " WHERE MAILID=?";
        try {
            Connection connection = DBUtil.getConnection();
            try (PreparedStatement statement = connection.prepareStatement(query)) {
                statement.setString(1, customerEmailId);
                try (ResultSet result = statement.executeQuery()) {
                    if (!result.next()) {
                        throw new TrainException(ResponseCode.NO_CONTENT);
                    }

                    UserBean customer = new UserBean();
                    customer.setFName(result.getString("fname"));
                    customer.setLName(result.getString("lname"));
                    customer.setAddr(result.getString("addr"));
                    customer.setMailId(result.getString("mailid"));
                    customer.setPhNo(result.getLong("phno"));
                    return customer;
                }
            }
        } catch (SQLException exception) {
            LOGGER.log(Level.SEVERE, "Unable to load user profile.", exception);
            throw new TrainException(ResponseCode.INTERNAL_SERVER_ERROR);
        }
    }

    @Override
    public List<UserBean> getAllUsers() throws TrainException {
        String query = "SELECT * FROM " + TABLE_NAME;
        List<UserBean> customers = new ArrayList<>();

        try {
            Connection connection = DBUtil.getConnection();
            try (PreparedStatement statement = connection.prepareStatement(query);
                    ResultSet result = statement.executeQuery()) {
                while (result.next()) {
                    UserBean customer = new UserBean();
                    customer.setFName(result.getString("fname"));
                    customer.setLName(result.getString("lname"));
                    customer.setAddr(result.getString("addr"));
                    customer.setMailId(result.getString("mailid"));
                    customer.setPhNo(result.getLong("phno"));
                    customers.add(customer);
                }
            }

            if (customers.isEmpty()) {
                throw new TrainException(ResponseCode.NO_CONTENT);
            }
            return customers;
        } catch (SQLException exception) {
            LOGGER.log(Level.SEVERE, "Unable to load user list.", exception);
            throw new TrainException(ResponseCode.INTERNAL_SERVER_ERROR);
        }
    }

    @Override
    public String updateUser(UserBean customer) {
        String query = "UPDATE " + TABLE_NAME
                + " SET PWORD=?, FNAME=?, LNAME=?, ADDR=?, PHNO=? WHERE MAILID=?";

        try {
            String currentPassword = customer.getPWord();
            String storedPassword = PasswordUtil.isEncoded(currentPassword)
                    ? currentPassword
                    : PasswordUtil.hash(currentPassword);

            Connection connection = DBUtil.getConnection();
            try (PreparedStatement statement = connection.prepareStatement(query)) {
                statement.setString(1, storedPassword);
                statement.setString(2, customer.getFName());
                statement.setString(3, customer.getLName());
                statement.setString(4, customer.getAddr());
                statement.setLong(5, customer.getPhNo());
                statement.setString(6, customer.getMailId());

                int updated = statement.executeUpdate();
                if (updated > 0) {
                    customer.setPWord(storedPassword);
                    return ResponseCode.SUCCESS.toString();
                }
            }
        } catch (SQLException | TrainException | IllegalArgumentException exception) {
            LOGGER.log(Level.WARNING, "Unable to update user account.", exception);
        }
        return ResponseCode.FAILURE.toString();
    }

    @Override
    public String deleteUser(UserBean customer) {
        String query = "DELETE FROM " + TABLE_NAME + " WHERE MAILID=?";
        try {
            Connection connection = DBUtil.getConnection();
            try (PreparedStatement statement = connection.prepareStatement(query)) {
                statement.setString(1, customer.getMailId());
                return statement.executeUpdate() > 0
                        ? ResponseCode.SUCCESS.toString()
                        : ResponseCode.FAILURE.toString();
            }
        } catch (SQLException | TrainException exception) {
            LOGGER.log(Level.WARNING, "Unable to delete user account.", exception);
            return ResponseCode.FAILURE.toString();
        }
    }

    @Override
    public String registerUser(UserBean customer) {
        String query = "INSERT INTO " + TABLE_NAME
                + " (MAILID, PWORD, FNAME, LNAME, ADDR, PHNO) VALUES (?, ?, ?, ?, ?, ?)";

        try {
            String encodedPassword = PasswordUtil.hash(customer.getPWord());
            Connection connection = DBUtil.getConnection();

            try (PreparedStatement statement = connection.prepareStatement(query)) {
                statement.setString(1, customer.getMailId());
                statement.setString(2, encodedPassword);
                statement.setString(3, customer.getFName());
                statement.setString(4, customer.getLName());
                statement.setString(5, customer.getAddr());
                statement.setLong(6, customer.getPhNo());

                if (statement.executeUpdate() > 0) {
                    return ResponseCode.SUCCESS.toString();
                }
            }
        } catch (SQLException | TrainException | IllegalArgumentException exception) {
            LOGGER.log(Level.WARNING, "Unable to register user.", exception);
            String message = exception.getMessage();
            if (message != null && message.toUpperCase().contains("ORA-00001")) {
                return "User is already registered.";
            }
            return ResponseCode.FAILURE.toString();
        }
        return ResponseCode.FAILURE.toString();
    }

    @Override
    public UserBean loginUser(String username, String password) throws TrainException {
        String query = "SELECT * FROM " + TABLE_NAME + " WHERE MAILID=?";
        UserBean customer;
        String storedPassword;

        try {
            Connection connection = DBUtil.getConnection();
            try (PreparedStatement statement = connection.prepareStatement(query)) {
                statement.setString(1, username);
                try (ResultSet result = statement.executeQuery()) {
                    if (!result.next()) {
                        throw new TrainException(ResponseCode.UNAUTHORIZED);
                    }

                    storedPassword = result.getString("pword");
                    customer = new UserBean();
                    customer.setFName(result.getString("fname"));
                    customer.setLName(result.getString("lname"));
                    customer.setAddr(result.getString("addr"));
                    customer.setMailId(result.getString("mailid"));
                    customer.setPhNo(result.getLong("phno"));
                }
            }

            if (!PasswordUtil.matches(password, storedPassword)) {
                throw new TrainException(ResponseCode.UNAUTHORIZED);
            }

            if (!PasswordUtil.isEncoded(storedPassword)) {
                String upgradedPassword = PasswordUtil.hash(password);
                String upgradeQuery = "UPDATE " + TABLE_NAME
                        + " SET PWORD=? WHERE MAILID=? AND PWORD=?";
                try (PreparedStatement upgrade = connection.prepareStatement(upgradeQuery)) {
                    upgrade.setString(1, upgradedPassword);
                    upgrade.setString(2, username);
                    upgrade.setString(3, storedPassword);
                    upgrade.executeUpdate();
                }
                storedPassword = upgradedPassword;
            }

            customer.setPWord(storedPassword);
            return customer;
        } catch (SQLException exception) {
            LOGGER.log(Level.SEVERE, "Unable to authenticate user against the database.", exception);
            throw new TrainException(ResponseCode.INTERNAL_SERVER_ERROR);
        }
    }
}

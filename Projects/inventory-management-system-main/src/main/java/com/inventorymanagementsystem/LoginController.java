package com.inventorymanagementsystem;

import com.inventorymanagementsystem.entity.User;
import com.inventorymanagementsystem.config.Database;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.fxml.Initializable;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.effect.DropShadow;
import javafx.scene.layout.AnchorPane;
import javafx.scene.paint.Color;
import javafx.stage.Stage;
import javafx.stage.StageStyle;

import java.net.URL;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ResourceBundle;

public class LoginController implements Initializable {
    @FXML
    private Label c_logo;

    @FXML
    private Label f_logo;

    @FXML
    private Button login_btn;

    @FXML
    private PasswordField password;

    @FXML
    private TextField username;

    @FXML
    private AnchorPane login_form;


    private Connection connection;

    private Statement statement;

    private PreparedStatement preparedStatement;

    private ResultSet resultSet;
    private double x;
    private double y;


    public void textfieldDesign(){
        if(username.isFocused()){
            username.setStyle("-fx-background-color:#fff;"+"-fx-border-width:2px");
            password.setStyle("-fx-background-color:transparent;"+"-fx-border-width:1px");
        }else if(password.isFocused()){
            username.setStyle("-fx-background-color:transparent;"+"-fx-border-width:1px");
            password.setStyle("-fx-background-color:#fff;"+"-fx-border-width:2px");

        }
    }

    public void dropShowAffect(){
        DropShadow original=new DropShadow(20, Color.valueOf("#ae44a5"));
        f_logo.setEffect(original);
        c_logo.setEffect(original);
    }

    public void onExit(){
        System.exit(0);
    }

    public void login() {
        String enteredUsername = username.getText() == null ? "" : username.getText().trim();
        char[] passwordChars = password.getText() == null
                ? new char[0]
                : password.getText().toCharArray();

        if (enteredUsername.isEmpty() || passwordChars.length == 0) {
            showLoginError("Enter your username and password.");
            java.util.Arrays.fill(passwordChars, (char) 0);
            password.clear();
            return;
        }

        String enteredPassword = new String(passwordChars);
        try (Connection dbConnection = Database.getInstance().connectDB()) {
            if (dbConnection == null) {
                showLoginError("Database connection unavailable. Check DB_URL, DB_USERNAME, and DB_PASSWORD.");
                return;
            }

            String storedPassword = null;
            try (PreparedStatement query = dbConnection.prepareStatement(
                    "SELECT password FROM users WHERE username = ?")) {
                query.setString(1, enteredUsername);
                try (ResultSet result = query.executeQuery()) {
                    if (result.next()) {
                        storedPassword = result.getString("password");
                    }
                }
            }

            if (!com.inventorymanagementsystem.security.PasswordUtil.matches(
                    enteredPassword, storedPassword)) {
                showLoginError("Invalid username or password.");
                return;
            }

            if (!com.inventorymanagementsystem.security.PasswordUtil.isEncoded(storedPassword)
                    && enteredPassword.length() >= 8) {
                String upgradedHash = com.inventorymanagementsystem.security.PasswordUtil.hash(enteredPassword);
                try (PreparedStatement upgrade = dbConnection.prepareStatement(
                        "UPDATE users SET password = ? WHERE username = ? AND password = ?")) {
                    upgrade.setString(1, upgradedHash);
                    upgrade.setString(2, enteredUsername);
                    upgrade.setString(3, storedPassword);
                    upgrade.executeUpdate();
                }
            }

            User.name = enteredUsername;
            Alert alert = new Alert(Alert.AlertType.INFORMATION);
            alert.setTitle("Success Message");
            alert.setHeaderText(null);
            alert.setContentText("Login Successful!");
            alert.showAndWait();

            login_btn.getScene().getWindow().hide();
            Parent root = FXMLLoader.load(getClass().getResource("dashboard.fxml"));
            Scene scene = new Scene(root);
            Stage stage = new Stage();

            root.setOnMousePressed(event -> {
                x = event.getSceneX();
                y = event.getSceneY();
            });
            root.setOnMouseDragged(event -> {
                stage.setX(event.getScreenX() - x);
                stage.setY(event.getScreenY() - y);
            });
            stage.initStyle(StageStyle.TRANSPARENT);
            stage.setScene(scene);
            stage.show();
        } catch (Exception exception) {
            showLoginError("Unable to sign in. Check the database and try again.");
        } finally {
            java.util.Arrays.fill(passwordChars, (char) 0);
            password.clear();
        }
    }

    private void showLoginError(String message) {
        Alert alert = new Alert(Alert.AlertType.ERROR);
        alert.setTitle("Login");
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.showAndWait();
    }

    @Override
    public void initialize(URL url, ResourceBundle resourceBundle) {
        dropShowAffect();
    }
}
package com.shashi.servlets;

import java.io.IOException;
import java.io.PrintWriter;

import javax.servlet.RequestDispatcher;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.shashi.beans.TrainException;
import com.shashi.beans.UserBean;
import com.shashi.constant.UserRole;
import com.shashi.service.UserService;
import com.shashi.service.impl.UserServiceImpl;
import com.shashi.utility.PasswordUtil;
import com.shashi.utility.TrainUtil;

@SuppressWarnings("serial")
@WebServlet("/changeuserpwd")
public class ChangeUserPwd extends HttpServlet {

    private final UserService userService = new UserServiceImpl(UserRole.CUSTOMER);

    @Override
    protected void doPost(
            HttpServletRequest request,
            HttpServletResponse response) throws IOException, ServletException {

        response.setContentType("text/html");
        PrintWriter writer = response.getWriter();
        UserBean currentUser = TrainUtil.getCurrentCustomer(request);

        try {
            String username = request.getParameter("username");
            String oldPassword = request.getParameter("oldpassword");
            String newPassword = request.getParameter("newpassword");

            if (currentUser == null || username == null
                    || !currentUser.getMailId().equalsIgnoreCase(username.trim())) {
                showMessage(request, response, writer, "Invalid user account.");
                return;
            }

            if (!PasswordUtil.matches(oldPassword, currentUser.getPWord())) {
                showMessage(request, response, writer, "The current password is incorrect.");
                return;
            }

            if (newPassword == null || newPassword.length() < 8) {
                showMessage(request, response, writer, "The new password must contain at least 8 characters.");
                return;
            }

            currentUser.setPWord(newPassword);
            String result = userService.updateUser(currentUser);

            if (ResponseCode.SUCCESS.toString().equalsIgnoreCase(result)) {
                TrainUtil.logout(response);
                request.getSession().invalidate();
                showMessage(request, response, writer,
                        "Your password has been updated. Please sign in again.");
                return;
            }

            showMessage(request, response, writer, "The password could not be updated.");
        } catch (Exception exception) {
            throw new TrainException(422, this.getClass().getName() + "_FAILED",
                    "Unable to update the password. Please try again.");
        }
    }

    private void showMessage(
            HttpServletRequest request,
            HttpServletResponse response,
            PrintWriter writer,
            String message) throws ServletException, IOException {

        RequestDispatcher dispatcher = request.getRequestDispatcher("UserHome.html");
        dispatcher.include(request, response);
        writer.println("<div class='tab'>" + message + "</div>");
    }
}

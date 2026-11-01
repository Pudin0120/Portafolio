package servlets;

import java.io.IOException;
import java.io.PrintWriter;

import javax.servlet.RequestDispatcher;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.bittercode.constant.BookStoreConstants;
import com.bittercode.constant.ResponseCode;
import com.bittercode.constant.db.UsersDBConstants;
import com.bittercode.model.User;
import com.bittercode.model.UserRole;
import com.bittercode.service.UserService;
import com.bittercode.service.impl.UserServiceImpl;
import com.bittercode.util.StoreUtil;

public class CustomerRegisterServlet extends HttpServlet {

    private final UserService userService = new UserServiceImpl();

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws IOException, ServletException {
        request.setCharacterEncoding("UTF-8");
        response.setContentType(BookStoreConstants.CONTENT_TYPE_TEXT_HTML + "; charset=UTF-8");
        PrintWriter writer = response.getWriter();

        String password = request.getParameter(UsersDBConstants.COLUMN_PASSWORD);
        String firstName = request.getParameter(UsersDBConstants.COLUMN_FIRSTNAME);
        String lastName = request.getParameter(UsersDBConstants.COLUMN_LASTNAME);
        String address = request.getParameter(UsersDBConstants.COLUMN_ADDRESS);
        String phoneValue = request.getParameter(UsersDBConstants.COLUMN_PHONE);
        String email = request.getParameter(UsersDBConstants.COLUMN_MAILID);

        if (phoneValue == null || !phoneValue.matches("\\d{7,15}")) {
            showRegistrationError(request, response, writer, "Enter a valid phone number.");
            return;
        }

        User user = new User();
        user.setEmailId(email);
        user.setFirstName(firstName);
        user.setLastName(lastName);
        user.setPassword(password);
        user.setAddress(address);
        try {
            user.setPhone(Long.parseLong(phoneValue));
            String result = userService.register(UserRole.CUSTOMER, user);
            if (ResponseCode.SUCCESS.name().equalsIgnoreCase(result)) {
                RequestDispatcher dispatcher = request.getRequestDispatcher("CustomerLogin.html");
                dispatcher.include(request, response);
                writer.println("<table class=\"tab\"><tr><td>Account registered successfully.</td></tr></table>");
            } else {
                showRegistrationError(request, response, writer, result);
            }
        } catch (NumberFormatException exception) {
            showRegistrationError(request, response, writer, "Enter a valid phone number.");
        }
    }

    private void showRegistrationError(
            HttpServletRequest request,
            HttpServletResponse response,
            PrintWriter writer,
            String message) throws ServletException, IOException {
        RequestDispatcher dispatcher = request.getRequestDispatcher("CustomerRegister.html");
        dispatcher.include(request, response);
        writer.println("<table class=\"tab\"><tr><td>"
                + StoreUtil.escapeHtml(message)
                + "</td></tr></table>");
    }
}

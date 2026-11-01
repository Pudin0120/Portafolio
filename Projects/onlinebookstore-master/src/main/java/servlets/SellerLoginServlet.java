package servlets;

import java.io.IOException;
import java.io.PrintWriter;

import javax.servlet.RequestDispatcher;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import com.bittercode.constant.BookStoreConstants;
import com.bittercode.constant.db.UsersDBConstants;
import com.bittercode.model.User;
import com.bittercode.model.UserRole;
import com.bittercode.service.UserService;
import com.bittercode.service.impl.UserServiceImpl;
import com.bittercode.util.StoreUtil;

public class SellerLoginServlet extends HttpServlet {

    private final UserService userService = new UserServiceImpl();

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws IOException, ServletException {
        request.setCharacterEncoding("UTF-8");
        response.setContentType(BookStoreConstants.CONTENT_TYPE_TEXT_HTML + "; charset=UTF-8");
        PrintWriter writer = response.getWriter();

        try {
            String username = request.getParameter(UsersDBConstants.COLUMN_USERNAME);
            String password = request.getParameter(UsersDBConstants.COLUMN_PASSWORD);
            User user = userService.login(UserRole.SELLER, username, password);

            if (user != null) {
                HttpSession previousSession = request.getSession(false);
                if (previousSession != null) {
                    previousSession.invalidate();
                }
                HttpSession authenticatedSession = request.getSession(true);
                authenticatedSession.setAttribute(UserRole.SELLER.toString(), user.getEmailId());

                RequestDispatcher dispatcher = request.getRequestDispatcher("SellerHome.html");
                dispatcher.include(request, response);
                writer.println("<div id=\"topmid\"><h1>Welcome to Online <br>Book Store</h1></div>");
                writer.println("<br><table class=\"tab\"><tr><td><p>Welcome "
                        + StoreUtil.escapeHtml(user.getFirstName())
                        + ", Happy Learning !!</p></td></tr></table>");
            } else {
                RequestDispatcher dispatcher = request.getRequestDispatcher("SellerLogin.html");
                dispatcher.include(request, response);
                writer.println("<div class=\"tab\">Incorrect username or password.</div>");
            }
        } catch (Exception exception) {
            throw new ServletException("Unable to complete seller login.", exception);
        }
    }
}

<%--
  Created by IntelliJ IDEA.
  User: Lenovo
  Date: 2017/10/25
  Time: 12:52
  To change this template use File | Settings | File Templates.
--%>
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<html>
  <head>
    <title></title>
  </head>
  <body>
    <form action="${pageContext.request.contextPath}/RegistServlet" method="post">
      <table width="500" border="1" align="center">
        <tr>
          <td></td>
          <td><input type="text" name="username"/></td>
        </tr>
        <tr>
          <td></td>
          <td><input type="password" name="password"/></td>
        </tr>
        <tr>
          <td></td>
          <td><input type="email" name="email" /></td>
        </tr>
        <tr>
          <td colspan="2"><input type="submit" value=""/></td>
        </tr>
      </table>
    </form>
  </body>
</html>

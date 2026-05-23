<%@ page language="java" import="java.util.*" pageEncoding="UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/fmt" prefix="fmt"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/functions" prefix="fn"%>
<%
	String root = request.getContextPath();
	pageContext.setAttribute("root", root);
	String basePath = request.getScheme() + "://" + request.getServerName() + ":" + request.getServerPort() + root + "/";
%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
	<head>
		<base href="<%=basePath%>">
		<title></title>
		<meta http-equiv="pragma" content="no-cache">
		<meta http-equiv="cache-control" content="no-cache">
		<meta http-equiv="expires" content="0">
		<meta http-equiv="keywords" content="keyword1,keyword2,keyword3">
		<meta http-equiv="description" content="This is my page">
		<script type="text/javascript" src="${root}/js/jquery.js"></script>
		<script type="text/javascript">
		function query() {
			var form = $("#queryForm");
			form.attr("action", "${root}/tbMessageTypeAction!conditionSelectAll.action");
			form.submit();
		}

		function deleteAll() {
			if($("input[name^=list][name$=messageTypeId]:checked").length == 0) {
				alert("");
			} else {
				var form = $("#queryForm");
				form.attr("action", "${root}/tbMessageTypeAction!deleteAll.action");
				form.submit();
			}
		}

		function selectAll(obj) {
			$("input[name^=list][name$=messageTypeId]").attr("checked", obj.checked);
		}
		</script>
	</head>
	<body>
	<form id="queryForm" action="" method="post">
	<table border="1">
		<tr>
			<td>messageTypeId</td>
			<td><input type="text" id="tbMessageType_messageTypeId" name="tbMessageType.messageTypeId" value="${tbMessageType.messageTypeId}" /></td>
		</tr>
		<tr>
			<td>messageTypeName</td>
			<td><input type="text" id="tbMessageType_messageTypeName" name="tbMessageType.messageTypeName" value="${tbMessageType.messageTypeName}" /></td>
		</tr>
  		<tr>
  			<td colspan="2">
  				<input type="button" value="" onclick="query()" />
  				<input type="button" value="" onclick="deleteAll()" />
  			</td>
  		</tr>
	</table>

	<c:if test="${list == null}">
	
	</c:if>

	<c:if test="${list != null && fn:length(list) == 0}">
	
	</c:if>

	<c:if test="${list != null && fn:length(list) > 0}">
	<table border="1">
		<tr>
			<td><input type="checkbox" onclick="selectAll(this)" /></td>
			<td></td>
			<td>messageTypeId</td>
			<td>messageTypeName</td>
			<td></td>
			<td></td>
		</tr>
		<c:forEach var="tbMessageType" items="${list}" varStatus="i">
		<tr>
			<td><input type="checkbox" name="list[${i.index}].messageTypeId" value="${tbMessageType.messageTypeId}" /></td>
			<td>${i.index + 1}</td>
			<td>${tbMessageType.messageTypeId}</td>
			<td>${tbMessageType.messageTypeName}</td>
			<td><a href="${root}/tbMessageTypeAction!delete.action?tbMessageType.messageTypeId=${tbMessageType.messageTypeId}"></a></td>
			<td><a href="${root}/tbMessageTypeAction!initUpdate.action?tbMessageType.messageTypeId=${tbMessageType.messageTypeId}"></a></td>
		</tr>
		</c:forEach>
	</table>
	</c:if>
	</form>
	</body>
</html>
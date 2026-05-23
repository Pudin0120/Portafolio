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
			form.attr("action", "${root}/bgInfoAction!conditionSelectAll.action");
			form.submit();
		}

		function deleteAll() {
			if($("input[name^=list][name$=infoId]:checked").length == 0) {
				alert("");
			} else {
				var form = $("#queryForm");
				form.attr("action", "${root}/bgInfoAction!deleteAll.action");
				form.submit();
			}
		}

		function selectAll(obj) {
			$("input[name^=list][name$=infoId]").attr("checked", obj.checked);
		}
		</script>
	</head>
	<body>
	<form id="queryForm" action="" method="post">
	<table border="1">
		<tr>
			<td>infoId</td>
			<td><input type="text" id="bgInfo_infoId" name="bgInfo.infoId" value="${bgInfo.infoId}" /></td>
		</tr>
		<tr>
			<td>adminId</td>
			<td><input type="text" id="bgInfo_adminId" name="bgInfo.adminId" value="${bgInfo.adminId}" /></td>
		</tr>
		<tr>
			<td>infoTypeId</td>
			<td><input type="text" id="bgInfo_infoTypeId" name="bgInfo.infoTypeId" value="${bgInfo.infoTypeId}" /></td>
		</tr>
		<tr>
			<td>infoCon</td>
			<td><input type="text" id="bgInfo_infoCon" name="bgInfo.infoCon" value="${bgInfo.infoCon}" /></td>
		</tr>
		<tr>
			<td>infoTitle</td>
			<td><input type="text" id="bgInfo_infoTitle" name="bgInfo.infoTitle" value="${bgInfo.infoTitle}" /></td>
		</tr>
		<tr>
			<td>infoDate</td>
			<td><input type="text" id="bgInfo_infoDateBegin" name="bgInfo.infoDateBegin" value="<fmt:formatDate value="${bgInfo.infoDateBegin}" pattern="yyyy-MM-dd HH:mm:ss" />" /> <input type="text" id="bgInfo_infoDateEnd" name="bgInfo.infoDateEnd" value="<fmt:formatDate value="${bgInfo.infoDateEnd}" pattern="yyyy-MM-dd HH:mm:ss" />" /></td>
		</tr>
		<tr>
			<td>infoHits</td>
			<td><input type="text" id="bgInfo_infoHits" name="bgInfo.infoHits" value="${bgInfo.infoHits}" /></td>
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
			<td>infoId</td>
			<td>adminId</td>
			<td>infoTypeId</td>
			<td>infoCon</td>
			<td>infoTitle</td>
			<td>infoDate</td>
			<td>infoHits</td>
			<td></td>
			<td></td>
		</tr>
		<c:forEach var="bgInfo" items="${list}" varStatus="i">
		<tr>
			<td><input type="checkbox" name="list[${i.index}].infoId" value="${bgInfo.infoId}" /></td>
			<td>${i.index + 1}</td>
			<td>${bgInfo.infoId}</td>
			<td>${bgInfo.adminId}</td>
			<td>${bgInfo.infoTypeId}</td>
			<td>${bgInfo.infoCon}</td>
			<td>${bgInfo.infoTitle}</td>
			<td><fmt:formatDate value="${bgInfo.infoDate}" pattern="yyyy-MM-dd HH:mm:ss" /></td>
			<td>${bgInfo.infoHits}</td>
			<td><a href="${root}/bgInfoAction!delete.action?bgInfo.infoId=${bgInfo.infoId}"></a></td>
			<td><a href="${root}/bgInfoAction!initUpdate.action?bgInfo.infoId=${bgInfo.infoId}"></a></td>
		</tr>
		</c:forEach>
	</table>
	</c:if>
	</form>
	</body>
</html>
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
			form.attr("action", "${root}/bgInfoimgAction!conditionSelectAll.action");
			form.submit();
		}

		function deleteAll() {
			if($("input[name^=list][name$=infoImgId]:checked").length == 0) {
				alert("");
			} else {
				var form = $("#queryForm");
				form.attr("action", "${root}/bgInfoimgAction!deleteAll.action");
				form.submit();
			}
		}

		function selectAll(obj) {
			$("input[name^=list][name$=infoImgId]").attr("checked", obj.checked);
		}
		</script>
	</head>
	<body>
	<form id="queryForm" action="" method="post">
	<table border="1">
		<tr>
			<td>infoImgId</td>
			<td><input type="text" id="bgInfoimg_infoImgId" name="bgInfoimg.infoImgId" value="${bgInfoimg.infoImgId}" /></td>
		</tr>
		<tr>
			<td>infoId</td>
			<td><input type="text" id="bgInfoimg_infoId" name="bgInfoimg.infoId" value="${bgInfoimg.infoId}" /></td>
		</tr>
		<tr>
			<td>infoImgName</td>
			<td><input type="text" id="bgInfoimg_infoImgName" name="bgInfoimg.infoImgName" value="${bgInfoimg.infoImgName}" /></td>
		</tr>
		<tr>
			<td>infoImgPath</td>
			<td><input type="text" id="bgInfoimg_infoImgPath" name="bgInfoimg.infoImgPath" value="${bgInfoimg.infoImgPath}" /></td>
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
			<td>infoImgId</td>
			<td>infoId</td>
			<td>infoImgName</td>
			<td>infoImgPath</td>
			<td></td>
			<td></td>
		</tr>
		<c:forEach var="bgInfoimg" items="${list}" varStatus="i">
		<tr>
			<td><input type="checkbox" name="list[${i.index}].infoImgId" value="${bgInfoimg.infoImgId}" /></td>
			<td>${i.index + 1}</td>
			<td>${bgInfoimg.infoImgId}</td>
			<td>${bgInfoimg.infoId}</td>
			<td>${bgInfoimg.infoImgName}</td>
			<td>${bgInfoimg.infoImgPath}</td>
			<td><a href="${root}/bgInfoimgAction!delete.action?bgInfoimg.infoImgId=${bgInfoimg.infoImgId}"></a></td>
			<td><a href="${root}/bgInfoimgAction!initUpdate.action?bgInfoimg.infoImgId=${bgInfoimg.infoImgId}"></a></td>
		</tr>
		</c:forEach>
	</table>
	</c:if>
	</form>
	</body>
</html>
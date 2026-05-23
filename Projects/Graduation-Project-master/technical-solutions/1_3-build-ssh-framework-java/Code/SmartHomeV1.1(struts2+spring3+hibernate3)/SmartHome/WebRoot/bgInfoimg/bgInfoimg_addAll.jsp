<%@ page language="java" import="java.util.*" pageEncoding="UTF-8"%>
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
		var listIndex = -1;
		function addRow() {
			listIndex = listIndex + 1;
			var tab = $("#tab");
			var newRow = $("<tr></tr>");
			newRow.append($("<td></td>").append("<input type='text' id='list_"+ listIndex +"_infoId' name='list[" + listIndex + "].infoId' index='"+ listIndex +"' />"));
			newRow.append($("<td></td>").append("<input type='text' id='list_"+ listIndex +"_infoImgName' name='list[" + listIndex + "].infoImgName' index='"+ listIndex +"' />"));
			newRow.append($("<td></td>").append("<input type='text' id='list_"+ listIndex +"_infoImgPath' name='list[" + listIndex + "].infoImgPath' index='"+ listIndex +"' />"));
			newRow.append($("<td></td>").append("<input type='button' value='' onclick='deleteRow(this)' />"));
			tab.append(newRow);
		}

		function deleteRow(obj) {
			if($("#tab tr").length == 2) {
				alert("");
			} else {
				$(obj).parent().parent().remove();
			}
		}

		$(function() {
			addRow();
		});
	
		function checkForm() {
			return true;
		}
	</script>
	</head>
	<body>
	<form action="${root}/bgInfoimgAction!addAll.action" method="post" onsubmit="return checkForm()">
	<input type="button" value="" onclick="addRow()" />
	<input type="submit" value="" onclick="checkForm()" />
	<table id="tab" border="1">
		<tr>
			<td>infoId</td>
			<td>infoImgName</td>
			<td>infoImgPath</td>
			<td></td>
		</tr>
	</table>
	</form>
	</body>
</html>
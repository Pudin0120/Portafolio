<%@ page language="java" import="java.util.*" pageEncoding="UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/functions" prefix="fn"%>
<%
	String root = request.getContextPath();
	pageContext.setAttribute("root", root);
%>
<input type="hidden" name="pageModel.currentPage" id="currentPage" />
<c:if test="${pageModel.list != null && fn:length(pageModel.list) > 0}">
${pageModel.currentPage}/${pageModel.totalPages}
<c:if test="${pageModel.hasPreviousPage}">
<a href="#" onclick="return goPage(1)"></a>  
<a href="#" onclick="return goPage(${pageModel.previousPage})"></a>
</c:if>
<c:if test="${!pageModel.hasPreviousPage}">
  
</c:if>

<c:if test="${pageModel.hasNextPage}">
<a href="#" onclick="return goPage(${pageModel.nextPage})"></a>  
<a href="#" onclick="return goPage(${pageModel.totalPages})"></a>  
</c:if>
<c:if test="${!pageModel.hasNextPage}">
    
</c:if>
${pageModel.pageSize}  
${pageModel.totalRows}  
<input type="text" id="gotoPageNum" style="width: 30px;" />  
<input type="button" value="GO" onclick="gotoPage()" />
<script language="JavaScript">
// 
function goPage(pageNum) {
	var page = document.getElementById("currentPage");
	page.value = pageNum;
	if(page.value.length > 0) {
		var form = document.pageQueryForm;
		form.submit();
	}
	return false;
}
// 
function gotoPage() {
	var page = document.getElementById("gotoPageNum").value;
	var gotoPageNum = parseInt(page);
	var totalPagesNum = parseInt("${pageModel.totalPages}");
	var currentPage = parseInt("${pageModel.currentPage}");
	if(gotoPageNum > 0) {
		if(gotoPageNum > totalPagesNum) {
			alert("");
		} else if(gotoPageNum == currentPage) {
			alert("" + gotoPageNum + "");
		} else {
			goPage(gotoPageNum);
		}
	} else {
		alert("");
	}
}
</script>
</c:if>
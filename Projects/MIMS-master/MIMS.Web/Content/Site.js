function addTab(title, url) {
	if ($('#tabs').tabs('exists', title)) {
		$('#tabs').tabs('select', title);
	} else {
		var content = '<iframe scrolling="no" frameborder="0"  src="' + url + '" style="width:100%;height:99%;margin:0;padding:0"></iframe>';
		$('#tabs').tabs('add', {
			title: title,
			content: content,
			closable: true
		});
	}
}



/* Ajax 
--------------------------------------------------*/
function getAjax(url, parm, callBack) {
	$.ajax({
		type: 'post',
		dataType: "text",
		url: url,
		data: parm,
		cache: false,
		async: false,
		success: function (msg) {
			callBack(msg);
		}
	});
}

//
function GetWebControls(element) {
	var reVal = "";
	$(element).find('input,select,textarea').each(function (r) {
		var id = $(this).attr('id');
		var value = $(this).val();
		var type = $(this).attr('type');
		switch (type) {
			case "checkbox":
				if ($(this).is(':checked')) {
					reVal += '"' + id + '"' + ':' + '"1",';
				} else {
					reVal += '"' + id + '"' + ':' + '"0",';
				}
				break;
			default:
				reVal += '"' + id + '"' + ':' + '"' + $.trim(value) + '",';
				break;
		}
	});
	/* 
	\\n
	*/
	reVal = reVal.replace(/\n/g, " ");
	reVal = reVal.substr(0, reVal.length - 1);
	return jQuery.parseJSON('{' + reVal + '}');
}
//
function SetWebControls(data) {
	for (var key in data) {
		var id = $('#' + key);
		var value = $.trim(data[key]).replace("&nbsp;", "");
		var type = id.attr('type');
		switch (type) {
			case "checkbox":
				if (value == 1) {
					id.attr("checked", 'checked');
				} else {
					id.removeAttr("checked");
				}
				break;
			default:
				id.val(value);
				break;
		}
	}
}
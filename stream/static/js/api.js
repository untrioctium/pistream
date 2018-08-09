function json_query( method, data, success )
{
	data.method = method;
	$.getJSON( "/json/", data, function( data ) {
		if( !("error" in data) ) success(data);
		else console.log( "JSON error: " + data.error )
	});
}

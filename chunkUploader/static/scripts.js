$(document).ready(function() {

    var total_steps = 0;
    var chunk_size = 10000000;
    var final_filename = "";
    var spark = new SparkMD5.ArrayBuffer();
    var backend_url = "";
    backend_url = "http://192.168.10.70:9999/api/services/vmimage";

    function pad(num, size) {
	var s = num+"";
	while (s.length < size) s = "0" + s;
	return s;
    }

    function readBlob(file, uuid, step, opt_startByte, opt_stopByte) {
	var start = parseInt(opt_startByte) || 0;
	var stop = parseInt(opt_stopByte) || file.size - 1;
	var reader = new FileReader();
	reader.onloadend = function(evt) {
	    if (evt.target.readyState == FileReader.DONE) {
		var formData = new FormData();
		file2send = new File([evt.target.result], uuid+'_'+pad(step,6));
		spark.append(evt.target.result);
		formData.append('file', file2send);
		// Subimos el trozo que toque segun step
		$.ajax({
		    url: backend_url+"/chunked",
		    type: "post",
		    data: formData,
		    processData: false,
		    contentType: false,
		    success: function(){
			step = step+1;
			if ( step < total_steps ) {
			    var start = step*chunk_size;
			    var stop = (step+1)*chunk_size-1;
			    // Subimos el siguiente trozo
			    readBlob(file,uuid,step,start,stop);
			}
			$("#progress").html('Uploaded file parts: '+step+' / '+total_steps+' completed');
			$("#file_upload_result").html('submitted successfully');
			if ( step === total_steps ) {
			    // Si step === total_steps hemos acabado y lanzamos el post final
			    //       con los datos para que el backend recomponga y verifique
			    $("#end").html('Successfully uploaded <strong>'+
					   final_filename+'</strong> with id=<i>'+
					   uuid+'</i> in <strong>'+total_steps+'</strong> steps');
			    var md5sum = spark.end();
			    $("#md5").html('<strong style="color:olive">md5sum</strong>: '+md5sum);
			    $.ajax({
				url: backend_url+"/unchunked",
				type: "post",
				contentType: "application/json",
				data: JSON.stringify({ "filename": final_filename,
						       "uuid": uuid,
						       "md5sum": md5sum
						     }),
				dataType: "json",
				success: function() {
				    $.ajax({
					url: backend_url+"/upload",
					type: "post",
					contentType: "application/json",
					data: JSON.stringify({ "filename": final_filename }),
					dataType: "json",
					success: function() {
					    $("#upload").html("<h3 style=\"color:olive\">"+final_filename+" database upload performed</h3>");
					}
				    });
				},
			    	error: function() {
				    $("#upload").html("<h3 style=\"color:red\">md5sums don't match!!!</h3>");
				}
			    })
			}
		    },
		    error:function(){
			$("#progress").html('There was an error while uploading');
		    }
		});
	    }
	};
	var blob = file.slice(start, stop + 1);
	reader.readAsArrayBuffer(blob);
    }

    function guid() {
	function s4() {
	    return Math.floor((1 + Math.random()) * 0x10000)
		.toString(16)
		.substring(1);
	}
	return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
	    s4() + '-' + s4() + s4() + s4();
    }

    function onFileSelected(e) {
        var files = e.target.files;
	var i = 0;
	$("#progress").html('');
	$("#end").html('');
	$("#md5").html('');
	$("#upload").html('');
	
        file = files[i].name;
	final_filename = file;
	var steps = files[i].size/chunk_size;
	total_steps = Math.floor(steps)+1;
	var uuid = guid();
	j = 0;
	var start = j*chunk_size;
	var stop = (j+1)*chunk_size-1;
	$("#init").html('Starting the upload in '+total_steps+' parts');
	// Llamada para subir la primera parte (el resto sube recursivamente
	//    en el on_success del post de jquery para que vaya secuencial)
	readBlob(files[i], uuid, j, start, stop);
    }

    var file_input = $('#file_input');
    file_input.on("change", onFileSelected);

});

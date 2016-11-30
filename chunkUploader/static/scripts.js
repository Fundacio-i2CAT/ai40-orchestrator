$(document).ready(function() {
    
    var total_steps = 0;
    var chunk_size = 100000000;
    var final_filename = "";
    var spark = new SparkMD5.ArrayBuffer();
    
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
		$.ajax({
		    url: "upload",
		    // url: "http://192.168.10.70:9999/api/services/vmimage/local",
		    type: "post",
		    data: formData,
		    processData: false,
		    contentType: false,
		    success: function(){
			step = step+1;
			if ( step < total_steps ) {
			    var start = step*chunk_size;
			    var stop = (step+1)*chunk_size-1;
			    readBlob(file,uuid,step,start,stop);
			}
			$("#progress").html('Uploaded file parts: '+step+' / '+total_steps+' completed');
			$("#file_upload_result").html('submitted successfully');
			if ( step === total_steps ) {
			    $("#end").html('Successfully uploaded '+
						final_filename+' with id='+
						uuid+' in '+total_steps+' steps');
			    $("#md5").html('<strong>md5sum</strong>: '+spark.end());
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
        file = files[i].name;
	final_filename = file;
	var steps = files[i].size/chunk_size;
	total_steps = Math.floor(steps)+1;
	var uuid = guid();
	j = 0;
	var start = j*chunk_size;
	var stop = (j+1)*chunk_size-1;
	$("#init").html('Starting the upload in '+total_steps+' parts');
	readBlob(files[i], uuid, j, start, stop);
    }

    var file_input = $('#file_input');
    file_input.on("change", onFileSelected);

});

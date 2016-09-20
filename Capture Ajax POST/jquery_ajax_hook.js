function SEND(data){
    var http = new XMLHttpRequest();
    var url = "http://127.0.0.1:9090/capture?data="+window.btoa(data);
    http.open("GET", url, true);
    http.onreadystatechange = function() {
        if(http.readyState == 4 && http.status == 200) {
            console.log(http.responseText);
        }
    }
    http.send();
}

$(document).ajaxComplete(function myErrorHandler(event, xhr, ajaxOptions, thrownError) {
  if (ajaxOptions.type === "POST"){
      var url = '';
      if (String(ajaxOptions.url).indexOf("://") === -1){
          url = window.location.href.replace(location.hash, "");
          if (ajaxOptions.url.startsWith('/')){
             url = url.substring(0, url.lastIndexOf("/")) + ajaxOptions.url;
          }
          else{
          url = url.substring(0, url.lastIndexOf("/")) + "/" + ajaxOptions.url;
          }
      }
      else{
          url = ajaxOptions.url;
      }
      console.log("POST "+url + " DATA: "+ ajaxOptions.data);
      SEND('{"method": "POST", "url": "'+ url+ '", "body": "'+ajaxOptions.data+'"}');
  }
});
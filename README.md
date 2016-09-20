# WebGoat Priming Script

Script for Priming WebGoat with IMMUNIO Installed

## Capture AJAX POST
```
npm install express
node server.js
```

## Priming WebGoat

```
pip install -r requirements.txt
python prime.py
```

## How To

* Run the node application `server.js`
* Inject `http://localhost:9090/script.js` to the page where you need to intercept Ajax POST calls using any browser addon. 
For Chrome, you can use: [Script Injector](https://chrome.google.com/webstore/detail/script-injector/fddnddnolonllcgfbenaloajnbhebmob)
* The captured AJAX POSTs are saved in `captured_post_reqs.txt`.
* Copy the `captured_post_reqs.txt` to the directory that contains `prime.py` and rename it as `prime.json`
* Run `prime.py`



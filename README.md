# proxy_mod_req

## run the proxy server
```
python proxy.py
```

## proxify the requests
```
sqlmap -r <request_file> --proxy="http://127.0.0.1:9090" -vv
```
Note: do not add `--force-ssl` as it will force the request to be https.
the proxy server will only accept HTTP, and will upgrade the connection to HTTPS.
if the endpoint only accept HTTP, then modify line 47 so it will not automatically upgrade the connection.

## modify as you need
modify the lines 66 and 67 pointing to your upsteam proxy (e.g. burpsuite)

## flow
proxy.py (9090) (http) -> burpsuite proxy (8081) (http/https) -> endpoint
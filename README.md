# nate-tls-public

## Quick Python Install
```
git clone https://github.com/natewong1313/nate-tls-public/
```
```
cd nate-tls-public
```
```
pip install -r requirements.txt
```

## Usage
The Python api is pretty much the same as the requests api. Only main difference is that you can specify a custom ClientHello when creating a session object. See [here](https://github.com/natewong1313/nate-tls-public/blob/master/test.py) for an example file.
```py
from client import Session, ClientHello
session = Session(client_hello = ClientHello.chrome_83)
```


## Tips
Make sure to include the main.so and main.h files when packaging with pyarmor or pyinstaller. Use the --add-data command

If you want the content length to be in a specific place, include it in your headers dict. Whatever value you put in quotes will be overwritten with a calculated length but the header will remain ordered.


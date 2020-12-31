from client import Session

headers = {
    "Host": "eggrolldev.herokuapp.com",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9"
}

proxies = {
    "http": "http://localhost:8888",
    "https": "https://localhost:8888"
}

data = {
	"productQuantity": 1,
	"productId": "22451497"
}

session = Session(proxies = proxies)
r = session.get("https://eggrolldev.herokuapp.com/", headers = headers)

print(r.status_code)
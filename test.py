from client import Session

headers = {
    "content-length": "44",
    "x-csrf-token": "c3b165cb-5554-420a-84ad-cc4d76de570d",
    "x-fl-productid": "22451497",
    "content-type": "application/json",
    "accept": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "x-fl-request-id": "85618e30-3524-11eb-b4ed-07b86e3b0278",
    "origin": "https://www.footlocker.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.footlocker.com/product/nike-air-force-1-low-mens/24300657.html",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9"
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
r = session.post("https://www.footlocker.com/api/users/carts/current/entries?timestamp=0", json = data, headers = headers)

print(r.status_code)
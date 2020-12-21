from ctypes import *
from urllib.parse import urlparse, urlencode
import ujson
import os

lib = cdll.LoadLibrary("./main.so") if os.name == "nt" else cdll.LoadLibrary("./main-mac.so")

class GoString(Structure):
    _fields_ = [("p", c_char_p), ("n", c_longlong)]

lib.MakeReq.argtypes = [GoString, GoString, GoString, GoString, GoString, GoString, GoString]
lib.MakeReq.restype = c_char_p

class ClientHello(object):
    chrome_83 = "chrome83"
    chrome_72 = "chrome72"
    ios_12 = "ios12"
    ios_11 = "ios11"
    firefox_65 = "firefox65"
    firefox_63 = "firefox63"

class Session:
    def __init__(self, proxies = None, client_hello = ClientHello.chrome_83):
        self.client_hello = client_hello
        self.proxies = proxies
        self.cookies = CookieJar()

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)
    
    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)
    
    def put(self, url, **kwargs):
        return self.request("PUT", url, **kwargs)
    
    def patch(self, url, **kwargs):
        return self.request("PATCH", url, **kwargs)
    
    def delete(self, url, **kwargs):
        return self.request("DELETE", url, **kwargs)

    def request(self, request_method, url, params = None, headers = {}, data = None, json = None, proxies = None):
        req_data, data_type, data_type_string = self.__format_data(data, json)
        headers = self.__format_headers(url, headers, data_type_string)
        url = self.__format_url(url, params)
        proxy = self.__get_proxy(proxies)
        response_data = lib.MakeReq(url, GoString(request_method.encode(), len(request_method)), GoString(self.client_hello.encode(), len(self.client_hello)), headers, req_data, data_type, proxy)
        return Response(ujson.loads(response_data.decode()), self.cookies)

    def __format_url(self, url, params):
        if params != None:
            url += ("&" if urlparse(url).query else "?") + urlencode(params)
        return GoString(url.encode(), len(url))
    
    def __format_headers(self, url, headers, data_type_string):
        list_headers = [f"{name}: {headers[name]}" for name in headers]
        list_headers, http_ver, domain = self.__add_cookie_to_headers(url, list_headers)
        list_headers = self.__check_headers(list_headers, http_ver, domain, data_type_string)
        list_headers = self.__order_headers(list_headers)
        string_headers = "\n".join(list_headers)
        return GoString(string_headers.encode(), len(string_headers))
    
    def __order_headers(self, headers):
        header_names = [header.split(": ")[0] for header in headers]
        headers.append(f"header-order: {','.join(header_names)}")
        return headers
    
    def __add_cookie_to_headers(self, url, list_headers):
        domain = urlparse(url).netloc
        cookies = []
        for cookie in self.cookies:
            if cookie.domain in domain:
                cookies.append(f"{cookie.name}={cookie.value}")
                # list_headers.append(f"Cookie: {cookie.name}={cookie.value};")
        
        cookie_header_name = "Cookie"
        http_ver = 1
        if list_headers[0][0] == list_headers[0][0].lower() and list_headers[1][0] == list_headers[1][0].lower():
            cookie_header_name = "cookie"
            http_ver = 2

        if len(cookies) > 0:
            list_headers.append(f"{cookie_header_name}: {'; '.join(cookies)}")
        return list_headers, http_ver, domain
    
    def __check_headers(self, list_headers, http_ver, domain, data_type_string):
        if http_ver == 1:
            host_found, connection_found, content_length_found, user_agent_found = self.__search_header_names(list_headers, http_ver)
            
            if not host_found:
                list_headers.insert(0, f"Host: {domain}")
            if not connection_found:
                list_headers.insert(1, "Connection: keep-alive")
            if not user_agent_found:
                list_headers.insert(3, "User-Agent: natetls")
            if data_type_string != "" and not content_length_found:
                list_headers.insert(2, "Content-Length: 0")
        else:
            host_found, connection_found, content_length_found, user_agent_found = self.__search_header_names(list_headers, http_ver)
            if data_type_string != "" and not content_length_found:
                list_headers.insert(0, "content-length: 0")
            if not user_agent_found:
                list_headers.insert(1, "user-agent: natetls")

        return list_headers
    
    def __search_header_names(self, list_headers, http_ver):
        host_found, connection_found, content_length_found, user_agent_found = False, False, False, False
        for header in list_headers:
            if "host: " in header.lower():
                host_found = True
            elif "connection: " in header.lower():
                connection_found = True
            elif "content-length" in header.lower():
                content_length_found = True
            elif "user-agent" in header.lower():
                user_agent_found = True
        return host_found, connection_found, content_length_found, user_agent_found
    
    def __get_proxy(self, proxies):
        if proxies != None or self.proxies != None:
            proxy = self.__format_proxy(proxies) if proxies != None else self.__format_proxy(self.proxies)
            return GoString(proxy.encode(), len(proxy))
        return GoString(b"", 0)
    
    def __format_data(self, data, json):
        if data != None:
            list_data = [f"{key}: {data[key]}" for key in data]
            string_data = "\n".join(list_data)
            return GoString(string_data.encode(), len(string_data)), GoString(b"data", 4), "data"
        if json != None:
            string_data = ujson.dumps(json)
            return GoString(string_data.encode(), len(string_data)), GoString(b"json", 4), "json"
        return GoString(b"", 0), GoString(b"", 0), ""
    
    def __format_proxy(self, proxy):
        return proxy["http"]

class CookieJar(object):
    def __init__(self):
        self.cookies = []
    
    def __iter__(self):
        return iter(self.cookies)
    
    def update_cookies_from_response(self, cookies_list):
        if cookies_list != None:
            for cookie in cookies_list:
                self.__add_new_cookie(cookie)
    
    def clear(self):
        self.cookies = []
    
    def delete(self, cookie_name):
        cookies_copy = self.cookies
        for cookie in cookies_copy:
            if cookie.name == cookie_name:
                self.cookies.remove(cookie)
    
    def get(self, name, domain = None, path = None):
        for cookie in self.cookies:
            if cookie.name == name and (cookie.domain == domain if domain else True):
                return cookie.value
        raise ValueError(f"Cookie with name {cookie.name} not found")
    
    def get_dict(self):
        cookie_dict = {}
        for cookie in self.cookies:
            cookie_dict[cookie.name] = cookie.value
        return cookie_dict
    
    def set(self, name, value, domain = None, path = "/"):
        if domain == None:
            raise TypeError("You must specify a domain to set a cookie")
        else:
            self.__add_new_cookie({"name": name, "value": value, "domain": domain, "path": path})
    
    def __add_new_cookie(self, new_cookie):
        for cookie in self.cookies:
            if cookie.name == new_cookie["name"] and cookie.domain == new_cookie["domain"]:
                self.cookies.remove(cookie)
                break
        self.cookies.append(Cookie(new_cookie))

class Cookie(object):
    def __init__(self, cookie_data):
        self.name = cookie_data["name"]
        self.value = cookie_data["value"]
        self.domain = cookie_data["domain"]
        self.path = cookie_data["path"]

class Response(object):
    def __init__(self, response_data, session_cookies):
        error = response_data["error"]
        if error != "":
            self.handle_error(error)
        self.status_code = response_data["statusCode"]
        self.text = response_data["body"]
        self.headers = response_data["headers"]
        self.url = response_data["url"]
        session_cookies.update_cookies_from_response(response_data["cookies"])
    
    def json(self):
        try:
            return ujson.loads(self.text)
        except ValueError:
            raise ValueError("Body is not of type JSON") 
    
    def handle_error(self, error):
        if "EOF" in error or "dial tcp: lookup " in error and "no such host" in error:
            raise ConnectionError("Failed to connect to host")
        elif "No connection could be made because the target machine actively refused it" in error:
            raise ProxyError("Failed to connect to proxy/host")
        elif "tls: first record does not look like a TLS handshake" in error:
            raise ProxyError("Proxy TLS error")
        elif "407 Proxy Authentication Required" in error:
            raise ProxyError("Invalid proxy username or password")
        elif "http: server gave HTTP response to HTTPS client" in error:
            raise ProxyError("Invalid proxy format (HTTPS error)")
        elif "502 Proxy Error" in error:
            raise ProxyError("Proxy connection busy")
        elif "503 Error" in error or "timeout" in error or "connected host has failed to respond" in error:
            raise TimeoutError("Connection timed out")
        else:
            raise UnknownError(error)

class ProxyError(Exception):
    __module__ = Exception.__module__

class UnknownError(Exception):
    __module__ = Exception.__module__
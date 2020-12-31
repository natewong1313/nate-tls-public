package main

import "C"

import (
	"bytes"
	"compress/gzip"
	"encoding/json"
	"github.com/natewong1313/client/cclient"
	"github.com/natewong1313/client/http"
	"github.com/natewong1313/client/utls"
	"io"
	"io/ioutil"
	"net/url"
	"strings"
)

type Response struct {
	Error      string            `json:"error"`
	URL        string            `json:"url"`
	Body       string            `json:"body"`
	Headers    map[string]string `json:"headers"`
	Cookies    []Cookie          `json:"cookies"`
	StatusCode int               `json:"statusCode"`
}

type Cookie struct {
	Name   string `json:"name"`
	Value  string `json:"value"`
	Domain string `json:"domain"`
	Path   string `json:"path"`
}

//export MakeReq
func MakeReq(reqUrl, reqType, clientHello, headers, data, dataType, proxy string) *C.char {

	respHeaders := make(map[string]string)
	var respCookies []Cookie

	tlsClientHello := tls.HelloChrome_83
	switch clientHello {
	case "chrome83":
		tlsClientHello = tls.HelloChrome_83
	case "chrome72":
		tlsClientHello = tls.HelloChrome_72
	case "ios12":
		tlsClientHello = tls.HelloIOS_12_1
	case "ios11":
		tlsClientHello = tls.HelloIOS_11_1
	case "firefox65":
		tlsClientHello = tls.HelloFirefox_65
	case "firefox63":
		tlsClientHello = tls.HelloFirefox_63
	}

	client, err := cclient.NewClient(tlsClientHello)
	if proxy != "" {
		client, err = cclient.NewClient(tlsClientHello, proxy)
	}
	if err != nil {
		stringData, _ := json.Marshal(Response{err.Error(), reqUrl, "", respHeaders, respCookies, 0})
		return C.CString(string(stringData))
	}
	req, err := http.NewRequest(reqType, reqUrl, nil)
	if dataType == "data" {
		form := url.Values{}
		for _, line := range strings.Split(strings.TrimSuffix(data, "\n"), "\n") {
			line = strings.TrimSpace(line)
			if line != "" {
				dataSplit := strings.Split(line, ": ")
				if len(dataSplit) == 2 {
					form.Add(dataSplit[0], dataSplit[1])
				} else {
					form.Add(line[:len(line)-1], "")
				}
			}
		}
		req, err = http.NewRequest(reqType, reqUrl, strings.NewReader(form.Encode()))
	} else if dataType == "json" {
		jsonData := []byte(data)
		req, err = http.NewRequest(reqType, reqUrl, bytes.NewBuffer(jsonData))
	}
	if err != nil {
		stringData, _ := json.Marshal(Response{err.Error(), reqUrl, "", respHeaders, respCookies, 0})
		return C.CString(string(stringData))
	}
	req.Close = true

	for _, line := range strings.Split(strings.TrimSuffix(headers, "\n"), "\n") {
		line = strings.TrimSpace(line)
		if line != "" {
			headerSplit := strings.Split(line, ": ")
			if len(headerSplit) == 2 {
				req.Header.Add(headerSplit[0], headerSplit[1])
			} else {
				req.Header.Add(line[:len(line)-1], "")
			}
		}
	}

	resp, err := client.Do(req)
	if err != nil {
		stringData, _ := json.Marshal(Response{err.Error(), reqUrl, "", respHeaders, respCookies, 0})
		return C.CString(string(stringData))
	}

	var reader io.ReadCloser
	switch resp.Header.Get("Content-Encoding") {
	case "gzip":
		reader, err = gzip.NewReader(resp.Body)
	default:
		reader = resp.Body
	}
	if err != nil {
		stringData, _ := json.Marshal(Response{err.Error(), reqUrl, "", respHeaders, respCookies, 0})
		return C.CString(string(stringData))
	}

	bodyBytes, err := ioutil.ReadAll(reader)
	if err != nil {
		stringData, _ := json.Marshal(Response{err.Error(), reqUrl, "", respHeaders, respCookies, 0})
		return C.CString(string(stringData))
	}
	resp.Body.Close()
	reader.Close()
	respBody := string(bodyBytes)

	for name, values := range resp.Header {
		if name == "Set-Cookie" {
			respHeaders[name] = strings.Join(values, "/,/")
		} else {
			for _, value := range values {
				respHeaders[name] = value
			}
		}
	}
	domainURL, err := url.Parse(resp.Request.URL.String())
	if err != nil {
		stringData, _ := json.Marshal(Response{err.Error(), reqUrl, "", respHeaders, respCookies, 0})
		return C.CString(string(stringData))
	}
	for _, cookie := range client.Jar.Cookies(domainURL) {
		domain := cookie.Domain
		if domain == "" {
			domain = domainURL.Host
		}
		respCookies = append(respCookies, Cookie{cookie.Name, cookie.Value, domain, cookie.Path})
	}

	stringData, err := json.Marshal(Response{"", resp.Request.URL.String(), respBody, respHeaders, respCookies, resp.StatusCode})
	if err != nil {
		stringData, _ := json.Marshal(Response{err.Error(), reqUrl, "", respHeaders, respCookies, 0})
		return C.CString(string(stringData))
	}
	return C.CString(string(stringData))
}

func main() {}

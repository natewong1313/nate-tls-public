package cclient

import (
	"github.com/natewong1313/client/http"
	"github.com/natewong1313/client/http/cookiejar"
	utls "github.com/natewong1313/client/utls"
	"golang.org/x/net/proxy"
	"strings"
)

func NewClient(clientHello utls.ClientHelloID, proxyUrl ...string) (http.Client, error) {
	jar, _ := cookiejar.New(nil)
	if len(proxyUrl) > 0 && len(proxyUrl) > 0 {
		dialer, err := newConnectDialer(proxyUrl[0])
		if err != nil {
			return http.Client{}, err
		}
		return http.Client{
			Jar:       jar,
			Transport: newRoundTripper(clientHello, dialer),
			CheckRedirect: func(req *http.Request, via []*http.Request) error {
				req.Header.Del("content-length")
				req.Header.Set("header-order", strings.Replace(req.Header.Get("header-order"), "content-length,", "", 1))
				return nil
			},
		}, nil
	} else {
		return http.Client{
			Jar:       jar,
			Transport: newRoundTripper(clientHello, proxy.Direct),
			CheckRedirect: func(req *http.Request, via []*http.Request) error {
				req.Header.Del("content-length")
				req.Header.Set("header-order", strings.Replace(req.Header.Get("header-order"), "content-length,", "", 1))
				return nil
			},
		}, nil
	}
}

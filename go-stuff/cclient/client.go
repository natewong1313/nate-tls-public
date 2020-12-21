package cclient

import (
	"github.com/natewong1313/client/http"
	utls "github.com/refraction-networking/utls"
	"golang.org/x/net/proxy"
	"strings"
)

func NewClient(clientHello utls.ClientHelloID, proxyUrl ...string) (http.Client, error) {
	if len(proxyUrl) > 0 && len(proxyUrl) > 0 {
		dialer, err := newConnectDialer(proxyUrl[0])
		if err != nil {
			return http.Client{}, err
		}
		return http.Client{
			Transport: newRoundTripper(clientHello, dialer),
			CheckRedirect: func(req *http.Request, via []*http.Request) error {
				req.Header.Del("content-length")
				req.Header.Set("header-order", strings.Replace(req.Header.Get("header-order"), "content-length,", "", 1))
				return nil
			},
		}, nil
	} else {
		return http.Client{
			Transport: newRoundTripper(clientHello, proxy.Direct),
			CheckRedirect: func(req *http.Request, via []*http.Request) error {
				req.Header.Del("content-length")
				req.Header.Set("header-order", strings.Replace(req.Header.Get("header-order"), "content-length,", "", 1))
				return nil
			},
		}, nil
	}
}

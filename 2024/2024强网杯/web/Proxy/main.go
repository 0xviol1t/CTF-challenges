package main

import (
	"bytes"
	"io"
	"net/http"
	"os/exec"

	"github.com/gin-gonic/gin"
)

type ProxyRequest struct {
	URL             string            `json:"url" binding:"required"`
	Method          string            `json:"method" binding:"required"`
	Body            string            `json:"body"`
	Headers         map[string]string `json:"headers"`
	FollowRedirects bool              `json:"follow_redirects"`
}

func main() {
	r := gin.Default()

	v1 := r.Group("/v1")
	{
		v1.POST("/api/flag", func(c *gin.Context) {
			cmd := exec.Command("/readflag")
			flag, err := cmd.CombinedOutput()
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"status": "error", "message": "Internal Server Error"})
				return
			}
			c.JSON(http.StatusOK, gin.H{"flag": flag})
		})
	}

	v2 := r.Group("/v2")
	{
		v2.POST("/api/proxy", func(c *gin.Context) {
			var proxyRequest ProxyRequest
			if err := c.ShouldBindJSON(&proxyRequest); err != nil {
				c.JSON(http.StatusBadRequest, gin.H{"status": "error", "message": "Invalid request"})
				return
			}

			client := &http.Client{
				CheckRedirect: func(req *http.Request, via []*http.Request) error {
					if !req.URL.IsAbs() {
						return http.ErrUseLastResponse
					}

					if !proxyRequest.FollowRedirects {
						return http.ErrUseLastResponse
					}

					return nil
				},
			}

			req, err := http.NewRequest(proxyRequest.Method, proxyRequest.URL, bytes.NewReader([]byte(proxyRequest.Body)))
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"status": "error", "message": "Internal Server Error"})
				return
			}

			for key, value := range proxyRequest.Headers {
				req.Header.Set(key, value)
			}

			resp, err := client.Do(req)

			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"status": "error", "message": "Internal Server Error"})
				return
			}

			defer resp.Body.Close()

			body, err := io.ReadAll(resp.Body)
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"status": "error", "message": "Internal Server Error"})
				return
			}

			c.Status(resp.StatusCode)
			for key, value := range resp.Header {
				c.Header(key, value[0])
			}

			c.Writer.Write(body)
			c.Abort()
		})
	}

	r.Run("127.0.0.1:8769")
}

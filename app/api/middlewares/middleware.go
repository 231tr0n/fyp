package middlewares

import (
	"fmt"
	"fyp/router"
	"net/http"
	"time"

	"github.com/google/uuid"
)

var middlewares map[string]router.Middleware

func init() {
	middlewares = make(map[string]router.Middleware)
	middlewares["session"] = func(next router.Controller) router.Controller {
		return func(res http.ResponseWriter, req *http.Request) {
			cookie, err := req.Cookie("uuid")
			var sessionCookie *http.Cookie
			if err != nil {
				sessionCookie = &http.Cookie{
					Name:     "uuid",
					Value:    uuid.NewString(),
					HttpOnly: true,
					SameSite: http.SameSiteStrictMode,
					Path:     "/",
				}
				http.SetCookie(res, sessionCookie)
			} else {
				if _, err1 := uuid.Parse(cookie.Value); err1 != nil {
					sessionCookie = &http.Cookie{
						Name:     "uuid",
						Value:    uuid.NewString(),
						HttpOnly: true,
						SameSite: http.SameSiteStrictMode,
						Path:     "/",
					}
					http.SetCookie(res, sessionCookie)
				}
			}
			next(res, req)
		}
	}

	middlewares["logger"] = func(next router.Controller) router.Controller {
		return func(res http.ResponseWriter, req *http.Request) {
			startTime := time.Now().UnixMilli()
			cookie, err := req.Cookie("uuid")
			next(res, req)
			endTime := time.Now().UnixMilli()
			if err != nil {
				fmt.Println(req.Method, "\t", "Not Set", "\t", req.RemoteAddr, "\t", req.URL.Path, "\t", endTime-startTime)
			} else {
				fmt.Println(req.Method, "\t", cookie.Value, "\t", req.RemoteAddr, "\t", req.URL.Path, "\t", endTime-startTime)
			}
		}
	}
}

func AddMiddlewares(r *router.Router) {
	for key, value := range middlewares {
		r.Use(key, value)
	}
}

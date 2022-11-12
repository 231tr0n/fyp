package routes

import (
  "os"
  "soubhagya/api/controllers"
  "soubhagya/router"
)

func AddRoutes(r *router.Router) {
  temp, _ := os.Getwd()
  r.ServeStatic("/public", []string{"session", "logger"}, temp+"/public")
  r.ServeStaticFile("/", []string{"session", "logger"}, temp+"/views/homepage.html")
  r.ServeStaticFile("/favicon.ico", []string{"session", "logger"}, temp+"/public/favicon.ico")
  r.Route("POST", "/calibrate", []string{"session", "logger"}, controllers.Calibrate)
}

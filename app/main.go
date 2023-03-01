package main

import (
	"fmt"
	"fyp/api/middlewares"
	"fyp/api/routes"
	"fyp/config"
	"fyp/router"
	"net/http"
	"os"
	"os/signal"
	"path/filepath"
	"syscall"
)

func main() {
	os.RemoveAll("temp")
	os.Mkdir("temp", os.ModePerm)
	os.Mkdir(filepath.FromSlash("temp/pictures"), os.ModePerm)
	defer os.RemoveAll("temp")
	r := router.Router{}
	r.Init(false)
	middlewares.AddMiddlewares(&r)
	routes.AddRoutes(&r)
	server := http.Server{
		Addr:    config.Port,
		Handler: r,
	}
	fmt.Println("----------------")
	fmt.Println(r)
	fmt.Println("----------------")
	go (func() {
		if err := server.ListenAndServe(); err != nil {
			fmt.Println()
			fmt.Println("----------------")
			fmt.Println(err)
		}
	})()
	interrupt := make(chan os.Signal, 1)
	defer (func() {
		if err := recover(); err != nil {
			fmt.Println("-----------------")
			fmt.Println(err)
			fmt.Println("-----------------")
		}
		close(interrupt)
	})()
	go (func() {
		signal.Notify(interrupt, os.Interrupt, syscall.SIGTERM, syscall.SIGINT)
	})()
	<-interrupt
	server.Close()
}

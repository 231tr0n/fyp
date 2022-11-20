package controllers

import (
	"bufio"
	"fmt"
	"fyp/ml"
	"fyp/router"
	"io"
	"net/http"
	"os"
	"path/filepath"
)

var calibrateModel ml.Model
var spellCheckModel ml.Model

func init() {
	temp, _ := os.Getwd()
	calibrateModel.Init("python3", filepath.FromSlash(temp+"/mlmodels/calibrate/main.py"))
	fmt.Println("Model 1 Loaded.")
	spellCheckModel.Init("python3", filepath.FromSlash(temp+"/mlmodels/nlp/main.py"))
	fmt.Println("Model 2 Loaded.")
}

var SpellCheck router.Controller = func(res http.ResponseWriter, req *http.Request) {
	req.Body = http.MaxBytesReader(res, req.Body, 50<<20)
	bodyStream, _ := io.ReadAll(req.Body)
	body := string(bodyStream)
	res.Header().Set("Content-Type", "text/plain")
	answer := []byte(spellCheckModel.Predict(body))
	res.Write(answer)
}

var Calibrate router.Controller = func(res http.ResponseWriter, req *http.Request) {
	req.Body = http.MaxBytesReader(res, req.Body, 50<<20)
	multipartReader, err := req.MultipartReader()
	if err != nil {
		http.Error(res, err.Error(), http.StatusBadRequest)
		return
	}
	part, err := multipartReader.NextPart()
	if err != nil {
		http.Error(res, err.Error(), http.StatusInternalServerError)
		return
	}
	if part.FormName() != "image" {
		http.Error(res, "Image File is expected", http.StatusBadRequest)
		return
	}
	reader := bufio.NewReader(part)
	cookie, _ := req.Cookie("uuid")
	filePath := filepath.Join("temp", "pictures", cookie.Value+".jpg")
	file, err := os.Create(filePath)
	defer os.Remove(filePath)
	defer file.Close()
	if err != nil {
		http.Error(res, err.Error(), http.StatusInternalServerError)
		return
	}
	if _, err := io.Copy(file, reader); err != nil {
		http.Error(res, err.Error(), http.StatusInternalServerError)
		return
	}
	res.Header().Set("Content-Type", "text/plain")
	temp, _ := os.Getwd()
	answer := []byte(calibrateModel.Predict(filepath.FromSlash(temp + "/" + filePath)))
	res.Write(answer)
}

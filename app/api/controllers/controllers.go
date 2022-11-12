package controllers

import (
  "bufio"
  "io"
  "net/http"
  "os"
  "path/filepath"
  "soubhagya/ml"
  "soubhagya/router"
  "fmt"
)

var calibrateModel ml.Model

func init() {
  temp, _ := os.Getwd()
  calibrateModel.Init("python3", temp+"/mlmodels/calibrate/main1.py")
  fmt.Println("Model 1 Loaded.")
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
	answer := []byte(calibrateModel.Predict(temp + "/" + filePath))
  res.Write(answer)
}

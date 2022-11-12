## soubhagyo

Installing dependencies
```bash
sudo apt install software-properties-common
sudo add-apt-repository ppa:longsleep/golang-backports
sudo apt update
sudo apt install golang-go python3 python3-pip libgl1
sudo pip3 install mediapipe opencv-python numpy tensorflow
sudo pip3 install protobuf==3.20.*
```

Installing go dependencies and building (**Go to the app directory in the source code root using `cd app`**)
```bash
go mod tidy
go fmt ./...
go generate
```

Running the server
```bash
go run main.go
```


Building docker image (**Go to the source code root**)
```bash
sudo docker build -t soubhagya .
```

Running a container of that image
```bash
sudo docker run -it -p 8080:8080 soubhagya
```

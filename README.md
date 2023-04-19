## fyp

Installing dependencies
```bash
pacman -Syu --noconfirm
pacman -Syu go --noconfirm
pacman -Syu python --noconfirm
pacman -Syu python-pip --noconfirm
pacman -Syu libgl --noconfirm
pip install tensorflow
pip install opencv-python
pip install mediapipe
pip install numpy
pip install pyspellchecker 
pip install wordsegment
```

Running the server
```bash
go mod tidy
go fmt ./...
go generate
go run main.go
```

Building docker image
```bash
sudo docker build -t fyp .
```

Running a container of that image
```bash
sudo docker run -it -p 8080:8080 fyp
```

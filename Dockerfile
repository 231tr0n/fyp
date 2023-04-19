FROM ubuntu:20.04
RUN apt-get update
RUN apt-get install -y curl software-properties-common
RUN add-apt-repository ppa:longsleep/golang-backports
RUN apt-get update
RUN apt-get install -y golang-go python3 python3-pip libgl1
RUN pip3 install mediapipe opencv-python numpy tensorflow pyspellchecker spellchecker wordsegment
RUN pip3 install protobuf==3.20.*
EXPOSE 8080
COPY app /root/app
WORKDIR /root/app
RUN go mod tidy
CMD ["go", "run", "main.go"]

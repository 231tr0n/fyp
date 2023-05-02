FROM archlinux:latest
RUN pacman -Syu --noconfirm
RUN pacman -Syu go --noconfirm
RUN pacman -Syu python --noconfirm
RUN pacman -Syu python-pip --noconfirm
RUN pacman -Syu libgl --noconfirm
RUN pacman -Syu tensorflow --noconfirm
RUN pacman -Syu python-tensorflow --noconfirm
RUN pip install opencv-python
RUN pip install mediapipe
RUN pip install pyspellchecker 
RUN pip install wordsegment
EXPOSE 8080
COPY app /root/app
WORKDIR /root/app
RUN go mod tidy
CMD ["go", "run", "."]

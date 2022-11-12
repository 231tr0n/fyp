package ml

import (
	"bufio"
	"io"
	"os/exec"
	"strings"
	"sync"
)

type Model struct {
	model			*exec.Cmd
	in				io.WriteCloser
	out				io.ReadCloser
	err				io.ReadCloser
	outReader *bufio.Reader
	errReader *bufio.Reader
	mu				sync.Mutex
}

func (m *Model) Init(command string, arguments ...string) {
	m.model = exec.Command(command, arguments...)
	m.in, _ = m.model.StdinPipe()
	m.out, _ = m.model.StdoutPipe()
	m.err, _ = m.model.StderrPipe()
	m.outReader = bufio.NewReader(m.out)
	m.errReader = bufio.NewReader(m.err)
	m.model.Start()
	for {
		data, _ := m.outReader.ReadString('\n')
		if strings.Contains(string(data), "Ready") {
			break
		}
	}
}

func (m *Model) Predict(filePath string) string {
	m.mu.Lock()
	defer m.mu.Unlock()
	io.WriteString(m.in, filePath+"\n")
	data, _ := m.outReader.ReadString('\n')
	return strings.Trim(data, "\n ")
}

func (m *Model) Close() {
	m.mu.Lock()
	defer m.mu.Unlock()
	io.WriteString(m.in, "Exit\n")
	m.in.Close()
	m.model.Wait()
}

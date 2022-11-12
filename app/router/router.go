package router

import (
  "embed"
  "fmt"
  "io"
  "io/fs"
  "mime"
  "net/http"
  "os"
  "path/filepath"
  "strings"
)

type Controller func(http.ResponseWriter, *http.Request)

type Middleware func(Controller) Controller

type Router struct {
  log         bool
  middlewares map[string]Middleware
  routes      map[string]map[string]Controller
}

func (r *Router) Init(log bool) {
  r.routes = make(map[string]map[string]Controller)
  r.middlewares = make(map[string]Middleware)
  r.log = log
  if r.log {
    fmt.Println("Router Initialized.")
  }
}

func (r *Router) Route(method string, path string, middlewares []string, controller Controller) {
  for _, key := range middlewares {
    _, ok := r.middlewares[key]
    if !ok {
      fmt.Println("One middleware is not present in the chain given")
      return
    }
  }
  _, ok := r.routes[method]
  if !ok {
    r.routes[method] = make(map[string]Controller)
  }
  temp := controller
  if len(middlewares) != 0 {
    for _, i := range middlewares {
      temp = r.middlewares[i](temp)
    }
  }
  r.routes[method][path] = temp
  if r.log {
    fmt.Println("Added Route", method, path)
  }
}

func (r *Router) Use(name string, m Middleware) {
  r.middlewares[name] = m
  if r.log {
    fmt.Println("Added Middleware", len(r.middlewares)-1)
  }
}

func (r *Router) FSDownloadStaticFile(path string, filePath string, middlewares []string, fileSystem embed.FS) {
  file, err := fileSystem.Open(filePath)
  if err != nil {
    fmt.Println("File not found", filePath)
    return
  }
  file.Close()
  temp := filepath.Base(filePath)
  temp1 := mime.TypeByExtension(filepath.Ext(temp))
  r.Route("GET", path, middlewares, func(res http.ResponseWriter, req *http.Request) {
    file, _ := fileSystem.Open(filePath)
    defer file.Close()
    res.Header().Set("Content-Disposition", "attachment; filename="+temp)
    if temp1 != "" {
      res.Header().Set("Content-Type", temp1)
    }
    io.Copy(res, file)
  })
}

func (r *Router) FSServeStaticFile(path string, filePath string, middlewares []string, fileSystem embed.FS) {
  file, err := fileSystem.Open(filePath)
  if err != nil {
    fmt.Println("File not found", filePath)
    return
  }
  file.Close()
  temp := filepath.Base(filePath)
  temp1 := mime.TypeByExtension(filepath.Ext(temp))
  r.Route("GET", path, middlewares, func(res http.ResponseWriter, req *http.Request) {
    file, _ := fileSystem.Open(filePath)
    defer file.Close()
    if temp1 != "" {
      res.Header().Set("Content-Type", temp1)
    }
    io.Copy(res, file)
  })
}

func (r *Router) FSDownloadStatic(middlewares []string, fileSystem embed.FS) {
  fs.WalkDir(fileSystem, ".", func(path string, info fs.DirEntry, err error) error {
    if !info.IsDir() {
      temp := filepath.Base(path)
      temp1 := mime.TypeByExtension(filepath.Ext(temp))
      r.Route("GET", "/"+path, middlewares, func(res http.ResponseWriter, req *http.Request) {
        res.Header().Set("Content-Disposition", "attachment; filename="+temp)
        if temp1 != "" {
          res.Header().Set("Content-Type", temp1)
        }
        file, _ := fileSystem.Open(path)
        defer file.Close()
        io.Copy(res, file)
      })
    }
    return nil
  })
}

func (r *Router) FSServeStatic(middlewares []string, fileSystem embed.FS) {
  fs.WalkDir(fileSystem, ".", func(path string, info fs.DirEntry, err error) error {
    if !info.IsDir() {
      temp := filepath.Base(path)
      temp1 := mime.TypeByExtension(filepath.Ext(temp))
      r.Route("GET", "/"+path, middlewares, func(res http.ResponseWriter, req *http.Request) {
        if temp1 != "" {
          res.Header().Set("Content-Type", temp1)
        }
        file, _ := fileSystem.Open(path)
        defer file.Close()
        io.Copy(res, file)
      })
    }
    return nil
  })
}

func (r *Router) DownloadStaticFile(path string, middlewares []string, filePath string) {
  if _, err := os.Stat(filePath); os.IsNotExist(err) {
    fmt.Println("File not found", filePath)
    return
  }
  temp := filepath.Base(filePath)
  temp1 := mime.TypeByExtension(filepath.Ext(temp))
  r.Route("GET", path, middlewares, func(res http.ResponseWriter, req *http.Request) {
    file, _ := os.Open(filePath)
    defer file.Close()
    res.Header().Set("Content-Disposition", "attachment; filename="+temp)
    if temp1 != "" {
      res.Header().Set("Content-Type", temp1)
    }
    io.Copy(res, file)
  })
}

func (r *Router) ServeStaticFile(path string, middlewares []string, filePath string) {
  if _, err := os.Stat(filePath); os.IsNotExist(err) {
    fmt.Println("File not found", filePath)
    return
  }
  temp := filepath.Base(filePath)
  temp1 := mime.TypeByExtension(filepath.Ext(temp))
  r.Route("GET", path, middlewares, func(res http.ResponseWriter, req *http.Request) {
    file, _ := os.Open(filePath)
    defer file.Close()
    if temp1 != "" {
      res.Header().Set("Content-Type", temp1)
    }
    io.Copy(res, file)
  })
}

func (r *Router) DownloadStatic(mount string, middlewares []string, dirPath string) {
  if _, err := os.Stat(dirPath); os.IsNotExist(err) {
    fmt.Println("Directory not found", dirPath)
    return
  }
  filepath.WalkDir(dirPath, func(path string, info fs.DirEntry, err error) error {
    if !info.IsDir() {
      temp := filepath.Base(path)
      temp1 := mime.TypeByExtension(filepath.Ext(temp))
      r.Route("GET", strings.Replace(path, dirPath, mount, 1), middlewares, func(res http.ResponseWriter, req *http.Request) {
        res.Header().Set("Content-Disposition", "attachment; filename="+temp)
        if temp1 != "" {
          res.Header().Set("Content-Type", temp1)
        }
        file, _ := os.Open(path)
        defer file.Close()
        io.Copy(res, file)
      })
    }
    return nil
  })
}

func (r *Router) ServeStatic(mount string, middlewares []string, dirPath string) {
  if _, err := os.Stat(dirPath); os.IsNotExist(err) {
    fmt.Println("Directory not found", dirPath)
    return
  }
  filepath.WalkDir(dirPath, func(path string, info fs.DirEntry, err error) error {
    if !info.IsDir() {
      temp := filepath.Base(path)
      temp1 := mime.TypeByExtension(filepath.Ext(temp))
      r.Route("GET", strings.Replace(path, dirPath, mount, 1), middlewares, func(res http.ResponseWriter, req *http.Request) {
        if temp1 != "" {
          res.Header().Set("Content-Type", temp1)
        }
        file, _ := os.Open(path)
        defer file.Close()
        io.Copy(res, file)
      })
    }
    return nil
  })
}

func (r *Router) match(req *http.Request) Controller {
  controller, ok := r.routes[req.Method][req.URL.Path]
  if ok {
    return controller
  }
  return http.NotFound
}

func (r Router) String() string {
  s := fmt.Sprintf("\nMiddlewares: %d\nRoutes:\n", len(r.middlewares))
  for key, value := range r.routes {
    for key1 := range value {
      s += fmt.Sprintf("%s\t%s\n", key, key1)
    }
  }
  return s
}

func (r Router) ServeHTTP(res http.ResponseWriter, req *http.Request) {
  r.match(req)(res, req)
  defer (func() {
    if err := recover(); err != nil {
      fmt.Println("---------------")
      fmt.Println(err)
      fmt.Println("---------------")
    }
  })()
}

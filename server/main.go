// Package main
package main

import (
	"log"
	"net"
	"os"
	"runtime"
)

// Для данной задачи больше одного процессора не требуется.
func init() { runtime.GOMAXPROCS(1) }

func main() {
	var (
		err error
		cfg *Configuration
		srv Server
	)

	// Загрузка конфигурации сервера.
	cfg = &Configuration{
		MqttUrl:      os.Getenv(envMqttUrl),
		MqttUsername: os.Getenv(envMqttUsername),
		MqttPassword: os.Getenv(envMqttPassword),
		VakioIp:      net.ParseIP(os.Getenv(envVakioIp)),
		WebServer:    os.Getenv(envWebServer),
	}
	// Создание сервера.
	srv = NewServer(cfg)
	if err = srv.Start(); err != nil {
		log.Fatalf(err.Error())
		return
	}
	if err = srv.Do(); err != nil {
		log.Fatalf(err.Error())
		return
	}
}

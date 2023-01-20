// Package main
package main

import (
	"log"
	"os"

	mqtt "github.com/eclipse/paho.mqtt.golang"
)

// Log Логирование MQTT.
func (srv *impl) Log() {
	//mqtt.DEBUG = log.New(os.Stdout, "[D]", 0)
	//mqtt.WARN = log.New(os.Stdout, "[W]", 0)
	mqtt.ERROR = log.New(os.Stdout, "[E]", 0)
	mqtt.CRITICAL = log.New(os.Stdout, "[C] ", 0)
}

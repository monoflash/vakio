// Package main
package main

import (
	"net"

	mqtt "github.com/eclipse/paho.mqtt.golang"
)

const (
	envMqttUrl      = "MQTT_URL"      // URL адрес MQTT брокера. Пример: tcp://192.168.1.15:1883
	envMqttUsername = "MQTT_USERNAME" // Имя пользователя MQTT брокера.
	envMqttPassword = "MQTT_PASSWORD" // Пароль пользователя MQTT брокера.
	envVakioIp      = "VAKIO_IP"      // IP адрес вентиляционной системы.
	envWebServer    = "WEB_SERVER"    // Хост и порт открытия веб сервера.
)

// Server Интерфейс сервера.
type Server interface {
	// Start Запуск сервера.
	Start() (err error)

	// Do Выполнение сервера с блокировкой функции.
	Do() (err error)

	// Reboot Перезагрузка вентиляционной системы.
	Reboot() (err error)
}

// Server Основной объект сервера вентиляционной системы.
type impl struct {
	Cfg           *Configuration      // Конфигурация сервера.
	Mco           *mqtt.ClientOptions // Настройки MQTT клиента.
	Mct           mqtt.Client         // Интерфейс MQTT клиента.
	Status        *status             // Статус вентиляционной системы.
	StatusHexHash string              // Контрольная сумма статуса вентиляционной системы.
	done          chan struct{}       // Канал завершения работы сервера.
	in            chan *Message       // Канал входящих сообщений.
}

// Message Сообщение получаемое и отправляемое в MQTT брокер.
type Message struct {
	Topic    string
	Qos      byte
	Retained bool
	Payload  string
	Client   *mqtt.Client
	Msg      *mqtt.Message
}

// Configuration Описание конфигурации сервера.
type Configuration struct {
	MqttUrl      string // Адрес MQTT сервера сообщений.
	MqttUsername string // Имя пользователя MQTT сервера сообщений.
	MqttPassword string // Пароль пользователя MQTT сервера сообщений.
	VakioIp      net.IP // IP адрес вентиляционной системы.
	WebServer    string // Хост и порт открытия веб сервера.
}

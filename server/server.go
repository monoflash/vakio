// Package main
package main

import (
	"context"
	"log"
	"strconv"
	"time"

	mqtt "github.com/eclipse/paho.mqtt.golang"
)

// NewServer Создание объекта сервера.
func NewServer(cfg *Configuration) Server {
	var srv = &impl{
		Cfg:    cfg,
		Mco:    mqtt.NewClientOptions(),
		Status: new(status),
		done:   make(chan struct{}),
		in:     make(chan *Message, chanInBuffer),
	}

	srv.Mco.SetCleanSession(true)
	srv.Mco.AddBroker(srv.Cfg.MqttUrl)
	//srv.Mco.SetClientID("client-id")
	srv.Mco.SetUsername(srv.Cfg.MqttUsername)
	srv.Mco.SetPassword(srv.Cfg.MqttPassword)
	srv.Mco.OnConnect = srv.onConnect
	srv.Mco.OnConnectionLost = srv.onConnectionLost

	return srv
}

// Start Запуск сервера.
func (srv *impl) Start() (err error) {
	const waitTimeout = time.Second * 5
	var token mqtt.Token

	srv.Log()
	srv.Mct = mqtt.NewClient(srv.Mco)
	log.Println("Запуск сервера.")
	for {
		token = srv.Mct.Connect()
		if token.WaitTimeout(waitTimeout) {
			if token.Error() == nil {
				break
			}
			log.Printf("Подключение к MQTT брокеру прервана ошибкой: %s\n", token.Error())
		} else {
			log.Println("Истекло время ожидания установки соединения.")
		}
		time.Sleep(waitTimeout)
	}
	log.Println("Сервер запущен.")

	return
}

// Do Выполнение сервера с блокировкой функции.
func (srv *impl) Do() (err error) {
	var cfn context.CancelFunc

	log.Println("Запуск клиента MQTT брокера.")
	cfn = srv.runServer()
	defer cfn()
	<-srv.done

	return
}

func (srv *impl) runServer() (ret context.CancelFunc) {
	var ctx context.Context

	ctx, ret = context.WithCancel(context.Background())
	go srv.msgServer(ctx)
	go srv.pingServer(ctx)
	go srv.webServer(ctx)

	return
}

func (srv *impl) onConnectionLost(_ mqtt.Client, err error) {
	log.Printf("Соединение с MQTT ьрокером разорвано с ошибкой: %s.\n", err)
}

func (srv *impl) onConnect(client mqtt.Client) {
	const subscribeTimeout = time.Second * 10
	var (
		err   error
		n     int
		chl   []string
		sub   func(mqtt.Client, mqtt.Message)
		token mqtt.Token
	)

	chl = []string{topicSystem, topicState, topicSpeed, topicWorkmode, topicMode}
	sub = func(client mqtt.Client, message mqtt.Message) {
		msg := &Message{
			Topic:    message.Topic(),
			Qos:      message.Qos(),
			Retained: message.Retained(),
			Payload:  string(message.Payload()),
			Client:   &client,
			Msg:      &message,
		}
		srv.in <- msg
	}
	log.Println("Соединение с MQTT брокером установлено.")
	for n = range chl {
		if token = client.Subscribe(chl[n], 0, sub); !token.WaitTimeout(subscribeTimeout) {
			log.Printf("Подписка на канал %q прервана по таймауту.\n", chl[n])
			srv.done <- struct{}{}
			return
		}
		if err = token.Error(); err != nil {
			log.Printf("Подписка на канал %q прервана ошибкой: %s", chl[n], err)
			srv.done <- struct{}{}
			return
		}
		log.Printf("Выполнена подписка на канал %q.", chl[n])
	}
	log.Println("Завершена подписка на каналы.")
}

// Reboot Перезагрузка вентиляционной системы.
func (srv *impl) Reboot() (err error) {
	var (
		token mqtt.Token
		qos   int
	)

	token = srv.Mct.Publish(topicSystem, byte(qos), false, CommandReboot)
	<-token.Done()
	err = token.Error()

	return
}

// TurnOnOff Включение и отключение вентиляционной системы.
func (srv *impl) TurnOnOff(state bool) (err error) {
	var (
		token mqtt.Token
		qos   int
		cmd   StateType
	)

	if cmd = StateOn; !state {
		cmd = StateOff
		srv.Status.Speed = 0
	}
	srv.Status.State = cmd
	token = srv.Mct.Publish(topicState, byte(qos), false, cmd.String())
	<-token.Done()
	err = token.Error()

	return
}

// Speed Установка скорости работы вентиляционной системы.
func (srv *impl) Speed(speed uint8) (err error) {
	var (
		token mqtt.Token
		qos   int
	)

	srv.Status.Speed = uint64(speed)
	if srv.Status.State = StateOff; srv.Status.Speed > 0 {
		srv.Status.State = StateOn
	}
	token = srv.Mct.Publish(topicSpeed, byte(qos), false, strconv.FormatUint(srv.Status.Speed, 10))
	<-token.Done()
	err = token.Error()

	return
}

// Workmode Установка предопределённого режима работы вентиляционной системы.
func (srv *impl) Workmode(wmode WorkType) (err error) {
	var (
		token mqtt.Token
		qos   int
	)

	srv.Status.Work = wmode
	token = srv.Mct.Publish(topicWorkmode, byte(qos), false, wmode.String())
	<-token.Done()
	err = token.Error()

	return
}

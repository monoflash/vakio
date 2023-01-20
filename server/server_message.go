// Package main
package main

import (
	"context"
	"fmt"
	"log"
	"strconv"
	"strings"
	"time"

	"github.com/go-ping/ping"
)

// Процесс мониторинга доступности вентиляционной системы через ICMP пинги по IP адресу.
func (srv *impl) pingServer(ctx context.Context) {
	const (
		tickerAvailableTimeout = time.Second * 30
		pingCount              = 4
	)
	var (
		err            error
		end, first, f1 bool
		ticker         *time.Ticker
		pingo          *ping.Pinger
		pings          *ping.Statistics
	)

	ticker, first = time.NewTicker(time.Second/2), true
	defer ticker.Stop()
	for {
		if end {
			break
		}
		if first && f1 {
			first = false
			ticker.Stop()
			ticker = time.NewTicker(tickerAvailableTimeout)
		}
		select {
		case <-ctx.Done():
			end = true
			continue
		case <-ticker.C:
			f1 = true
			if srv.Cfg.VakioIp == nil {
				log.Println("ip == nil")
				continue
			}
			if pingo, err = ping.NewPinger(srv.Cfg.VakioIp.String()); err != nil {
				log.Printf("создание объекта пинг прервано ошибкой: %s\n", err)
				continue
			}
			pingo.SetPrivileged(true)
			pingo.Count = pingCount
			pingo.Timeout = tickerAvailableTimeout / 2
			if err = pingo.Run(); err != nil {
				log.Printf("пинг завершился ошибкой: %s\n", err)
				continue
			}
			switch pings = pingo.Statistics(); pings.PacketLoss {
			case 100.0:
				srv.Status.Available = false
			default:
				srv.Status.Available = true
			}
			srv.checkStatus()
		}
	}
}

// Процесс обработки входящих сообщений MQTT брокера.
func (srv *impl) msgServer(ctx context.Context) {
	const timeout = time.Second * 5
	var (
		err    error
		end    bool
		ticker *time.Ticker
		msg    *Message
	)

	ticker = time.NewTicker(timeout)
	defer ticker.Stop()
	for {
		if end {
			break
		}
		select {
		case <-ctx.Done():
			end = true
			continue
		case msg = <-srv.in:
			if err = srv.onMessage(msg); err != nil {
				log.Printf("Обработка входящего сообщения прервана ошибкой: %s\n", err)
				continue
			}
			srv.checkStatus()
		case <-ticker.C:

			_ = err

		}
	}
}

// Разбор входящих сообщений MQTT брокера в статус вентиляционной системы.
func (srv *impl) onMessage(msg *Message) (err error) {
	var (
		topic string
		state StateType
		speed uint64
		work  WorkType
		mode  ModeType
		commd CommandType
		ok    bool
	)

	switch topic = strings.ToLower(strings.TrimSpace(msg.Topic)); topic {
	case topicState:
		if state = StateParse(msg.Payload); state == StateUnknown {
			err = fmt.Errorf("неизвестное состояние вентиляционной системы: %q", msg.Payload)
			return
		}
		srv.Status.State = state
	case topicSpeed:
		if speed, err = strconv.ParseUint(msg.Payload, 10, 64); err != nil {
			err = fmt.Errorf("неизвестная скорость вентиляторов: %q", msg.Payload)
			return
		}
		srv.Status.Speed = speed
	case topicWorkmode:
		if work = WorkParse(msg.Payload); work == WorkUnknown {
			err = fmt.Errorf("неизвестный режим работы вентиляционной системы: %q", msg.Payload)
			return
		}
		srv.Status.Work = work
	case topicMode:
		if mode = ModeParse(msg.Payload); mode == ModeUnknown {
			err = fmt.Errorf("неизвестный режим вентиляционной системы: %q", msg.Payload)
			return
		}
		srv.Status.Mode = mode
		if ok, state, speed, work = mode.ToState(srv.Status); ok {
			srv.Status.State, srv.Status.Speed, srv.Status.Work = state, speed, work
		}
	case topicSystem:
		if commd = CommandParse(msg.Payload); commd == CommandUnknown {
			err = fmt.Errorf("неизвестная команда вентиляционной системы: %q", msg.Payload)
			return
		}
		srv.Status.Command = commd
		log.Printf("Системная команда: %s\n", msg.Payload)
	default:
		err = fmt.Errorf("поступило сообщение в неизвестный топик %q, сообщение: %s", topic, msg.Payload)
		return
	}
	srv.Status.LastActivityAt = time.Now()

	return
}

// Package main
package main

import (
	"context"
	"encoding/json"
	"log"
	"net"
	"net/http"

	"github.com/webnice/kit/modules/answer"
	"github.com/webnice/web/v2/header"
	"github.com/webnice/web/v2/mime"
	webStatus "github.com/webnice/web/v2/status"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
)

func (srv *impl) webServer(ctx context.Context) {
	var (
		listener net.Listener
		router   *chi.Mux
		err      error
		end      chan error
	)

	router = chi.NewRouter()
	router.Use(middleware.RealIP)
	router.Use(middleware.Recoverer)
	// Заглушка.
	router.Get("/", func(wr http.ResponseWriter, rq *http.Request) {
		wr.Header().Set(header.Location, "https://github.com/monoflash/vakio")
		answer.Response(wr, webStatus.MovedPermanently, nil)
	})
	// Состояние вентиляционной системы.
	router.Get("/condition", func(wr http.ResponseWriter, rq *http.Request) {
		wr.Header().Set(header.ContentType, mime.TextPlainCharsetUTF8)
		answer.JSON(wr, webStatus.Ok, srv.Status)
	})
	// Включение и отключение вентиляционной системы.
	router.Put("/state", func(wr http.ResponseWriter, rq *http.Request) {
		var (
			err     error
			decoder *json.Decoder
			req     *stateRequest
		)

		decoder = json.NewDecoder(rq.Body)
		decoder.DisallowUnknownFields()
		req = new(stateRequest)
		if err = decoder.Decode(req); err != nil {
			answer.InternalServerError(wr, err)
			return
		}
		if err = srv.TurnOnOff(req.State); err != nil {
			answer.InternalServerError(wr, err)
			return
		}
		answer.Response(wr, webStatus.NoContent, nil)
	})
	// Установка скорости работы вентиляции.
	router.Put("/speed", func(wr http.ResponseWriter, rq *http.Request) {
		var (
			err     error
			decoder *json.Decoder
			req     *speedRequest
		)

		decoder = json.NewDecoder(rq.Body)
		decoder.DisallowUnknownFields()
		req = new(speedRequest)
		if err = decoder.Decode(req); err != nil {
			answer.InternalServerError(wr, err)
			return
		}
		if err = srv.Speed(req.Speed); err != nil {
			answer.InternalServerError(wr, err)
			return
		}
		answer.Response(wr, webStatus.NoContent, nil)
	})
	// Установка предустановленного режима работы вентиляции.
	router.Put("/workmode", func(wr http.ResponseWriter, rq *http.Request) {
		var (
			err     error
			decoder *json.Decoder
			req     *workmodeRequest
			wmode   WorkType
		)

		decoder = json.NewDecoder(rq.Body)
		decoder.DisallowUnknownFields()
		req = new(workmodeRequest)
		if err = decoder.Decode(req); err != nil {
			answer.InternalServerError(wr, err)
			return
		}
		if wmode = WorkParse(req.Workmode); wmode == WorkUnknown {
			answer.Response(wr, webStatus.UnprocessableEntity, nil)
			return
		}
		if err = srv.Workmode(wmode); err != nil {
			answer.InternalServerError(wr, err)
			return
		}
		answer.Response(wr, webStatus.NoContent, nil)
	})
	// Настройка сервера.
	server := &http.Server{Addr: srv.Cfg.WebServer, Handler: router}
	addr := server.Addr
	if addr == "" {
		addr = ":http"
	}
	if listener, err = net.Listen("tcp", addr); err != nil {
		log.Printf("запуск web сервера прерван ошибкой: %s", err)
		srv.done <- struct{}{}
		return
	}
	end = make(chan error)
	go func(e chan<- error, l net.Listener) { e <- server.Serve(listener) }(end, listener)
	select {
	case err = <-end:
		log.Printf("работа web сервера прервана ошибкой: %s", err)
		srv.done <- struct{}{}
	case <-ctx.Done():
	}
}

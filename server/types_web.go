// Package main
package main

type stateRequest struct {
	State bool `json:"state"` // Новое состояние. Истина=включить, Ложь=выключить.
}

type speedRequest struct {
	Speed uint8 `json:"speed"` // Новое значение скорости.
}

type workmodeRequest struct {
	Workmode string `json:"workmode"`
}

// Package main
package main

import "strings"

// StateType Константа состояния вентиляционной системы.
type StateType string

// String Интерфейс Stringify.
func (sto StateType) String() string { return string(sto) }

// StateParse Разбор строки в тип.
func StateParse(s string) (ret StateType) {
	switch s = strings.ToLower(strings.TrimSpace(s)); s {
	case StateOn.String():
		ret = StateOn
	case StateOff.String():
		ret = StateOff
	default:
		ret = StateUnknown
	}

	return
}

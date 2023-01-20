// Package main
package main

import "strings"

// WorkType Константа режима работы вентиляционной системы.
type WorkType string

// String Интерфейс Stringify.
func (wto WorkType) String() string { return string(wto) }

// WorkParse Разбор строки в тип.
func WorkParse(s string) (ret WorkType) {
	switch s = strings.ToLower(strings.TrimSpace(s)); s {
	case WorkInflow.String():
		ret = WorkInflow
	case WorkRecuperator.String():
		ret = WorkRecuperator
	case WorkInflowMax.String():
		ret = WorkInflowMax
	case WorkWinter.String():
		ret = WorkWinter
	case WorkOutflow.String():
		ret = WorkOutflow
	case WorkOutflowMax.String():
		ret = WorkOutflowMax
	case WorkNight.String():
		ret = WorkNight
	default:
		ret = WorkUnknown
	}

	return
}

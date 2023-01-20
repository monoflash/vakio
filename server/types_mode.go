// Package main
package main

import "strings"

// ModeType Константа режима вентиляционной системы.
type ModeType string

// String Интерфейс Stringify.
func (mto ModeType) String() string { return string(mto) }

// ToState Конвертация режима вентиляционной системы в состояние вентиляционной системы.
func (mto ModeType) ToState(status *status) (ret bool, state StateType, speed uint64, work WorkType) {
	switch mto {
	case ModeOff:
		state, speed, work = StateOff, SpeedOff, status.Work
	case ModeOn:
		state, speed, work = StateOn, status.Speed, status.Work
	case ModeRecuperatorSummer:
		state, speed, work = status.State, status.Speed, WorkRecuperator
	case ModeRecuperatorWinter:
		state, speed, work = status.State, status.Speed, WorkWinter
	case ModeInflow:
		state, speed, work = status.State, status.Speed, WorkInflow
	case ModeInflowMax:
		state, speed, work = status.State, SpeedMax, WorkInflowMax
	case ModeOutflow:
		state, speed, work = status.State, status.Speed, WorkOutflow
	case ModeOutflowMax:
		state, speed, work = status.State, SpeedMax, WorkOutflowMax
	case ModeNight:
		state, speed, work = status.State, status.Speed, WorkNight
	case ModeSpeed1:
		state, speed, work = status.State, Speed1, status.Work
	case ModeSpeed2:
		state, speed, work = status.State, Speed2, status.Work
	case ModeSpeed3:
		state, speed, work = status.State, Speed3, status.Work
	case ModeSpeed4:
		state, speed, work = status.State, Speed4, status.Work
	case ModeSpeed5:
		state, speed, work = status.State, Speed5, status.Work
	case ModeSpeed6:
		state, speed, work = status.State, Speed6, status.Work
	case ModeSpeed7:
		state, speed, work = status.State, Speed7, status.Work
	default:
		return
	}
	ret = true

	return
}

// ModeParse Разбор режима работы в типы.
func ModeParse(s string) (ret ModeType) {
	switch s = strings.ToLower(strings.TrimSpace(s)); s {
	case ModeOff.String():
		ret = ModeOff
	case ModeOn.String():
		ret = ModeOn
	case ModeRecuperatorSummer.String():
		ret = ModeRecuperatorSummer
	case ModeRecuperatorWinter.String():
		ret = ModeRecuperatorWinter
	case ModeInflow.String():
		ret = ModeInflow
	case ModeInflowMax.String():
		ret = ModeInflowMax
	case ModeOutflow.String():
		ret = ModeOutflow
	case ModeOutflowMax.String():
		ret = ModeOutflowMax
	case ModeNight.String():
		ret = ModeNight
	case ModeSpeed1.String():
		ret = ModeSpeed1
	case ModeSpeed2.String():
		ret = ModeSpeed2
	case ModeSpeed3.String():
		ret = ModeSpeed3
	case ModeSpeed4.String():
		ret = ModeSpeed4
	case ModeSpeed5.String():
		ret = ModeSpeed5
	case ModeSpeed6.String():
		ret = ModeSpeed6
	case ModeSpeed7.String():
		ret = ModeSpeed7
	default:
		ret = ModeUnknown
	}

	return
}

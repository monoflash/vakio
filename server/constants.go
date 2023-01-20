// Package main
package main

import "math"

const (
	chanInBuffer  = 1000 // Размер канала входящих сообщений.
	topicSystem   = "vakio/system"
	topicState    = "vakio/state"
	topicSpeed    = "vakio/speed"
	topicWorkmode = "vakio/workmode"
	topicMode     = "vakio/mode"
)

// Константы состояния вентиляционной системы.
const (
	// StateUnknown Неизвестное состояние.
	StateUnknown = StateType("")

	// StateOff Вентиляционная система отключена.
	StateOff = StateType("off")

	// StateOn Вентиляционная система включена.
	StateOn = StateType("on")
)

// Константы режима работы вентиляционной системы.
const (
	// WorkUnknown Неизвестный режим работы вентиляционной системы.
	WorkUnknown = WorkType("")

	// WorkInflow Приток.
	WorkInflow = WorkType("inflow")

	// WorkRecuperator Рекуператор.
	WorkRecuperator = WorkType("recuperator")

	// WorkInflowMax Приток максимальный режим.
	WorkInflowMax = WorkType("inflow_max")

	// WorkWinter Рекуператор зимний режим.
	WorkWinter = WorkType("winter")

	// WorkOutflow Вытяжка.
	WorkOutflow = WorkType("outflow")

	// WorkOutflowMax Вытяжка максимальный режим.
	WorkOutflowMax = WorkType("outflow_max")

	// WorkNight Ночной режим.
	WorkNight = WorkType("night")
)

// Константы скорости работы вентиляционной системы.
const (
	// SpeedOff Вентиляционная система выключена.
	SpeedOff = 0

	// Speed1 Скорость 1.
	Speed1 = 1

	// Speed2 Скорость 2.
	Speed2 = 2

	// Speed3 Скорость 3.
	Speed3 = 3

	// Speed4 Скорость 4.
	Speed4 = 4

	// Speed5 Скорость 5.
	Speed5 = 5

	// Speed6 Скорость 6.
	Speed6 = 6

	// Speed7 Скорость 7.
	Speed7 = 7

	// SpeedMax Максимальная скорость работы вентиляционной системы.
	SpeedMax = math.MaxUint64
)

// Константы режима работы.
const (
	// ModeUnknown Неизвестный режим.
	ModeUnknown = ModeType("")

	// ModeOff Выключить.
	ModeOff = ModeType("06000")

	// ModeOn Включить с предыдущим режимом.
	ModeOn = ModeType("06001")

	// ModeRecuperatorSummer Рекуператор лето.
	ModeRecuperatorSummer = ModeType("06010")

	// ModeRecuperatorWinter Рекуператор зима.
	ModeRecuperatorWinter = ModeType("06011")

	// ModeInflow Приток.
	ModeInflow = ModeType("06021")

	// ModeInflowMax Приток максимальный режим.
	ModeInflowMax = ModeType("06022")

	// ModeOutflow Вытяжка.
	ModeOutflow = ModeType("06031")

	// ModeOutflowMax Вытяжка максимальный режим.
	ModeOutflowMax = ModeType("06032")

	// ModeNight Ночной режим.
	ModeNight = ModeType("06041")

	// ModeSpeed1 Скорость вентиляции. Скорость 1.
	ModeSpeed1 = ModeType("06501")

	// ModeSpeed2 Скорость вентиляции. Скорость 2.
	ModeSpeed2 = ModeType("06502")

	// ModeSpeed3 Скорость вентиляции. Скорость 3.
	ModeSpeed3 = ModeType("06503")

	// ModeSpeed4 Скорость вентиляции. Скорость 4.
	ModeSpeed4 = ModeType("06504")

	// ModeSpeed5 Скорость вентиляции. Скорость 5.
	ModeSpeed5 = ModeType("06505")

	// ModeSpeed6 Скорость вентиляции. Скорость 6.
	ModeSpeed6 = ModeType("06506")

	// ModeSpeed7 Скорость вентиляции. Скорость 7.
	ModeSpeed7 = ModeType("06507")
)

const (
	// CommandUnknown Неизвестная команда.
	CommandUnknown = CommandType("")

	CommandInternalSystem = CommandType("internal_system")

	// CommandFullReset Полный сброс устройства.
	CommandFullReset = CommandType("0608")

	// CommandUpdateFirmware Обновление прошивки и перезагрузка устройства.
	CommandUpdateFirmware = CommandType("0609")

	// CommandReboot Перезагрузка устройства.
	CommandReboot = CommandType("0689")
)

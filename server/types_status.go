// Package main
package main

import (
	"crypto/sha1"
	"hash"
	"strconv"
	"time"
)

type status struct {
	LastActivityAt time.Time   `json:"last_activity_at"` // Дата и время последней активности.
	Available      bool        `json:"available"`        // Доступность вентиляционной системы по IP адресу.
	Speed          uint64      `json:"speed"`            // Скорость вращения вентилятора. 0-Остановлен. math.MaxUint64-Максимальная скорость.
	State          StateType   `json:"state"`            // Константа состояния.
	Work           WorkType    `json:"work"`             // Константа текущего режима.
	Mode           ModeType    `json:"mode"`             // Константа режима одним числом.
	Command        CommandType `json:"command"`          // Последняя команда отправленная или полученная вентиляционной системой.
}

// Hash Вычисление контрольной суммы на основе основных свойств объекта статуса вентиляционной системы.
// Игнорируются:
// - LastActivityAt
// - Mode
// - Command
func (sto status) Hash() (ret hash.Hash) {
	ret = sha1.New()
	if sto.Available {
		ret.Write([]byte("true"))
	} else {
		ret.Write([]byte("false"))
	}
	ret.Write([]byte(strconv.FormatUint(sto.Speed, 10)))
	ret.Write([]byte(sto.State.String()))
	ret.Write([]byte(sto.Work.String()))

	return
}

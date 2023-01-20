// Package main
package main

import (
	"encoding/base64"
)

func (srv *impl) checkStatus() {
	var nowHex string

	if nowHex = base64.URLEncoding.EncodeToString(srv.Status.Hash().Sum(nil)); nowHex != srv.StatusHexHash {
		srv.StatusHexHash = nowHex
		srv.onChangeStatus()
	}
}

// Выбор действия в зависимости от состояния вентиляционной системы.
func (srv *impl) onChangeStatus() {

	//log.Println(debug.DumperString(srv.Status))

}

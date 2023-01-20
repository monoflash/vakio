// Package main
package main

import "strings"

// CommandType Константа системной команды вентиляционной системы.
type CommandType string

// String Интерфейс Stringify.
func (cto CommandType) String() string { return string(cto) }

// CommandParse Разбор системной команды вентиляционной системы в тип.
func CommandParse(s string) (ret CommandType) {
	switch s = strings.ToLower(strings.TrimSpace(s)); s {
	case CommandFullReset.String():
		ret = CommandFullReset
	case CommandUpdateFirmware.String():
		ret = CommandUpdateFirmware
	case CommandReboot.String():
		ret = CommandReboot
	default:
		if strings.HasPrefix(s, "0600") || strings.HasPrefix(s, "0601") {
			ret = CommandInternalSystem
			return
		}
		ret = CommandUnknown
	}

	return
}

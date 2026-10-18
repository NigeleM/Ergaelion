//go:build !darwin && !linux

package lineedit

import (
	"errors"
	"os"
)

// Other platforms fall back to plain line input.

func IsTerminal(f *os.File) bool { return false }

func makeRaw(f *os.File) (func(), error) {
	return nil, errors.New("raw terminal mode is not supported on this platform")
}

// TerminalRows is a fixed default on platforms without terminal size support.
func TerminalRows(f *os.File) int { return 24 }

// TerminalColumns is a fixed default on platforms without terminal size support.
func TerminalColumns(f *os.File) int { return 80 }

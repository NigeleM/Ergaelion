package lineedit

import (
	"fmt"
	"strings"
)

// Splash shows text full screen until Enter or Space (true), or q (false). Off a terminal there is
// nothing to wait for, so it returns true.
func (e *Editor) Splash(text string) bool {
	if !IsTerminal(e.file) {
		return true
	}
	restore, err := makeRaw(e.file)
	if err != nil {
		return true
	}
	defer restore()
	fmt.Fprint(e.out, "\x1b[?1049h\x1b[H\x1b[J"+strings.ReplaceAll(text, "\n", "\r\n")+"\r\n"+
		Highlight+" Press Enter or Space to continue   q quit \x1b[0m")
	defer fmt.Fprint(e.out, "\x1b[?1049l")
	for {
		r, _, err := e.in.ReadRune()
		if err != nil {
			return true
		}
		switch r {
		case '\r', '\n', ' ':
			return true
		case 'q', 3:
			return false
		}
	}
}

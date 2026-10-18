package lineedit

import (
	"fmt"
)

// ErrNotTerminal is returned by Choose when the input is not an interactive terminal.
// Callers should then ask for a typed number instead.
const ErrNotTerminal = -2

// Choose shows a numbered list with the highlighted item moved by the arrow keys. Enter picks the
// highlighted item, a number picks that item directly, and q or Escape cancels. It returns the
// chosen index, -1 if cancelled, or ErrNotTerminal when the input is not a terminal.
func (e *Editor) Choose(title string, items []string) int {
	if !IsTerminal(e.file) {
		return ErrNotTerminal
	}
	restore, err := makeRaw(e.file)
	if err != nil {
		return ErrNotTerminal
	}
	defer restore()

	selected := 0
	fmt.Fprintf(e.out, "%s\r\n", title)
	// draw starts and ends on the first item line, so each redraw overwrites the list in place.
	draw := func(first bool) {
		for i, item := range items {
			fmt.Fprint(e.out, "\r\x1b[2K")
			if i == selected {
				fmt.Fprintf(e.out, "\x1b[1;7m > %d) %s \x1b[0m\r\n", i+1, item)
			} else {
				fmt.Fprintf(e.out, "   %d) %s\r\n", i+1, item)
			}
		}
		fmt.Fprint(e.out, "\r\x1b[2K\x1b[2m  up/down to move, Enter to choose, a number to jump, q to go back\x1b[0m")
		fmt.Fprintf(e.out, "\x1b[%dA", len(items))
	}
	// clearChooser removes the list and hint, leaving the cursor where the list started.
	clearChooser := func() {
		fmt.Fprint(e.out, "\r\x1b[J")
	}
	draw(true)
	for {
		r, _, err := e.in.ReadRune()
		if err != nil {
			return -1
		}
		switch {
		case r == '\r' || r == '\n':
			clearChooser()
			return selected
		case r == 'q' || r == 3:
			clearChooser()
			return -1
		case r >= '1' && r <= '9' && int(r-'1') < len(items):
			clearChooser()
			return int(r - '1')
		case r == 'k':
			selected = (selected - 1 + len(items)) % len(items)
		case r == 'j':
			selected = (selected + 1) % len(items)
		case r == 27:
			switch readEscape(e.in) {
			case "[A", "OA":
				selected = (selected - 1 + len(items)) % len(items)
			case "[B", "OB":
				selected = (selected + 1) % len(items)
			case "":
				clearChooser()
				return -1
			}
		}
		draw(false)
	}
}

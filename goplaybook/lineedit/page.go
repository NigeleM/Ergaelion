package lineedit

import (
	"fmt"
	"strings"
)

// Page shows text one screen at a time with the arrow keys, Page Up and Page Down, Space, g and G.
// q or Escape closes it. Off a terminal, or when the text fits the screen, it is printed as it is.
func (e *Editor) Page(text string) {
	lines := strings.Split(strings.TrimRight(text, "\n"), "\n")
	height := TerminalRows(e.file) - 2
	if height < 5 {
		height = 5
	}
	if !IsTerminal(e.file) || len(lines) <= height {
		fmt.Fprint(e.out, text)
		return
	}
	e.pageLoop(text, false)
}

// pageLoop runs the scrolling view. With force set it shows the view even when the text fits.
func (e *Editor) pageLoop(text string, force bool) {
	lines := strings.Split(strings.TrimRight(text, "\n"), "\n")
	height := TerminalRows(e.file) - 2
	if height < 5 {
		height = 5
	}
	if !force && len(lines) <= height {
		fmt.Fprint(e.out, text)
		return
	}
	restore, err := makeRaw(e.file)
	if err != nil {
		fmt.Fprint(e.out, text)
		return
	}
	defer restore()
	fmt.Fprint(e.out, "\x1b[?1049h")
	defer fmt.Fprint(e.out, "\x1b[?1049l")

	top, maxTop := 0, max(len(lines)-height, 0)
	draw := func() {
		fmt.Fprint(e.out, "\x1b[H\x1b[J")
		for i := top; i < top+height && i < len(lines); i++ {
			fmt.Fprintf(e.out, "%s\r\n", lines[i])
		}
		fmt.Fprintf(e.out, Highlight+" lines %d-%d of %d  up/down, PgUp/PgDn, g/G, q to close \x1b[0m",
			top+1, min(top+height, len(lines)), len(lines))
	}
	clamp := func() {
		if top < 0 {
			top = 0
		}
		if top > maxTop {
			top = maxTop
		}
	}
	draw()
	for {
		r, _, err := e.in.ReadRune()
		if err != nil {
			return
		}
		switch {
		case r == 'q' || r == 3 || r == '\r' || r == '\n':
			return
		case r == 'k':
			top--
		case r == 'j' || r == ' ':
			top += map[bool]int{true: height, false: 1}[r == ' ']
		case r == 'g':
			top = 0
		case r == 'G':
			top = maxTop
		case r == 27:
			switch readEscape(e.in) {
			case "":
				return
			case "[A", "OA":
				top--
			case "[B", "OB":
				top++
			case "[5~":
				top -= height
			case "[6~":
				top += height
			}
		}
		clamp()
		draw()
	}
}

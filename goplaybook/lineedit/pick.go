package lineedit

import (
	"fmt"
	"sort"
	"strings"
)

// Item is one row of a full-screen list: a label, and a detail shown while the row is highlighted.
type Item struct {
	Label  string
	Detail string
}

// remembered holds the row last highlighted in each list, by title, so a menu reopens on the same row.
var remembered = map[string]int{}

// Pick shows a full-screen list. The highlighted item's detail appears below the list, and long lists
// scroll. Enter returns the highlighted item. q or Escape returns -1. Each key in extra (with its
// label) returns that key along with the item. Off a terminal it returns ErrNotTerminal.
func (e *Editor) Pick(title string, items []Item, extra map[string]string) (int, string) {
	if len(items) == 0 || !IsTerminal(e.file) {
		return ErrNotTerminal, ""
	}
	restore, err := makeRaw(e.file)
	if err != nil {
		return ErrNotTerminal, ""
	}
	defer restore()
	fmt.Fprint(e.out, "\x1b[?1049h")
	defer fmt.Fprint(e.out, "\x1b[?1049l")

	hint := "up/down move  PgUp/PgDn page  Enter open  q back"
	extraKeys := make([]string, 0, len(extra))
	for key := range extra {
		extraKeys = append(extraKeys, key)
	}
	sort.Strings(extraKeys)
	for _, key := range extraKeys {
		hint += fmt.Sprintf("  %s %s", key, extra[key])
	}

	selected, top := 0, 0
	if last, ok := remembered[title]; ok && last < len(items) {
		selected = last
	}
	draw := func() {
		remembered[title] = selected
		listRows := TerminalRows(e.file) - 9 - strings.Count(title, "\n")
		if listRows < 3 {
			listRows = 3
		}
		if selected < top {
			top = selected
		}
		if selected >= top+listRows {
			top = selected - listRows + 1
		}
		var b strings.Builder
		b.WriteString("\x1b[H\x1b[J")
		fmt.Fprintf(&b, "%s\r\n\r\n", strings.ReplaceAll(title, "\n", "\r\n"))
		for i := top; i < len(items) && i < top+listRows; i++ {
			if i == selected {
				fmt.Fprintf(&b, Highlight+" > %s \x1b[0m\r\n", items[i].Label)
			} else {
				fmt.Fprintf(&b, "   %s\r\n", items[i].Label)
			}
		}
		b.WriteString("\r\n")
		for _, line := range wrapWords(items[selected].Detail, 96, 4) {
			fmt.Fprintf(&b, Detail+"%s\x1b[0m\r\n", line)
		}
		fmt.Fprintf(&b, Highlight+" %d/%d  %s \x1b[0m", selected+1, len(items), hint)
		fmt.Fprint(e.out, b.String())
	}
	draw()
	for {
		r, _, err := e.in.ReadRune()
		if err != nil {
			return -1, ""
		}
		switch {
		case r == '\r' || r == '\n':
			return selected, ""
		case r == 'q' || r == 3:
			return -1, ""
		case r == 'k':
			selected = (selected - 1 + len(items)) % len(items)
		case r == 'j':
			selected = (selected + 1) % len(items)
		case r == 'g':
			selected = 0
		case r == 'G':
			selected = len(items) - 1
		case r == 27:
			switch seq := readEscape(e.in); seq {
			case "":
				return -1, ""
			case "[A", "OA":
				selected = (selected - 1 + len(items)) % len(items)
			case "[B", "OB":
				selected = (selected + 1) % len(items)
			case "[5~":
				selected = max(selected-(TerminalRows(e.file)-9), 0)
			case "[6~":
				selected = min(selected+(TerminalRows(e.file)-9), len(items)-1)
			}
		default:
			if _, ok := extra[string(r)]; ok {
				return selected, string(r)
			}
		}
		draw()
	}
}

// View shows text full screen, scrollable, until q or Escape. Unlike Page it is shown even when
// it would fit on the screen, so a command's result always gets its own screen.
func (e *Editor) View(text string) {
	if !IsTerminal(e.file) {
		fmt.Fprint(e.out, text)
		return
	}
	e.pageLoop(text, true)
}

// wrapWords splits text into lines of at most width characters, using at most maxLines lines.
func wrapWords(text string, width, maxLines int) []string {
	var lines []string
	line := ""
	for _, word := range strings.Fields(text) {
		if line != "" && len([]rune(line))+1+len([]rune(word)) > width {
			lines = append(lines, line)
			line = word
			if len(lines) == maxLines {
				return lines
			}
		} else if line == "" {
			line = word
		} else {
			line += " " + word
		}
	}
	if line != "" && len(lines) < maxLines {
		lines = append(lines, line)
	}
	return lines
}

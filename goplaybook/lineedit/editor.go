// Package lineedit reads a line from the terminal with editing, history, tab completion, a command
// list that appears when you type '/', a selectable menu, and a pager for long output.
//
// On a terminal it switches input to character-by-character mode. On other input (pipes, files,
// Windows) it falls back to plain lines, so scripts keep working.
package lineedit

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"strings"
)

// maxSuggestions is how many commands the '/' list shows at once.
const maxSuggestions = 8

// Editor reads lines from a file (usually stdin) and writes prompts and echoes to out.
type Editor struct {
	in      *bufio.Reader
	file    *os.File
	out     io.Writer
	history []string
	// Complete returns the candidates that start with the text typed so far. Nil disables Tab and the list.
	Complete func(prefix string) []string
	// CompletePhrase returns known phrases that continue the whole line, tried before Complete. Nil disables it.
	CompletePhrase func(text string) []string
	// Limit is the most history lines kept. Zero means 500.
	Limit int
}

// New makes an editor that reads from file and writes to out.
func New(file *os.File, out io.Writer) *Editor {
	return &Editor{in: bufio.NewReader(file), file: file, out: out, Limit: 500}
}

// File returns the terminal file the editor reads from.
func (e *Editor) File() *os.File { return e.file }

// LoadHistory reads history lines from a file. A missing file is not an error.
func (e *Editor) LoadHistory(path string) error {
	data, err := os.ReadFile(path)
	if os.IsNotExist(err) {
		return nil
	}
	if err != nil {
		return err
	}
	for _, line := range strings.Split(string(data), "\n") {
		if strings.TrimSpace(line) != "" {
			e.history = append(e.history, line)
		}
	}
	e.trimHistory()
	return nil
}

// SaveHistory writes the history to a file, one line per entry.
func (e *Editor) SaveHistory(path string) error {
	e.trimHistory()
	return os.WriteFile(path, []byte(strings.Join(e.history, "\n")+"\n"), 0o644)
}

func (e *Editor) trimHistory() {
	limit := e.Limit
	if limit == 0 {
		limit = 500
	}
	if len(e.history) > limit {
		e.history = e.history[len(e.history)-limit:]
	}
}

// ReadLine shows the prompt and reads one line. ok is false at end of input.
func (e *Editor) ReadLine(prompt string) (line string, ok bool) {
	if IsTerminal(e.file) {
		restore, err := makeRaw(e.file)
		if err == nil {
			defer restore()
			return e.readRaw(prompt)
		}
	}
	fmt.Fprint(e.out, prompt)
	text, err := e.in.ReadString('\n')
	if err != nil && text == "" {
		return "", false
	}
	return strings.TrimRight(text, "\r\n"), true
}

// listOf returns the command list for a line that starts with '/' and has no space yet.
func (e *Editor) listOf(buf []rune) []string {
	if e.Complete == nil || len(buf) == 0 || buf[0] != '/' || strings.ContainsRune(string(buf), ' ') {
		return nil
	}
	matches := e.Complete(string(buf))
	if len(matches) > maxSuggestions {
		matches = matches[:maxSuggestions]
	}
	return matches
}

func (e *Editor) readRaw(prompt string) (string, bool) {
	var buf []rune
	pos := 0
	index := len(e.history)
	saved := ""
	selected := 0
	shown := 0 // lines of the command list currently drawn below the prompt

	render := func() {
		list := e.listOf(buf)
		if selected >= len(list) {
			selected = 0
		}
		fmt.Fprintf(e.out, "\r\x1b[2K%s%s\x1b[J", prompt, string(buf))
		for i, item := range list {
			if i == selected {
				fmt.Fprintf(e.out, "\r\n"+Highlight+" %s \x1b[0m", item)
			} else {
				fmt.Fprintf(e.out, "\r\n  %s", item)
			}
		}
		if len(list) > 0 {
			fmt.Fprintf(e.out, "\x1b[%dA", len(list))
		}
		shown = len(list)
		column := visibleWidth(prompt) + pos + 1
		fmt.Fprintf(e.out, "\r\x1b[%dC", column-1)
		if column-1 == 0 {
			fmt.Fprint(e.out, "\r")
		}
	}
	clearList := func() {
		if shown > 0 {
			fmt.Fprint(e.out, "\x1b[J")
			shown = 0
		}
	}
	render()
	for {
		r, _, err := e.in.ReadRune()
		if err != nil {
			clearList()
			fmt.Fprint(e.out, "\r\n")
			return "", false
		}
		list := e.listOf(buf)
		switch r {
		case '\r', '\n':
			clearList()
			fmt.Fprint(e.out, "\r\n")
			line := string(buf)
			if strings.TrimSpace(line) != "" && (len(e.history) == 0 || e.history[len(e.history)-1] != line) {
				e.history = append(e.history, line)
				e.trimHistory()
			}
			return line, true
		case 3: // Ctrl-C: abandon this line
			clearList()
			fmt.Fprint(e.out, "^C\r\n")
			return "", true
		case 4: // Ctrl-D: end of input on an empty line, otherwise delete under the cursor
			if len(buf) == 0 {
				clearList()
				fmt.Fprint(e.out, "\r\n")
				return "", false
			}
			buf, pos = deleteAt(buf, pos)
		case 127, 8: // Backspace
			if pos > 0 {
				buf, pos = deleteAt(buf, pos-1)
			}
		case 1: // Ctrl-A
			pos = 0
		case 5: // Ctrl-E
			pos = len(buf)
		case 11: // Ctrl-K
			buf = buf[:pos]
		case 21: // Ctrl-U
			buf = buf[pos:]
			pos = 0
		case 9: // Tab: accept the highlighted command, or complete the word
			if len(list) > 0 {
				chosen := []rune(list[selected] + " ")
				buf = chosen
				pos = len(buf)
				selected = 0
				break
			}
			var shownList []string
			buf, pos, shownList = completeInput(buf, pos, e.Complete, e.CompletePhrase)
			if len(shownList) > 0 {
				clearList()
				fmt.Fprintf(e.out, "\r\n%s\r\n", strings.Join(shownList, "   "))
				shown = 0
			}
		case 27: // escape sequences
			seq := readEscape(e.in)
			switch seq {
			case "[A", "OA": // up: move in the command list, or back through history
				if len(list) > 0 {
					selected = (selected - 1 + len(list)) % len(list)
				} else if index > 0 {
					if index == len(e.history) {
						saved = string(buf)
					}
					index--
					buf = []rune(e.history[index])
					pos = len(buf)
				}
			case "[B", "OB": // down
				if len(list) > 0 {
					selected = (selected + 1) % len(list)
				} else if index < len(e.history) {
					index++
					if index == len(e.history) {
						buf = []rune(saved)
					} else {
						buf = []rune(e.history[index])
					}
					pos = len(buf)
				}
			case "[C", "OC":
				if pos < len(buf) {
					pos++
				}
			case "[D", "OD":
				if pos > 0 {
					pos--
				}
			case "[H", "OH", "[1~":
				pos = 0
			case "[F", "OF", "[4~":
				pos = len(buf)
			case "[3~":
				if pos < len(buf) {
					buf, pos = deleteAt(buf, pos)
				}
			}
		default:
			if r >= 32 && r != 127 {
				buf = append(buf[:pos], append([]rune{r}, buf[pos:]...)...)
				pos++
				selected = 0
			}
		}
		render()
	}
}

func deleteAt(buf []rune, pos int) ([]rune, int) {
	return append(buf[:pos], buf[pos+1:]...), pos
}

// readEscape reads the rest of an escape sequence such as "[A" (up arrow) or "[3~" (Delete).
func readEscape(in *bufio.Reader) string {
	first, _, err := in.ReadRune()
	if err != nil || (first != '[' && first != 'O') {
		return ""
	}
	seq := string(first)
	for {
		c, _, err := in.ReadRune()
		if err != nil {
			break
		}
		seq += string(c)
		if (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || c == '~' {
			break
		}
	}
	return seq
}

// completeInput tries whole-phrase completion first when the cursor is at the end of a command-free line,
// then falls back to completing the word at the cursor. It mirrors Editor._complete_word in gtplaybook/lineedit.py.
func completeInput(buf []rune, pos int, complete func(prefix string) []string, phrase func(text string) []string) ([]rune, int, []string) {
	if phrase != nil && pos == len(buf) && (len(buf) == 0 || buf[0] != '/') {
		typed := string(buf[:pos])
		if phrases := phrase(typed); len(phrases) > 0 {
			if len(phrases) == 1 {
				return []rune(phrases[0]), len([]rune(phrases[0])), nil
			}
			if common := commonPrefix(phrases); len(common) > len(typed) {
				return []rune(common), len([]rune(common)), nil
			}
			return buf, pos, phrases
		}
	}
	return CompleteAt(buf, pos, complete)
}

// CompleteAt completes the word that ends at the cursor. It returns the new text, the new cursor
// position, and any candidates to list when the completion is ambiguous and cannot be extended.
// It is a pure function, so it can be tested without a terminal.
func CompleteAt(buf []rune, pos int, complete func(prefix string) []string) ([]rune, int, []string) {
	if complete == nil {
		return buf, pos, nil
	}
	start := pos
	for start > 0 && buf[start-1] != ' ' {
		start--
	}
	prefix := string(buf[start:pos])
	matches := complete(prefix)
	if len(matches) == 0 {
		return buf, pos, nil
	}
	replacement := commonPrefix(matches)
	if len(matches) == 1 {
		replacement = matches[0] + " "
	}
	if len(replacement) <= len(prefix) {
		if len(matches) == 1 {
			return buf, pos, nil
		}
		return buf, pos, matches
	}
	rest := append([]rune{}, buf[pos:]...)
	out := append(append(append([]rune{}, buf[:start]...), []rune(replacement)...), rest...)
	return out, start + len([]rune(replacement)), nil
}

func commonPrefix(words []string) string {
	prefix := words[0]
	for _, w := range words[1:] {
		for !strings.HasPrefix(w, prefix) {
			prefix = prefix[:len(prefix)-1]
		}
	}
	return prefix
}

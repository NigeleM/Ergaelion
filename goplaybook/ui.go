package main

import (
	"fmt"
	"os"
	"regexp"
	"strings"
	"unicode/utf8"
)

// sgrPattern matches a colour escape sequence, which takes no columns on screen.
var sgrPattern = regexp.MustCompile("\x1b\\[[0-9;]*m")

// visibleWidth is the number of columns s takes on screen, not counting colour codes.
func visibleWidth(s string) int {
	return utf8.RuneCountInString(sgrPattern.ReplaceAllString(s, ""))
}

// Colour is only used when stdout is a terminal and NO_COLOR is not set, so
// piped or redirected output stays plain text.
var colorOn = detectColor()

func detectColor() bool {
	if os.Getenv("NO_COLOR") != "" {
		return false
	}
	info, err := os.Stdout.Stat()
	if err != nil {
		return false
	}
	return info.Mode()&os.ModeCharDevice != 0
}

const reset = "\x1b[0m"

// roleCodes holds the escape sequence for each colour role. An empty string means no colour.
var roleCodes = map[string]string{}

func init() {
	applyTheme(themes["classic"], nil)
}

func style(code, s string) string {
	if !colorOn || s == "" || code == "" {
		return s
	}
	return code + s + reset
}

func sgr(value *int) string {
	if value == nil {
		return ""
	}
	return fmt.Sprintf("\x1b[38;5;%dm", *value)
}

func plain(s string) string       { return s }
func bold(s string) string        { return style("\x1b[1m", s) }
func dim(s string) string         { return style("\x1b[2m", s) }
func good(s string) string        { return style(roleCodes["good"], s) }
func bad(s string) string         { return style(roleCodes["bad"], s) }
func mid(s string) string         { return style(roleCodes["mid"], s) }
func green(s string) string       { return good(s) }
func red(s string) string         { return bad(s) }
func accentStyle(s string) string { return style(roleCodes["accent"], s) }

// heading is the section title used throughout the session, in the accent colour.
func heading(s string) string { return style("\x1b[1m"+roleCodes["accent"], "▸ "+s) }

// box draws plain text inside a rounded border. The border is coloured with
// border; the text stays unstyled so padding is computed on visible characters.
// The plain theme draws the border with ASCII characters, for old terminals and fonts.
func box(lines []string, border func(string) string) string {
	if border == nil {
		border = accentStyle
	}
	tl, tr, bl, br, horiz, side := "╭", "╮", "╰", "╯", "─", "│"
	if currentThemeName == "plain" {
		tl, tr, bl, br, horiz, side = "+", "+", "+", "+", "-", "|"
	}
	w := 0
	for _, l := range lines {
		if n := visibleWidth(l); n > w {
			w = n
		}
	}
	var b strings.Builder
	b.WriteString(border(tl+strings.Repeat(horiz, w+2)+tr) + "\n")
	for _, l := range lines {
		pad := w - visibleWidth(l)
		b.WriteString(border(side) + " " + l + strings.Repeat(" ", pad) + " " + border(side) + "\n")
	}
	b.WriteString(border(bl + strings.Repeat(horiz, w+2) + br))
	return b.String()
}

package lineedit

import "regexp"

var ansiSequence = regexp.MustCompile(`\x1b\[[0-9;]*[A-Za-z]`)

// visibleWidth is the number of columns a string takes on screen, ignoring colour codes.
func visibleWidth(s string) int {
	plain := ansiSequence.ReplaceAllString(s, "")
	n := 0
	for range plain {
		n++
	}
	return n
}

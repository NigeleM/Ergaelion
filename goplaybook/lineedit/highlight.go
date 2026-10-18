package lineedit

// Highlight starts a highlighted menu item, and Detail starts the detail line under a menu. The main
// package sets both from the colour theme; they are empty when colour is off.
var (
	Highlight = "\x1b[7m"
	Detail    = "\x1b[2m"
)

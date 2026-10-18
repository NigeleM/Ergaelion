package main

import (
	"encoding/json"
	"fmt"
	"goplaybook/lineedit"
	"os"
	"path/filepath"
	"strconv"
	"strings"
)

// themeColours maps a colour role to a 256-colour number. A nil value means no colour.
type themeColours map[string]*int

// themeFile is the saved theme, theme.json in the playbook home. It has the same shape as the
// Python version writes, so either version reads the other's file.
type themeFile struct {
	Name   string       `json:"name"`
	Colors themeColours `json:"colors,omitempty"`
}

var themeNames = []string{"classic", "ocean", "forest", "contrast", "sunset", "midnight", "rose", "matrix", "paper", "claude-dark", "claude-light", "plain", "mono"}
var roleNames = []string{"accent", "good", "bad", "mid"}

var currentThemeName = "classic"

var themes = map[string]themeColours{
	"classic":      {"accent": intp(208), "good": intp(34), "bad": intp(160), "mid": intp(245)},
	"ocean":        {"accent": intp(39), "good": intp(43), "bad": intp(203), "mid": intp(111)},
	"forest":       {"accent": intp(70), "good": intp(76), "bad": intp(166), "mid": intp(143)},
	"contrast":     {"accent": intp(226), "good": intp(46), "bad": intp(196), "mid": intp(255)},
	"sunset":       {"accent": intp(209), "good": intp(220), "bad": intp(161), "mid": intp(180)},
	"midnight":     {"accent": intp(105), "good": intp(117), "bad": intp(210), "mid": intp(146)},
	"rose":         {"accent": intp(204), "good": intp(151), "bad": intp(124), "mid": intp(250)},
	"matrix":       {"accent": intp(46), "good": intp(40), "bad": intp(196), "mid": intp(22)},
	"paper":        {"accent": intp(94), "good": intp(64), "bad": intp(124), "mid": intp(137)},
	"claude-dark":  {"accent": intp(173), "good": intp(114), "bad": intp(167), "mid": intp(246)},
	"claude-light": {"accent": intp(166), "good": intp(28), "bad": intp(160), "mid": intp(241)},
	"plain":        {"accent": intp(250), "good": intp(252), "bad": intp(250), "mid": intp(245)},
	"mono":         {"accent": nil, "good": nil, "bad": nil, "mid": nil},
}

var colourNames = map[string]*int{
	"black": intp(16), "grey": intp(245), "white": intp(255), "red": intp(196), "green": intp(46),
	"yellow": intp(226), "blue": intp(33), "magenta": intp(201), "cyan": intp(51), "orange": intp(208),
	"purple": intp(135), "none": nil,
}

func intp(v int) *int { return &v }

// roleValues holds the 256-colour number of each role, or nil for no colour.
var roleValues = map[string]*int{}

// applyTheme sets the escape sequence for each role from the base theme, then any overrides.
func applyTheme(base, overrides themeColours) {
	for _, role := range roleNames {
		value := base[role]
		if o, ok := overrides[role]; ok {
			value = o
		}
		roleValues[role] = value
		roleCodes[role] = sgr(value)
	}
	lineedit.Highlight = roleCodes["accent"] + "\x1b[7m"
	lineedit.Detail = roleCodes["mid"]
	if !colorOn {
		lineedit.Highlight, lineedit.Detail = "\x1b[7m", "\x1b[2m"
	}
}

var standardHex = []string{"#000000", "#800000", "#008000", "#808000", "#000080", "#800080", "#008080", "#c0c0c0",
	"#808080", "#ff0000", "#00ff00", "#ffff00", "#0000ff", "#ff00ff", "#00ffff", "#ffffff"}

// xtermHex is the hex colour of a 256-colour number, for charts.
func xtermHex(n int) string {
	if n < 16 {
		return standardHex[n]
	}
	if n >= 232 {
		level := 8 + 10*(n-232)
		return fmt.Sprintf("#%02x%02x%02x", level, level, level)
	}
	steps := []int{0, 95, 135, 175, 215, 255}
	index := n - 16
	return fmt.Sprintf("#%02x%02x%02x", steps[index/36], steps[(index/6)%6], steps[index%6])
}

// roleHex is the hex colour for a role in the current theme, or the fallback when it has no colour.
func roleHex(role, fallback string) string {
	if value := roleValues[role]; value != nil {
		return xtermHex(*value)
	}
	return fallback
}

// outcomeColours returns the win, loss, draw and mixed colours, with light tints for fills.
func outcomeColours() map[string]string {
	win, loss := roleHex("good", "#16a34a"), roleHex("bad", "#dc2626")
	draw, mixed := roleHex("mid", "#9ca3af"), roleHex("accent", "#f59e0b")
	return map[string]string{
		"win": win, "loss": loss, "draw": draw, "mixed": mixed,
		"win_light": mixColour(win, "#ffffff", 0.6), "loss_light": mixColour(loss, "#ffffff", 0.6),
		"draw_light": mixColour(draw, "#ffffff", 0.7),
	}
}

// themeFilePath is where the saved theme lives.
func themeFilePath(home string) string {
	return filepath.Join(home, "theme.json")
}

func readThemeFile(home string) (themeFile, bool) {
	var f themeFile
	data, err := os.ReadFile(themeFilePath(home))
	if err != nil {
		return f, false
	}
	if err := json.Unmarshal(data, &f); err != nil {
		return f, false
	}
	return f, true
}

// loadTheme applies the saved theme. A missing or unreadable file keeps the classic theme.
func loadTheme(home string) {
	f, ok := readThemeFile(home)
	if !ok {
		return
	}
	name := f.Name
	if _, known := themes[name]; !known {
		name = "classic"
	}
	currentThemeName = name
	overrides := themeColours{}
	for role, value := range f.Colors {
		if !contains(roleNames, role) {
			continue
		}
		if value == nil || (*value >= 0 && *value <= 255) {
			overrides[role] = value
		}
	}
	applyTheme(themes[name], overrides)
}

// saveTheme writes a theme name, or colour overrides, to theme.json, then applies them.
func saveTheme(home, name string, colours themeColours) error {
	f, _ := readThemeFile(home)
	if name != "" {
		f = themeFile{Name: name, Colors: themeColours{}}
	}
	if colours != nil {
		if f.Name == "" {
			f.Name = "classic"
		}
		if f.Colors == nil {
			f.Colors = themeColours{}
		}
		for role, value := range colours {
			f.Colors[role] = value
		}
	}
	if err := os.MkdirAll(home, 0o755); err != nil {
		return err
	}
	data, err := json.MarshalIndent(f, "", "  ")
	if err != nil {
		return err
	}
	if err := os.WriteFile(themeFilePath(home), append(data, '\n'), 0o644); err != nil {
		return err
	}
	loadTheme(home)
	return nil
}

func resetTheme(home string) error {
	if err := os.Remove(themeFilePath(home)); err != nil && !os.IsNotExist(err) {
		return err
	}
	currentThemeName = "classic"
	applyTheme(themes["classic"], nil)
	return nil
}

// parseColour accepts a colour name such as red or cyan, or a number from 0 to 255.
func parseColour(text string) (*int, error) {
	key := strings.ToLower(strings.TrimSpace(text))
	if value, ok := colourNames[key]; ok {
		return value, nil
	}
	if n, err := strconv.Atoi(key); err == nil && n >= 0 && n <= 255 {
		return intp(n), nil
	}
	return nil, fmt.Errorf("'%s' is not a colour. Use a name such as red or cyan, or a number from 0 to 255.", text)
}

func showTheme() {
	fmt.Println("\n" + bold("Theme: ") + currentThemeName)
	labels := map[string]string{"accent": "accent", "good": "victory", "bad": "failure", "mid": "draw"}
	stylers := map[string]func(string) string{"accent": accentStyle, "good": good, "bad": bad, "mid": mid}
	home := PlaybookHome()
	f, _ := readThemeFile(home)
	active := themes[currentThemeName]
	for _, role := range roleNames {
		value := active[role]
		if o, ok := f.Colors[role]; ok {
			value = o
		}
		shown := "none"
		if value != nil {
			shown = strconv.Itoa(*value)
		}
		fmt.Println("  " + cell(role, 8, plain) + cell(labels[role], 10, stylers[role]) + dim("colour "+shown))
	}
	fmt.Println(dim("\nThemes: " + strings.Join(themeNames, ", ") + ".  Change with 'theme <name>', or 'theme set <role> <colour>'."))
	fmt.Println(dim("Roles: accent, good, bad, mid.  Colours: a name such as red, cyan or orange, or a number 0-255."))
	fmt.Println(dim("Reset to the default with 'theme reset'.  Turn colour off for one run with NO_COLOR=1."))
}

// cmdTheme shows or changes the look of the terminal: theme, theme <name>, theme set <role> <colour>, theme reset.
func cmdTheme(args []string) error {
	home := PlaybookHome()
	if len(args) == 0 {
		showTheme()
		return nil
	}
	words := make([]string, len(args))
	for i, a := range args {
		words[i] = strings.ToLower(a)
	}
	if len(words) == 1 && words[0] == "reset" {
		if err := resetTheme(home); err != nil {
			return err
		}
		fmt.Println(dim("Theme reset to classic."))
		showTheme()
		return nil
	}
	if words[0] == "set" {
		if len(words) != 3 || !contains(roleNames, words[1]) {
			return fmt.Errorf("use: theme set <accent|good|bad|mid> <colour>")
		}
		value, err := parseColour(words[2])
		if err != nil {
			return err
		}
		if err := saveTheme(home, "", themeColours{words[1]: value}); err != nil {
			return err
		}
		showTheme()
		return nil
	}
	if len(words) == 1 {
		if _, ok := themes[words[0]]; ok {
			if err := saveTheme(home, words[0], nil); err != nil {
				return err
			}
			showTheme()
			return nil
		}
	}
	return fmt.Errorf("'%s' is not a theme. Themes: %s.", strings.Join(args, " "), strings.Join(themeNames, ", "))
}

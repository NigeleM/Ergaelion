package main

import (
	"fmt"
	"os"
	"strings"

	"goplaybook/lineedit"
)

// The main menu. Each entry opens its own full-screen list, with a description of the highlighted
// item. Results open full screen too, and q returns to the list that was open.

var menuKeys = []string{"menu_games", "menu_simulations", "menu_advise", "menu_solve", "menu_areas",
	"menu_guide", "menu_records", "menu_repeat", "menu_claude", "menu_theme", "menu_quit"}

var menuDetails = map[string]string{
	"menu_games": "detail_games", "menu_simulations": "detail_simulations", "menu_advise": "detail_advise",
	"menu_solve": "detail_solve", "menu_areas": "detail_areas", "menu_guide": "detail_guide",
	"menu_records": "detail_records", "menu_repeat": "detail_repeat",
	"menu_theme": "detail_theme", "menu_command": "detail_command", "menu_claude": "detail_claude",
	"menu_quit": "detail_quit",
}

// quoteArg wraps text so the session's word splitting keeps it as one argument.
func quoteArg(text string) string {
	return "'" + strings.ReplaceAll(text, "'", `'\''`) + "'"
}

// captureCommand runs a session command with its output captured, and returns that output.
func captureCommand(fn func() (bool, error)) (string, bool, error) {
	tmp, err := os.CreateTemp("", "playbook-view-*.txt")
	if err != nil {
		quit, runErr := fn()
		return "", quit, runErr
	}
	defer os.Remove(tmp.Name())
	original := os.Stdout
	os.Stdout = tmp
	quit, runErr := fn()
	os.Stdout = original
	tmp.Close()
	raw, _ := os.ReadFile(tmp.Name())
	return string(raw), quit, runErr
}

// runView runs a command and shows its result full screen until the user presses q.
func runView(s *session, line string) {
	text, _, err := captureCommand(func() (bool, error) { return s.command(line) })
	if err != nil {
		text += red("✗ "+err.Error()) + "\n"
	}
	lineEditor().View(text)
}

// runPlain runs an interactive command directly on the terminal, then waits for Enter.
func runPlain(s *session, line string) {
	fmt.Print("\x1b[?1049l\x1b[H\x1b[2J")
	if _, err := s.command(line); err != nil {
		fmt.Println(red("✗ " + err.Error()))
	}
	askLine(dim("\n" + t("press_enter") + " "))
}

// clearScreen wipes the screen before asking a question on its own.
func clearScreen() {
	fmt.Print("\x1b[H\x1b[2J")
}

// wordmark is the name in three rows of block letters: bigger than plain text, with no artwork.
var wordmark = []string{
	"█▀▀ █▀█ █▀▀ ▄▀█ █   █▀▀ ▀█▀ ▄▀▄ █▄ █",
	"█▀  █▀▄ █▄█ █▀█ █   █▀   █  █ █ █ ▀█",
	"█▄▄ ▀ ▀ ▀▀▀ ▀ ▀ █▄▄ █▄▄ ▄█▄ ▀▄▀ ▀  ▀",
}

// appBoxLines is the text inside the green app box: the name in block letters, then the version.
func appBoxLines() []string {
	cols := 80
	if file := lineEditor().File(); lineedit.IsTerminal(file) {
		cols = lineedit.TerminalColumns(file)
	}
	width := min(cols, 120) - 4
	rows := make([]string, 0, len(wordmark)+1)
	for _, row := range wordmark {
		rows = append(rows, bold(accentStyle(row)))
	}
	rows = append(rows, "  "+dim("Game Theory Playbook")+"  v"+version)
	for i, row := range rows {
		rows[i] = row + strings.Repeat(" ", max(0, width-visibleWidth(row)))
	}
	return rows
}

// menuTitle is the green app box above the main menu.
func menuTitle() string {
	return box(appBoxLines(), green) + "\n" + heading(t("menu_title"))
}

// runMenu opens the main menu from the prompt: backing out returns to the prompt.
func runMenu(s *session) bool {
	return runMenuWith(s, false)
}

// runMenuWith runs the main menu. backQuits is true at launch, where backing out means leaving the program.
func runMenuWith(s *session, backQuits bool) bool {
	entries := append([]string{"menu_command"}, menuKeys...)
	for {
		items := make([]lineedit.Item, len(entries))
		for i, key := range entries {
			label := t(key)
			if i > 0 {
				label = fmt.Sprintf("%d) %s", i, t(key))
			}
			items[i] = lineedit.Item{Label: label, Detail: t(menuDetails[key])}
		}
		idx, _ := lineEditor().Pick(menuTitle(), items, nil)
		if idx == lineedit.ErrNotTerminal {
			return runMenuTyped(s)
		}
		if idx < 0 {
			return backQuits
		}
		switch entries[idx] {
		case "menu_command":
			return false
		case "menu_games":
			menuGames(s)
		case "menu_simulations":
			menuSimulations(s)
		case "menu_advise":
			clearScreen()
			if text := askLine(t("ask_situation") + ": "); text != "" {
				runView(s, "advise -d "+quoteArg(text))
			}
		case "menu_solve":
			clearScreen()
			if text := askLine(t("ask_matrix") + ": "); text != "" {
				runView(s, "solve "+quoteArg(text))
			}
		case "menu_areas":
			menuFamilies(s)
		case "menu_guide":
			menuGuide(s)
		case "menu_records":
			menuRecords(s)
		case "menu_repeat":
			menuRepeat(s)
		case "menu_claude":
			menuClaude(s)
		case "menu_theme":
			menuTheme(s)
		case "menu_quit":
			return true
		}
	}
}

func gameItems(games []Game) []lineedit.Item {
	items := make([]lineedit.Item, len(games))
	for i, g := range games {
		items[i] = lineedit.Item{Label: g.Name, Detail: g.Summary + " " + dim(g.Category)}
	}
	return items
}

func menuGames(s *session) {
	items := gameItems(s.games)
	for {
		idx, _ := lineEditor().Pick(heading(t("pick_game")), items, nil)
		if idx < 0 || idx == lineedit.ErrNotTerminal {
			return
		}
		runView(s, "show "+quoteArg(s.games[idx].ID))
	}
}

func menuSimulations(s *session) {
	sims, err := LoadSimulations()
	if err != nil {
		return
	}
	items := make([]lineedit.Item, len(sims))
	for i, sim := range sims {
		items[i] = lineedit.Item{Label: sim.Name, Detail: sim.Summary + " " + t("works_across") + ": " + strings.Join(sim.Families, ", ")}
	}
	extra := map[string]string{"p": t("play")}
	for {
		idx, key := lineEditor().Pick(heading(t("pick_sim")), items, extra)
		if idx < 0 || idx == lineedit.ErrNotTerminal {
			return
		}
		if key == "p" {
			runPlain(s, "sim "+quoteArg(sims[idx].ID)+" --play")
			continue
		}
		runView(s, "sim "+quoteArg(sims[idx].ID))
	}
}

func menuFamilies(s *session) {
	areas, err := LoadAreas()
	if err != nil {
		return
	}
	items := make([]lineedit.Item, len(areas))
	for i, f := range areas {
		items[i] = lineedit.Item{Label: f.Family, Detail: f.Summary}
	}
	extra := map[string]string{"p": t("problems")}
	for {
		idx, key := lineEditor().Pick(heading(t("pick_family")), items, extra)
		if idx < 0 || idx == lineedit.ErrNotTerminal {
			return
		}
		if key == "p" {
			runView(s, "problems")
			continue
		}
		runView(s, "areas "+quoteArg(areas[idx].Family))
	}
}

func menuGuide(s *session) {
	items := []lineedit.Item{
		{Label: t("guide_power"), Detail: t("detail_guide")},
		{Label: t("guide_defend"), Detail: t("detail_guide")},
		{Label: t("research_steps"), Detail: t("detail_guide")},
		{Label: t("guide_life"), Detail: t("detail_guide")},
		{Label: t("setup_game"), Detail: t("pick_setup")},
	}
	sections := []string{"power", "defend", "research", "life"}
	for {
		idx, _ := lineEditor().Pick(heading(t("pick_guide")), items, nil)
		if idx < 0 || idx == lineedit.ErrNotTerminal {
			return
		}
		if idx < len(sections) {
			runView(s, "guide "+sections[idx])
			continue
		}
		game, ok := pickGame(s, t("pick_setup"))
		if ok {
			runView(s, "setup "+quoteArg(game.ID))
		}
	}
}

func pickGame(s *session, title string) (Game, bool) {
	idx, _ := lineEditor().Pick(heading(title), gameItems(s.games), nil)
	if idx < 0 || idx == lineedit.ErrNotTerminal {
		return Game{}, false
	}
	return s.games[idx], true
}

func menuRecords(s *session) {
	items := []lineedit.Item{
		{Label: t("my_records"), Detail: t("detail_records")},
		{Label: t("record_chart"), Detail: t("detail_records")},
		{Label: t("play_chart"), Detail: t("detail_records")},
	}
	commands := []string{"record", "chart records", "chart plays"}
	for {
		idx, _ := lineEditor().Pick(heading(t("menu_records")), items, nil)
		if idx < 0 || idx == lineedit.ErrNotTerminal {
			return
		}
		runView(s, commands[idx])
	}
}

// themeDetails describes each built-in theme on the theme screen.
var themeDetails = map[string]string{
	"classic":      "Orange headings, green victories, red failures, grey draws.",
	"ocean":        "Blue headings, cyan victories, coral failures, soft yellow draws.",
	"forest":       "Green headings, bright green victories, rust failures, olive draws.",
	"contrast":     "Bright yellow headings, vivid green and red, white draws.",
	"sunset":       "Coral headings, gold victories, plum failures, tan draws.",
	"midnight":     "Lavender headings, sky-blue victories, pink failures, slate draws.",
	"rose":         "Pink headings, sage victories, deep red failures, pale draws.",
	"matrix":       "Bright green headings and victories, red failures, dark green draws.",
	"paper":        "Brown headings, olive victories, red failures, tan draws.",
	"claude-dark":  "Dark background with Claude's warm orange headings, soft green wins, clay-red losses.",
	"claude-light": "For light backgrounds: deep orange headings, forest green wins, brick-red losses.",
	"plain":        "Neutral grey colours with plain ASCII box edges, for old terminals and fonts.",
	"mono":         "No colour: bold headings only, for plain or high-contrast screens.",
}

// menuRepeat picks a game with a payoff table, how many rounds, and the bot to play against.
func menuRepeat(s *session) {
	var items []lineedit.Item
	var games []Game
	for _, g := range s.games {
		if g.Matrix != nil {
			games = append(games, g)
			items = append(items, lineedit.Item{Label: g.Name, Detail: g.Summary})
		}
	}
	idx, _ := lineEditor().Pick(heading(t("pick_repeat")), items, nil)
	if idx < 0 {
		return
	}
	var botItems []lineedit.Item
	for _, name := range repeatOpponents {
		botItems = append(botItems, lineedit.Item{Label: name, Detail: repeatDescriptions[name]})
	}
	botIdx, _ := lineEditor().Pick(heading(t("pick_bot")), botItems, nil)
	if botIdx < 0 {
		return
	}
	rounds := askLine(t("ask_rounds") + " [10]: ")
	if rounds == "" {
		rounds = "10"
	}
	s.command("repeat " + quoteArg(games[idx].ID) + " --rounds " + rounds + " --opponent " + repeatOpponents[botIdx] + " --log")
}

// menuClaude asks Claude about a game, a simulation or the situation, or switches it on or off.
func menuClaude(s *session) {
	options := []lineedit.Item{
		{Label: t("claude_game"), Detail: t("detail_claude_game")},
		{Label: t("claude_sim"), Detail: t("detail_claude_sim")},
		{Label: t("claude_scenario"), Detail: t("detail_claude_scenario")},
		{Label: t("claude_on"), Detail: t("detail_claude_on")},
		{Label: t("claude_off"), Detail: t("detail_claude_off")},
	}
	for {
		idx, _ := lineEditor().Pick(heading(t("menu_claude")), options, nil)
		if idx < 0 || idx == lineedit.ErrNotTerminal {
			return
		}
		switch idx {
		case 0:
			gameIdx, _ := lineEditor().Pick(heading(t("pick_game")), gameItems(s.games), nil)
			if gameIdx < 0 || gameIdx == lineedit.ErrNotTerminal {
				continue
			}
			if q := menuQuestion(); q != "" {
				runView(s, "claude game "+quoteArg(s.games[gameIdx].ID)+" "+quoteArg(q))
			}
		case 1:
			sims, err := LoadSimulations()
			if err != nil {
				fmt.Println(red("✗ " + err.Error()))
				continue
			}
			items := make([]lineedit.Item, len(sims))
			for i, sim := range sims {
				items[i] = lineedit.Item{Label: sim.Name, Detail: sim.Summary}
			}
			simIdx, _ := lineEditor().Pick(heading(t("pick_sim")), items, nil)
			if simIdx < 0 || simIdx == lineedit.ErrNotTerminal {
				continue
			}
			if q := menuQuestion(); q != "" {
				runView(s, "claude sim "+quoteArg(sims[simIdx].ID)+" "+quoteArg(q))
			}
		case 2:
			if q := menuQuestion(); q != "" {
				runView(s, "claude scenario "+quoteArg(q))
			}
		case 3:
			runView(s, "claude on")
		default:
			runView(s, "claude off")
		}
	}
}

// menuQuestion asks for one question inside the Claude menu. It clears the screen first.
func menuQuestion() string {
	clearScreen()
	return askLine(t("ask_claude_question") + ": ")
}

func menuTheme(s *session) {
	var items []lineedit.Item
	for _, name := range themeNames {
		items = append(items, lineedit.Item{Label: name, Detail: themeDetails[name]})
	}
	idx, _ := lineEditor().Pick(heading(t("pick_theme")), items, nil)
	if idx >= 0 {
		s.command("theme " + themeNames[idx])
	}
}

// runMenuTyped is the numbered menu used when the input is not an interactive terminal. It asks the
// same questions as the Python version, so scripted sessions behave the same in both.
func runMenuTyped(s *session) bool {
	for {
		fmt.Println("\n" + heading(t("menu_title")))
		fmt.Printf("  0) %s\n", t("menu_command"))
		for i, key := range menuKeys {
			fmt.Printf("  %d) %s\n", i+1, t(key))
		}
		raw, ok := readInput(accentStyle("❯ ") + t("menu_prompt") + ": ")
		if !ok {
			fmt.Println()
			return true
		}
		choice := strings.TrimSpace(raw)
		if choice == "" || choice == "0" || choice == "b" {
			return false
		}
		if choice == "11" {
			return true
		}
		line := ""
		switch choice {
		case "1":
			if text := askLine(t("ask_game") + ": "); text != "" {
				line = "show " + quoteArg(text)
			} else {
				line = "list"
			}
		case "2":
			if text := askLine(t("ask_sim") + ": "); text == "" {
				line = "sim"
			} else {
				line = map[string]string{
					"1": "sim " + quoteArg(text),
					"2": "sim " + quoteArg(text) + " --play",
					"3": "sim " + quoteArg(text) + " --matrix",
					"4": "sim " + quoteArg(text) + " --matrix --play",
				}[askLine(t("ask_sim_mode")+": ")]
			}
		case "3":
			if text := askLine(t("ask_situation") + ": "); text != "" {
				line = "advise -d " + quoteArg(text)
			}
		case "4":
			if text := askLine(t("ask_matrix") + ": "); text != "" {
				line = "solve " + quoteArg(text)
			}
		case "5":
			if text := askLine(t("ask_query") + ": "); text != "" {
				line = "problems " + quoteArg(text)
			} else {
				line = "areas"
			}
		case "6":
			mode := askLine(t("ask_guide") + ": ")
			if mode == "1" {
				line = strings.TrimSpace("guide " + askLine(t("ask_guide_section")+": "))
			} else if mode == "2" {
				if text := askLine(t("ask_game") + ": "); text != "" {
					line = "setup " + quoteArg(text)
				}
			}
		case "7":
			line = map[string]string{"1": "record", "2": "chart records", "3": "chart plays"}[askLine(t("ask_records")+": ")]
		case "8":
			text := askLine(t("ask_game") + ": ")
			rounds := askLine(t("ask_rounds") + " [10]: ")
			if rounds == "" {
				rounds = "10"
			}
			bot := askLine(t("pick_bot") + " (" + strings.Join(repeatOpponents, ", ") + "): ")
			if text != "" && bot != "" {
				line = "repeat " + quoteArg(text) + " --rounds " + rounds + " --opponent " + bot + " --log"
			}
		case "9":
			if text := askLine(t("ask_claude_question") + ": "); text != "" {
				line = "claude ask " + quoteArg(text)
			} else {
				line = "claude status"
			}
		case "10":
			if name := askLine(t("pick_theme") + " (" + strings.Join(themeNames, ", ") + "): "); name != "" {
				line = "theme " + name
			}
		}
		if line == "" {
			fmt.Println(red("  Nothing to run. Choose again."))
			continue
		}
		if _, err := s.command(line); err != nil {
			fmt.Println(red("✗ " + err.Error()))
		}
	}
}

// askLine asks one question inside a menu and returns the trimmed answer, or "" at end of input.
func askLine(prompt string) string {
	line, ok := readInput(prompt)
	if !ok {
		return ""
	}
	return strings.TrimSpace(line)
}

// runMenuProgram starts the program on the menu, used by 'playbook menu'.
// runMenuProgram starts on the menu: the default in a terminal, and 'playbook menu'. The Command prompt
// entry, or Esc, goes to the prompt. Quit leaves the program.
func runMenuProgram(games []Game) int {
	save := setupLineEditing(games)
	defer save()
	if !lineEditor().Splash(box(appBoxLines(), green) + "\n") {
		return 0
	}
	s := &session{games: games, sc: newScenario()}
	if runMenuWith(s, true) {
		return 0
	}
	printBanner()
	return runREPLLoop(s)
}

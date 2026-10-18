package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// session holds the state of one interactive run: the current situation and
// the game catalogue it is matched against.
type session struct {
	games []Game
	sc    *Scenario
}

// runREPL is the interactive session. Plain text describes a
// situation; lines starting with '/' are commands.
// slashCommands are the words Tab completes after a '/'.
var slashCommands = []string{"/list", "/show", "/advise", "/set", "/unset", "/scenario", "/clear", "/solve", "/new",
	"/template", "/areas", "/log", "/record", "/edit", "/add-play", "/sim", "/problems", "/setup", "/guide", "/chart",
	"/disable", "/enable", "/check", "/unlog", "/theme", "/repeat", "/keywords", "/claude", "/menu", "/cls", "/help", "/quit"}

// setupLineEditing loads history from the playbook home and sets up Tab completion.
// The returned function saves the history when the session ends.
func setupLineEditing(games []Game) func() {
	ed := lineEditor()
	historyFile := filepath.Join(PlaybookHome(), "history")
	_ = ed.LoadHistory(historyFile)
	kw, _ := loadKeywords()
	combos, _ := loadCombinations()
	vocabulary := completionWords(games, kw, combos)
	known := phrases(kw, combos)
	ed.CompletePhrase = func(text string) []string {
		return completePhrase(text, known)
	}
	ed.Complete = func(prefix string) []string {
		var out []string
		if strings.HasPrefix(prefix, "/") || prefix == "" {
			for _, w := range slashCommands {
				if strings.HasPrefix(w, prefix) {
					out = append(out, w)
				}
			}
			return out
		}
		for _, g := range games {
			if strings.HasPrefix(g.ID, prefix) {
				out = append(out, g.ID)
			}
		}
		return append(out, completeWord(prefix, vocabulary, 12)...)
	}
	return func() {
		_ = os.MkdirAll(PlaybookHome(), 0o755)
		_ = ed.SaveHistory(historyFile)
	}
}

// runREPL is what 'playbook' with no arguments does: the menu in a terminal, the prompt when input is piped.
func runREPL(games []Game) int {
	if stdinIsTerminal() {
		return runMenuProgram(games)
	}
	printBanner()
	save := setupLineEditing(games)
	defer save()
	return runREPLLoop(&session{games: games, sc: newScenario()})
}

// runREPLLoop reads and runs lines until the user quits.
func runREPLLoop(s *session) int {
	for {
		line, ok := readInput(accentStyle("❯ "))
		if !ok {
			fmt.Println()
			return 0
		}
		if line == "" {
			continue
		}
		if strings.HasPrefix(line, "/") {
			quit, err := runPaged(line, func() (bool, error) { return s.command(line[1:]) })
			if quit {
				return 0
			}
			if err != nil {
				fmt.Println(red("✗ " + err.Error()))
			}
			continue
		}
		_, err := runPaged(line, func() (bool, error) { return false, s.describe(line) })
		if err != nil {
			fmt.Println(red("✗ " + err.Error()))
		}
	}
}

// interactiveCommands ask questions or run a game, so their output must not be captured.
var interactiveCommands = map[string]bool{"menu": true, "new": true, "cls": true}

// shouldPage reports whether a command's output can be captured and scrolled. Commands that ask
// questions, play a game or save one print straight to the terminal.
func shouldPage(line string) bool {
	fields := strings.Fields(line)
	if len(fields) == 0 {
		return false
	}
	if interactiveCommands[strings.TrimPrefix(fields[0], "/")] {
		return false
	}
	for _, f := range fields {
		if f == "--play" || f == "--resume" || f == "--save" {
			return false
		}
	}
	return true
}

// runPaged runs a command with its output captured, then shows it through the pager if it is long.
func runPaged(line string, run func() (bool, error)) (bool, error) {
	if !shouldPage(line) {
		return run()
	}
	tmp, err := os.CreateTemp("", "playbook-output-*.txt")
	if err != nil {
		return run()
	}
	defer os.Remove(tmp.Name())
	original := os.Stdout
	os.Stdout = tmp
	quit, runErr := run()
	os.Stdout = original
	tmp.Close()
	raw, readErr := os.ReadFile(tmp.Name())
	if readErr != nil {
		return quit, runErr
	}
	lineEditor().Page(string(raw))
	return quit, runErr
}

func printBanner() {
	lines := append(appBoxLines(),
		"",
		"Describe a situation in plain English, or type /help.",
		"Type /menu to browse games, simulations, advice, solving and more.",
	)
	fmt.Println(box(lines, green))
	fmt.Println(dim("  e.g.  two companies set prices at the same time, once only"))
	fmt.Println()
}

// describe reads a plain-English situation, replaces the current one, and advises.
func (s *session) describe(text string) error {
	if _, err := FindGame(s.games, text); err == nil {
		return cmdShow([]string{text}, s.games)
	}
	sc := Describe(text)
	s.sc = sc
	showInferred(sc)
	return printAdvice(sc, s.games, 3)
}

// command runs one slash command. quit is true when the session should end.
func (s *session) command(line string) (quit bool, err error) {
	parts, err := shellSplit(line)
	if err != nil {
		return false, err
	}
	if len(parts) == 0 {
		return false, nil
	}
	name, args := parts[0], parts[1:]
	switch name {
	case "help", "h", "?":
		printHelp()
	case "quit", "exit", "q":
		return true, nil
	case "areas":
		return false, cmdAreas(args, s.games)
	case "log":
		return false, cmdLog(args, s.games)
	case "record":
		return false, cmdRecord(args, s.games)
	case "edit":
		return false, cmdEdit(args, s.games)
	case "add-play":
		return false, cmdAddPlay(args, s.games)
	case "sim":
		return false, cmdSim(args, s.games)
	case "setup":
		return false, cmdSetup(args, s.games)
	case "guide":
		return false, cmdGuide(args, s.games)
	case "disable":
		return false, cmdDisable(args, s.games)
	case "enable":
		return false, cmdEnable(args, s.games)
	case "check":
		return false, cmdCheck(args, s.games)
	case "unlog":
		return false, cmdUnlog(args, s.games)
	case "chart":
		return false, cmdChart(args, s.games)
	case "theme":
		return false, cmdTheme(args)
	case "keywords":
		return false, cmdKeywords(args, s.games)
	case "repeat":
		return false, cmdRepeat(args, s.games)
	case "menu":
		return runMenu(s), nil
	case "problems":
		return false, cmdProblems(args, s.games)
	case "list":
		return false, cmdList(args, s.games)
	case "show":
		return false, cmdShow(args, s.games)
	case "template":
		fmt.Print(Template)
	case "solve":
		return false, cmdSolve(args)
	case "new":
		return false, cmdNew(args, s.games)
	case "clear":
		s.sc = newScenario()
		fmt.Println(dim("Situation cleared."))
	case "claude":
		return false, s.claude(args)
	case "cls":
		clearScreen()
		printBanner()
	case "scenario":
		s.showScenario()
	case "set":
		if len(args) == 0 {
			return false, fmt.Errorf("usage: /set key=value [key=value ...]")
		}
		if err := applySets(s.sc, args); err != nil {
			return false, err
		}
		return false, printAdvice(s.sc, s.games, 3)
	case "unset":
		if len(args) == 0 {
			return false, fmt.Errorf("usage: /unset key [key ...]")
		}
		for _, key := range args {
			delete(s.sc.Traits, strings.ToLower(key))
		}
		return false, printAdvice(s.sc, s.games, 3)
	case "advise":
		if len(args) > 0 {
			sc, err := loadScenarioFile(args[0])
			if err != nil {
				return false, err
			}
			s.sc = sc
		}
		return false, printAdvice(s.sc, s.games, 3)
	default:
		return false, fmt.Errorf("unknown command /%s. Type /help for the list", name)
	}
	return false, nil
}

// claude handles /claude on|off|status, then ask, game, sim or scenario. Off unless switched on.
func (s *session) claude(args []string) error {
	action, rest := "help", []string{}
	if len(args) > 0 {
		action, rest = args[0], args[1:]
	}
	switch action {
	case "on", "off":
		if err := claudeSetOn(action == "on", ""); err != nil {
			return err
		}
		if action == "on" {
			fmt.Println(bold("Claude is on.") + " Questions go to Anthropic when you ask one, nothing else is sent.")
			fmt.Println(dim("Sent with each question: your question, and the text of the game, simulation or situation you named."))
			fmt.Println(dim("Model: " + claudeModel() + ". Type /claude off to stop."))
		} else {
			fmt.Println(dim("Claude is off. Nothing is sent."))
		}
	case "status":
		on, key := "off", "not set"
		if claudeIsOn("") {
			on = "on"
		}
		if claudeAPIKey() != "" {
			key = "set"
		}
		fmt.Printf("Claude: %s · key: %s · model: %s\n", on, key, claudeModel())
	case "ask":
		return s.askClaude(strings.Join(rest, " "), []claudePart{{"Situation", s.situationText()}})
	case "game":
		if len(rest) == 0 {
			return fmt.Errorf("usage: /claude game <game> <question>")
		}
		game, err := FindGame(s.games, rest[0])
		if err != nil {
			return err
		}
		return s.askClaude(strings.Join(rest[1:], " "), []claudePart{{"Game", claudeGamePart(game)}})
	case "sim":
		if len(rest) < 2 {
			return fmt.Errorf("usage: /claude sim <simulation> <question>")
		}
		sims, err := LoadSimulations()
		if err != nil {
			return err
		}
		sim, err := FindSimulation(sims, rest[0])
		if err != nil {
			return err
		}
		return s.askClaude(strings.Join(rest[1:], " "), []claudePart{{"Simulation", claudeSimulationPart(sim)}})
	case "scenario":
		if len(s.sc.Traits) == 0 && s.sc.Text == "" {
			return fmt.Errorf("describe a situation first, then ask /claude scenario <question>")
		}
		kw, _ := loadKeywords()
		hits := RankGames(s.games, s.sc.Traits, s.sc.Domains, 3, tallyOrEmpty(), s.sc.Text, kw)
		var gameTexts []string
		for _, hit := range hits {
			if hit.Score > 0 {
				gameTexts = append(gameTexts, claudeGamePart(hit.Game))
			}
		}
		situation := s.sc.Text
		if situation == "" {
			situation = formatTraits(s.sc.Traits)
		}
		return s.askClaude(strings.Join(rest, " "), []claudePart{{"Situation and matching games",
			claudeScenarioPart(situation, strings.Join(gameTexts, "\n\n"))}})
	default:
		fmt.Println(bold("Claude help"))
		for _, line := range []string{"/claude on | off | status", "/claude ask <question>      the current situation and your question",
			"/claude game <game> <question>", "/claude sim <simulation> <question>",
			"/claude scenario <question>   the current situation with its top matching games"} {
			fmt.Println("  " + line)
		}
	}
	return nil
}

// situationText is the current situation as plain text, or an empty string when none is set.
func (s *session) situationText() string {
	var parts []string
	if s.sc.Text != "" {
		parts = append(parts, s.sc.Text)
	}
	if len(s.sc.Traits) > 0 {
		parts = append(parts, formatTraits(s.sc.Traits))
	}
	return strings.Join(parts, "\n")
}

func (s *session) askClaude(question string, parts []claudePart) error {
	if strings.TrimSpace(question) == "" {
		return fmt.Errorf("type a question after the command")
	}
	if err := claudeCheckReady(""); err != nil {
		return err
	}
	answer, sent, err := claudeAsk(question, parts, "")
	if err != nil {
		return err
	}
	fmt.Println(dim(fmt.Sprintf("Sent %d characters to %s.", sent, claudeModel())))
	fmt.Println("\n" + heading("Claude"))
	lines := strings.Split(answer, "\n")
	for i, line := range lines {
		if strings.TrimSpace(line) != "" {
			lines[i] = paragraph(line)
		} else {
			lines[i] = ""
		}
	}
	fmt.Println(strings.Join(lines, "\n"))
	return nil
}

func (s *session) showScenario() {
	if len(s.sc.Traits) == 0 {
		fmt.Println(dim("No situation yet. Describe one in plain English, or use /set key=value."))
		return
	}
	title := s.sc.Title
	if title == "" {
		title = "Current situation"
	}
	fmt.Println(bold(title))
	fmt.Println(dim(formatTraits(s.sc.Traits)))
	if len(s.sc.Domains) > 0 {
		fmt.Println(dim("domains: " + strings.Join(s.sc.Domains, ", ")))
	}
}

func printHelp() {
	fmt.Println("\n" + heading(t("commands")))
	rows := [][2]string{
		{"/list [domain]", "list games, optionally for one domain"},
		{"/show <game>", "explain a game and its playbook"},
		{"/advise [file.gt]", "rank games for the current or a loaded situation"},
		{"/set key=value ...", "set or override traits on the current situation"},
		{"/unset key ...", "remove traits from the current situation"},
		{"/scenario", "show the current situation"},
		{"/solve \"a,b c,d; …\"", "analyse a payoff matrix"},
		{"/new [file.gt]", "build a scenario file with guided prompts"},
		{"/template", "print the scenario file syntax"},
		{"/clear", "forget the current situation"},
		{"/help", "show this list"},
		{"/menu", "open the full menu: games, simulations, advice, solving, Claude, colours"},
		{"/cls", "clear the screen and show the banner again"},
		{"/claude on|ask|game|sim|scenario", "ask Claude about a game or simulation (opt-in)"},
		{"/quit", "leave the session"},
	}
	for _, r := range rows {
		fmt.Println("  " + cell(r[0], 26, bold) + dim(r[1]))
	}
	fmt.Println("\n" + dim("Or just type a situation in plain English. The playbook matches it to games and gives the rules to play."))
}

// shellSplit splits a command line into words, honouring single and double quotes,
// so /solve "3,3 0,5; 5,0 1,1" arrives as one argument.
func shellSplit(s string) ([]string, error) {
	var out []string
	var cur strings.Builder
	var quote rune
	started := false
	for _, r := range s {
		switch {
		case quote != 0:
			if r == quote {
				quote = 0
			} else {
				cur.WriteRune(r)
			}
		case r == '"' || r == '\'':
			quote = r
			started = true
		case r == ' ' || r == '\t':
			if cur.Len() > 0 || started {
				out = append(out, cur.String())
				cur.Reset()
				started = false
			}
		default:
			cur.WriteRune(r)
		}
	}
	if quote != 0 {
		return nil, fmt.Errorf("unclosed quote")
	}
	if cur.Len() > 0 || started {
		out = append(out, cur.String())
	}
	return out, nil
}

// Command playbook is a terminal tool that identifies the game behind a situation
// and tells you how to play it. It runs offline from a single binary.
//
// With no arguments it opens an interactive session: describe a situation in
// plain English, or type a slash command such as /list, /show or /solve.
// The same commands are also available as subcommands for scripting:
//
//	playbook                       interactive session
//	playbook list --domain military
//	playbook show chicken
//	playbook advise scenario.gt
//	playbook advise -d "two companies set prices at the same time, once"
//	playbook solve "3,3 0,5; 5,0 1,1" --rows Cooperate,Defect --cols Cooperate,Defect
//	playbook new my-situation.gt
//	playbook template
package main

import (
	_ "embed"
	"encoding/json"
	"flag"
	"fmt"
	"math/big"
	"os"
	"strings"
	"time"
	"unicode/utf8"

	"goplaybook/lineedit"
)

// version is set at build time from the release tag: -ldflags "-X main.version=1.2.3".
var version = "1.0.0"

var editor *lineedit.Editor

// lineEditor returns the shared line editor, creating it on first use.
func lineEditor() *lineedit.Editor {
	if editor == nil {
		editor = lineedit.New(os.Stdin, os.Stdout)
	}
	return editor
}

func main() {
	loadTheme(PlaybookHome())
	if len(os.Args) > 1 && os.Args[1] == "check" {
		if err := cmdCheck(nil, nil); err != nil {
			os.Exit(1)
		}
		return
	}
	games, err := LoadGames()
	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}
	args := os.Args[1:]
	if len(args) == 0 {
		os.Exit(runREPL(games))
	}
	if args[0] == "menu" {
		os.Exit(runMenuProgram(games))
	}
	if args[0] != "sim" {
		for _, a := range args {
			if a == "--export" {
				os.Exit(runWithExport(args, games))
			}
		}
	}
	os.Exit(run(args, games))
}

func run(args []string, games []Game) int {
	var err error
	switch args[0] {
	case "list":
		err = cmdList(args[1:], games)
	case "show":
		err = cmdShow(args[1:], games)
	case "advise":
		err = cmdAdvise(args[1:], games)
	case "solve":
		err = cmdSolve(args[1:])
	case "new":
		err = cmdNew(args[1:], games)
	case "areas":
		err = cmdAreas(args[1:], games)
	case "topics":
		err = cmdTopics(args[1:], games)
	case "log":
		err = cmdLog(args[1:], games)
	case "record":
		err = cmdRecord(args[1:], games)
	case "edit":
		err = cmdEdit(args[1:], games)
	case "add-play":
		err = cmdAddPlay(args[1:], games)
	case "sim":
		err = cmdSim(args[1:], games)
	case "engine":
		err = cmdEngine(args[1:], games)
	case "setup":
		err = cmdSetup(args[1:], games)
	case "guide":
		err = cmdGuide(args[1:], games)
	case "disable":
		err = cmdDisable(args[1:], games)
	case "enable":
		err = cmdEnable(args[1:], games)
	case "check":
		err = cmdCheck(args[1:], games)
	case "unlog":
		err = cmdUnlog(args[1:], games)
	case "theme":
		err = cmdTheme(args[1:])
	case "keywords":
		err = cmdKeywords(args[1:], games)
	case "tools":
		err = cmdTools(args[1:])
	case "tool":
		err = cmdTool(args[1:], games)
	case "repeat":
		err = cmdRepeat(args[1:], games)
	case "chart":
		err = cmdChart(args[1:], games)
	case "menu":
		os.Exit(runMenuProgram(games))
	case "problems":
		err = cmdProblems(args[1:], games)
	case "template":
		fmt.Print(Template)
	case "version", "--version":
		fmt.Println("playbook", version)
	case "help", "-h", "--help":
		usage()
	default:
		fmt.Fprintf(os.Stderr, "unknown command %q\n\n", args[0])
		usage()
		return 2
	}
	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		return 1
	}
	return 0
}

//go:embed data/help.txt
var helpText string

// usage prints the complete help. The same text is in data/help.txt for the Python version.
func usage() {
	fmt.Print(helpText)
}

// parseArgs lets flags and positional arguments appear in any order, which the
// standard flag package does not. valueFlags names the flags that take a value.
// A token that starts with '-' but is not a known flag is kept as positional,
// so a payoff matrix such as "-1,0 2,-3; ..." still parses.
func parseArgs(fs *flag.FlagSet, args []string, valueFlags ...string) ([]string, error) {
	var flags, positional []string
	for i := 0; i < len(args); i++ {
		a := args[i]
		if !strings.HasPrefix(a, "-") {
			positional = append(positional, a)
			continue
		}
		name := strings.TrimLeft(a, "-")
		if f := fs.Lookup(name); f != nil {
			if bf, ok := f.Value.(interface{ IsBoolFlag() bool }); ok && bf.IsBoolFlag() {
				flags = append(flags, a)
				continue
			}
		}
		if base, _, hasEq := strings.Cut(name, "="); hasEq {
			if contains(valueFlags, base) {
				flags = append(flags, a)
				continue
			}
			positional = append(positional, a)
			continue
		}
		if contains(valueFlags, name) && i+1 < len(args) {
			flags = append(flags, a, args[i+1])
			i++
			continue
		}
		positional = append(positional, a)
	}
	if err := fs.Parse(flags); err != nil {
		return nil, err
	}
	return positional, nil
}

// Repeated --set flags are collected into a slice.
type multiFlag []string

func (m *multiFlag) String() string     { return strings.Join(*m, ",") }
func (m *multiFlag) Set(v string) error { *m = append(*m, v); return nil }

func cmdList(args []string, games []Game) error {
	fs := flag.NewFlagSet("list", flag.ContinueOnError)
	domain := fs.String("domain", "", "only games that fit this domain")
	search := fs.String("search", "", "text to look for across all game fields")
	if _, err := parseArgs(fs, args, "domain", "search"); err != nil {
		return err
	}
	if *domain != "" && !contains(DomainNames, *domain) {
		return fmt.Errorf("unknown domain %q; choose from %s", *domain, strings.Join(DomainNames, ", "))
	}
	var selected []Game
	for _, g := range games {
		if *domain != "" && !contains(g.Domains, *domain) {
			continue
		}
		if *search != "" && !strings.Contains(strings.ToLower(gameText(g)), strings.ToLower(*search)) {
			continue
		}
		selected = append(selected, g)
	}
	// Columns are as wide as the longest entry in this list, so nothing overflows and nothing is wasted.
	idWidth, nameWidth := 0, 0
	for _, g := range selected {
		idWidth = max(idWidth, utf8.RuneCountInString(g.ID))
		nameWidth = max(nameWidth, utf8.RuneCountInString(g.Name))
	}
	for _, g := range selected {
		fmt.Printf("%s%s%s\n", cell(g.ID, idWidth+2, bold), cell(g.Name, nameWidth+2, plain), dim(g.Category))
	}
	fmt.Println()
	fmt.Println(dim(fmt.Sprintf("%d game(s). Run 'show <id>' for its playbook.", len(selected))))
	return nil
}

// gameText concatenates the searchable fields of a game.
func gameText(g Game) string {
	parts := []string{g.ID, g.Name, g.Category, g.Summary, g.HowItWorks}
	parts = append(parts, g.Examples...)
	parts = append(parts, g.Strategies...)
	parts = append(parts, g.Pitfalls...)
	return strings.Join(parts, " ")
}

func cmdShow(args []string, games []Game) error {
	formats := ""
	var pos []string
	for i := 0; i < len(args); i++ {
		if args[i] == "--formats" && i+1 < len(args) {
			formats = args[i+1]
			i++
			continue
		}
		pos = append(pos, args[i])
	}
	if len(pos) != 1 {
		return fmt.Errorf("show takes one game id or name")
	}
	found, err := FindGame(games, pos[0])
	if err != nil {
		return err
	}
	g := found
	name, summary := g.Name, g.Summary
	fmt.Printf("\n%s  %s\n\n", bold(name), dim("["+g.Category+"]"))
	fmt.Println(paragraph(summary))
	fmt.Println("\n" + heading(t("how_it_works")))
	fmt.Println(paragraph(g.HowItWorks))
	fmt.Println("\n" + dim("Traits: "+formatTraits(g.Traits)))
	fmt.Println(dim("Domains: " + strings.Join(g.Domains, ", ")))
	if len(g.Examples) > 0 {
		fmt.Println("\n" + heading(t("scenarios_fit")))
		for _, e := range g.Examples {
			fmt.Println(bullet(e, "•"))
		}
	}
	if g.Matrix != nil {
		fmt.Println("\n" + heading(t("reference_matrix")))
		printGrid(g.Matrix.Rows, g.Matrix.Cols, intsToCells(g.Matrix.Payoffs), nil, nil, nil)
		if note := g.MatrixNote; note != "" {
			fmt.Println(dim(paragraph(note)))
		}
	} else if g.MatrixUnavailable != "" {
		fmt.Println("\n" + heading("Payoff table"))
		fmt.Println(dim(paragraph("No table: " + g.MatrixUnavailable)))
	}
	fmt.Println("\n" + heading(t("how_to_play")))
	for i, rule := range g.Strategies {
		fmt.Println(bullet(rule, fmt.Sprintf("%d.", i+1)))
	}
	if len(g.Pitfalls) > 0 {
		fmt.Println("\n" + heading(t("pitfalls")))
		for _, p := range g.Pitfalls {
			fmt.Println(bullet(p, "•"))
		}
	}
	if len(g.Sources) > 0 {
		fmt.Println("\n" + heading(t("sources")))
		for _, s := range g.Sources {
			fmt.Println(bullet(s, "•"))
		}
	}
	fmt.Println("\n" + dim(t("verify_note")))
	if formats != "" {
		chosen, err := parseFormats(formats)
		if err != nil {
			return err
		}
		folder, written, err := writeGame(*g, chosen, PlaybookHome(), time.Now())
		if err != nil {
			return err
		}
		fmt.Println(dim("Exported to " + folder + ": " + strings.Join(written, ", ")))
	}
	return nil
}

func cmdAdvise(args []string, games []Game) error {
	fs := flag.NewFlagSet("advise", flag.ContinueOnError)
	describe := fs.String("d", "", "plain-English description of the situation")
	fs.StringVar(describe, "describe", "", "plain-English description of the situation")
	top := fs.Int("top", 3, "how many games to rank")
	var sets multiFlag
	fs.Var(&sets, "set", "set or override a trait, e.g. --set timing=sequential (repeatable)")
	positional, err := parseArgs(fs, args, "d", "describe", "top", "set")
	if err != nil {
		return err
	}
	sc, err := scenarioFromArgs(positional, *describe)
	if err != nil {
		return err
	}
	if err := applySets(sc, sets); err != nil {
		return err
	}
	return printAdvice(sc, games, *top)
}

// scenarioFromArgs builds a scenario from a file, a description, or an empty one.
func scenarioFromArgs(positional []string, describeText string) (*Scenario, error) {
	switch {
	case len(positional) > 0:
		return loadScenarioFile(positional[0])
	case describeText != "":
		sc := Describe(describeText)
		showInferred(sc)
		return sc, nil
	}
	return newScenario(), nil
}

func newScenario() *Scenario {
	return &Scenario{Traits: map[string]string{}}
}

func loadScenarioFile(path string) (*Scenario, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	return ParseScenario(string(data))
}

// applySets validates KEY=VALUE overrides and stores them on the scenario.
func applySets(sc *Scenario, sets []string) error {
	for _, item := range sets {
		key, value, ok := strings.Cut(item, "=")
		if !ok {
			return fmt.Errorf("expected KEY=VALUE, got '%s'", item)
		}
		key = strings.ToLower(strings.TrimSpace(key))
		v, err := Normalise(key, value)
		if err != nil {
			return err
		}
		sc.Traits[key] = v
	}
	return nil
}

// printAdvice ranks games for a scenario and prints the best fits, the general
// rules that apply, and the playbook of the top game. Both the advise subcommand
// and the interactive session use it.
func printAdvice(sc *Scenario, games []Game, top int) error {
	if len(sc.Traits) == 0 && len(sc.Domains) == 0 && sc.Text == "" {
		return fmt.Errorf("no traits yet: describe a situation, or use /set key=value")
	}
	records := tallyOrEmpty()
	kw, _ := loadKeywords()
	combos, _ := loadCombinations()
	text, corrections := correctText(sc.Text, completionWords(games, kw, combos))
	sc.Text = text
	hits := RankGames(games, sc.Traits, sc.Domains, top, records, text, kw)
	if len(sc.Traits) == 0 && len(sc.Domains) == 0 && (len(hits) == 0 || hits[0].Score == 0) {
		if len(matchedCombinations(text, combos)) > 0 {
			printCombined(sc, games, hits)
			return nil
		}
		lines, err := keywordSuggestion(text, games)
		if err != nil {
			return err
		}
		for _, line := range lines {
			fmt.Println(line)
		}
		return nil
	}
	title := sc.Title
	if title == "" {
		title = "Scenario"
	}
	fmt.Println("\n" + bold(title))
	if len(sc.Traits) > 0 {
		fmt.Println(dim(formatTraits(sc.Traits)))
	}
	if len(sc.Domains) > 0 {
		fmt.Println(dim("domains: " + strings.Join(sc.Domains, ", ")))
	}
	if len(sc.Traits) == 0 && len(sc.Domains) > 0 {
		fmt.Println(dim("Only the domain matched. Add traits with /set for sharper advice."))
	}
	if len(corrections) > 0 {
		fmt.Println(dim("Reading your words as: " + text))
	}
	fmt.Println("\n" + heading(t("best_fit")))
	for i, hit := range hits {
		fmt.Printf("\n%s %s  %s\n", bold(fmt.Sprintf("%d.", i+1)), bold(hit.Game.Name), dim(fmt.Sprintf("fit %+.1f", hit.Score)))
		if len(hit.Phrases) > 0 {
			fmt.Println(green(bullet("phrases: "+strings.Join(hit.Phrases, ", "), "+")))
		}
		if len(hit.Words) > 0 {
			fmt.Println(green(bullet("shared words: "+strings.Join(hit.Words, ", "), "+")))
		}
		if len(hit.Matched) > 0 {
			fmt.Println(green(bullet("agrees on: "+strings.Join(hit.Matched, ", "), "+")))
		}
		if len(hit.Clashed) > 0 {
			fmt.Println(red(bullet("differs on: "+strings.Join(hit.Clashed, ", "), "−")))
		}
		if line := recordLine(hit.Game.ID); line != "" {
			effect := ""
			if hit.Adjustment != 0 {
				effect = fmt.Sprintf(", your results adjust the fit by %+.1f", hit.Adjustment)
			}
			fmt.Println(dim(t("your_record") + ": " + line + effect))
		}
		fmt.Println(dim(paragraph(hit.Game.Summary)))
	}
	if len(hits) == 0 || hits[0].Score < 1 {
		fmt.Println("\n" + red("The match is weak. Add traits with /set, or describe the situation in more detail."))
		suggestSpelling(sc.Text, games, kw)
	}
	printCombined(sc, games, hits)

	fmt.Println("\n" + heading(t("rules_here")))
	for _, rule := range GeneralRules(sc.Traits) {
		fmt.Println(bullet(rule, "•"))
	}
	if len(hits) > 0 {
		top := hits[0].Game
		fmt.Println("\n" + heading(t("playbook_for", "name", top.Name)))
		for i, step := range top.Strategies {
			fmt.Println(bullet(step, fmt.Sprintf("%d.", i+1)))
		}
	}
	return nil
}

func showInferred(sc *Scenario) {
	fmt.Println("\n" + heading(t("reading")))
	if len(sc.Traits) == 0 && len(sc.Domains) == 0 {
		fmt.Println(bullet("nothing recognised", "•"))
	}
	for _, key := range Traits {
		value, ok := sc.Traits[key]
		if !ok {
			continue
		}
		fmt.Println(bullet(fmt.Sprintf("%s = %s  %s", key, value, dim("(matched '"+sc.Evidence[key]+"')")), "•"))
	}
	for _, domain := range sc.Domains {
		fmt.Println(bullet("domain = "+domain, "•"))
	}
	fmt.Println(dim("Override any trait with /set key=value."))
}

func cmdSolve(args []string) error {
	fs := flag.NewFlagSet("solve", flag.ContinueOnError)
	rowsFlag := fs.String("rows", "", "comma-separated names for your actions")
	colsFlag := fs.String("cols", "", "comma-separated names for their actions")
	jsonFlag := fs.Bool("json", false, "print the solution as JSON")
	positional, err := parseArgs(fs, args, "rows", "cols")
	if err != nil {
		return err
	}
	if len(positional) != 1 {
		return fmt.Errorf(`solve takes one quoted matrix, e.g. "3,3 0,5; 5,0 1,1"`)
	}
	m, err := ParseMatrix(positional[0])
	if err != nil {
		return err
	}
	rows, err := actionNames(*rowsFlag, len(m), "R")
	if err != nil {
		return err
	}
	cols, err := actionNames(*colsFlag, len(m[0]), "C")
	if err != nil {
		return err
	}
	if *jsonFlag {
		data, err := json.MarshalIndent(solveJSON(m, rows, cols), "", "  ")
		if err != nil {
			return err
		}
		fmt.Println(string(data))
		return nil
	}
	analysis := Analyse(m)
	fmt.Println("\n" + heading(t("payoff_matrix")))
	printGrid(rows, cols, ratCells(m), analysis.Equilibria,
		droppedSet(analysis.Eliminated, "row"), droppedSet(analysis.Eliminated, "col"))
	printSolution(analysis, rows, cols, m)
	if len(m) <= 4 && len(m[0]) <= 4 {
		fmt.Println("\n" + heading(t("every_equilibrium")))
		eqs := SupportEquilibria(m)
		for n, e := range eqs {
			var you, them []string
			for i, x := range e.Row {
				if x.Sign() != 0 {
					you = append(you, fmt.Sprintf("%s %s", rows[i], percent(x)))
				}
			}
			for j, x := range e.Col {
				if x.Sign() != 0 {
					them = append(them, fmt.Sprintf("%s %s", cols[j], percent(x)))
				}
			}
			fmt.Println(bullet(fmt.Sprintf("equilibrium %d: you %s; them %s", n+1, strings.Join(you, ", "), strings.Join(them, ", ")), "•"))
		}
		if len(eqs) == 0 {
			fmt.Println(bullet("none found", "•"))
		}
	}
	return nil
}

func actionNames(text string, count int, prefix string) ([]string, error) {
	if text == "" {
		names := make([]string, count)
		for i := range names {
			names[i] = fmt.Sprintf("%s%d", prefix, i+1)
		}
		return names, nil
	}
	names := strings.Split(text, ",")
	for i := range names {
		names[i] = strings.TrimSpace(names[i])
	}
	if len(names) != count {
		return nil, fmt.Errorf("expected %d action names, got %d", count, len(names))
	}
	return names, nil
}

func printSolution(res Analysis, rows, cols []string, m Matrix) {
	fmt.Println("\n" + heading(t("analysis")))
	for _, e := range res.Eliminated {
		if e.Player == "row" {
			fmt.Println(bullet(fmt.Sprintf("strictly dominated, can be dropped: %s (you)", rows[e.Index]), "•"))
		} else {
			fmt.Println(bullet(fmt.Sprintf("strictly dominated, can be dropped: %s (them)", cols[e.Index]), "•"))
		}
		if reason := dominanceReason(m, rows, cols, e.Player, e.Index); reason != "" {
			fmt.Println(dim(paragraph(reason)))
		}
	}
	fmt.Println(bullet(fmt.Sprintf("after dominance: you %s, them %s", strings.Join(pick(rows, res.SurvivingRows), ", "), strings.Join(pick(cols, res.SurvivingCols), ", ")), "•"))

	if len(res.Equilibria) > 0 {
		for _, eq := range res.Equilibria {
			a, b := m[eq[0]][eq[1]].Row, m[eq[0]][eq[1]].Col
			fmt.Println(green(bullet(fmt.Sprintf("pure equilibrium: you %s, them %s  payoffs (%s, %s)",
				rows[eq[0]], cols[eq[1]], a.RatString(), b.RatString()), "•")))
		}
	} else {
		fmt.Println(bullet("no pure-strategy equilibrium", "•"))
	}

	if res.Mixed != nil {
		p, q := res.Mixed[0], res.Mixed[1]
		one := big.NewRat(1, 1)
		fmt.Println(bullet(fmt.Sprintf(
			"mixed equilibrium: you play %s %s, %s %s; they play %s %s, %s %s",
			rows[0], percent(p), rows[1], percent(new(big.Rat).Sub(one, p)),
			cols[0], percent(q), cols[1], percent(new(big.Rat).Sub(one, q))), "•"))
	}

	fmt.Println(bullet(fmt.Sprintf("your maximin (safe) value: %s, achieved by %s",
		res.RowMaximin.RatString(), strings.Join(pick(rows, res.RowMaximinIdx), ", ")), "•"))
	fmt.Println(bullet(fmt.Sprintf("their maximin (safe) value: %s, achieved by %s",
		res.ColMaximin.RatString(), strings.Join(pick(cols, res.ColMaximinIdx), ", ")), "•"))
	if res.ConstantSum != nil {
		fmt.Println(bullet(fmt.Sprintf("constant-sum game: totals are always %s, so one side's gain is the other's loss",
			res.ConstantSum.RatString()), "•"))
	}

	fmt.Println("\n" + heading(t("recommendation")))
	fmt.Println(box(strings.Split(wrapAt(recommendation(res, rows, cols), "", "", 70), "\n"), accentStyle))
}

func recommendation(res Analysis, rows, cols []string) string {
	if len(res.SurvivingRows) == 1 && len(res.SurvivingCols) == 1 {
		return fmt.Sprintf("Dominance settles it: play %s. Expect them to play %s.",
			rows[res.SurvivingRows[0]], cols[res.SurvivingCols[0]])
	}
	if len(res.Equilibria) == 1 {
		return "Play your part of the equilibrium. It holds if they also reason to it."
	}
	if len(res.Equilibria) > 1 {
		return "Several pure equilibria: pick the one you prefer and agree it in advance, because uncoordinated play can land on a bad outcome."
	}
	if res.Mixed != nil {
		return "No pure equilibrium: randomise with the mixed probabilities above so they cannot predict or exploit you."
	}
	return fmt.Sprintf("No equilibrium here: play maximin (%s) to guarantee at least %s.",
		strings.Join(pick(rows, res.RowMaximinIdx), ", "), res.RowMaximin.RatString())
}

func cmdNew(args []string, games []Game) error {
	path := "scenario.gt"
	if len(args) > 0 {
		path = args[0]
	}
	if _, err := os.Stat(path); err == nil {
		if strings.ToLower(prompt(path+" exists. Overwrite? [y/N] ")) != "y" {
			fmt.Println("Cancelled.")
			return nil
		}
	}
	title := prompt("Title for this situation: ")
	domains := prompt(fmt.Sprintf("Domains, comma separated (%s), Enter to skip: ", strings.Join(DomainNames, ", ")))
	fmt.Println(dim("\nFor each question, type a number, or press Enter to skip that trait."))

	var lines []string
	if title != "" {
		lines = append(lines, "title: "+title)
	}
	for _, key := range Traits {
		if choice := askChoice(key, TraitOptions(key)); choice != "" {
			lines = append(lines, key+": "+choice)
		}
	}
	if domains != "" {
		lines = append(lines, "domain: "+domains)
	}
	if err := os.WriteFile(path, []byte(strings.Join(lines, "\n")+"\n"), 0o644); err != nil {
		return err
	}
	fmt.Println(green("Saved " + path))
	if strings.ToLower(prompt("Advise on it now? [Y/n] ")) != "n" {
		return cmdAdvise([]string{path}, games)
	}
	return nil
}

func askChoice(key string, options []string) string {
	var parts []string
	for i, o := range options {
		parts = append(parts, fmt.Sprintf("%d) %s", i+1, o))
	}
	answer := strings.ToLower(prompt(fmt.Sprintf("%s: %s  [Enter to skip] ", key, strings.Join(parts, " / "))))
	if answer == "" {
		return ""
	}
	var n int
	if _, err := fmt.Sscanf(answer, "%d", &n); err == nil && n >= 1 && n <= len(options) {
		return options[n-1]
	}
	if contains(options, answer) {
		return answer
	}
	fmt.Println(red("  not recognised, skipping"))
	return ""
}

// prompt reads one trimmed line. At end of input the program exits cleanly.
func prompt(message string) string {
	line, ok := readInput(message)
	if !ok {
		fmt.Println()
		os.Exit(0)
	}
	return line
}

// readInput prints a prompt and reads one trimmed line. ok is false at end of input.
func readInput(message string) (string, bool) {
	line, ok := lineEditor().ReadLine(message)
	return strings.TrimSpace(line), ok
}

// ---- formatting helpers ----

const width = 88

func paragraph(text string) string {
	return wrap(text, "  ", "  ")
}

func bullet(text, marker string) string {
	pad := "  "
	return wrap(marker+" "+text, pad, pad+strings.Repeat(" ", utf8.RuneCountInString(marker)+1))
}

// wrap word-wraps text to width, using the given first-line and continuation indents.
func wrap(text, first, rest string) string {
	return wrapAt(text, first, rest, width)
}

// wrapAt is wrap with an explicit line width.
func wrapAt(text, first, rest string, limit int) string {
	// Keep runs of spaces inside a line, as the Python version does; only line breaks drop them.
	type token struct {
		word  string
		extra int
	}
	var tokens []token
	extra := 0
	for _, part := range strings.Split(text, " ") {
		if part == "" {
			extra++
			continue
		}
		tokens = append(tokens, token{part, extra})
		extra = 0
	}
	var out []string
	line := first
	lineHasWord := false
	for _, t := range tokens {
		gap := 1 + t.extra
		if lineHasWord && utf8.RuneCountInString(line)+gap+utf8.RuneCountInString(t.word) > limit {
			out = append(out, line)
			line = rest
			lineHasWord = false
		}
		if lineHasWord {
			line += strings.Repeat(" ", gap)
		}
		line += t.word
		lineHasWord = true
	}
	out = append(out, line)
	return strings.Join(out, "\n")
}

func formatTraits(traits map[string]string) string {
	var parts []string
	for _, key := range Traits {
		if v, ok := traits[key]; ok {
			parts = append(parts, key+"="+v)
		}
	}
	return strings.Join(parts, ", ")
}

// printGrid draws the payoff grid. Pure equilibria are green; strategies removed by dominance are dimmed.
func printGrid(rows, cols []string, payoffs [][][2]string, equilibria [][2]int, droppedRows, droppedCols map[int]bool) {
	labelW := 0
	for _, r := range rows {
		if len(r) > labelW {
			labelW = len(r)
		}
	}
	labelW += 2
	colW := 12
	for _, c := range cols {
		if len(c)+2 > colW {
			colW = len(c) + 2
		}
	}
	fmt.Print(strings.Repeat(" ", labelW))
	for j, c := range cols {
		styler := bold
		if droppedCols[j] {
			styler = dim
		}
		fmt.Print(cell(c, colW, styler))
	}
	fmt.Println()
	for i, r := range rows {
		labelStyler := bold
		if droppedRows[i] {
			labelStyler = dim
		}
		fmt.Print(cell(r, labelW, labelStyler))
		for j, c := range payoffs[i] {
			styler := plain
			isEquilibrium := false
			for _, eq := range equilibria {
				if eq[0] == i && eq[1] == j {
					isEquilibrium = true
				}
			}
			if isEquilibrium {
				styler = good
			} else if droppedRows[i] || droppedCols[j] {
				styler = dim
			}
			fmt.Print(cell(fmt.Sprintf("(%s, %s)", c[0], c[1]), colW, styler))
		}
		fmt.Println()
	}
	fmt.Println(dim("  " + t("each_cell")))
	if len(equilibria) > 0 || len(droppedRows) > 0 || len(droppedCols) > 0 {
		fmt.Println(dim("  " + t("grid_key")))
	}
}

// droppedSet is the set of strategy indexes removed for one player by dominance.
func droppedSet(eliminated []Elimination, player string) map[int]bool {
	dropped := map[int]bool{}
	for _, e := range eliminated {
		if e.Player == player {
			dropped[e.Index] = true
		}
	}
	return dropped
}

// dominanceReason explains why a strategy is strictly dominated, using the whole grid.
// It returns "" when only the steps before it show the dominance.
func dominanceReason(m Matrix, rows, cols []string, player string, index int) string {
	if player == "row" {
		for k := range rows {
			if k == index {
				continue
			}
			dominates := true
			for j := range cols {
				if m[k][j].Row.Cmp(m[index][j].Row) <= 0 {
					dominates = false
					break
				}
			}
			if dominates {
				var cases []string
				for j := range cols {
					cases = append(cases, fmt.Sprintf("If they play %s, %s gives you %s and %s gives you %s.",
						cols[j], rows[k], m[k][j].Row.RatString(), rows[index], m[index][j].Row.RatString()))
				}
				return fmt.Sprintf("%s is strictly dominated by %s: whatever they play, %s pays you more. %s",
					rows[index], rows[k], rows[k], strings.Join(cases, " "))
			}
		}
		return ""
	}
	for k := range cols {
		if k == index {
			continue
		}
		dominates := true
		for i := range rows {
			if m[i][k].Col.Cmp(m[i][index].Col) <= 0 {
				dominates = false
				break
			}
		}
		if dominates {
			var cases []string
			for i := range rows {
				cases = append(cases, fmt.Sprintf("If you play %s, %s gives them %s and %s gives them %s.",
					rows[i], cols[k], m[i][k].Col.RatString(), cols[index], m[i][index].Col.RatString()))
			}
			return fmt.Sprintf("%s is strictly dominated by %s: whatever you play, %s pays them more. %s",
				cols[index], cols[k], cols[k], strings.Join(cases, " "))
		}
	}
	return ""
}

// cell pads plain text to a column width, then applies the style, so ANSI codes
// do not disturb the alignment.
func cell(s string, w int, styler func(string) string) string {
	pad := w - utf8.RuneCountInString(s)
	if pad < 0 {
		pad = 0
	}
	return styler(s) + strings.Repeat(" ", pad)
}

func intsToCells(payoffs [][][2]int) [][][2]string {
	out := make([][][2]string, len(payoffs))
	for i, row := range payoffs {
		out[i] = make([][2]string, len(row))
		for j, c := range row {
			out[i][j] = [2]string{fmt.Sprint(c[0]), fmt.Sprint(c[1])}
		}
	}
	return out
}

func ratCells(m Matrix) [][][2]string {
	out := make([][][2]string, len(m))
	for i, row := range m {
		out[i] = make([][2]string, len(row))
		for j, c := range row {
			out[i][j] = [2]string{c.Row.RatString(), c.Col.RatString()}
		}
	}
	return out
}

func percent(r *big.Rat) string {
	f, _ := new(big.Float).SetRat(r).Float64()
	return fmt.Sprintf("%.1f%%", f*100)
}

func pick(names []string, indices []int) []string {
	out := make([]string, len(indices))
	for i, idx := range indices {
		out[i] = names[idx]
	}
	return out
}

package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

// Commands added with the families, records, editing and simulations.

// positionalArgs returns the arguments that are not flags.
func positionalArgs(args []string) []string {
	var out []string
	for _, a := range args {
		if !strings.HasPrefix(a, "--") {
			out = append(out, a)
		}
	}
	return out
}

func cmdAreas(args []string, games []Game) error {
	families, err := LoadAreas()
	if err != nil {
		return err
	}
	name := strings.ToLower(strings.Join(positionalArgs(args), " "))
	if name == "" {
		fmt.Println()
		for _, f := range families {
			seen := map[string]bool{}
			for _, sd := range f.Subdomains {
				for _, id := range sd.Games {
					seen[id] = true
				}
			}
			fmt.Println(bold(f.Family) + "  " + dim(fmt.Sprintf("%d games", len(seen))))
			fmt.Println(dim(paragraph(f.Summary)))
		}
		fmt.Println(dim("\nRun 'areas <family>' for its sub-domains and what to read, e.g. 'areas war'."))
		return nil
	}

	var exact, partial []Family
	for _, f := range families {
		if strings.ToLower(f.Family) == name {
			exact = append(exact, f)
		} else if strings.Contains(strings.ToLower(f.Family), name) {
			partial = append(partial, f)
		}
	}
	matches := exact
	if len(matches) == 0 {
		matches = partial
	}
	if len(matches) == 0 {
		return fmt.Errorf("no family matches '%s'. Run 'areas' to list them", name)
	}
	if len(matches) > 1 {
		names := make([]string, len(matches))
		for i, f := range matches {
			names[i] = f.Family
		}
		return fmt.Errorf("'%s' is ambiguous: %s", name, strings.Join(names, ", "))
	}

	family := matches[0]
	names := map[string]string{}
	for _, g := range games {
		names[g.ID] = g.Name
	}
	fmt.Println("\n" + bold(family.Family))
	fmt.Println(dim(paragraph(family.Summary)))
	for _, sd := range family.Subdomains {
		fmt.Println("\n" + heading(sd.Name))
		for _, id := range sd.Games {
			label, ok := names[id]
			if !ok {
				label = id
			}
			fmt.Println(bullet(label+"  "+dim(id), "•"))
		}
	}
	fmt.Println("\n" + heading(t("learn_more")))
	for _, ref := range family.Learn {
		fmt.Println(bullet(ref, "•"))
	}
	return nil
}

func cmdLog(args []string, games []Game) error {
	play := 0
	var rest []string
	for i := 0; i < len(args); i++ {
		if args[i] == "--play" && i+1 < len(args) {
			n, err := strconv.Atoi(args[i+1])
			if err != nil {
				return fmt.Errorf("--play expects a number")
			}
			play = n
			i++
			continue
		}
		if strings.HasPrefix(args[i], "--") {
			return fmt.Errorf("unknown option %s. Use --play N, then the note as plain words", args[i])
		}
		rest = append(rest, args[i])
	}
	pos := positionalArgs(rest)
	if len(pos) < 2 {
		return fmt.Errorf("usage: log <game> win|loss|draw|mixed [--play N] [note]")
	}
	game, err := FindGame(games, pos[0])
	if err != nil {
		return err
	}
	if play != 0 && (play < 1 || play > len(game.Strategies)) {
		return fmt.Errorf("'%s' has plays 1 to %d", game.Name, len(game.Strategies))
	}
	if _, err := LogOutcome(game.ID, pos[1], strings.Join(pos[2:], " "), play); err != nil {
		return err
	}
	where := ""
	if play != 0 {
		where = fmt.Sprintf(" with play %d", play)
	}
	fmt.Println(green(fmt.Sprintf("Logged %s for %s%s. Record: %s.", pos[1], game.Name, where, recordLine(game.ID))))
	return nil
}

func cmdRecord(args []string, games []Game) error {
	if contains(args, "--json") {
		var rest []string
		for _, a := range args {
			if a != "--json" {
				rest = append(rest, a)
			}
		}
		return recordJSON(rest, games)
	}
	for i := 0; i < len(args); i++ {
		if args[i] == "--csv" && i+1 < len(args) {
			csv, err := ResultsCSV()
			if err != nil {
				return err
			}
			if err := os.WriteFile(args[i+1], []byte(csv), 0o644); err != nil {
				return err
			}
			fmt.Println(green("Wrote your results to " + args[i+1]))
			return nil
		}
	}
	pos := positionalArgs(args)
	if len(pos) > 0 {
		game, err := FindGame(games, strings.Join(pos, " "))
		if err != nil {
			return err
		}
		entries, err := History(game.ID)
		if err != nil {
			return err
		}
		line := recordLine(game.ID)
		if line == "" {
			line = "no outcomes yet"
		}
		fmt.Println("\n" + bold(game.Name) + "  " + dim(line))
		for _, e := range entries {
			note := ""
			if e.Note != "" {
				note = "  " + e.Note
			}
			play := ""
			if e.Play != 0 {
				play = fmt.Sprintf("  play %d", e.Play)
			}
			fmt.Println(bullet(e.Date+"  "+e.Result+play+note, "•"))
		}
		byPlay := map[int]map[string]int{}
		for _, e := range entries {
			if e.Play != 0 {
				if byPlay[e.Play] == nil {
					byPlay[e.Play] = map[string]int{}
				}
				byPlay[e.Play][e.Result]++
			}
		}
		if len(byPlay) > 0 {
			fmt.Println("\n" + heading(t("record_by_play")))
			for n := 1; n <= len(game.Strategies); n++ {
				if counts, ok := byPlay[n]; ok {
					fmt.Println(bullet(fmt.Sprintf("play %d: %s  %s", n, FormatRecord(counts), dim(truncate(game.Strategies[n-1], 60))), fmt.Sprintf("%d.", n)))
				}
			}
		}
		return nil
	}
	counts, err := Tally()
	if err != nil {
		return err
	}
	if len(counts) == 0 {
		fmt.Println(dim("No outcomes logged yet. Try: log <game> win|loss|draw|mixed [note]"))
		return nil
	}
	names := map[string]string{}
	for _, g := range games {
		names[g.ID] = g.Name
	}
	fmt.Println()
	for id, row := range counts {
		label, ok := names[id]
		if !ok {
			label = id
		}
		fmt.Println(cell(label, 36, bold) + dim(FormatRecord(row)))
	}
	return nil
}

func cmdEdit(args []string, games []Game) error {
	pos := positionalArgs(args)
	if len(pos) == 0 {
		return fmt.Errorf("usage: edit <game>")
	}
	game, err := FindGame(games, strings.Join(pos, " "))
	if err != nil {
		return err
	}
	path, err := SaveOverlay(*game)
	if err != nil {
		return err
	}
	fmt.Println(green(fmt.Sprintf("Copied '%s' to %s", game.Name, path)))
	fmt.Println(dim("Edit that file to change its plays, pitfalls or examples. Changes load on the next start."))
	return nil
}

func cmdAddPlay(args []string, games []Game) error {
	pos := positionalArgs(args)
	if len(pos) < 2 {
		return fmt.Errorf("usage: add-play <game> <text of the play>")
	}
	game, err := FindGame(games, pos[0])
	if err != nil {
		return err
	}
	updated := *game
	updated.Strategies = append(append([]string{}, game.Strategies...), strings.Join(pos[1:], " "))
	path, err := SaveOverlay(updated)
	if err != nil {
		return err
	}
	fmt.Println(green(fmt.Sprintf("Added play %d to '%s' (%s).", len(updated.Strategies), game.Name, path)))
	return nil
}

func printEnding(outcome, text string, steps []Step) {
	var style func(string) string
	switch outcome {
	case "victory":
		style = green
	case "failure":
		style = red
	default:
		style = dim
	}
	fmt.Println(style(t("ending") + ": " + strings.ToUpper(outcome)))
	if len(steps) > 0 {
		last := steps[len(steps)-1]
		if last.Kind == "you" {
			fmt.Println(dim("  " + t("followed_last") + ": " + last.Label))
		} else {
			fmt.Println(dim("  " + t("followed_chance") + ": " + last.Label))
		}
	}
	fmt.Println(paragraph(text))
}

func printPath(title string, steps []Step, outcome, text string, chance float64) {
	fmt.Println("\n" + heading(title) + "  " + dim(fmt.Sprintf("%.0f%% %s", chance*100, t("chance"))))
	for i, s := range steps {
		marker := fmt.Sprintf("%d.", i+1)
		if s.Kind == "you" {
			fmt.Println(bullet(s.Prompt+"  "+bold(s.Label), marker))
		} else {
			fmt.Println(bullet(dim(fmt.Sprintf("chance: %s (%.0f%%)", s.Label, s.P*100)), marker))
		}
		if s.Why != "" {
			fmt.Println(dim(wrapAt(t("why")+": "+s.Why, "     ", "      ", width)))
		}
	}
	printEnding(outcome, text, steps)
}

func cmdSim(args []string, games []Game) error {
	sims, err := LoadSimulations()
	if err != nil {
		return err
	}
	play := false
	noHints := false
	family := ""
	export := ""
	matrix := false
	opponent := "equilibrium"
	lam := 2.0
	save, resume := "", ""
	var exportAs []string
	mode := ""
	var pos []string
	for i := 0; i < len(args); i++ {
		switch {
		case args[i] == "--play":
			play = true
		case args[i] == "--no-hints":
			noHints = true
		case args[i] == "--matrix":
			matrix = true
		case args[i] == "--opponent" && i+1 < len(args):
			opponent = args[i+1]
			i++
		case args[i] == "--lam" && i+1 < len(args):
			v, err := strconv.ParseFloat(args[i+1], 64)
			if err != nil {
				return fmt.Errorf("--lam expects a number")
			}
			lam = v
			i++
		case args[i] == "--formats" && i+1 < len(args):
			formats, err := parseFormats(args[i+1])
			if err != nil {
				return err
			}
			exportAs = formats
			i++
		case args[i] == "--save" && i+1 < len(args):
			save = args[i+1]
			i++
		case args[i] == "--resume" && i+1 < len(args):
			resume = args[i+1]
			i++
		case args[i] == "--export" && i+1 < len(args):
			export = args[i+1]
			i++
		case args[i] == "--mode" && i+1 < len(args):
			mode = args[i+1]
			i++
		case args[i] == "--family" && i+1 < len(args):
			family = strings.ToLower(args[i+1])
			i++
		case strings.HasPrefix(args[i], "--"):
			return fmt.Errorf("unknown option %s", args[i])
		default:
			pos = append(pos, args[i])
		}
	}
	if family != "" {
		var kept []Simulation
		for _, s := range sims {
			for _, f := range s.Families {
				if strings.Contains(strings.ToLower(f), family) {
					kept = append(kept, s)
					break
				}
			}
		}
		if len(kept) == 0 {
			return fmt.Errorf("no simulation covers '%s'. Run 'sim' to list them", family)
		}
		sims = kept
	}
	if mode != "" {
		if mode != "basic" && mode != "live" {
			return fmt.Errorf("--mode must be basic or live")
		}
		var kept []Simulation
		for _, s := range sims {
			if s.modeOrBasic() == mode {
				kept = append(kept, s)
			}
		}
		sims = kept
	}
	if len(pos) == 0 {
		fmt.Println()
		for _, s := range sims {
			tag := "[basic]"
			if s.modeOrBasic() == "live" {
				tag = "[live]"
			}
			fmt.Println(cell(s.ID, 34, bold) + cell(s.Name, 42, plain) + dim(tag+" "+strings.Join(s.Families, ", ")))
		}
		fmt.Println(dim(fmt.Sprintf("\n%d simulation(s). Run 'sim <id>' for the paths to victory and failure, or 'sim <id> --play' to play it.", len(sims))))
		return nil
	}
	var sim *Simulation
	if matrix {
		game, err := FindGame(games, strings.Join(pos, " "))
		if err != nil {
			return err
		}
		areas, err := LoadAreas()
		if err != nil {
			return err
		}
		var families []string
		for _, f := range areas {
			for _, sd := range f.Subdomains {
				if contains(sd.Games, game.ID) {
					families = append(families, f.Family)
					break
				}
			}
		}
		if sim, err = MatrixSimulation(*game, families, opponent, lam); err != nil {
			return err
		}
	} else {
		found, err := FindSimulation(sims, strings.Join(pos, " "))
		if err != nil {
			return err
		}
		sim = found
	}
	simName, simSummary := sim.Name, sim.Summary
	fmt.Printf("\n%s\n", bold(simName))
	fmt.Println(dim(t("works_across") + ": " + strings.Join(sim.Families, ", ")))
	fmt.Println()
	fmt.Println(paragraph(simSummary))
	if export != "" {
		return exportSimulation(sim, export)
	}
	if play || save != "" || resume != "" {
		return runSimPlay(sim, save, resume, exportAs, noHints)
	}

	winSteps, winEnd, winChance := trace(sim, solve(sim, "victory"))
	failSteps, failEnd, failChance := trace(sim, solve(sim, "failure"))
	printPath(t("path_victory"), winSteps, winEnd.Outcome, winEnd.Text, winChance)
	printPath(t("path_failure"), failSteps, failEnd.Outcome, failEnd.Text, failChance)

	every := endings(sim)
	counts := map[string]int{}
	for _, e := range every {
		counts[e.Outcome]++
	}
	fmt.Println("\n" + heading(t("all_endings")))
	fmt.Println(bullet(fmt.Sprintf("%d ways to play out, across all of your choices: %d victory, %d draw, %d failure.",
		len(every), counts["victory"], counts["draw"], counts["failure"]), "•"))
	fmt.Println(bullet(fmt.Sprintf("The best plan wins %.0f%% of the time; the plan most likely to fail, fails %.0f%% of the time.",
		winChance*100, failChance*100), "•"))
	fmt.Println(dim("Chance steps follow their most likely outcome in each path; the percentages cover all branches."))
	return nil
}

// runSimPlay plays a simulation in the terminal. Hints (the chance of victory and the best
// strategy) start as you choose before the game, or off with --no-hints; h at any choice turns
// them on or off from that choice on.
func runSimPlay(sim *Simulation, save, resume string, formats []string, noHints bool) error {
	hintState := !noHints
	if !noHints && stdinIsTerminal() {
		answer := strings.ToLower(strings.TrimSpace(promptLine("Show the chance of victory and the best strategy as you play? (Y/n) ")))
		hintState = answer != "n" && answer != "no"
	}
	ask := func(prompt string, options []PlayOption) int {
		for {
			show := hintState
			best := 0.0
			for _, o := range options {
				if o.Chance > best {
					best = o.Chance
				}
			}
			hintWord := "on"
			if show {
				hintWord = "off"
			}
			fmt.Println("\n" + bold(prompt))
			fmt.Println(dim("  b  go back to your previous decision    h  hints " + hintWord))
			for i, o := range options {
				if !show {
					fmt.Printf("  %d) %s\n", i+1, o.Label)
					continue
				}
				marker := ""
				if o.Chance == best {
					marker = green(" (" + t("best") + ")")
				}
				fmt.Printf("  %d) %s  %s%s\n", i+1, o.Label, dim(fmt.Sprintf("%s: %.0f%%", t("chance_from_here"), o.Chance*100)), marker)
			}
			answer := strings.ToLower(strings.TrimSpace(promptLine("> ")))
			if answer == "b" || answer == "back" {
				return -1
			}
			if answer == "h" {
				hintState = !show
				if hintState {
					fmt.Println(dim("  hints on from this choice"))
				} else {
					fmt.Println(dim("  hints off from this choice"))
				}
				continue
			}
			var n int
			if _, err := fmt.Sscanf(answer, "%d", &n); err == nil && n >= 1 && n <= len(options) {
				if chosen := options[n-1]; chosen.Why != "" {
					fmt.Println(dim("  " + t("why") + ": " + chosen.Why))
				}
				for i, o := range options {
					if i != n-1 && o.Why != "" {
						if show {
							fmt.Println(dim(fmt.Sprintf("  %s %d) %s (%.0f%%): %s", t("why_not"), i+1, o.Label, o.Chance*100, o.Why)))
						} else {
							fmt.Println(dim(fmt.Sprintf("  %s %d) %s: %s", t("why_not"), i+1, o.Label, o.Why)))
						}
					}
				}
				return n - 1
			}
			fmt.Println(red(fmt.Sprintf("  choose a number from 1 to %d", len(options))))
		}
	}
	say := func(text string) { fmt.Println(dim("  " + text)) }
	start, taken := sim.Start, []Step(nil)
	if resume != "" {
		node, steps, err := loadGame(resume, sim)
		if err != nil {
			return err
		}
		start, taken = node, steps
		fmt.Println(dim(fmt.Sprintf("Resuming from a saved game with %d step(s) taken.", len(steps))))
	}
	var checkpoint func(string, []Step)
	if save != "" {
		checkpoint = func(node string, steps []Step) {
			if err := saveGame(save, sim, node, steps); err != nil {
				fmt.Println(red("could not save: " + err.Error()))
			}
		}
	}
	steps, end := playSimFrom(sim, start, taken, ask, say, checkpoint)
	fmt.Println()
	printEnding(end.Outcome, end.Text, steps)
	if save != "" {
		fmt.Println(dim(fmt.Sprintf("Your game is saved in %s; resume it with --resume %s.", save, save)))
	}
	if hintState {
		best := solve(sim, "victory")[sim.Start].value
		fmt.Println(dim(t("best_plan_wins", "percent", fmt.Sprintf("%.0f%%", best*100)) + fmt.Sprintf(" Run 'sim %s' to see it.", sim.ID)))
	}
	if formats == nil && stdinIsTerminal() {
		formats = askFormats()
	}
	if len(formats) > 0 {
		folder, written, err := writeRun(sim, steps, end.Outcome, end.Text, formats, PlaybookHome(), time.Now())
		if err != nil {
			return err
		}
		fmt.Println(dim("Exported to " + folder + ":"))
		for _, name := range written {
			fmt.Println(dim("  " + name))
		}
	}
	if stdinIsTerminal() && resume == "" {
		if answer := strings.ToLower(strings.TrimSpace(promptLine("Play again from the start? (y/N) "))); answer == "y" || answer == "yes" {
			return runSimPlay(sim, "", "", formats, !hintState)
		}
	}
	return nil
}

// promptLine reads one line for interactive commands, exiting cleanly at end of input.
func promptLine(message string) string {
	line, ok := readInput(message)
	if !ok {
		fmt.Println()
		os.Exit(0)
	}
	return line
}

// Problem is one everyday or professional problem and the games that work best for it.
type Problem struct {
	Problem string   `json:"problem"`
	Games   []string `json:"games"`
	Sims    []string `json:"sims"`
}

type ProblemArea struct {
	Area     string    `json:"area"`
	Problems []Problem `json:"problems"`
}

func LoadProblems() ([]ProblemArea, error) {
	data, err := dataFS.ReadFile("data/problems.json")
	if err != nil {
		return nil, err
	}
	var areas []ProblemArea
	if err := json.Unmarshal(data, &areas); err != nil {
		return nil, fmt.Errorf("parsing problems.json: %w", err)
	}
	return areas, nil
}

func cmdProblems(args []string, games []Game) error {
	areas, err := LoadProblems()
	if err != nil {
		return err
	}
	query := strings.ToLower(strings.TrimSpace(strings.Join(positionalArgs(args), " ")))
	byID := map[string]Game{}
	for _, g := range games {
		byID[g.ID] = g
	}
	if query == "" {
		fmt.Println()
		for _, a := range areas {
			fmt.Println(bold(a.Area) + "  " + dim(fmt.Sprintf("%d problems", len(a.Problems))))
			for _, p := range a.Problems {
				fmt.Println(bullet(p.Problem, "•"))
			}
		}
		fmt.Println(dim("\nRun 'problems <problem or area>' for the best games and their scenarios."))
		return nil
	}

	var exactArea []ProblemArea
	for _, a := range areas {
		if strings.ToLower(a.Area) == query {
			exactArea = append(exactArea, a)
		}
	}
	if len(exactArea) > 0 {
		a := exactArea[0]
		fmt.Println("\n" + bold(a.Area))
		for _, p := range a.Problems {
			fmt.Println(bullet(p.Problem, "•"))
		}
		fmt.Println(dim("\nRun 'problems <problem>' with part of a problem above for the best games."))
		return nil
	}

	type hit struct {
		area string
		p    Problem
	}
	var hits []hit
	for _, a := range areas {
		for _, p := range a.Problems {
			if strings.Contains(strings.ToLower(p.Problem), query) {
				hits = append(hits, hit{a.Area, p})
			}
		}
	}
	if len(hits) > 0 {
		for _, h := range hits {
			fmt.Println("\n" + heading(h.p.Problem) + "  " + dim(h.area))
			fmt.Println(dim("Best games for this problem, in order:"))
			for i, id := range h.p.Games {
				g, ok := byID[id]
				if !ok {
					continue
				}
				fmt.Println(bullet(fmt.Sprintf("%s  %s", g.Name, dim(id)), fmt.Sprintf("%d.", i+1)))
				for j, ex := range g.Examples {
					if j == 3 {
						break
					}
					fmt.Println("     " + dim("· "+ex))
				}
			}
			if len(h.p.Sims) > 0 {
				tries := make([]string, len(h.p.Sims))
				for i, s := range h.p.Sims {
					tries[i] = "sim " + s
				}
				fmt.Println(bullet("Try it: "+strings.Join(tries, ", "), "→"))
			}
		}
		return nil
	}

	for _, a := range areas {
		if strings.Contains(strings.ToLower(a.Area), query) {
			fmt.Println("\n" + bold(a.Area))
			for _, p := range a.Problems {
				fmt.Println(bullet(p.Problem, "•"))
			}
			return nil
		}
	}
	return fmt.Errorf("no problem or area matches '%s'. Run 'problems' to list them", query)
}

func truncate(s string, n int) string {
	if len(s) <= n {
		return s
	}
	return s[:n]
}

// tallyOrEmpty returns your logged results per game, or an empty map if none can be read.
func tallyOrEmpty() map[string]map[string]int {
	counts, err := Tally()
	if err != nil || counts == nil {
		return map[string]map[string]int{}
	}
	return counts
}

// exportSimulation writes the paths and endings of a simulation as Markdown.
func exportSimulation(sim *Simulation, path string) error {
	winSteps, winEnd, winChance := trace(sim, solve(sim, "victory"))
	failSteps, failEnd, failChance := trace(sim, solve(sim, "failure"))
	every := endings(sim)
	counts := map[string]int{}
	for _, e := range every {
		counts[e.Outcome]++
	}
	var b strings.Builder
	fmt.Fprintf(&b, "# %s\n\n*Works across: %s*\n\n%s\n\n", sim.Name, strings.Join(sim.Families, ", "), sim.Summary)
	writePath := func(title string, steps []Step, end SimNode, chance float64) {
		fmt.Fprintf(&b, "## %s (%.0f%% chance)\n\n", title, chance*100)
		for i, st := range steps {
			if st.Kind == "you" {
				fmt.Fprintf(&b, "%d. %s **%s**\n", i+1, st.Prompt, st.Label)
			} else {
				fmt.Fprintf(&b, "%d. Chance: %s (%.0f%%)\n", i+1, st.Label, st.P*100)
			}
			if st.Why != "" {
				fmt.Fprintf(&b, "   - Why: %s\n", st.Why)
			}
		}
		fmt.Fprintf(&b, "\n**Ending: %s.** %s\n\n", strings.ToUpper(end.Outcome), end.Text)
	}
	writePath("Path to victory", winSteps, winEnd, winChance)
	writePath("Path to failure", failSteps, failEnd, failChance)
	fmt.Fprintf(&b, "## All possible endings\n\n- %d ways to play out: %d victory, %d draw, %d failure.\n",
		len(every), counts["victory"], counts["draw"], counts["failure"])
	fmt.Fprintf(&b, "- The best plan wins %.0f%% of the time; the plan most likely to fail, fails %.0f%% of the time.\n\n",
		winChance*100, failChance*100)
	b.WriteString("*Chance steps follow their most likely outcome in each path. Probabilities are illustrative, not measured.*\n")
	if err := os.WriteFile(path, []byte(b.String()), 0o644); err != nil {
		return err
	}
	fmt.Println(green(fmt.Sprintf("Exported '%s' to %s", sim.Name, path)))
	return nil
}

// cmdChart draws an SVG chart: families, traits, map, records, or sim <id>.
func cmdChart(args []string, games []Game) error {
	kind := ""
	var target []string
	out := ""
	for i := 0; i < len(args); i++ {
		switch {
		case args[i] == "--out" && i+1 < len(args):
			out = args[i+1]
			i++
		case kind == "":
			kind = args[i]
		default:
			target = append(target, args[i])
		}
	}
	families, err := LoadAreas()
	if err != nil {
		return err
	}
	var svg, name string
	switch kind {
	case "families":
		svg, name = FamiliesChart(families), "families"
	case "traits":
		svg, name = TraitsHeatmap(games), "traits"
	case "map":
		svg, name = FamilyMap(families), "map"
	case "plays":
		history, err := History("")
		if err != nil {
			return err
		}
		type cell struct {
			game string
			play int
		}
		byCell := map[cell]map[string]int{}
		var order []cell
		for _, e := range history {
			if e.Play == 0 {
				continue
			}
			k := cell{e.Game, e.Play}
			if byCell[k] == nil {
				byCell[k] = map[string]int{}
				order = append(order, k)
			}
			byCell[k][e.Result]++
		}
		if len(order) == 0 {
			return fmt.Errorf("no per-play results logged yet. Use: log <game> win|loss --play N")
		}
		byID := map[string]Game{}
		for _, g := range games {
			byID[g.ID] = g
		}
		var rows []PlayRow
		for _, k := range order {
			g := byID[k.game]
			text := ""
			if k.play <= len(g.Strategies) {
				text = truncate(g.Strategies[k.play-1], 34)
			}
			name := g.Name
			if name == "" {
				name = k.game
			}
			rows = append(rows, PlayRow{Label: fmt.Sprintf("%s - play %d: %s", name, k.play, text), Counts: byCell[k]})
		}
		svg, name = PlaysChart(rows), "plays"
	case "records":
		counts, err := Tally()
		if err != nil {
			return err
		}
		if len(counts) == 0 {
			return fmt.Errorf("no results logged yet. Use: log <game> win|loss|draw|mixed")
		}
		names := map[string]string{}
		for _, g := range games {
			names[g.ID] = g.Name
		}
		svg, name = RecordsChart(counts, names), "records"
	case "sim":
		if len(target) == 0 {
			return fmt.Errorf("name a simulation, e.g. 'chart sim chicken'")
		}
		sims, err := LoadSimulations()
		if err != nil {
			return err
		}
		sim, err := FindSimulation(sims, strings.Join(target, " "))
		if err != nil {
			return err
		}
		svg, name = SimTree(sim, nil), "sim-"+sim.ID
	default:
		return fmt.Errorf("kinds are families, traits, map, records and sim")
	}
	if out == "" {
		if err := os.MkdirAll("charts", 0o755); err != nil {
			return err
		}
		out = filepath.Join("charts", name+".svg")
	}
	if err := os.WriteFile(out, []byte(svg), 0o644); err != nil {
		return err
	}
	fmt.Println(green("Wrote " + out))
	return nil
}

// recordJSON prints the records as JSON: one game's entries and tally, or every game's tally.
func recordJSON(args []string, games []Game) error {
	tallies, err := Tally()
	if err != nil {
		return err
	}
	pos := positionalArgs(args)
	var data any
	if len(pos) > 0 {
		game, err := FindGame(games, strings.Join(pos, " "))
		if err != nil {
			return err
		}
		entries, err := History(game.ID)
		if err != nil {
			return err
		}
		rows := []map[string]any{}
		for _, e := range entries {
			row := map[string]any{"game": e.Game, "result": e.Result, "note": e.Note, "date": e.Date}
			if e.Play != 0 {
				row["play"] = e.Play
			}
			rows = append(rows, row)
		}
		data = map[string]any{"game": game.ID, "entries": rows, "tally": fullTally(tallies[game.ID])}
	} else {
		all := map[string]map[string]int{}
		for id, row := range tallies {
			all[id] = fullTally(row)
		}
		data = map[string]any{"tally": all}
	}
	out, err := json.MarshalIndent(data, "", "  ")
	if err != nil {
		return err
	}
	fmt.Println(string(out))
	return nil
}

// fullTally returns the four result counts, with zeros for results not yet logged, as the Python version does.
func fullTally(counts map[string]int) map[string]int {
	out := map[string]int{"win": 0, "loss": 0, "draw": 0, "mixed": 0}
	for k, v := range counts {
		out[k] = v
	}
	return out
}

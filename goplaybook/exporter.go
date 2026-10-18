package main

import (
	"bytes"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"time"
)

// exportFolder makes a new folder for one export, named after its kind, the item and the time.
func exportFolder(home, kind, name string, when time.Time) (string, error) {
	folder := filepath.Join(home, "exports", kind+"-"+safeFileName(name)+"-"+when.Format("20060102-150405"))
	return folder, os.MkdirAll(folder, 0o755)
}

// gameMarkdown is the game card as Markdown, in the same order as the Python version.
func gameMarkdown(g Game) string {
	var b strings.Builder
	fmt.Fprintf(&b, "# %s\n\n*%s*\n\n%s\n\n", g.Name, g.Category, g.Summary)
	if g.HowItWorks != "" {
		fmt.Fprintf(&b, "## How it works\n\n%s\n\n", g.HowItWorks)
	}
	if len(g.Examples) > 0 {
		b.WriteString("## Scenarios it fits\n\n")
		for _, ex := range g.Examples {
			fmt.Fprintf(&b, "- %s\n", ex)
		}
		b.WriteString("\n")
	}
	if m := g.Matrix; m != nil {
		b.WriteString("## Reference payoff matrix\n\nEach cell is (your payoff, their payoff).\n\n")
		b.WriteString("| | " + strings.Join(m.Cols, " | ") + " |\n")
		b.WriteString(strings.Repeat("|---", len(m.Cols)+1) + "|\n")
		for i, label := range m.Rows {
			cells := make([]string, len(m.Cols))
			for j := range m.Cols {
				cells[j] = fmt.Sprintf("(%d, %d)", m.Payoffs[i][j][0], m.Payoffs[i][j][1])
			}
			fmt.Fprintf(&b, "| %s | %s |\n", label, strings.Join(cells, " | "))
		}
		if g.MatrixNote != "" {
			fmt.Fprintf(&b, "\n*%s*\n", g.MatrixNote)
		}
		b.WriteString("\n")
	} else if g.MatrixUnavailable != "" {
		fmt.Fprintf(&b, "## Payoff table\n\nNo table: %s\n\n", g.MatrixUnavailable)
	}
	b.WriteString("## How to play it\n\n")
	for i, rule := range g.Strategies {
		fmt.Fprintf(&b, "%d. %s\n", i+1, rule)
	}
	b.WriteString("\n")
	if len(g.Pitfalls) > 0 {
		b.WriteString("## Pitfalls\n\n")
		for _, p := range g.Pitfalls {
			fmt.Fprintf(&b, "- %s\n", p)
		}
	}
	return strings.TrimRight(b.String(), "\n") + "\n"
}

// writeGame exports a game card. Games take md and json; the chart and CSV formats are for simulation runs.
func writeGame(g Game, formats []string, home string, when time.Time) (string, []string, error) {
	for _, f := range formats {
		if f != "md" && f != "json" {
			return "", nil, fmt.Errorf("games export as md or json; %s is for simulation runs.", f)
		}
	}
	folder, err := exportFolder(home, "game", g.ID, when)
	if err != nil {
		return "", nil, err
	}
	var written []string
	for _, f := range formats {
		name := "game." + f
		var content []byte
		if f == "md" {
			content = []byte(gameMarkdown(g))
		} else {
			content, err = json.MarshalIndent(g, "", "  ")
			if err != nil {
				return folder, written, err
			}
			content = append(content, '\n')
		}
		if err := os.WriteFile(filepath.Join(folder, name), content, 0o644); err != nil {
			return folder, written, err
		}
		written = append(written, name)
	}
	return folder, written, nil
}

// repeatRecord is the repeated-play run as data, the same shape the Python version writes.
type repeatRecord struct {
	Game         string           `json:"game"`
	Name         string           `json:"name"`
	Opponent     string           `json:"opponent"`
	Rounds       int              `json:"rounds"`
	Seed         int64            `json:"seed"`
	YourTotal    int              `json:"your_total"`
	BestFixed    map[string]any   `json:"best_fixed_plan"`
	RoundsPlayed []map[string]any `json:"rounds_played"`
}

// writeRepeat exports a repeated-play run: the rounds, the totals and the best fixed plan as a reference.
func writeRepeat(g Game, opponent string, rounds int, seed int64, history []repeatRound, total, bestRow, bestTotal int, home string, when time.Time) (string, []string, error) {
	folder, err := exportFolder(home, "repeat", g.ID, when)
	if err != nil {
		return "", nil, err
	}
	m := *g.Matrix
	rec := repeatRecord{Game: g.ID, Name: g.Name, Opponent: opponent, Rounds: rounds, Seed: seed, YourTotal: total,
		BestFixed: map[string]any{"row": m.Rows[bestRow], "total": bestTotal}}
	var md strings.Builder
	fmt.Fprintf(&md, "# %s: repeated against a %s bot\n\nRounds: %d. Your total: %d. Best always-the-same plan: always %s, total %d.\n\n",
		g.Name, opponent, rounds, total, m.Rows[bestRow], bestTotal)
	md.WriteString("| Round | You | Bot | You get | Bot gets |\n|---|---|---|---|---|\n")
	for i, r := range history {
		rec.RoundsPlayed = append(rec.RoundsPlayed, map[string]any{"round": i + 1, "your_choice": m.Rows[r.row],
			"bot_choice": m.Cols[r.col], "your_payoff": r.mine, "bot_payoff": r.theirs})
		fmt.Fprintf(&md, "| %d | %s | %s | %d | %d |\n", i+1, m.Rows[r.row], m.Cols[r.col], r.mine, r.theirs)
	}
	data, err := json.MarshalIndent(rec, "", "  ")
	if err != nil {
		return folder, nil, err
	}
	if err := os.WriteFile(filepath.Join(folder, "run.md"), []byte(md.String()), 0o644); err != nil {
		return folder, nil, err
	}
	if err := os.WriteFile(filepath.Join(folder, "run.json"), append(data, '\n'), 0o644); err != nil {
		return folder, nil, err
	}
	return folder, []string{"run.md", "run.json"}, nil
}

// exportFormats is the fixed order of export formats.
var exportFormats = []string{"md", "json", "csv", "svg"}

// parseFormats reads a list such as "md,csv" or "all". It returns the formats in their fixed order.
func parseFormats(text string) ([]string, error) {
	tokens := strings.Fields(strings.ToLower(strings.ReplaceAll(text, ",", " ")))
	for _, token := range tokens {
		if token == "all" {
			return exportFormats, nil
		}
	}
	var unknown []string
	for _, token := range tokens {
		if !contains(exportFormats, token) {
			unknown = append(unknown, token)
		}
	}
	if len(unknown) > 0 {
		return nil, fmt.Errorf("unknown format(s): %s. Use md, json, csv, svg or all.", strings.Join(unknown, ", "))
	}
	var out []string
	for _, f := range exportFormats {
		if contains(tokens, f) {
			out = append(out, f)
		}
	}
	return out, nil
}

// exportStep is one step of a run. Probability is null for your own choices, as in the Python version.
type exportStep struct {
	Kind        string   `json:"kind"`
	Prompt      string   `json:"prompt"`
	Choice      string   `json:"choice"`
	Probability *float64 `json:"probability"`
	Why         string   `json:"why"`
}

type exportEnding struct {
	Outcome string `json:"outcome"`
	Text    string `json:"text"`
}

// runRecord is the run as plain data, the same shape the Python version writes to run.json.
type runRecord struct {
	Simulation            string       `json:"simulation"`
	Name                  string       `json:"name"`
	Families              []string     `json:"families"`
	VictoryChanceBestPlan float64      `json:"victory_chance_best_plan"`
	Ending                exportEnding `json:"ending"`
	Steps                 []exportStep `json:"steps"`
}

func buildRunRecord(sim *Simulation, steps []Step, outcome, text string) runRecord {
	best := solve(sim, "victory")[sim.Start].value
	record := runRecord{
		Simulation:            sim.ID,
		Name:                  sim.Name,
		Families:              sim.Families,
		VictoryChanceBestPlan: roundTo(best, 4),
		Ending:                exportEnding{Outcome: outcome, Text: text},
		Steps:                 []exportStep{},
	}
	for _, s := range steps {
		step := exportStep{Kind: s.Kind, Prompt: s.Prompt, Choice: s.Label, Why: s.Why}
		if s.Kind == "chance" {
			p := s.P
			step.Probability = &p
		}
		record.Steps = append(record.Steps, step)
	}
	return record
}

func roundTo(v float64, places int) float64 {
	scale := 1.0
	for i := 0; i < places; i++ {
		scale *= 10
	}
	return float64(int64(v*scale+0.5)) / scale
}

func runMarkdown(sim *Simulation, record runRecord) string {
	var b strings.Builder
	fmt.Fprintf(&b, "# %s\n\n*Works across: %s*\n\n%s\n\n", sim.Name, strings.Join(sim.Families, ", "), sim.Summary)
	fmt.Fprintf(&b, "## Your run (best plan: %.0f%% chance of victory)\n\n", record.VictoryChanceBestPlan*100)
	for i, step := range record.Steps {
		if step.Kind == "you" {
			fmt.Fprintf(&b, "%d. %s **%s**\n", i+1, step.Prompt, step.Choice)
		} else {
			fmt.Fprintf(&b, "%d. Chance: %s (%.0f%%)\n", i+1, step.Choice, *step.Probability*100)
		}
		if step.Why != "" {
			fmt.Fprintf(&b, "   - Why: %s\n", step.Why)
		}
	}
	fmt.Fprintf(&b, "\n**Ending: %s.** %s\n", strings.ToUpper(record.Ending.Outcome), record.Ending.Text)
	return b.String()
}

func runCSV(record runRecord) (string, error) {
	var buf bytes.Buffer
	w := csv.NewWriter(&buf)
	if err := w.Write([]string{"step", "kind", "prompt", "choice", "probability", "why"}); err != nil {
		return "", err
	}
	for i, step := range record.Steps {
		prob := ""
		if step.Probability != nil {
			prob = strconv.FormatFloat(*step.Probability, 'f', -1, 64)
		}
		if err := w.Write([]string{strconv.Itoa(i + 1), step.Kind, step.Prompt, step.Choice, prob, step.Why}); err != nil {
			return "", err
		}
	}
	w.Flush()
	return buf.String(), w.Error()
}

// writeRun writes the chosen formats for one run into its own folder under the playbook home.
func writeRun(sim *Simulation, steps []Step, outcome, text string, formats []string, home string, when time.Time) (string, []string, error) {
	folder := filepath.Join(home, "exports", safeFileName(sim.ID)+"-"+when.Format("20060102-150405"))
	if err := os.MkdirAll(folder, 0o755); err != nil {
		return "", nil, err
	}
	record := buildRunRecord(sim, steps, outcome, text)
	var written []string
	for _, format := range formats {
		name := "run." + format
		var content string
		switch format {
		case "md":
			content = runMarkdown(sim, record)
		case "json":
			data, err := json.MarshalIndent(record, "", "  ")
			if err != nil {
				return folder, written, err
			}
			content = string(data) + "\n"
		case "csv":
			csvText, err := runCSV(record)
			if err != nil {
				return folder, written, err
			}
			content = csvText
		case "svg":
			name = "tree.svg"
			content = SimTree(sim, steps)
		}
		path := filepath.Join(folder, name)
		if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
			return folder, written, err
		}
		written = append(written, name)
	}
	return folder, written, nil
}

// askFormats offers the export choice after a run. Enter skips it.
func askFormats() []string {
	fmt.Println("\nExport this run? Type formats: md, json, csv, svg, or all. Press Enter to skip.")
	for {
		answer := strings.TrimSpace(promptLine("> "))
		if answer == "" {
			return nil
		}
		formats, err := parseFormats(answer)
		if err != nil {
			fmt.Println("  " + err.Error())
			continue
		}
		return formats
	}
}

// stdinIsTerminal reports whether standard input is an interactive terminal.
func stdinIsTerminal() bool {
	info, err := os.Stdin.Stat()
	if err != nil {
		return false
	}
	return info.Mode()&os.ModeCharDevice != 0
}

// unsafeNameChars matches anything that is not a letter, digit, dash or underscore.
var unsafeNameChars = regexp.MustCompile(`[^A-Za-z0-9_-]+`)

// safeFileName turns a name into text that is safe as a file or folder name: dots and slashes go,
// so a name cannot point outside the exports folder.
func safeFileName(name string) string {
	safe := strings.Trim(unsafeNameChars.ReplaceAllString(name, "-"), "-")
	if safe == "" {
		return "item"
	}
	return safe
}

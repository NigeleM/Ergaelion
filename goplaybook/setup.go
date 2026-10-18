package main

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"
)

// Setup guides: how to describe your own situation for any game. The text comes
// from data/setup-help.json, the same file the Python version reads.

type SetupHelp struct {
	Traits map[string]map[string]string `json:"traits"`
	Steps  []string                     `json:"steps"`
	Labels map[string]string            `json:"labels"`
}

func LoadSetupHelp() (SetupHelp, error) {
	var help SetupHelp
	data, err := dataFS.ReadFile("data/setup-help.json")
	if err != nil {
		return help, err
	}
	if err := json.Unmarshal(data, &help); err != nil {
		return help, fmt.Errorf("parsing setup-help.json: %w", err)
	}
	return help, nil
}

// ScenarioTemplate is a .gt scenario file prefilled with the game's traits and domains.
func ScenarioTemplate(g Game) string {
	lines := []string{"title: My " + g.Name + " situation"}
	for _, key := range Traits {
		if v, ok := g.Traits[key]; ok {
			lines = append(lines, key+": "+v)
		}
	}
	if len(g.Domains) > 0 {
		lines = append(lines, "domain: "+strings.Join(g.Domains, ", "))
	}
	lines = append(lines, "notes: Describe your situation here. Replace the example options with your own.")
	return strings.Join(lines, "\n") + "\n"
}

// GuideText builds the markdown guide for one game.
func GuideText(g Game, help SetupHelp, hasSim bool) string {
	labels := withLabels(englishSetupLabels, help.Labels)
	name, summary := g.Name, g.Summary
	var b strings.Builder
	fmt.Fprintf(&b, "# %s\n\n%s\n\n%s\n", name, summary, labels["traits_heading"])
	for _, key := range Traits {
		if v, ok := g.Traits[key]; ok {
			fmt.Fprintf(&b, "- %s = %s: %s\n", key, v, help.Traits[key][v])
		}
	}
	b.WriteString("\n" + labels["steps_heading"] + "\n")
	for _, step := range help.Steps {
		b.WriteString(step + "\n")
	}
	b.WriteString("\n" + labels["options_heading"] + "\n")
	for i, rule := range g.Strategies {
		if i == 3 {
			break
		}
		fmt.Fprintf(&b, "- %s\n", fillLabel(labels["option_idea"], "n", fmt.Sprint(i+1), "rule", rule))
	}
	if m := g.Matrix; m != nil {
		var rows []string
		for _, row := range m.Payoffs {
			var cells []string
			for _, c := range row {
				cells = append(cells, fmt.Sprintf("%d,%d", c[0], c[1]))
			}
			rows = append(rows, strings.Join(cells, " "))
		}
		rowList, colList := strings.Join(m.Rows, ", "), strings.Join(m.Cols, ", ")
		fmt.Fprintf(&b, "\n%s\n%s\n", labels["payoff_heading"],
			fillLabel(labels["payoff_rows"], "rows", rowList, "cols", colList))
		fmt.Fprintf(&b, "%s\n", fillLabel(labels["payoff_enter"], "cells", strings.Join(rows, "; "),
			"rows", strings.Join(m.Rows, ","), "cols", strings.Join(m.Cols, ",")))
	}
	if hasSim {
		fmt.Fprintf(&b, "\n%s\n", fillLabel(labels["simulation_line"], "id", g.ID))
	}
	b.WriteString("\n" + labels["template_heading"] + "\n```\n" + strings.TrimRight(ScenarioTemplate(g), "\n") + "\n```\n")
	return b.String()
}

func cmdSetup(args []string, games []Game) error {
	help, err := LoadSetupHelp()
	if err != nil {
		return err
	}
	sims, err := LoadSimulations()
	if err != nil {
		return err
	}
	hasSim := map[string]bool{}
	for _, s := range sims {
		hasSim[s.ID] = true
	}

	var write string
	var pos []string
	all := false
	for i := 0; i < len(args); i++ {
		switch {
		case args[i] == "--all":
			all = true
		case args[i] == "--write" && i+1 < len(args):
			write = args[i+1]
			i++
		case strings.HasPrefix(args[i], "--"):
			return fmt.Errorf("unknown option %s", args[i])
		default:
			pos = append(pos, args[i])
		}
	}

	if all {
		for _, g := range games {
			fmt.Println(GuideText(g, help, hasSim[g.ID]))
		}
		return nil
	}
	if len(pos) == 0 {
		return fmt.Errorf("name a game, e.g. 'setup chicken', or use --all for every game")
	}
	game, err := FindGame(games, strings.Join(pos, " "))
	if err != nil {
		return err
	}
	if write != "" {
		if err := os.WriteFile(write, []byte(ScenarioTemplate(*game)), 0o644); err != nil {
			return err
		}
		fmt.Println(green(fmt.Sprintf("Wrote a scenario template for %s to %s", game.Name, write)))
		fmt.Println(dim("Edit it, then run: advise " + write))
		return nil
	}
	fmt.Println(GuideText(*game, help, hasSim[game.ID]))
	return nil
}

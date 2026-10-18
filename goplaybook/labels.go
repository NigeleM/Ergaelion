package main

import "strings"

// englishSetupLabels are the headings and lines of a setup guide. A data file can override any of them.
var englishSetupLabels = map[string]string{
	"traits_heading":   "## Traits and what each one means",
	"steps_heading":    "## Steps to set up your own version",
	"options_heading":  "## Options to model",
	"option_idea":      "Option idea {n}: {rule}",
	"payoff_heading":   "## Payoff grid",
	"payoff_rows":      "Rows (you): {rows}. Columns (them): {cols}.",
	"payoff_enter":     `Enter it with: solve "{cells}" --rows {rows} --cols {cols}`,
	"simulation_line":  "Simulation: `sim {id}` shows the paths, and `sim {id} --play` lets you choose.",
	"template_heading": "## Start from this template",
}

// englishGuideLabels are the lines of the guide command. A data file can override any of them.
var englishGuideLabels = map[string]string{
	"sections":           "Guide sections",
	"power_line":         "power: {n} principles of strategy, influence and judgement",
	"defend_line":        "defend: {n} manipulation tactics and how to recognise and resist them",
	"research_line":      "research: {n} steps for research, and starting references",
	"life_line":          "life: {n} practical habits for decisions",
	"run_hint":           "Run 'guide power', 'guide power 48', or 'guide defend pressure' for details.",
	"defence":            "defence",
	"signs":              "signs",
	"tested_in":          "tested in",
	"no_match_principle": "no principle matches '{query}'",
	"no_match_tactic":    "no tactic matches '{query}'",
}

// withLabels returns the labels, with any overrides from a data file.
func withLabels(english, overrides map[string]string) map[string]string {
	out := make(map[string]string, len(english))
	for k, v := range english {
		out[k] = v
	}
	for k, v := range overrides {
		out[k] = v
	}
	return out
}

// fillLabel replaces {name} placeholders in a label with the values given as name, value pairs.
func fillLabel(template string, pairs ...string) string {
	args := make([]string, 0, len(pairs)*2)
	for i := 0; i+1 < len(pairs); i += 2 {
		args = append(args, "{"+pairs[i]+"}", pairs[i+1])
	}
	return strings.NewReplacer(args...).Replace(template)
}

package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"math"
	"strconv"
	"strings"
)

// This file is the Go side of the tool layer. It mirrors
// gtplaybook/tool_api.py: the same seven tools, the same schemas (data/tools.json) and the
// same JSON results. Results use sorted keys, as the Python version prints them.

// toolNames are the tools, in the order the Python version lists them.
var toolNames = []string{"find_games", "get_game", "list_games", "solve_matrix", "list_simulations", "get_simulation", "repeat_summary"}

// toolsText is the schema list, exactly as data/tools.json holds it.
func toolsText() (string, error) {
	data, err := dataFS.ReadFile("data/tools.json")
	return string(data), err
}

// roundedChance writes whole numbers as integers and other chances to four places, as the Python version does.
func roundedChance(v float64) any {
	if v == math.Trunc(v) {
		return int64(v)
	}
	r, _ := strconv.ParseFloat(strconv.FormatFloat(v, 'f', 4, 64), 64)
	return r
}

// encodeToolJSON prints a result the way the Python version does: indented, keys sorted, no HTML escaping.
func encodeToolJSON(value any) (string, error) {
	var buf bytes.Buffer
	enc := json.NewEncoder(&buf)
	enc.SetEscapeHTML(false)
	enc.SetIndent("", "  ")
	if err := enc.Encode(value); err != nil {
		return "", err
	}
	return strings.TrimSuffix(buf.String(), "\n"), nil
}

func toolError(err error) map[string]any {
	return map[string]any{"error": err.Error()}
}

func stringArg(args map[string]any, key string) (string, bool) {
	v, ok := args[key].(string)
	return v, ok && v != ""
}

// callTool runs one tool and returns its result as JSON-ready data. Errors come back as {"error": ...}.
func callTool(name string, args map[string]any, games []Game) any {
	if args == nil {
		args = map[string]any{}
	}
	switch name {
	case "find_games":
		text, _ := stringArg(args, "description")
		return toolFindGames(text, games)
	case "get_game":
		query, _ := stringArg(args, "game")
		g, err := FindGame(games, query)
		if err != nil {
			return toolError(err)
		}
		return toolGameSummary(*g)
	case "list_games":
		area, _ := stringArg(args, "area")
		return toolListGames(area, games)
	case "solve_matrix":
		text, _ := stringArg(args, "matrix")
		m, err := ParseMatrix(text)
		if err != nil {
			return toolError(err)
		}
		rows := make([]string, len(m))
		for i := range m {
			rows[i] = fmt.Sprintf("R%d", i+1)
		}
		cols := make([]string, len(m[0]))
		for j := range m[0] {
			cols[j] = fmt.Sprintf("C%d", j+1)
		}
		data, err := json.Marshal(solveJSON(m, rows, cols))
		if err != nil {
			return toolError(err)
		}
		return json.RawMessage(data)
	case "list_simulations":
		mode, _ := stringArg(args, "mode")
		return toolListSimulations(mode)
	case "get_simulation":
		query, _ := stringArg(args, "simulation")
		return toolGetSimulation(query)
	case "repeat_summary":
		query, _ := stringArg(args, "game")
		opponent, _ := stringArg(args, "opponent")
		rounds := 10
		if r, ok := args["rounds"].(float64); ok {
			rounds = int(r)
		}
		return toolRepeatSummary(query, opponent, rounds, games)
	}
	return toolError(fmt.Errorf("unknown tool '%s'. Tools: %s", name, strings.Join(toolNames, ", ")))
}

func toolFindGames(text string, games []Game) map[string]any {
	kw, err := loadKeywords()
	if err != nil {
		return toolError(err)
	}
	areas, err := LoadAreas()
	if err != nil {
		return toolError(err)
	}
	sims, err := LoadSimulations()
	if err != nil {
		return toolError(err)
	}
	s := suggest(text, games, sims, kw, areas, 5)
	phrases := append([]string{}, s.Phrases...)
	gameList := []map[string]any{}
	for _, g := range s.Games {
		gameList = append(gameList, map[string]any{"id": g.ID, "name": g.Name, "matched": g.Matched})
	}
	areaList := []string{}
	for _, f := range s.Families {
		areaList = append(areaList, f.Name)
	}
	simList := []map[string]any{}
	for _, sim := range s.Simulations {
		simList = append(simList, map[string]any{"id": sim.ID, "name": sim.Name})
	}
	return map[string]any{
		"matched_phrases": phrases,
		"games":           gameList,
		"areas":           areaList,
		"simulations":     simList,
		"message":         describeSuggestion(s, text),
	}
}

func toolGameSummary(g Game) map[string]any {
	out := map[string]any{
		"id": g.ID, "name": g.Name, "category": g.Category, "summary": g.Summary,
		"how_it_works": g.HowItWorks, "strategies": nonNilStrings(g.Strategies),
		"pitfalls": nonNilStrings(g.Pitfalls), "examples": nonNilStrings(g.Examples),
	}
	if m := g.Matrix; m != nil {
		out["payoff_table"] = map[string]any{"rows": m.Rows, "cols": m.Cols, "payoffs": m.Payoffs}
		out["payoff_table_note"] = g.MatrixNote
	} else if g.MatrixUnavailable != "" {
		out["payoff_table"] = nil
		out["payoff_table_note"] = g.MatrixUnavailable
	}
	return out
}

func nonNilStrings(s []string) []string {
	if s == nil {
		return []string{}
	}
	return s
}

func toolListGames(area string, games []Game) any {
	list := games
	if area != "" {
		areas, err := LoadAreas()
		if err != nil {
			return toolError(err)
		}
		in := map[string]bool{}
		found := false
		for _, a := range areas {
			if strings.EqualFold(a.Family, area) {
				found = true
				for _, sub := range a.Subdomains {
					for _, gid := range sub.Games {
						in[gid] = true
					}
				}
			}
		}
		if !found {
			return toolError(fmt.Errorf("no area named '%s'", area))
		}
		list = nil
		for _, g := range games {
			if in[g.ID] {
				list = append(list, g)
			}
		}
	}
	out := []map[string]any{}
	for _, g := range list {
		out = append(out, map[string]any{"id": g.ID, "name": g.Name, "category": g.Category})
	}
	return out
}

func toolListSimulations(mode string) any {
	sims, err := LoadSimulations()
	if err != nil {
		return toolError(err)
	}
	out := []map[string]any{}
	for _, s := range sims {
		if mode != "" && s.modeOrBasic() != mode {
			continue
		}
		out = append(out, map[string]any{"id": s.ID, "name": s.Name, "mode": s.modeOrBasic(), "families": nonNilStrings(s.Families)})
	}
	return out
}

func toolGetSimulation(query string) any {
	sims, err := LoadSimulations()
	if err != nil {
		return toolError(err)
	}
	sim, err := FindSimulation(sims, query)
	if err != nil {
		return toolError(err)
	}
	victory := solve(sim, "victory")[sim.Start].value
	failure := solve(sim, "failure")[sim.Start].value
	counts := map[string]int{"victory": 0, "draw": 0, "failure": 0}
	for _, e := range endings(sim) {
		counts[e.Outcome]++
	}
	return map[string]any{
		"id": sim.ID, "name": sim.Name, "mode": sim.modeOrBasic(), "summary": sim.Summary,
		"chance_of_victory_on_best_path":  roundedChance(victory),
		"chance_of_failure_on_worst_path": roundedChance(failure),
		"endings_found":                   counts,
	}
}

func toolRepeatSummary(query, opponent string, rounds int, games []Game) any {
	g, err := FindGame(games, query)
	if err != nil {
		return toolError(err)
	}
	if g.Matrix == nil {
		return toolError(fmt.Errorf("%s has no payoff table, so it cannot be repeated", g.Name))
	}
	if rounds < 1 || rounds > maxRepeatRounds {
		return toolError(fmt.Errorf("rounds must be from 1 to %d", maxRepeatRounds))
	}
	if !contains(repeatOpponents, opponent) {
		return toolError(fmt.Errorf("unknown opponent '%s'", opponent))
	}
	row, total, err := bestFixedPlan(*g.Matrix, rounds, opponent, 1)
	if err != nil {
		return toolError(err)
	}
	return map[string]any{
		"game": g.ID, "opponent": opponent, "rounds": rounds,
		"bot_rule":        repeatDescriptions[opponent],
		"best_fixed_plan": map[string]any{"row": g.Matrix.Rows[row], "total": total},
	}
}

// cmdTools prints the tool schemas, exactly as the Python version does.
func cmdTools(args []string) error {
	text, err := toolsText()
	if err != nil {
		return err
	}
	fmt.Print(text)
	return nil
}

// cmdTool runs one tool with JSON arguments and prints its result.
func cmdTool(args []string, games []Game) error {
	if len(args) == 0 || len(args) > 2 {
		return fmt.Errorf("usage: tool <name> [json arguments]")
	}
	arguments := map[string]any{}
	if len(args) == 2 {
		if err := json.Unmarshal([]byte(args[1]), &arguments); err != nil {
			return fmt.Errorf("the arguments must be JSON: %v", err)
		}
	}
	text, err := encodeToolJSON(callTool(args[0], arguments, games))
	if err != nil {
		return err
	}
	fmt.Println(text)
	return nil
}

package main

import (
	"encoding/json"
	"fmt"
	"sort"
)

// Combination is a multi-game playbook for a complex situation (data/combinations.json).
type Combination struct {
	ID        string   `json:"id"`
	Name      string   `json:"name"`
	Phrases   []string `json:"phrases"`
	Games     []string `json:"games"`
	Combined  string   `json:"combined"`
	Steps     []string `json:"steps"`
	WatchOuts []string `json:"watch_outs"`
}

// loadCombinations reads the multi-game playbooks from the embedded data.
func loadCombinations() ([]Combination, error) {
	data, err := dataFS.ReadFile("data/combinations.json")
	if err != nil {
		return nil, err
	}
	var out []Combination
	if err := json.Unmarshal(data, &out); err != nil {
		return nil, fmt.Errorf("parsing combinations.json: %w", err)
	}
	return out, nil
}

// combinationHit is a combination whose phrases appear in the description.
type combinationHit struct {
	Combination Combination
	Phrases     []string
}

// matchedCombinations returns the combinations whose phrases appear in the text, most phrases first.
func matchedCombinations(text string, combos []Combination) []combinationHit {
	tokens := keywordTokens(text)
	var hits []combinationHit
	for _, combo := range combos {
		var found []string
		for _, p := range combo.Phrases {
			if phraseMatches(tokens, p) {
				found = append(found, p)
			}
		}
		if len(found) > 0 {
			hits = append(hits, combinationHit{Combination: combo, Phrases: found})
		}
	}
	sort.SliceStable(hits, func(a, b int) bool {
		if len(hits[a].Phrases) != len(hits[b].Phrases) {
			return len(hits[a].Phrases) > len(hits[b].Phrases)
		}
		return hits[a].Combination.Name < hits[b].Combination.Name
	})
	return hits
}

// combinedRule is one strategy and the game it comes from.
type combinedRule struct {
	Game     string
	Strategy string
}

// combinedRules takes the first two strategies from each of the top games, so the advice blends several models.
func combinedRules(hits []Hit, count int) []combinedRule {
	var rules []combinedRule
	for i, hit := range hits {
		if i >= count {
			break
		}
		for j, strategy := range hit.Game.Strategies {
			if j >= 2 {
				break
			}
			rules = append(rules, combinedRule{Game: hit.Game.Name, Strategy: strategy})
		}
	}
	return rules
}

// printCombined prints the blended advice for a plain-English description: strategies from several games,
// multi-game playbooks, and scenarios to play. It mirrors print_combined in gtplaybook/cli.py.
func printCombined(sc *Scenario, games []Game, hits []Hit) {
	if sc.Text == "" {
		return
	}
	combos, err := loadCombinations()
	if err != nil {
		combos = nil
	}
	matches := matchedCombinations(sc.Text, combos)
	if len(hits) >= 2 && hits[1].Score >= 1 {
		fmt.Println("\n" + heading("Combined advice"))
		fmt.Println(dim("No single game covers all of this, so these come from the best fits together."))
		for _, rule := range combinedRules(hits, 3) {
			fmt.Println(bullet(rule.Strategy+"  ("+rule.Game+")", "•"))
		}
	}
	for _, m := range matches {
		combo := m.Combination
		fmt.Println("\n" + heading(combo.Name))
		fmt.Println(dim("matched: " + joinStrings(m.Phrases, ", ")))
		fmt.Println(paragraph(combo.Combined))
		fmt.Println(dim("Games that combine here: " + joinStrings(combo.Games, ", ")))
		for _, step := range combo.Steps {
			fmt.Println(bullet(step, "•"))
		}
		for _, warn := range combo.WatchOuts {
			fmt.Println(dim(bullet("watch out: "+warn, "!")))
		}
	}
	sims, _ := LoadSimulations()
	kw, _ := loadKeywords()
	areas, _ := LoadAreas()
	sug := suggest(sc.Text, games, sims, kw, areas, 5)
	if len(sug.Simulations) > 0 {
		fmt.Println("\n" + heading("Scenarios to play"))
		for i, s := range sug.Simulations {
			if i >= 3 {
				break
			}
			fmt.Println(bullet(s.Name+"  "+dim(s.ID), "•"))
		}
	}
}

// suggestSpelling points out words that may be typos when nothing matches. It mirrors suggest_spelling in cli.py.
func suggestSpelling(text string, games []Game, kw keywordData) {
	if text == "" {
		return
	}
	combos, _ := loadCombinations()
	close := closeWords(text, completionWords(games, kw, combos), 3)
	if len(close) == 0 {
		return
	}
	var parts []string
	for _, c := range close {
		parts = append(parts, c[0].(string)+" → "+joinStrings(c[1].([]string), ", "))
	}
	fmt.Println(dim("Did you mean: " + joinStrings(parts, "; ")))
}

func joinStrings(items []string, sep string) string {
	out := ""
	for i, item := range items {
		if i > 0 {
			out += sep
		}
		out += item
	}
	return out
}

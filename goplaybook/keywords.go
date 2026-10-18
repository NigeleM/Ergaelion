package main

import (
	"encoding/json"
	"fmt"
	"regexp"
	"sort"
	"strings"
)

// keywordData is the phrase groups for each game and the words for each area (data/keywords.json).
type keywordData struct {
	Games    map[string][]string `json:"games"`
	Families map[string][]string `json:"families"`
}

func loadKeywords() (keywordData, error) {
	var kw keywordData
	data, err := dataFS.ReadFile("data/keywords.json")
	if err != nil {
		return kw, err
	}
	return kw, json.Unmarshal(data, &kw)
}

var keywordWordRE = regexp.MustCompile(`[a-z]+`)

func keywordTokens(text string) []string {
	return keywordWordRE.FindAllString(strings.ReplaceAll(strings.ToLower(text), "'", ""), -1)
}

// sameKeyWord matches words that are equal, or one is the other with a plural 's' or 'es'.
func sameKeyWord(a, b string) bool {
	return a == b || a+"s" == b || b+"s" == a || a+"es" == b || b+"es" == a
}

// phraseMatches reports whether every word of the phrase appears in order in the tokens.
func phraseMatches(tokens []string, phrase string) bool {
	words := keywordTokens(phrase)
	if len(words) == 0 {
		return false
	}
	for start := 0; start+len(words) <= len(tokens); start++ {
		ok := true
		for i, w := range words {
			if !sameKeyWord(tokens[start+i], w) {
				ok = false
				break
			}
		}
		if ok {
			return true
		}
	}
	return false
}

func matchedPhrases(text string, phrases []string) []string {
	tokens := keywordTokens(text)
	var out []string
	for _, p := range phrases {
		if phraseMatches(tokens, p) {
			out = append(out, p)
		}
	}
	return out
}

type suggestedGame struct {
	ID      string
	Name    string
	Matched []string
}

type suggestedFamily struct {
	Name  string
	Score int
}

type suggestedSim struct {
	ID   string
	Name string
}

type suggestion struct {
	Phrases     []string
	Games       []suggestedGame
	Families    []suggestedFamily
	Simulations []suggestedSim
}

// suggest ranks games, areas and simulations by the phrases a description matches. It mirrors
// gtplaybook/keywords.py, so both versions give the same answer.
func suggest(text string, games []Game, sims []Simulation, kw keywordData, areas []Family, top int) suggestion {
	familyOfGame := map[string]map[string]bool{}
	for _, area := range areas {
		for _, sub := range area.Subdomains {
			for _, gid := range sub.Games {
				if familyOfGame[gid] == nil {
					familyOfGame[gid] = map[string]bool{}
				}
				familyOfGame[gid][area.Family] = true
			}
		}
	}

	familyHits := map[string][]string{}
	for family, words := range kw.Families {
		if found := matchedPhrases(text, words); len(found) > 0 {
			familyHits[family] = found
		}
	}
	gameHits := map[string][]string{}
	gameName := map[string]string{}
	for _, g := range games {
		gameName[g.ID] = g.Name
		if found := matchedPhrases(text, kw.Games[g.ID]); len(found) > 0 {
			gameHits[g.ID] = found
		}
	}

	var rankedGames []string
	for gid := range gameHits {
		rankedGames = append(rankedGames, gid)
	}
	// A longer matched phrase is stronger evidence than a single word, so weigh by words matched.
	weight := func(gid string) int {
		n := 0
		for _, p := range gameHits[gid] {
			n += len(keywordTokens(p))
		}
		return n
	}
	sort.Slice(rankedGames, func(i, j int) bool {
		a, b := weight(rankedGames[i]), weight(rankedGames[j])
		if a != b {
			return a > b
		}
		return rankedGames[i] < rankedGames[j]
	})

	familyScore := map[string]int{}
	for family, found := range familyHits {
		familyScore[family] = len(found)
	}
	for gid := range gameHits {
		for family := range familyOfGame[gid] {
			familyScore[family]++
		}
	}
	var rankedFamilies []suggestedFamily
	for family, score := range familyScore {
		rankedFamilies = append(rankedFamilies, suggestedFamily{family, score})
	}
	sort.Slice(rankedFamilies, func(i, j int) bool {
		if rankedFamilies[i].Score != rankedFamilies[j].Score {
			return rankedFamilies[i].Score > rankedFamilies[j].Score
		}
		return rankedFamilies[i].Name < rankedFamilies[j].Name
	})

	type simScore struct {
		score int
		sim   Simulation
	}
	var scored []simScore
	for _, s := range sims {
		n := 0
		for _, f := range s.Families {
			if familyScore[f] > 0 {
				n++
			}
		}
		if n > 0 {
			scored = append(scored, simScore{n, s})
		}
	}
	sort.Slice(scored, func(i, j int) bool {
		if scored[i].score != scored[j].score {
			return scored[i].score > scored[j].score
		}
		return scored[i].sim.ID < scored[j].sim.ID
	})

	var out suggestion
	seen := map[string]bool{}
	for _, found := range familyHits {
		for _, p := range found {
			seen[p] = true
		}
	}
	for _, found := range gameHits {
		for _, p := range found {
			seen[p] = true
		}
	}
	for p := range seen {
		out.Phrases = append(out.Phrases, p)
	}
	sort.Strings(out.Phrases)

	for _, gid := range rankedGames {
		if len(out.Games) == top {
			break
		}
		out.Games = append(out.Games, suggestedGame{gid, gameName[gid], gameHits[gid]})
	}
	if len(out.Games) == 0 && len(rankedFamilies) > 0 {
		best := rankedFamilies[0].Name
		var inArea []string
		for gid, fams := range familyOfGame {
			if fams[best] {
				inArea = append(inArea, gid)
			}
		}
		sort.Strings(inArea)
		for _, gid := range inArea {
			if len(out.Games) == top {
				break
			}
			out.Games = append(out.Games, suggestedGame{gid, gameName[gid], []string{"in " + best}})
		}
	}
	for i, f := range rankedFamilies {
		if i == top {
			break
		}
		out.Families = append(out.Families, f)
	}
	for i, s := range scored {
		if i == top {
			break
		}
		out.Simulations = append(out.Simulations, suggestedSim{s.sim.ID, s.sim.Name})
	}
	return out
}

// describeSuggestion is the suggestion as lines of text, ending with a question about whether it fits.
func describeSuggestion(s suggestion, text string) []string {
	if len(s.Games) == 0 && len(s.Families) == 0 {
		return []string{
			fmt.Sprintf("Nothing in '%s' matched a known game, family or phrase.", text),
			"Try a few more words, such as a situation (price war, bank run), a role (boss, voter, rebel)" +
				" or a kind of game (bluff, bargain, shared resource).",
		}
	}
	var lines []string
	if len(s.Phrases) > 0 {
		lines = append(lines, "Based on these words ("+strings.Join(s.Phrases, ", ")+") it looks like you're looking for:")
	} else {
		lines = append(lines, "Based on your words it looks like you're looking for:")
	}
	if len(s.Games) > 0 {
		lines = append(lines, "Games:")
		for _, g := range s.Games {
			lines = append(lines, fmt.Sprintf("  - %s  (matched: %s)", g.Name, strings.Join(g.Matched, ", ")))
		}
	}
	if len(s.Families) > 0 {
		var names []string
		for _, f := range s.Families {
			names = append(names, f.Name)
		}
		lines = append(lines, "Areas: "+strings.Join(names, ", "))
	}
	if len(s.Simulations) > 0 {
		var names []string
		for _, sim := range s.Simulations {
			names = append(names, sim.Name)
		}
		lines = append(lines, "Simulations: "+strings.Join(names, ", "))
	}
	lines = append(lines, "Does this fit? If not, add or change words, for example 'price war with a new competitor'.")
	return lines
}

// keywordSuggestion runs the parser on text with the embedded data and returns the lines to print.
func keywordSuggestion(text string, games []Game) ([]string, error) {
	kw, err := loadKeywords()
	if err != nil {
		return nil, err
	}
	areas, err := LoadAreas()
	if err != nil {
		return nil, err
	}
	sims, err := LoadSimulations()
	if err != nil {
		return nil, err
	}
	return describeSuggestion(suggest(text, games, sims, kw, areas, 5), text), nil
}

// cmdKeywords shows which games, areas and simulations a few words point to.
func cmdKeywords(args []string, games []Game) error {
	if len(args) == 0 {
		return fmt.Errorf("usage: keywords <a few words describing the situation>")
	}
	text := strings.Join(args, " ")
	lines, err := keywordSuggestion(text, games)
	if err != nil {
		return err
	}
	fmt.Println()
	for _, line := range lines {
		fmt.Println(line)
	}
	return nil
}

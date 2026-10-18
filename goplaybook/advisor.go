package main

import (
	"regexp"
	"sort"
	"strings"
)

// Hit is one game scored against a scenario.
type Hit struct {
	Game       *Game
	Score      float64
	Matched    []string
	Clashed    []string
	Shared     []string
	Phrases    []string
	Words      []string
	Adjustment float64
}

// Points for each kind of evidence. Phrases count most, because they were written for the way people
// describe these situations. The same values are used in gtplaybook/advisor.py.
const (
	phrasePoints = 3.0
	wordPoints   = 1.0
	traitPoints  = 0.5
	domainPoints = 0.5
)

// stopWords say nothing about which game fits. Kept in step with STOP_WORDS in gtplaybook/advisor.py.
var stopWords = map[string]bool{}

func init() {
	for _, w := range strings.Fields(`a an the and or but if then else of to in on at by for with from as is are was were be been
being it its this that these those i me my we our you your they their them he she his her there here what which
who whom whose do does did doing have has had having will would should could can cannot not no yes so than too
very just also about into over under up down out off again once only own same other each both all any some such
more most less least how when where why s t don't dont want wants need needs get gets make makes one two three
many much time times round decide decides people prefer prefers really think something things thing going goes
know knows different problem try tries trying keeps keep`) {
		stopWords[w] = true
	}
}

var wordTokenRE = regexp.MustCompile(`[a-z]+`)

// contentWords returns the distinct content words in a text, lower-case, with a simple plural ending removed.
func contentWords(text string) map[string]bool {
	out := map[string]bool{}
	for _, word := range wordTokenRE.FindAllString(strings.ReplaceAll(strings.ToLower(text), "'", ""), -1) {
		if len(word) < 3 || stopWords[word] {
			continue
		}
		if len(word) > 4 && strings.HasSuffix(word, "ies") {
			word = word[:len(word)-3] + "y"
		} else if len(word) > 4 && strings.HasSuffix(word, "s") && !strings.HasSuffix(word, "ss") {
			word = word[:len(word)-1]
		}
		out[word] = true
	}
	return out
}

// gameWords returns the content words in a game's name (counted twice), category, summary, how it works and examples.
func gameWords(g *Game) map[string]bool {
	parts := []string{g.Name, g.Name, g.Category, g.Summary, g.HowItWorks}
	parts = append(parts, g.Examples...)
	return contentWords(strings.Join(parts, " "))
}

// RankGames scores games against a scenario. text is the description the traits came from (may be empty);
// kw holds the phrases each game is known by; records holds your logged results per game id.
func RankGames(games []Game, traits map[string]string, domains []string, top int, records map[string]map[string]int, text string, kw keywordData) []Hit {
	described := contentWords(text)
	tokens := keywordTokens(text)
	var hits []Hit
	for i := range games {
		g := &games[i]
		var hit Hit
		hit.Game = g
		for _, key := range Traits {
			value, ok := traits[key]
			if !ok {
				continue
			}
			expected, ok := g.Traits[key]
			if !ok {
				continue
			}
			if expected == value {
				hit.Matched = append(hit.Matched, key)
			} else {
				hit.Clashed = append(hit.Clashed, key)
			}
		}
		for _, d := range domains {
			if contains(g.Domains, d) && !contains(hit.Shared, d) {
				hit.Shared = append(hit.Shared, d)
			}
		}
		sort.Strings(hit.Shared)
		for _, phrase := range kw.Games[g.ID] {
			if phraseMatches(tokens, phrase) {
				hit.Phrases = append(hit.Phrases, phrase)
			}
		}
		for word := range gameWords(g) {
			if described[word] {
				hit.Words = append(hit.Words, word)
			}
		}
		sort.Strings(hit.Words)
		hit.Adjustment = recordAdjustment(records[g.ID])
		hit.Score = phrasePoints*float64(len(hit.Phrases)) + wordPoints*float64(len(hit.Words)) +
			traitPoints*float64(len(hit.Matched)-len(hit.Clashed)) + domainPoints*float64(len(hit.Shared)) + hit.Adjustment
		hits = append(hits, hit)
	}
	sort.SliceStable(hits, func(a, b int) bool {
		if hits[a].Score != hits[b].Score {
			return hits[a].Score > hits[b].Score
		}
		return hits[a].Game.Name < hits[b].Game.Name
	})
	if top < len(hits) {
		hits = hits[:top]
	}
	return hits
}

// recordAdjustment nudges a game's fit by your results: +0.5 per net win, capped at +/-2.
func recordAdjustment(counts map[string]int) float64 {
	if counts == nil {
		return 0
	}
	adj := 0.5 * float64(counts["win"]-counts["loss"])
	if adj > 2 {
		return 2
	}
	if adj < -2 {
		return -2
	}
	return adj
}

type generalRule struct {
	when func(t map[string]string) bool
	text string
}

var generalRules = []generalRule{
	{func(t map[string]string) bool { return t["interaction"] == "repeated" },
		"Repeated play: cooperation can last if the future matters enough. Never defect in a known final round, and make your moves easy to read."},
	{func(t map[string]string) bool {
		return t["interaction"] == "one-shot" && t["payoff"] == "mixed" && t["enforcement"] != "yes"
	},
		"One-shot, mixed payoffs, no enforcement: expect the other side to defect if it can. Change the structure (contracts, penalties, escrow) rather than relying on goodwill."},
	{func(t map[string]string) bool { return t["timing"] == "sequential" },
		"Sequential moves: reason backward from the end. Ask what you would do at your last decision, work back, and check whether each threat or promise is credible."},
	{func(t map[string]string) bool { return t["information"] == "imperfect" },
		"Hidden information: costly signals are believable and cheap talk is not. Screen the other side with choices they must make, and verify claims."},
	{func(t map[string]string) bool { return t["commitment"] == "yes" },
		"Commitment matters: a threat or promise only works if it is visible and hard to reverse. Make backing out costly."},
	{func(t map[string]string) bool { return t["payoff"] == "zero-sum" },
		"Zero-sum: assume a capable opponent. Play maximin (the best worst case), avoid predictable patterns, and randomise where needed."},
	{func(t map[string]string) bool { return t["players"] == "many" },
		"Many players: free-riding is the default. Make contributions visible and add sanctions that are credible and proportionate."},
	{func(t map[string]string) bool { return t["bargaining"] == "yes" },
		"Bargaining: know your outside option (BATNA) before you talk. The better your alternative, the bigger your share. Patience is leverage, so notice who is under more time pressure."},
	{func(t map[string]string) bool { return t["communication"] == "yes" && t["payoff"] != "zero-sum" },
		"Communication: promises are cheap. Use talk to agree on a focal point, then confirm it with an action the other side can observe."},
}

// GeneralRules returns the rules that apply to the given traits.
func GeneralRules(traits map[string]string) []string {
	var out []string
	for _, r := range generalRules {
		if r.when(traits) {
			out = append(out, r.text)
		}
	}
	return out
}

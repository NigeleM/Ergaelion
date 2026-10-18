package main

import (
	"regexp"
	"sort"
	"strings"
)

// completionWords is every word a description is likely to use: words from the game phrases, area words,
// combination phrases and game names. It mirrors keywords.vocabulary in gtplaybook/keywords.py.
func completionWords(games []Game, kw keywordData, combos []Combination) []string {
	words := map[string]bool{}
	add := func(text string) {
		for _, w := range keywordTokens(text) {
			words[w] = true
		}
	}
	for _, phrases := range kw.Games {
		for _, p := range phrases {
			add(p)
		}
	}
	for _, phrases := range kw.Families {
		for _, p := range phrases {
			add(p)
		}
	}
	for _, c := range combos {
		for _, p := range c.Phrases {
			add(p)
		}
	}
	for _, g := range games {
		add(g.Name)
	}
	var out []string
	for w := range words {
		if len(w) > 2 {
			out = append(out, w)
		}
	}
	sort.Strings(out)
	return out
}

// phrases is every known scenario phrase in lower case, sorted. It mirrors keywords.phrase_list.
func phrases(kw keywordData, combos []Combination) []string {
	set := map[string]bool{}
	for _, items := range kw.Games {
		for _, p := range items {
			set[strings.ToLower(p)] = true
		}
	}
	for _, c := range combos {
		for _, p := range c.Phrases {
			set[strings.ToLower(p)] = true
		}
	}
	var out []string
	for p := range set {
		out = append(out, p)
	}
	sort.Strings(out)
	return out
}

// completePhrase returns known phrases that continue the text: at least two words and eight characters,
// shortest first, at most twelve. It mirrors keywords.complete_phrase in gtplaybook/keywords.py.
func completePhrase(text string, known []string) []string {
	typed := strings.ToLower(strings.TrimLeft(text, " \t"))
	if !strings.Contains(strings.TrimSpace(typed), " ") || len(typed) < 8 {
		return nil
	}
	var matches []string
	for _, p := range known {
		if strings.HasPrefix(p, typed) && p != typed {
			matches = append(matches, p)
		}
	}
	sort.SliceStable(matches, func(a, b int) bool {
		if len(matches[a]) != len(matches[b]) {
			return len(matches[a]) < len(matches[b])
		}
		return matches[a] < matches[b]
	})
	if len(matches) > 12 {
		matches = matches[:12]
	}
	return matches
}

// completeWord returns vocabulary words that start with the prefix, shortest first, at most limit of them.
// It mirrors keywords.complete_word in gtplaybook/keywords.py.
func completeWord(prefix string, words []string, limit int) []string {
	prefix = strings.ToLower(prefix)
	var matches []string
	for _, w := range words {
		if strings.HasPrefix(w, prefix) && w != prefix {
			matches = append(matches, w)
		}
	}
	sort.SliceStable(matches, func(a, b int) bool {
		if len(matches[a]) != len(matches[b]) {
			return len(matches[a]) < len(matches[b])
		}
		return matches[a] < matches[b]
	})
	if len(matches) > limit {
		matches = matches[:limit]
	}
	return matches
}

// editDistance counts the single-letter insertions, deletions and substitutions that turn a into b.
func editDistance(a, b string) int {
	ra, rb := []rune(a), []rune(b)
	previous := make([]int, len(rb)+1)
	for j := range previous {
		previous[j] = j
	}
	for i := 1; i <= len(ra); i++ {
		current := make([]int, len(rb)+1)
		current[0] = i
		for j := 1; j <= len(rb); j++ {
			cost := 1
			if ra[i-1] == rb[j-1] {
				cost = 0
			}
			current[j] = minInt(previous[j]+1, minInt(current[j-1]+1, previous[j-1]+cost))
		}
		previous = current
	}
	return previous[len(rb)]
}

func minInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// correctionPair is a likely typo and the known word it was read as.
type correctionPair struct {
	From, To string
}

// correctText replaces a likely typo with the one known word closest to it, when that match is unambiguous.
// Only a one-letter substitution changes a word, in words of six letters or more, and only where exactly
// one known word matches that way. Insertions and deletions are left alone. It mirrors keywords.correct_text in gtplaybook/keywords.py.
func correctText(text string, words []string) (string, []correctionPair) {
	known := map[string]bool{}
	for _, w := range words {
		known[w] = true
	}
	seen := map[string]bool{}
	var unique []string
	for _, w := range keywordTokens(text) {
		if !seen[w] {
			seen[w] = true
			unique = append(unique, w)
		}
	}
	sort.Strings(unique)
	out := text
	var changes []correctionPair
	for _, word := range unique {
		if len([]rune(word)) < 6 || known[word] {
			continue
		}
		var near []string
		for _, v := range words {
			if len([]rune(v)) == len([]rune(word)) && editDistance(word, v) == 1 {
				near = append(near, v)
			}
		}
		if len(near) == 1 {
			pattern := regexp.MustCompile(`(?i)\b` + regexp.QuoteMeta(word) + `\b`)
			out = pattern.ReplaceAllLiteralString(out, near[0])
			changes = append(changes, correctionPair{From: word, To: near[0]})
		}
	}
	return out, changes
}

func absInt(a int) int {
	if a < 0 {
		return -a
	}
	return a
}

// closeWords lists, for each unknown word of four letters or more, the nearest known words (likely typos).
// It mirrors keywords.close_words in gtplaybook/keywords.py.
func closeWords(text string, words []string, limit int) [][2]interface{} {
	known := map[string]bool{}
	for _, w := range words {
		known[w] = true
	}
	seen := map[string]bool{}
	var unique []string
	for _, w := range keywordTokens(text) {
		if !seen[w] {
			seen[w] = true
			unique = append(unique, w)
		}
	}
	sort.Strings(unique)
	var out [][2]interface{}
	for _, word := range unique {
		if len([]rune(word)) < 4 || known[word] {
			continue
		}
		allowed := 1
		if len([]rune(word)) > 5 {
			allowed = 2
		}
		type cand struct {
			dist int
			word string
		}
		var near []cand
		for _, v := range words {
			if absInt(len([]rune(v))-len([]rune(word))) <= allowed {
				near = append(near, cand{editDistance(word, v), v})
			}
		}
		sort.SliceStable(near, func(a, b int) bool {
			if near[a].dist != near[b].dist {
				return near[a].dist < near[b].dist
			}
			return near[a].word < near[b].word
		})
		var suggestions []string
		for _, c := range near {
			if c.dist <= allowed && len(suggestions) < limit {
				suggestions = append(suggestions, c.word)
			}
		}
		if len(suggestions) > 0 {
			out = append(out, [2]interface{}{word, suggestions})
		}
	}
	return out
}

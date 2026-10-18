package main

import (
	"strings"
	"testing"
)

func analyse(t *testing.T, text string) Analysis {
	t.Helper()
	m, err := ParseMatrix(text)
	if err != nil {
		t.Fatalf("parse %q: %v", text, err)
	}
	return Analyse(m)
}

func TestPrisonersDilemmaDominance(t *testing.T) {
	res := analyse(t, "3,3 0,5; 5,0 1,1")
	if len(res.Equilibria) != 1 || res.Equilibria[0] != [2]int{1, 1} {
		t.Fatalf("equilibria = %v, want [[1 1]]", res.Equilibria)
	}
	if len(res.SurvivingRows) != 1 || res.SurvivingRows[0] != 1 {
		t.Fatalf("surviving rows = %v, want [1]", res.SurvivingRows)
	}
}

func TestMatchingPenniesMixed(t *testing.T) {
	res := analyse(t, "1,-1 -1,1; -1,1 1,-1")
	if len(res.Equilibria) != 0 {
		t.Fatalf("expected no pure equilibria, got %v", res.Equilibria)
	}
	if res.Mixed == nil || res.Mixed[0].RatString() != "1/2" || res.Mixed[1].RatString() != "1/2" {
		t.Fatalf("mixed = %v, want 1/2, 1/2", res.Mixed)
	}
	if res.ConstantSum == nil || res.ConstantSum.Sign() != 0 {
		t.Fatalf("constant sum = %v, want 0", res.ConstantSum)
	}
}

func TestInspectionGameMixed(t *testing.T) {
	res := analyse(t, "-1,0 2,-3; 0,0 -2,2")
	if res.Mixed == nil || res.Mixed[0].RatString() != "2/5" || res.Mixed[1].RatString() != "4/5" {
		t.Fatalf("mixed = %v, want 2/5, 4/5", res.Mixed)
	}
}

func TestBattleOfSexesTwoPureEquilibria(t *testing.T) {
	res := analyse(t, "2,1 0,0; 0,0 1,2")
	if len(res.Equilibria) != 2 {
		t.Fatalf("equilibria = %v, want two", res.Equilibria)
	}
}

func TestParseRejectsBadCell(t *testing.T) {
	if _, err := ParseMatrix("3 0,5; 5,0 1,1"); err == nil {
		t.Fatal("expected error for cell without comma")
	}
}

func TestParseRejectsRaggedMatrix(t *testing.T) {
	if _, err := ParseMatrix("1,1 2,2; 3,3"); err == nil {
		t.Fatal("expected error for ragged matrix")
	}
}

func TestParseScenarioNormalises(t *testing.T) {
	sc, err := ParseScenario("title: T\nplayers: 2\ntiming: Sequential\ndomain: work, business\n")
	if err != nil {
		t.Fatal(err)
	}
	if sc.Traits["players"] != "two" || sc.Traits["timing"] != "sequential" {
		t.Fatalf("traits = %v", sc.Traits)
	}
	if len(sc.Domains) != 2 {
		t.Fatalf("domains = %v", sc.Domains)
	}
}

func TestParseScenarioReportsLine(t *testing.T) {
	_, err := ParseScenario("title: x\ntiming: never\n")
	if err == nil || !strings.Contains(err.Error(), "line 2") {
		t.Fatalf("error = %v, want line 2", err)
	}
}

func TestDescribeNegotiation(t *testing.T) {
	sc := Describe("I'm negotiating my salary with a new employer, we will talk once")
	if sc.Traits["bargaining"] != "yes" || sc.Traits["interaction"] != "one-shot" {
		t.Fatalf("traits = %v", sc.Traits)
	}
	if !contains(sc.Domains, "work") {
		t.Fatalf("domains = %v, want work", sc.Domains)
	}
}

func TestDescribeIrreversibleIsCommitment(t *testing.T) {
	sc := Describe("The army makes an irreversible threat")
	if sc.Traits["commitment"] != "yes" {
		t.Fatalf("commitment = %q, want yes", sc.Traits["commitment"])
	}
}

func TestDescribeImperfectIsNotPerfect(t *testing.T) {
	sc := Describe("We have imperfect information about rival costs")
	if sc.Traits["information"] != "imperfect" {
		t.Fatalf("information = %q, want imperfect", sc.Traits["information"])
	}
}

func TestOneShotMixedRanksPrisonersDilemmaTopThree(t *testing.T) {
	games, err := LoadGames()
	if err != nil {
		t.Fatal(err)
	}
	traits := map[string]string{
		"players": "two", "timing": "simultaneous", "interaction": "one-shot",
		"payoff": "mixed", "enforcement": "no",
	}
	// Several games share the same traits, so ties are broken by name. Check the score, not the position.
	scores := map[string]float64{}
	kw, _ := loadKeywords()
	for _, h := range RankGames(games, traits, nil, len(games), nil, "", kw) {
		scores[h.Game.ID] = h.Score
	}
	best := 0.0
	for _, s := range scores {
		if s > best {
			best = s
		}
	}
	if scores["prisoners-dilemma"] != best {
		t.Fatalf("prisoners-dilemma scores %v, best is %v", scores["prisoners-dilemma"], best)
	}
}

func TestFindGameAmbiguous(t *testing.T) {
	games, _ := LoadGames()
	if _, err := FindGame(games, "game"); err == nil {
		t.Fatal("expected ambiguous error")
	}
}

func TestCorrectTextOnlyFixesOneLetterSubstitutions(t *testing.T) {
	vocab := []string{"trojan", "troops", "tariff", "order"}
	got, changes := correctText("a trojen horse", vocab)
	if got != "a trojan horse" || len(changes) != 1 {
		t.Fatalf("trojen not corrected: %q %v", got, changes)
	}
	// "border" is one letter longer than "order": it is a real word, so it must stay.
	if got, _ := correctText("the border", vocab); got != "the border" {
		t.Fatalf("border was changed to %q", got)
	}
}

func TestCompleteWordOffersShortestFirst(t *testing.T) {
	words := []string{"tariff", "tariffs", "trojan", "troops"}
	got := completeWord("tar", words, 12)
	if len(got) != 2 || got[0] != "tariff" || got[1] != "tariffs" {
		t.Fatalf("completions for tar: %v", got)
	}
}

func TestEditDistance(t *testing.T) {
	if d := editDistance("kitten", "sitting"); d != 3 {
		t.Fatalf("kitten/sitting = %d, want 3", d)
	}
}

func TestTrojanHorseBringsInItsPlaybook(t *testing.T) {
	combos, err := loadCombinations()
	if err != nil {
		t.Fatal(err)
	}
	hits := matchedCombinations("a trojan horse hidden in a gift", combos)
	if len(hits) == 0 || hits[0].Combination.ID != "hidden-threat-deception" {
		t.Fatalf("no trojan-horse playbook: %v", hits)
	}
}

func TestCompletePhraseNeedsTwoWordsAndContinuesTheText(t *testing.T) {
	known := []string{"coin toss", "heads or tails", "heads or tails bet"}
	if got := completePhrase("coin", known); got != nil {
		t.Fatalf("a single word should not complete a phrase: %v", got)
	}
	got := completePhrase("heads or", known)
	if len(got) != 2 || got[0] != "heads or tails" || got[1] != "heads or tails bet" {
		t.Fatalf("phrase completions for 'heads or': %v", got)
	}
}

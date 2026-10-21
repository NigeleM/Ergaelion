package main

import (
	"os"
	"path/filepath"
	"testing"
)

func TestCatalogHasAtLeast50Games(t *testing.T) {
	games, err := LoadGames()
	if err != nil {
		t.Fatal(err)
	}
	if len(games) < 50 {
		t.Fatalf("got %d games, want at least 50", len(games))
	}
}

func TestEveryGameIsInAFamily(t *testing.T) {
	games, err := LoadGames()
	if err != nil {
		t.Fatal(err)
	}
	families, err := LoadAreas()
	if err != nil {
		t.Fatal(err)
	}
	listed := map[string]bool{}
	for _, f := range families {
		for _, sd := range f.Subdomains {
			for _, id := range sd.Games {
				listed[id] = true
			}
		}
	}
	for _, g := range games {
		if !listed[g.ID] {
			t.Errorf("game %s is not in any family", g.ID)
		}
	}
}

func TestEveryGameIsInATopic(t *testing.T) {
	games, err := LoadGames()
	if err != nil {
		t.Fatal(err)
	}
	topics, err := LoadTopics()
	if err != nil {
		t.Fatal(err)
	}
	known := map[string]bool{}
	for _, topic := range topics {
		known[topic.ID] = true
	}
	for _, g := range games {
		if len(g.Domains) == 0 {
			t.Errorf("game %s has no domain", g.ID)
		}
		for _, d := range g.Domains {
			if !known[d] {
				t.Errorf("game %s has domain %s, which is not a topic", g.ID, d)
			}
		}
	}
	for _, topic := range topics {
		if len(topicGames(games, topic.ID)) == 0 {
			t.Errorf("topic %s has no games", topic.ID)
		}
	}
}

func TestEngineHelpers(t *testing.T) {
	if got := beautyEngineGuess(nil); got != 33 {
		t.Errorf("first guess = %d, want 33", got)
	}
	if got := beautyEngineGuess([]int{20}); got != 13 {
		t.Errorf("guess after 20 = %d, want 13", got)
	}
	for engine := 0; engine <= beautyTop; engine += 2 {
		if got := beautyTarget(engine/2, engine); got != engine/2 {
			t.Errorf("half of %d misses the target: %d", engine, got)
		}
	}
	if got := pennyEngineCoin(nil); got != "t" {
		t.Errorf("first coin = %s, want t", got)
	}
	if got := pennyEngineCoin([]string{"h", "h", "t"}); got != "t" {
		t.Errorf("coin against heads = %s, want t", got)
	}
	if got := pennyEngineCoin([]string{"t", "t", "h"}); got != "h" {
		t.Errorf("coin against tails = %s, want h", got)
	}
	if ultimatumAccepts(2) || !ultimatumAccepts(3) {
		t.Errorf("ultimatum threshold should be %d coins", ultimatumThreshold)
	}
	if n, ok := wholeNumber("007", 10); !ok || n != 7 {
		t.Errorf("wholeNumber(007) = %d, %v", n, ok)
	}
	if _, ok := wholeNumber("11", 10); ok {
		t.Errorf("wholeNumber(11) should be out of range")
	}
	if _, ok := wholeNumber("99999999999999999999", 10); ok {
		t.Errorf("a huge number should be out of range")
	}
}

func TestEverySimulationHasVictoryAndFailurePaths(t *testing.T) {
	sims, err := LoadSimulations()
	if err != nil {
		t.Fatal(err)
	}
	if len(sims) == 0 {
		t.Fatal("no simulations loaded")
	}
	for i := range sims {
		sim := &sims[i]
		win := solve(sim, "victory")[sim.Start].value
		fail := solve(sim, "failure")[sim.Start].value
		if win <= 0 && !reachesOutcome(sim, "draw") {
			// Under perfect play some games are a draw: then a draw must be reachable instead.
			t.Errorf("%s: no path to victory or draw", sim.ID)
		}
		if fail <= 0 {
			t.Errorf("%s: no path to failure", sim.ID)
		}
	}
}

func TestOverlayReplacesBuiltInGame(t *testing.T) {
	t.Setenv("PLAYBOOK_HOME", t.TempDir())
	games, err := LoadGames()
	if err != nil {
		t.Fatal(err)
	}
	chicken, err := FindGame(games, "chicken")
	if err != nil {
		t.Fatal(err)
	}
	edited := *chicken
	edited.Name = "Chicken (edited)"
	if _, err := SaveOverlay(edited); err != nil {
		t.Fatal(err)
	}
	reloaded, err := LoadGames()
	if err != nil {
		t.Fatal(err)
	}
	found, err := FindGame(reloaded, "chicken")
	if err != nil {
		t.Fatal(err)
	}
	if found.Name != "Chicken (edited)" {
		t.Fatalf("overlay not applied: name = %q", found.Name)
	}
	if len(reloaded) != len(games) {
		t.Fatalf("replacing a game changed the count: %d -> %d", len(games), len(reloaded))
	}
}

func TestRecordTally(t *testing.T) {
	t.Setenv("PLAYBOOK_HOME", filepath.Join(t.TempDir(), "home"))
	if _, err := LogOutcome("chicken", "win", "held firm", 2); err != nil {
		t.Fatal(err)
	}
	if _, err := LogOutcome("chicken", "loss", "", 0); err != nil {
		t.Fatal(err)
	}
	if _, err := LogOutcome("chicken", "bogus", "", 0); err == nil {
		t.Fatal("expected an error for an unknown result")
	}
	counts, err := Tally()
	if err != nil {
		t.Fatal(err)
	}
	if got := FormatRecord(counts["chicken"]); got != "1W 1L 0D 0M" {
		t.Fatalf("record = %q", got)
	}
	if _, err := os.Stat(filepath.Join(PlaybookHome(), "outcomes.jsonl")); err != nil {
		t.Fatal(err)
	}
}

func TestAtLeastHalfTheGamesHaveASimulation(t *testing.T) {
	games, _ := LoadGames()
	sims, err := LoadSimulations()
	if err != nil {
		t.Fatal(err)
	}
	if len(sims) < len(games)/2 {
		t.Fatalf("got %d simulations for %d games, want at least half", len(sims), len(games))
	}
}

func TestEverySimulationListsAtLeastTwoAreas(t *testing.T) {
	sims, _ := LoadSimulations()
	for _, s := range sims {
		if len(s.Families) < 2 {
			t.Errorf("%s lists %d areas, want at least 2", s.ID, len(s.Families))
		}
	}
}

func TestEveryBranchSetSumsToOne(t *testing.T) {
	sims, _ := LoadSimulations()
	for _, s := range sims {
		for id, node := range s.Nodes {
			if node.Type != "nature" {
				continue
			}
			total := 0.0
			for _, b := range node.Branches {
				total += b.P
			}
			if total < 0.999999 || total > 1.000001 {
				t.Errorf("%s node %s: branches sum to %v", s.ID, id, total)
			}
		}
	}
}

func reachesOutcome(sim *Simulation, outcome string) bool {
	for _, e := range endings(sim) {
		if e.Outcome == outcome {
			return true
		}
	}
	return false
}

func TestParseFormatsReadsListsAndAll(t *testing.T) {
	all, err := parseFormats("all")
	if err != nil || len(all) != 4 {
		t.Fatalf("all: got %v, %v", all, err)
	}
	some, err := parseFormats("csv, md")
	if err != nil || len(some) != 2 || some[0] != "md" || some[1] != "csv" {
		t.Fatalf("csv, md: got %v, %v", some, err)
	}
	if _, err := parseFormats("pdf"); err == nil {
		t.Fatal("pdf should be rejected")
	}
}

func TestDuelEngineRules(t *testing.T) {
	m := &GameMatrix{
		Rows:    []string{"a", "b"},
		Cols:    []string{"x", "y"},
		Payoffs: [][][2]int{{{0, 3}, {2, 0}}, {{0, 0}, {1, 5}}},
	}
	if got := duelEngineCol(m, nil, "learner"); got != 0 {
		t.Errorf("learner first column = %d, want 0", got)
	}
	if got := duelEngineCol(m, []int{0, 0, 1}, "learner"); got != 0 {
		t.Errorf("learner after mostly a = %d, want 0", got)
	}
	if got := duelEngineCol(m, []int{1, 1, 0}, "learner"); got != 1 {
		t.Errorf("learner after mostly b = %d, want 1", got)
	}
	if got := duelBestRow(m, 1); got != 0 {
		t.Errorf("best row against y = %d, want 0", got)
	}
	if got := duelEngineCol(m, nil, "reactive"); got != 0 {
		t.Errorf("reactive first column = %d, want 0", got)
	}
	if got := duelEngineCol(m, []int{0, 1}, "reactive"); got != 1 {
		t.Errorf("reactive after b = %d, want 1", got)
	}
}

func TestEveryDuelEngineNamesAGameWithAPayoffTable(t *testing.T) {
	catalog, err := LoadGames()
	if err != nil {
		t.Fatal(err)
	}
	engines, err := loadEngineGames()
	if err != nil {
		t.Fatal(err)
	}
	byID := map[string]Game{}
	for _, g := range catalog {
		byID[g.ID] = g
	}
	duels := 0
	for _, e := range engines {
		if e.Kind != "duel" {
			continue
		}
		duels++
		g, ok := byID[e.Game]
		if !ok || g.Matrix == nil {
			t.Errorf("%s names %s, which has no payoff table", e.ID, e.Game)
		}
		if e.Policy != "learner" && e.Policy != "reactive" && e.Policy != "exploiter" && e.Policy != "mirror" {
			t.Errorf("%s has policy %q", e.ID, e.Policy)
		}
	}
	if duels < 40 {
		t.Errorf("got %d duel engines, want at least 40", duels)
	}
}

func TestDuelExploiterPredictsTheRowAfterYourLast(t *testing.T) {
	m := &GameMatrix{
		Rows:    []string{"a", "b"},
		Cols:    []string{"x", "y"},
		Payoffs: [][][2]int{{{0, 3}, {2, 0}}, {{0, 0}, {1, 5}}},
	}
	if got := duelPredictedRow(m, nil); got != 0 {
		t.Errorf("first predicted row = %d, want 0", got)
	}
	played := []int{0, 1, 0, 1, 0}
	if got := duelPredictedRow(m, played); got != 1 {
		t.Errorf("predicted row = %d, want 1", got)
	}
	if got := duelEngineCol(m, played, "exploiter"); got != 1 {
		t.Errorf("exploiter column = %d, want 1", got)
	}
}

func TestDuelMirrorAnswersTheSameNumber(t *testing.T) {
	m := &GameMatrix{
		Rows:    []string{"cooperate", "defect"},
		Cols:    []string{"cooperate", "defect"},
		Payoffs: [][][2]int{{{3, 3}, {0, 5}}, {{5, 0}, {1, 1}}},
	}
	if got := duelEngineCol(m, nil, "mirror"); got != 0 {
		t.Errorf("first column = %d, want 0", got)
	}
	if got := duelEngineCol(m, []int{0, 1}, "mirror"); got != 1 {
		t.Errorf("after defect = %d, want 1", got)
	}
}

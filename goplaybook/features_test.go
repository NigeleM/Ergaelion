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

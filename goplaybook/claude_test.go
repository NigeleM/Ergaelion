package main

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestClaudeOffUntilSwitchedOn(t *testing.T) {
	home := t.TempDir()
	if claudeIsOn(home) {
		t.Fatal("Claude should be off by default")
	}
	if err := claudeCheckReady(home); err == nil || !strings.Contains(err.Error(), "Claude is off") {
		t.Fatalf("expected the off message, got %v", err)
	}
	if err := claudeSetOn(true, home); err != nil {
		t.Fatal(err)
	}
	if !claudeIsOn(home) {
		t.Fatal("Claude should be on after /claude on")
	}
	if err := claudeSetOn(false, home); err != nil {
		t.Fatal(err)
	}
	if claudeIsOn(home) {
		t.Fatal("Claude should be off after /claude off")
	}
}

func TestClaudeNeedsKey(t *testing.T) {
	home := t.TempDir()
	if err := claudeSetOn(true, home); err != nil {
		t.Fatal(err)
	}
	t.Setenv("ANTHROPIC_API_KEY", "")
	if err := claudeCheckReady(home); err == nil || !strings.Contains(err.Error(), "ANTHROPIC_API_KEY") {
		t.Fatalf("expected the key message, got %v", err)
	}
}

func TestClaudeGameTextHasPayoffsAndPlaybook(t *testing.T) {
	games, err := LoadGames()
	if err != nil {
		t.Fatal(err)
	}
	game, err := FindGame(games, "prisoners-dilemma")
	if err != nil {
		t.Fatal(err)
	}
	text := claudeGamePart(game)
	for _, want := range []string{"Cooperate: (3, 3)  (0, 5)", "Playbook:", "Pitfalls:"} {
		if !strings.Contains(text, want) {
			t.Errorf("game text is missing %q", want)
		}
	}
}

func TestClaudeSimulationTextLinksOptionsToNodes(t *testing.T) {
	sims, err := LoadSimulations()
	if err != nil {
		t.Fatal(err)
	}
	sim, err := FindSimulation(sims, "salary-negotiation")
	if err != nil {
		t.Fatal(err)
	}
	text := claudeSimulationPart(sim)
	for _, want := range []string{"[n0] Decision: You have an offer. What salary do you ask for? Ask 50k -> n1", "[n6] End: failure"} {
		if !strings.Contains(text, want) {
			t.Errorf("simulation text is missing %q", want)
		}
	}
}

func TestClaudeAskSendsOnlyPartsAndQuestion(t *testing.T) {
	home := t.TempDir()
	if err := claudeSetOn(true, home); err != nil {
		t.Fatal(err)
	}
	t.Setenv("ANTHROPIC_API_KEY", "test-key")
	var gotKey, gotVersion, gotBody string
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotKey = r.Header.Get("x-api-key")
		gotVersion = r.Header.Get("anthropic-version")
		buf := new(strings.Builder)
		var chunk [4096]byte
		for {
			n, err := r.Body.Read(chunk[:])
			buf.Write(chunk[:n])
			if err != nil {
				break
			}
		}
		gotBody = buf.String()
		w.Write([]byte(`{"content":[{"type":"text","text":"Because it pays."}]}`))
	}))
	defer server.Close()
	saved := claudeAPIURL
	claudeAPIURL = server.URL
	defer func() { claudeAPIURL = saved }()

	answer, sent, err := claudeAsk("why defect", []claudePart{{"Game", "Prisoner's Dilemma text"}}, home)
	if err != nil {
		t.Fatal(err)
	}
	if answer != "Because it pays." {
		t.Fatalf("answer = %q", answer)
	}
	if gotKey != "test-key" || gotVersion != claudeAPIVersion {
		t.Fatalf("headers: key %q, version %q", gotKey, gotVersion)
	}
	if !strings.Contains(gotBody, `## Game\nPrisoner's Dilemma text`) {
		t.Errorf("request does not contain the game part: %s", gotBody)
	}
	if sent != len([]rune(claudeBuildPrompt("why defect", []claudePart{{"Game", "Prisoner's Dilemma text"}}))) {
		t.Errorf("sent count %d does not match the prompt", sent)
	}
}

func TestClaudeHTTPErrorIsPlain(t *testing.T) {
	home := t.TempDir()
	if err := claudeSetOn(true, home); err != nil {
		t.Fatal(err)
	}
	t.Setenv("ANTHROPIC_API_KEY", "test-key")
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.Error(w, "denied", http.StatusUnauthorized)
	}))
	defer server.Close()
	saved := claudeAPIURL
	claudeAPIURL = server.URL
	defer func() { claudeAPIURL = saved }()

	_, _, err := claudeAsk("hi", nil, home)
	if err == nil || !strings.Contains(err.Error(), "error (401)") {
		t.Fatalf("expected a 401 message, got %v", err)
	}
}

func TestClaudeClipsLongText(t *testing.T) {
	long := strings.Repeat("x", claudeMaxQuestion+500)
	if n := len([]rune(claudeBuildPrompt(long, nil))); n > claudeMaxQuestion+40 {
		t.Errorf("prompt is %d characters, expected at most %d", n, claudeMaxQuestion+40)
	}
}

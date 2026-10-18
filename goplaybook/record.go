package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"
)

// Win and loss records. Each outcome is one JSON line in <home>/outcomes.jsonl,
// so earlier entries are never overwritten.

var RecordResults = []string{"win", "loss", "draw", "mixed"}

type Outcome struct {
	Game   string `json:"game"`
	Result string `json:"result"`
	Note   string `json:"note"`
	Date   string `json:"date"`
	Play   int    `json:"play,omitempty"`
}

func outcomesPath() string {
	return filepath.Join(PlaybookHome(), "outcomes.jsonl")
}

// LogOutcome appends one result for a game.
func LogOutcome(gameID, result, note string, play int) (Outcome, error) {
	if !contains(RecordResults, result) {
		return Outcome{}, fmt.Errorf("result must be one of win, loss, draw, mixed")
	}
	entry := Outcome{Game: gameID, Result: result, Note: note, Date: time.Now().Format("2006-01-02"), Play: play}
	if err := os.MkdirAll(PlaybookHome(), 0o755); err != nil {
		return entry, err
	}
	file, err := os.OpenFile(outcomesPath(), os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o644)
	if err != nil {
		return entry, err
	}
	defer file.Close()
	data, err := json.Marshal(entry)
	if err != nil {
		return entry, err
	}
	_, err = file.Write(append(data, '\n'))
	return entry, err
}

// History returns logged outcomes, oldest first, optionally for one game.
func History(gameID string) ([]Outcome, error) {
	file, err := os.Open(outcomesPath())
	if os.IsNotExist(err) {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}
	defer file.Close()
	var out []Outcome
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		if scanner.Text() == "" {
			continue
		}
		var entry Outcome
		if err := json.Unmarshal(scanner.Bytes(), &entry); err != nil {
			return nil, err
		}
		if gameID == "" || entry.Game == gameID {
			out = append(out, entry)
		}
	}
	return out, scanner.Err()
}

// Tally counts results per game id.
func Tally() (map[string]map[string]int, error) {
	entries, err := History("")
	if err != nil {
		return nil, err
	}
	counts := map[string]map[string]int{}
	for _, e := range entries {
		if counts[e.Game] == nil {
			counts[e.Game] = map[string]int{}
		}
		counts[e.Game][e.Result]++
	}
	return counts, nil
}

// FormatRecord renders a tally as 'NW NL ND NM'.
func FormatRecord(c map[string]int) string {
	return fmt.Sprintf("%dW %dL %dD %dM", c["win"], c["loss"], c["draw"], c["mixed"])
}

// recordLine returns the record for a game, or "" if none is logged.
func recordLine(gameID string) string {
	counts, err := Tally()
	if err != nil || counts[gameID] == nil {
		return ""
	}
	total := 0
	for _, n := range counts[gameID] {
		total += n
	}
	if total == 0 {
		return ""
	}
	return FormatRecord(counts[gameID])
}

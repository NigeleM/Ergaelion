package main

import (
	"embed"
	"encoding/json"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

// Every data file is embedded, so the binary runs without any data files on disk.
// data/ is kept in sync with gtplaybook/data/ by 'make sync'.
//
//go:embed data/*.json
var dataFS embed.FS

// nonGameFiles are data files that are not lists of games.
var nonGameFiles = map[string]bool{"areas.json": true, "topics.json": true, "simulations.json": true, "problems.json": true, "setup-help.json": true, "guide.json": true, "keywords.json": true, "tools.json": true, "combinations.json": true, "engine-games.json": true}

// Traits lists every trait a scenario or game can declare, in display order.
var Traits = []string{"players", "timing", "interaction", "information", "payoff", "communication", "enforcement", "commitment", "bargaining"}

var traitValues = map[string][]string{
	"players":       {"two", "many"},
	"timing":        {"simultaneous", "sequential"},
	"interaction":   {"one-shot", "repeated"},
	"information":   {"perfect", "imperfect"},
	"payoff":        {"zero-sum", "mixed", "common-interest"},
	"communication": {"yes", "no"},
	"enforcement":   {"yes", "no"},
	"commitment":    {"yes", "no"},
	"bargaining":    {"yes", "no"},
}

// TraitOptions returns the allowed values for a trait, or nil if the trait is unknown.
func TraitOptions(key string) []string {
	return traitValues[key]
}

type GameMatrix struct {
	Rows    []string   `json:"rows"`
	Cols    []string   `json:"cols"`
	Payoffs [][][2]int `json:"payoffs"`
}

type Game struct {
	ID                string            `json:"id"`
	Name              string            `json:"name"`
	Category          string            `json:"category"`
	Summary           string            `json:"summary"`
	HowItWorks        string            `json:"how_it_works"`
	Traits            map[string]string `json:"traits"`
	Domains           []string          `json:"domains"`
	Examples          []string          `json:"examples"`
	Matrix            *GameMatrix       `json:"matrix"`
	MatrixNote        string            `json:"matrix_note"`
	MatrixUnavailable string            `json:"matrix_unavailable"`
	Strategies        []string          `json:"strategies"`
	Pitfalls          []string          `json:"pitfalls"`
	Sources           []string          `json:"sources"`
}

// PlaybookHome is $PLAYBOOK_HOME if set, otherwise ~/.playbook. Overlays live here.
func PlaybookHome() string {
	if configured := os.Getenv("PLAYBOOK_HOME"); configured != "" {
		return configured
	}
	home, err := os.UserHomeDir()
	if err != nil {
		return ".playbook"
	}
	return filepath.Join(home, ".playbook")
}

// LoadGames merges the embedded catalogue with any whole-game files in <home>/games.
// An overlay with a matching id replaces the built-in game; a new id adds a game.
func LoadGames() ([]Game, error) {
	var games []Game
	entries, err := fs.ReadDir(dataFS, "data")
	if err != nil {
		return nil, err
	}
	for _, entry := range entries {
		if nonGameFiles[entry.Name()] {
			continue
		}
		data, err := dataFS.ReadFile("data/" + entry.Name())
		if err != nil {
			return nil, err
		}
		var batch []Game
		if err := json.Unmarshal(data, &batch); err != nil {
			return nil, fmt.Errorf("parsing %s: %w", entry.Name(), err)
		}
		games = append(games, batch...)
	}

	overlays, err := readOverlayGames()
	if err != nil {
		return nil, err
	}
	index := map[string]int{}
	for i, g := range games {
		index[g.ID] = i
	}
	for _, o := range overlays {
		if i, ok := index[o.ID]; ok {
			games[i] = o
		} else {
			index[o.ID] = len(games)
			games = append(games, o)
		}
	}

	hidden := DisabledIDs()
	visible := games[:0]
	for _, g := range games {
		if !hidden[g.ID] {
			visible = append(visible, g)
		}
	}
	games = visible
	if err := validateGames(games); err != nil {
		return nil, err
	}
	return games, nil
}

func readOverlayGames() ([]Game, error) {
	dir := filepath.Join(PlaybookHome(), "games")
	files, err := filepath.Glob(filepath.Join(dir, "*.json"))
	if err != nil {
		return nil, err
	}
	var out []Game
	for _, file := range files {
		data, err := os.ReadFile(file)
		if err != nil {
			return nil, err
		}
		var g Game
		if err := json.Unmarshal(data, &g); err != nil {
			return nil, fmt.Errorf("parsing %s: %w", file, err)
		}
		out = append(out, g)
	}
	return out, nil
}

func validateGames(games []Game) error {
	seen := map[string]bool{}
	for _, g := range games {
		if g.ID == "" || g.Name == "" || len(g.Strategies) == 0 {
			return fmt.Errorf("%q: missing required fields", g.ID)
		}
		if seen[g.ID] {
			return fmt.Errorf("duplicate game id: %s", g.ID)
		}
		seen[g.ID] = true
		for key, value := range g.Traits {
			if !contains(traitValues[key], value) {
				return fmt.Errorf("%s: invalid trait %s=%s", g.ID, key, value)
			}
		}
		if m := g.Matrix; m != nil {
			if len(m.Payoffs) != len(m.Rows) {
				return fmt.Errorf("%s: payoff matrix row count does not match action names", g.ID)
			}
			for _, row := range m.Payoffs {
				if len(row) != len(m.Cols) {
					return fmt.Errorf("%s: payoff matrix column count does not match action names", g.ID)
				}
			}
		}
	}
	return nil
}

// SaveOverlay writes a whole game into <home>/games so it can be edited by hand.
func SaveOverlay(g Game) (string, error) {
	dir := filepath.Join(PlaybookHome(), "games")
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return "", err
	}
	data, err := json.MarshalIndent(g, "", "  ")
	if err != nil {
		return "", err
	}
	if !safeIDPattern.MatchString(g.ID) {
		return "", fmt.Errorf("'%s' cannot be used as a file name. Use letters, numbers, dashes and underscores.", g.ID)
	}
	path := filepath.Join(dir, g.ID+".json")
	return path, os.WriteFile(path, append(data, '\n'), 0o644)
}

// FindGame matches by exact id or name, then by unique substring.
func FindGame(games []Game, query string) (*Game, error) {
	needle := strings.ToLower(strings.TrimSpace(query))
	for i := range games {
		if games[i].ID == needle || strings.ToLower(games[i].Name) == needle {
			return &games[i], nil
		}
	}
	var partial []*Game
	for i := range games {
		if strings.Contains(games[i].ID, needle) || strings.Contains(strings.ToLower(games[i].Name), needle) {
			partial = append(partial, &games[i])
		}
	}
	switch len(partial) {
	case 0:
		return nil, fmt.Errorf("no game matches '%s'", query)
	case 1:
		return partial[0], nil
	}
	ids := make([]string, len(partial))
	for i, g := range partial {
		ids[i] = g.ID
	}
	return nil, fmt.Errorf("'%s' is ambiguous: %s", query, strings.Join(ids, ", "))
}

// Family is a top-level area of study, such as 'War and security games'.
type Family struct {
	Family     string      `json:"family"`
	Summary    string      `json:"summary"`
	Learn      []string    `json:"learn"`
	Subdomains []Subdomain `json:"subdomains"`
}

type Subdomain struct {
	Name  string   `json:"name"`
	Games []string `json:"games"`
}

// LoadAreas reads the family map from <home>/areas.json if present, else the embedded copy.
func LoadAreas() ([]Family, error) {
	var data []byte
	overlay := filepath.Join(PlaybookHome(), "areas.json")
	if raw, err := os.ReadFile(overlay); err == nil {
		data = raw
	} else {
		raw, err := dataFS.ReadFile("data/areas.json")
		if err != nil {
			return nil, err
		}
		data = raw
	}
	var families []Family
	if err := json.Unmarshal(data, &families); err != nil {
		return nil, fmt.Errorf("parsing areas.json: %w", err)
	}
	return families, nil
}

func contains(list []string, value string) bool {
	for _, item := range list {
		if item == value {
			return true
		}
	}
	return false
}

// safeIDPattern is the only form a game id may take when it becomes a file name.
var safeIDPattern = regexp.MustCompile(`^[A-Za-z0-9][A-Za-z0-9_-]{0,99}$`)

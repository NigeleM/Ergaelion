package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

// Management: hide and show games, check overlay files, undo a logged result, export results as CSV.

// DisabledIDs returns the game ids you have hidden.
func DisabledIDs() map[string]bool {
	out := map[string]bool{}
	file, err := os.Open(filepath.Join(PlaybookHome(), "disabled.txt"))
	if err != nil {
		return out
	}
	defer file.Close()
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		if id := strings.TrimSpace(scanner.Text()); id != "" {
			out[id] = true
		}
	}
	return out
}

// SetDisabled hides or shows one game id in <home>/disabled.txt.
func SetDisabled(gameID string, disabled bool) error {
	if err := os.MkdirAll(PlaybookHome(), 0o755); err != nil {
		return err
	}
	current := DisabledIDs()
	delete(current, gameID)
	if disabled {
		current[gameID] = true
	}
	ids := make([]string, 0, len(current))
	for id := range current {
		ids = append(ids, id)
	}
	sort.Strings(ids)
	content := ""
	for _, id := range ids {
		content += id + "\n"
	}
	return os.WriteFile(filepath.Join(PlaybookHome(), "disabled.txt"), []byte(content), 0o644)
}

// AllBuiltinGames returns every built-in game, including hidden ones.
func AllBuiltinGames() ([]Game, error) {
	var games []Game
	entries, err := dataFS.ReadDir("data")
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
			return nil, err
		}
		games = append(games, batch...)
	}
	return games, nil
}

// CheckOverlays returns problems in your overlay files; an empty list means they are valid.
func CheckOverlays() []string {
	var problems []string
	files, _ := filepath.Glob(filepath.Join(PlaybookHome(), "games", "*.json"))
	sort.Strings(files)
	var parsed []Game
	for _, file := range files {
		data, err := os.ReadFile(file)
		if err != nil {
			problems = append(problems, fmt.Sprintf("%s: %v", filepath.Base(file), err))
			continue
		}
		var g Game
		if err := json.Unmarshal(data, &g); err != nil {
			problems = append(problems, fmt.Sprintf("%s: %v", filepath.Base(file), err))
			continue
		}
		parsed = append(parsed, g)
	}
	if err := validateGames(parsed); err != nil {
		problems = append(problems, err.Error())
	}
	return problems
}

// RemoveLast deletes the most recent logged result, for one game if gameID is set.
func RemoveLast(gameID string) (*Outcome, error) {
	entries, err := History("")
	if err != nil {
		return nil, err
	}
	for i := len(entries) - 1; i >= 0; i-- {
		if gameID == "" || entries[i].Game == gameID {
			removed := entries[i]
			entries = append(entries[:i], entries[i+1:]...)
			var b strings.Builder
			for _, e := range entries {
				line, _ := json.Marshal(e)
				b.Write(line)
				b.WriteString("\n")
			}
			return &removed, os.WriteFile(outcomesPath(), []byte(b.String()), 0o644)
		}
	}
	return nil, nil
}

// ResultsCSV renders every logged result as CSV.
func ResultsCSV() (string, error) {
	entries, err := History("")
	if err != nil {
		return "", err
	}
	var b strings.Builder
	b.WriteString("date,game,result,play,note\n")
	for _, e := range entries {
		play := ""
		if e.Play != 0 {
			play = fmt.Sprint(e.Play)
		}
		fmt.Fprintf(&b, "%s,%s,%s,%s,\"%s\"\n", e.Date, e.Game, e.Result, play, strings.ReplaceAll(e.Note, "\"", "\"\""))
	}
	return b.String(), nil
}

func cmdDisable(args []string, games []Game) error {
	all, err := AllBuiltinGames()
	if err != nil {
		return err
	}
	game, err := FindGame(all, strings.Join(positionalArgs(args), " "))
	if err != nil {
		return err
	}
	if err := SetDisabled(game.ID, true); err != nil {
		return err
	}
	fmt.Println(green(fmt.Sprintf("Hid '%s'. Run 'enable %s' to show it again.", game.Name, game.ID)))
	return nil
}

func cmdEnable(args []string, games []Game) error {
	all, err := AllBuiltinGames()
	if err != nil {
		return err
	}
	game, err := FindGame(all, strings.Join(positionalArgs(args), " "))
	if err != nil {
		return err
	}
	if err := SetDisabled(game.ID, false); err != nil {
		return err
	}
	fmt.Println(green(fmt.Sprintf("Showing '%s' again.", game.Name)))
	return nil
}

func cmdCheck(args []string, games []Game) error {
	problems := CheckOverlays()
	if len(problems) > 0 {
		for _, p := range problems {
			fmt.Println(red("✗ " + p))
		}
		return fmt.Errorf("%d problem(s) found in your overlay files", len(problems))
	}
	fmt.Println(green("Your overlay files are valid."))
	return nil
}

func cmdUnlog(args []string, games []Game) error {
	gameID := ""
	if pos := positionalArgs(args); len(pos) > 0 {
		game, err := FindGame(games, strings.Join(pos, " "))
		if err != nil {
			return err
		}
		gameID = game.ID
	}
	removed, err := RemoveLast(gameID)
	if err != nil {
		return err
	}
	if removed == nil {
		fmt.Println(dim("Nothing to remove."))
		return fmt.Errorf("nothing to remove")
	}
	fmt.Println(green(fmt.Sprintf("Removed the last %s for %s (%s).", removed.Result, removed.Game, removed.Date)))
	return nil
}

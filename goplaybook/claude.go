package main

// Optional Claude help inside the playbook. Mirrors gtplaybook/claude.py.
//
// Nothing here runs unless you switch it on with /claude on, and an API key is set in
// ANTHROPIC_API_KEY. When it runs, it sends only what you asked about: your question,
// and the text of the game, simulation or situation you are looking at.

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// claudeAPIURL is a variable so that tests can point it at a local server.
var claudeAPIURL = "https://api.anthropic.com/v1/messages"

const (
	claudeAPIVersion   = "2023-06-01"
	claudeDefaultModel = "claude-sonnet-5-5"
	claudeMaxTokens    = 1024
	claudeMaxPart      = 6000
	claudeMaxQuestion  = 2000
	claudeTimeout      = 60 * time.Second
	claudeSystem       = "You help a person understand game theory with a playbook app. Use only the game, " +
		"simulation or situation text given to you. Say plainly when that text does not " +
		"answer the question. Explain the reasoning and the trade-offs. Do not give tactics " +
		"for coercing, deceiving or harming specific people, and do not help with anything " +
		"illegal. Keep the answer under 300 words."
)

type claudeMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type claudeRequest struct {
	Model     string          `json:"model"`
	MaxTokens int             `json:"max_tokens"`
	System    string          `json:"system"`
	Messages  []claudeMessage `json:"messages"`
}

// claudePart is one labelled block of context sent with a question.
type claudePart struct {
	Heading string
	Text    string
}

func claudeConfigPath(home string) string {
	if home == "" {
		home = PlaybookHome()
	}
	return filepath.Join(home, "claude.json")
}

// claudeIsOn reports whether the person has switched Claude on. A missing or unreadable file means off.
func claudeIsOn(home string) bool {
	data, err := os.ReadFile(claudeConfigPath(home))
	if err != nil {
		return false
	}
	var saved struct {
		Consent bool `json:"consent"`
	}
	if json.Unmarshal(data, &saved) != nil {
		return false
	}
	return saved.Consent
}

func claudeSetOn(value bool, home string) error {
	path := claudeConfigPath(home)
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}
	text := "{\"consent\": false}\n"
	if value {
		text = "{\"consent\": true}\n"
	}
	return os.WriteFile(path, []byte(text), 0o644)
}

func claudeModel() string {
	if configured := os.Getenv("GTP_CLAUDE_MODEL"); configured != "" {
		return configured
	}
	return claudeDefaultModel
}

func claudeAPIKey() string {
	return os.Getenv("ANTHROPIC_API_KEY")
}

// clip trims text and shortens it to limit characters, adding an ellipsis when it cuts.
func clip(text string, limit int) string {
	text = strings.TrimSpace(text)
	runes := []rune(text)
	if len(runes) <= limit {
		return text
	}
	return strings.TrimRight(string(runes[:limit]), " \t\r\n") + " …"
}

// claudeGamePart is the text of one game, as Claude sees it.
func claudeGamePart(game *Game) string {
	lines := []string{game.Name, game.Summary}
	if game.HowItWorks != "" {
		lines = append(lines, "How it works: "+game.HowItWorks)
	}
	if game.Matrix != nil && len(game.Matrix.Payoffs) > 0 {
		lines = append(lines, "Payoffs (row player, column player):")
		for i, row := range game.Matrix.Payoffs {
			cells := make([]string, 0, len(row))
			for _, cellValue := range row {
				cells = append(cells, fmt.Sprintf("(%d, %d)", cellValue[0], cellValue[1]))
			}
			label := ""
			if i < len(game.Matrix.Rows) {
				label = game.Matrix.Rows[i]
			}
			lines = append(lines, "  "+label+": "+strings.Join(cells, "  "))
		}
	}
	for _, section := range []struct {
		items []string
		title string
	}{{game.Strategies, "Playbook"}, {game.Pitfalls, "Pitfalls"}} {
		if len(section.items) > 0 {
			lines = append(lines, section.title+":")
			for _, item := range section.items {
				lines = append(lines, "  - "+item)
			}
		}
	}
	return clip(strings.Join(lines, "\n"), claudeMaxPart)
}

// claudeSimulationPart lists each decision, option and ending in the order a person would reach them.
func claudeSimulationPart(sim *Simulation) string {
	lines := []string{sim.Name, sim.Summary, "Decisions and outcomes:"}
	seen := map[string]bool{}
	queue := []string{sim.Start}
	for len(queue) > 0 {
		id := queue[0]
		queue = queue[1:]
		node, ok := sim.Nodes[id]
		if seen[id] || !ok {
			continue
		}
		seen[id] = true
		switch node.Type {
		case "end":
			lines = append(lines, fmt.Sprintf("[%s] End: %s", id, node.Outcome))
		case "nature":
			branches := make([]string, 0, len(node.Branches))
			for _, b := range node.Branches {
				branches = append(branches, fmt.Sprintf("%.0f%% %s -> %s", b.P*100, b.Label, b.Next))
				queue = append(queue, b.Next)
			}
			lines = append(lines, fmt.Sprintf("[%s] Chance: %s %s", id, node.Prompt, strings.Join(branches, "; ")))
		default:
			options := make([]string, 0, len(node.Options))
			for _, o := range node.Options {
				options = append(options, o.Label+" -> "+o.Next)
				queue = append(queue, o.Next)
			}
			lines = append(lines, fmt.Sprintf("[%s] Decision: %s %s", id, node.Prompt, strings.Join(options, "; ")))
		}
	}
	return clip(strings.Join(lines, "\n"), claudeMaxPart)
}

// claudeScenarioPart is the situation the person described, with the top matching games.
func claudeScenarioPart(text, gamesText string) string {
	body := "Situation: " + strings.TrimSpace(text)
	if gamesText != "" {
		body += "\n\n" + gamesText
	}
	return clip(body, claudeMaxPart)
}

// claudeBuildPrompt is the user message: each non-empty part under its heading, then the question.
func claudeBuildPrompt(question string, parts []claudePart) string {
	var sections []string
	for _, part := range parts {
		if part.Text != "" {
			sections = append(sections, "## "+part.Heading+"\n"+part.Text)
		}
	}
	sections = append(sections, "## Question\n"+clip(question, claudeMaxQuestion))
	return strings.Join(sections, "\n\n")
}

func claudeCheckReady(home string) error {
	if !claudeIsOn(home) {
		return errors.New("Claude is off. Type /claude on to allow questions to be sent to Anthropic.")
	}
	if claudeAPIKey() == "" {
		return errors.New("Set ANTHROPIC_API_KEY to use Claude. The rest of the playbook works without it.")
	}
	return nil
}

// claudeAsk checks consent and the key, then sends the question. It returns the answer and the number of characters sent.
func claudeAsk(question string, parts []claudePart, home string) (string, int, error) {
	if err := claudeCheckReady(home); err != nil {
		return "", 0, err
	}
	prompt := claudeBuildPrompt(question, parts)
	body, err := json.Marshal(claudeRequest{
		Model:     claudeModel(),
		MaxTokens: claudeMaxTokens,
		System:    claudeSystem,
		Messages:  []claudeMessage{{Role: "user", Content: prompt}},
	})
	if err != nil {
		return "", 0, err
	}
	request, err := http.NewRequest(http.MethodPost, claudeAPIURL, bytes.NewReader(body))
	if err != nil {
		return "", 0, err
	}
	request.Header.Set("content-type", "application/json")
	request.Header.Set("x-api-key", claudeAPIKey())
	request.Header.Set("anthropic-version", claudeAPIVersion)
	client := &http.Client{Timeout: claudeTimeout}
	reply, err := client.Do(request)
	if err != nil {
		return "", 0, fmt.Errorf("could not reach Anthropic: %v", err)
	}
	defer reply.Body.Close()
	if reply.StatusCode >= 400 {
		return "", 0, fmt.Errorf("Claude returned an error (%d). Check the key and the model name.", reply.StatusCode)
	}
	data, err := io.ReadAll(reply.Body)
	if err != nil {
		return "", 0, err
	}
	var answer struct {
		Content []struct {
			Type string `json:"type"`
			Text string `json:"text"`
		} `json:"content"`
	}
	if err := json.Unmarshal(data, &answer); err != nil {
		return "", 0, err
	}
	var text strings.Builder
	for _, block := range answer.Content {
		if block.Type == "text" {
			text.WriteString(block.Text)
		}
	}
	if text.Len() == 0 {
		return "", 0, errors.New("Claude sent no text back")
	}
	return strings.TrimSpace(text.String()), len([]rune(prompt)), nil
}

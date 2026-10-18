package main

import (
	"encoding/json"
	"fmt"
	"strconv"
	"strings"
)

// The guide: 48 principles of strategy and influence, manipulation tactics and how to resist them,
// research steps and life habits. The data is shared with the Python version (data/guide.json).

type GuidePrinciple struct {
	ID        int      `json:"id"`
	Title     string   `json:"title"`
	Area      string   `json:"area"`
	Principle string   `json:"principle"`
	Games     []string `json:"games"`
	Defence   string   `json:"defence"`
}

type GuideTactic struct {
	Pattern string   `json:"pattern"`
	Signs   string   `json:"signs"`
	Defence string   `json:"defence"`
	Games   []string `json:"games"`
}

type GuideStep struct {
	Step   string `json:"step"`
	Detail string `json:"detail"`
}

type GuideLife struct {
	Title  string `json:"title"`
	Detail string `json:"detail"`
}

type Guide struct {
	Note       string            `json:"note"`
	Power      []GuidePrinciple  `json:"power"`
	Defend     []GuideTactic     `json:"defend"`
	Research   []GuideStep       `json:"research"`
	References []string          `json:"research_starting_points"`
	Life       []GuideLife       `json:"life"`
	Labels     map[string]string `json:"labels"`
}

func LoadGuide() (Guide, error) {
	var g Guide
	data, err := dataFS.ReadFile("data/guide.json")
	if err != nil {
		return g, err
	}
	if err := json.Unmarshal(data, &g); err != nil {
		return g, fmt.Errorf("parsing guide.json: %w", err)
	}
	return g, nil
}

func cmdGuide(args []string, games []Game) error {
	g, err := LoadGuide()
	if err != nil {
		return err
	}
	labels := withLabels(englishGuideLabels, g.Labels)
	byID := map[string]Game{}
	for _, game := range games {
		byID[game.ID] = game
	}
	if len(args) == 0 {
		fmt.Println("\n" + bold(labels["sections"]))
		fmt.Println(bullet(fillLabel(labels["power_line"], "n", fmt.Sprint(len(g.Power))), "•"))
		fmt.Println(bullet(fillLabel(labels["defend_line"], "n", fmt.Sprint(len(g.Defend))), "•"))
		fmt.Println(bullet(fillLabel(labels["research_line"], "n", fmt.Sprint(len(g.Research))), "•"))
		fmt.Println(bullet(fillLabel(labels["life_line"], "n", fmt.Sprint(len(g.Life))), "•"))
		fmt.Println(dim(g.Note))
		fmt.Println(dim("\n" + labels["run_hint"]))
		return nil
	}

	section := strings.ToLower(args[0])
	query := strings.ToLower(strings.Join(args[1:], " "))
	switch section {
	case "power":
		if query != "" {
			var matched []GuidePrinciple
			for _, p := range g.Power {
				if query == strconv.Itoa(p.ID) || strings.Contains(strings.ToLower(p.Title), query) {
					matched = append(matched, p)
				}
			}
			if len(matched) == 0 {
				return fmt.Errorf("%s", fillLabel(labels["no_match_principle"], "query", query))
			}
			for _, p := range matched {
				fmt.Println("\n" + heading(fmt.Sprintf("%d. %s", p.ID, p.Title)) + "  " + dim(p.Area))
				fmt.Println(paragraph(p.Principle))
				fmt.Println(bullet(labels["defence"]+": "+p.Defence, "→"))
				for _, id := range p.Games {
					if game, ok := byID[id]; ok {
						fmt.Println(bullet(fmt.Sprintf("%s: %s  %s", labels["tested_in"], game.Name, dim("sim "+id)), "·"))
					}
				}
			}
			return nil
		}
		current := ""
		for _, p := range g.Power {
			if p.Area != current {
				current = p.Area
				fmt.Println("\n" + heading(current))
			}
			fmt.Println(bullet(fmt.Sprintf("%d. %s", p.ID, p.Title), "•"))
		}
		return nil
	case "defend":
		if query != "" {
			found := false
			for _, d := range g.Defend {
				if strings.Contains(strings.ToLower(d.Pattern), query) {
					found = true
					fmt.Println("\n" + heading(d.Pattern))
					fmt.Println(bullet(labels["signs"]+": "+d.Signs, "•"))
					fmt.Println(bullet(labels["defence"]+": "+d.Defence, "→"))
				}
			}
			if !found {
				return fmt.Errorf("%s", fillLabel(labels["no_match_tactic"], "query", query))
			}
			return nil
		}
		for _, d := range g.Defend {
			fmt.Println(bullet(d.Pattern, "•"))
		}
		return nil
	case "research":
		fmt.Println("\n" + heading(t("research_steps")))
		for i, s := range g.Research {
			fmt.Println(bullet(s.Step+": "+s.Detail, fmt.Sprintf("%d.", i+1)))
		}
		fmt.Println("\n" + heading(t("starting_references")))
		for _, r := range g.References {
			fmt.Println(bullet(r, "•"))
		}
		return nil
	case "life":
		for i, item := range g.Life {
			fmt.Println(bullet(item.Title+": "+item.Detail, fmt.Sprintf("%d.", i+1)))
		}
		return nil
	}
	return fmt.Errorf("sections are power, defend, research and life")
}

package main

import (
	"encoding/json"
	"fmt"
	"sort"
	"strings"
)

// Topics group the games by what they are about, such as business or military. A game can be in
// several topics, because each game lists its domains.

// Topic is one entry of data/topics.json.
type Topic struct {
	ID      string `json:"id"`
	Name    string `json:"name"`
	Summary string `json:"summary"`
}

// LoadTopics reads the topics from the embedded data.
func LoadTopics() ([]Topic, error) {
	data, err := dataFS.ReadFile("data/topics.json")
	if err != nil {
		return nil, err
	}
	var topics []Topic
	if err := json.Unmarshal(data, &topics); err != nil {
		return nil, fmt.Errorf("parsing topics.json: %w", err)
	}
	return topics, nil
}

// topicGames returns the games in a topic, sorted by name.
func topicGames(games []Game, topicID string) []Game {
	var out []Game
	for _, g := range games {
		if contains(g.Domains, topicID) {
			out = append(out, g)
		}
	}
	sort.SliceStable(out, func(i, j int) bool { return out[i].Name < out[j].Name })
	return out
}

// gameLocations maps each game to its family and sub-domain, for showing where it sits in the families.
func gameLocations() (map[string]string, error) {
	families, err := LoadAreas()
	if err != nil {
		return nil, err
	}
	places := map[string]string{}
	for _, f := range families {
		for _, sd := range f.Subdomains {
			for _, id := range sd.Games {
				if _, seen := places[id]; !seen {
					places[id] = f.Family + ": " + sd.Name
				}
			}
		}
	}
	return places, nil
}

// cmdTopics lists the topics, or the games in one of them.
func cmdTopics(args []string, games []Game) error {
	topics, err := LoadTopics()
	if err != nil {
		return err
	}
	name := strings.ToLower(strings.Join(positionalArgs(args), " "))
	if name == "" {
		fmt.Println()
		for _, topic := range topics {
			fmt.Println(bold(topic.Name) + "  " + dim(fmt.Sprintf("%d games", len(topicGames(games, topic.ID)))))
			fmt.Println(dim(paragraph(topic.Summary)))
		}
		fmt.Println(dim("\nRun 'topics <topic>' for its games, e.g. 'topics military'."))
		return nil
	}

	var exact, partial []Topic
	for _, topic := range topics {
		if topic.ID == name || strings.ToLower(topic.Name) == name {
			exact = append(exact, topic)
		} else if strings.Contains(topic.ID, name) || strings.Contains(strings.ToLower(topic.Name), name) {
			partial = append(partial, topic)
		}
	}
	matches := exact
	if len(matches) == 0 {
		matches = partial
	}
	if len(matches) == 0 {
		return fmt.Errorf("no topic matches '%s'. Run 'topics' to list them", name)
	}
	if len(matches) > 1 {
		names := make([]string, len(matches))
		for i, topic := range matches {
			names[i] = topic.Name
		}
		return fmt.Errorf("'%s' is ambiguous: %s", name, strings.Join(names, ", "))
	}

	topic := matches[0]
	places, err := gameLocations()
	if err != nil {
		return err
	}
	fmt.Println("\n" + bold(topic.Name))
	fmt.Println(dim(paragraph(topic.Summary)))
	fmt.Println()
	for _, g := range topicGames(games, topic.ID) {
		where := places[g.ID]
		if where == "" {
			where = g.ID
		}
		fmt.Println(bullet(g.Name+"  "+dim(where), "•"))
	}
	fmt.Println(dim("\nRun 'show <game>' for any of them, or 'topics' for the other topics."))
	return nil
}

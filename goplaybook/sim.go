package main

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"strings"
)

// Simulations are decision trees stored in data/simulations.json. Each node is a
// player decision, a chance event, or an end state with an outcome. The engine
// finds the path to victory, the path most likely to fail, and every ending.

type SimOption struct {
	Label string `json:"label"`
	Next  string `json:"next"`
	Why   string `json:"why"`
}

type SimBranch struct {
	P     float64 `json:"p"`
	Label string  `json:"label"`
	Next  string  `json:"next"`
	Why   string  `json:"why"`
}

type SimNode struct {
	Type     string               `json:"type"`
	Prompt   string               `json:"prompt"`
	Outcome  string               `json:"outcome"`
	Text     string               `json:"text"`
	Options  []SimOption          `json:"options"`
	Branches []SimBranch          `json:"branches"`
	Replies  []SimOption          `json:"replies"`
	Policy   map[string][]float64 `json:"policy"`
	Default  []float64            `json:"default"`
}

type Simulation struct {
	ID       string             `json:"id"`
	Name     string             `json:"name"`
	Families []string           `json:"families"`
	Summary  string             `json:"summary"`
	Start    string             `json:"start"`
	Mode     string             `json:"mode"`
	Nodes    map[string]SimNode `json:"nodes"`
}

// modeOrBasic returns the simulation's mode, treating a missing mode as basic.
func (s Simulation) modeOrBasic() string {
	if s.Mode == "live" {
		return "live"
	}
	return "basic"
}

// Step is one move on a path: your choice, or a chance event, with its reason.
type Step struct {
	Kind   string  `json:"kind"`
	Prompt string  `json:"prompt"`
	Label  string  `json:"label"`
	P      float64 `json:"p"`
	Why    string  `json:"why"`
}

// Ending is one way a simulation can finish.
type Ending struct {
	Steps   []Step
	Prob    float64
	Outcome string
	Text    string
}

// PlayOption is one choice offered during play, with the chance of victory from there.
type PlayOption struct {
	Label  string
	Why    string
	Chance float64
}

type planEntry struct {
	value  float64
	choice int
}

// LoadSimulations reads the embedded simulation list.
func LoadSimulations() ([]Simulation, error) {
	data, err := dataFS.ReadFile("data/simulations.json")
	if err != nil {
		return nil, err
	}
	var sims []Simulation
	if err := json.Unmarshal(data, &sims); err != nil {
		return nil, fmt.Errorf("parsing simulations.json: %w", err)
	}
	for i := range sims {
		resolveOpponents(&sims[i])
	}
	return sims, nil
}

// resolveOpponents turns each opponent step into a chance step whose odds depend on the choice
// you just made. An opponent step lists its replies and a policy: for each of your choices, named
// by its label, the chance of each reply. A choice with no policy entry uses the default odds.
func resolveOpponents(sim *Simulation) {
	cameFrom := map[string]*string{}
	for _, node := range sim.Nodes {
		switch node.Type {
		case "player":
			for _, o := range node.Options {
				if _, ok := cameFrom[o.Next]; !ok {
					label := o.Label
					cameFrom[o.Next] = &label
				}
			}
		case "nature":
			for _, b := range node.Branches {
				if _, ok := cameFrom[b.Next]; !ok {
					cameFrom[b.Next] = nil
				}
			}
		}
	}
	for id, node := range sim.Nodes {
		if node.Type != "opponent" {
			continue
		}
		odds := node.Default
		if label := cameFrom[id]; label != nil {
			if o, ok := node.Policy[*label]; ok {
				odds = o
			}
		}
		var branches []SimBranch
		for i, r := range node.Replies {
			if i < len(odds) {
				branches = append(branches, SimBranch{P: odds[i], Label: r.Label, Next: r.Next, Why: r.Why})
			}
		}
		sim.Nodes[id] = SimNode{Type: "nature", Prompt: node.Prompt, Branches: branches}
	}
}

// FindSimulation matches by exact id or name, then by unique substring.
func FindSimulation(sims []Simulation, query string) (*Simulation, error) {
	needle := strings.ToLower(strings.TrimSpace(query))
	for i := range sims {
		if sims[i].ID == needle || strings.ToLower(sims[i].Name) == needle {
			return &sims[i], nil
		}
	}
	var partial []*Simulation
	for i := range sims {
		if strings.Contains(sims[i].ID, needle) || strings.Contains(strings.ToLower(sims[i].Name), needle) {
			partial = append(partial, &sims[i])
		}
	}
	if len(partial) == 1 {
		return partial[0], nil
	}
	if len(partial) == 0 {
		return nil, fmt.Errorf("no simulation matches '%s'", query)
	}
	ids := make([]string, len(partial))
	for i, s := range partial {
		ids[i] = s.ID
	}
	return nil, fmt.Errorf("'%s' is ambiguous: %s", query, strings.Join(ids, ", "))
}

// solve returns, for each node, the chance of reaching goal under the best plan
// for that goal, and the option the plan picks at each player node.
func solve(sim *Simulation, goal string) map[string]planEntry {
	memo := map[string]planEntry{}
	var value func(id string) float64
	value = func(id string) float64 {
		if entry, ok := memo[id]; ok {
			return entry.value
		}
		node := sim.Nodes[id]
		switch node.Type {
		case "end":
			v := 0.0
			if node.Outcome == goal {
				v = 1.0
			}
			memo[id] = planEntry{value: v, choice: -1}
		case "nature":
			total := 0.0
			for _, b := range node.Branches {
				total += b.P * value(b.Next)
			}
			memo[id] = planEntry{value: total, choice: -1}
		default:
			best, bestIndex := -1.0, 0
			for i, o := range node.Options {
				if v := value(o.Next); v > best {
					best, bestIndex = v, i
				}
			}
			memo[id] = planEntry{value: best, choice: bestIndex}
		}
		return memo[id].value
	}
	value(sim.Start)
	return memo
}

// trace follows a plan from the start. Chance is resolved by the likeliest branch.
// It returns the steps, the ending node, and the chance of the goal under the plan.
func trace(sim *Simulation, plan map[string]planEntry) ([]Step, SimNode, float64) {
	var steps []Step
	id := sim.Start
	for {
		node := sim.Nodes[id]
		switch node.Type {
		case "end":
			return steps, node, plan[sim.Start].value
		case "nature":
			best := node.Branches[0]
			for _, b := range node.Branches[1:] {
				if b.P > best.P {
					best = b
				}
			}
			steps = append(steps, Step{Kind: "chance", Prompt: node.Prompt, Label: best.Label, P: best.P, Why: best.Why})
			id = best.Next
		default:
			option := node.Options[plan[id].choice]
			steps = append(steps, Step{Kind: "you", Prompt: node.Prompt, Label: option.Label, Why: option.Why})
			id = option.Next
		}
	}
}

// endings lists every reachable ending, across all of your choices.
func endings(sim *Simulation) []Ending {
	const limit = 2000
	var out []Ending
	var walk func(id string, steps []Step, prob float64)
	walk = func(id string, steps []Step, prob float64) {
		if len(out) >= limit {
			return
		}
		node := sim.Nodes[id]
		switch node.Type {
		case "end":
			out = append(out, Ending{Steps: steps, Prob: prob, Outcome: node.Outcome, Text: node.Text})
		case "nature":
			for _, b := range node.Branches {
				step := Step{Kind: "chance", Prompt: node.Prompt, Label: b.Label, P: b.P, Why: b.Why}
				walk(b.Next, append(append([]Step{}, steps...), step), prob*b.P)
			}
		default:
			for _, o := range node.Options {
				step := Step{Kind: "you", Prompt: node.Prompt, Label: o.Label, Why: o.Why}
				walk(o.Next, append(append([]Step{}, steps...), step), prob)
			}
		}
	}
	walk(sim.Start, nil, 1.0)
	return out
}

// playSim runs one interactive game. ask receives the prompt and the options, each
// with its chance of victory from there under the best plan, and returns the index
// the player chose. say shows narration such as a chance result. It returns the
// steps taken and the ending node.
func playSim(sim *Simulation, ask func(prompt string, options []PlayOption) int, say func(string)) ([]Step, SimNode) {
	return playSimFrom(sim, sim.Start, nil, ask, say, nil)
}

// playSimFrom plays from a given node with the steps already taken. checkpoint, if set, is called
// before each decision so the game can be saved.
func playSimFrom(sim *Simulation, start string, taken []Step, ask func(prompt string, options []PlayOption) int, say func(string), checkpoint func(node string, steps []Step)) ([]Step, SimNode) {
	values := solve(sim, "victory")
	id := start
	steps := append([]Step{}, taken...)
	// history holds each decision node with the steps taken before it, for walking back.
	type decision struct {
		id    string
		steps []Step
	}
	var history []decision
	for {
		node := sim.Nodes[id]
		if checkpoint != nil {
			checkpoint(id, steps)
		}
		switch node.Type {
		case "end":
			return steps, node
		case "nature":
			roll := rand.Float64()
			chosen := node.Branches[len(node.Branches)-1]
			cumulative := 0.0
			for _, b := range node.Branches {
				cumulative += b.P
				if roll < cumulative {
					chosen = b
					break
				}
			}
			say(node.Prompt + " " + chosen.Label)
			steps = append(steps, Step{Kind: "chance", Prompt: node.Prompt, Label: chosen.Label, P: chosen.P, Why: chosen.Why})
			id = chosen.Next
		default:
			options := make([]PlayOption, len(node.Options))
			for i, o := range node.Options {
				options[i] = PlayOption{Label: o.Label, Why: o.Why, Chance: values[o.Next].value}
			}
			index := ask(node.Prompt, options)
			if index < 0 { // walk back to the previous decision and take it again
				if n := len(history); n > 0 {
					id, steps = history[n-1].id, append([]Step{}, history[n-1].steps...)
					history = history[:n-1]
				}
				continue
			}
			chosen := node.Options[index]
			history = append(history, decision{id: id, steps: append([]Step{}, steps...)})
			steps = append(steps, Step{Kind: "you", Prompt: node.Prompt, Label: chosen.Label, Why: chosen.Why})
			id = chosen.Next
		}
	}
}

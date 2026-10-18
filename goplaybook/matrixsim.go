package main

import (
	"encoding/json"
	"fmt"
	"math"
	"math/big"
	"os"
)

// MatrixSimulation builds a simulation from a game's payoff grid, so it agrees with the solver.
// You choose a row; the other player picks a column. Their choices follow an equilibrium mix, a
// uniform mix, or a noisy best response (weights exp(lam * payoff)). Victory if your payoff reaches
// the equilibrium value for you, failure if it falls short.
func MatrixSimulation(game Game, families []string, opponent string, lam float64) (*Simulation, error) {
	spec := game.Matrix
	if spec == nil {
		return nil, fmt.Errorf("'%s' has no payoff matrix", game.Name)
	}
	if opponent != "equilibrium" && opponent != "uniform" && opponent != "noisy" && opponent != "loss-averse" {
		return nil, fmt.Errorf("opponent must be equilibrium, uniform, noisy or loss-averse")
	}
	if lam < 0 {
		return nil, fmt.Errorf("lambda must be zero or more")
	}
	m := make(Matrix, len(spec.Payoffs))
	for i, row := range spec.Payoffs {
		m[i] = make([]Cell, len(row))
		for j, c := range row {
			m[i][j] = Cell{big.NewRat(int64(c[0]), 1), big.NewRat(int64(c[1]), 1)}
		}
	}
	eqs := SupportEquilibria(m)
	if len(eqs) == 0 {
		return nil, fmt.Errorf("'%s' has no equilibrium to build a simulation from", game.Name)
	}
	rowMix, colMix := eqs[0].Row, eqs[0].Col
	value := new(big.Rat)
	for i := range spec.Payoffs {
		for j := range spec.Payoffs[i] {
			term := new(big.Rat).Mul(rowMix[i], colMix[j])
			value.Add(value, term.Mul(term, m[i][j].Row))
		}
	}
	valueF, _ := value.Float64()
	uniform := make([]float64, len(spec.Cols))
	for j := range uniform {
		uniform[j] = 1 / float64(len(spec.Cols))
	}
	equilibriumProbs := make([]float64, len(colMix))
	for j, p := range colMix {
		equilibriumProbs[j], _ = p.Float64()
	}
	descriptions := map[string]string{
		"equilibrium": "the equilibrium mix",
		"uniform":     "a uniform random mix, not equilibrium play",
		"noisy":       fmt.Sprintf("a noisy best response: the better their payoff, the more likely they choose it (lambda %g)", lam),
		"loss-averse": fmt.Sprintf("a loss-averse response: they weigh falling below their average payoff about 2.25 times as heavily as gaining above it (lambda %g)", lam),
	}

	nodes := map[string]SimNode{}
	var startOptions []SimOption
	for i, rowName := range spec.Rows {
		var probs []float64
		switch opponent {
		case "uniform":
			probs = uniform
		case "noisy":
			probs = noisyResponse(spec.Payoffs, i, lam)
		case "loss-averse":
			probs = lossAverseResponse(spec.Payoffs, i, lam)
		default:
			probs = equilibriumProbs
		}
		var branches []SimBranch
		for j, colName := range spec.Cols {
			if probs[j] == 0 {
				continue
			}
			a := m[i][j].Row
			endID := fmt.Sprintf("end-%d-%d", i, j)
			var outcome, text string
			if a.Cmp(value) >= 0 {
				outcome = "victory"
				text = fmt.Sprintf("You get %s against their %d: at least the equilibrium value %g.", a.RatString(), spec.Payoffs[i][j][1], valueF)
			} else {
				outcome = "failure"
				text = fmt.Sprintf("You get %s against their %d: below the equilibrium value %g.", a.RatString(), spec.Payoffs[i][j][1], valueF)
			}
			nodes[endID] = SimNode{Type: "end", Outcome: outcome, Text: text}
			branches = append(branches, SimBranch{P: probs[j], Label: "They play " + colName, Next: endID,
				Why: fmt.Sprintf("They play %s %.0f%% of the time against %s. Your payoff: %s.", colName, probs[j]*100, rowName, a.RatString())})
		}
		natureID := fmt.Sprintf("chance-%d", i)
		nodes[natureID] = SimNode{Type: "nature", Prompt: fmt.Sprintf("After you play %s, they choose:", rowName), Branches: branches}
		startOptions = append(startOptions, SimOption{Label: "Play " + rowName, Next: natureID,
			Why: fmt.Sprintf("Playing %s faces their equilibrium mix; the outcome depends on what they choose.", rowName)})
	}
	nodes["n0"] = SimNode{Type: "player", Prompt: "Choose your action.", Options: startOptions}
	return &Simulation{
		ID:       game.ID + "-matrix",
		Name:     game.Name + " (from its payoff matrix)",
		Families: families,
		Summary:  fmt.Sprintf("Built from the payoff grid of %s. The equilibrium value for you is %g. The other player's choices follow %s.", game.Name, valueF, descriptions[opponent]),
		Start:    "n0",
		Nodes:    nodes,
	}, nil
}

// lossAverseLambda is prospect theory's loss aversion: losses weigh about 2.25 times as much as gains.
const lossAverseLambda = 2.25

// lossAverseResponse is the logit choice when the column player weighs payoffs below their row average
// about 2.25 times as heavily as payoffs above it.
func lossAverseResponse(payoffs [][][2]int, row int, lam float64) []float64 {
	n := len(payoffs[row])
	reference := 0.0
	for _, c := range payoffs[row] {
		reference += float64(c[1])
	}
	reference /= float64(n)
	utilities := make([]float64, n)
	top := math.Inf(-1)
	for j, c := range payoffs[row] {
		x := float64(c[1])
		if x >= reference {
			utilities[j] = x
		} else {
			utilities[j] = reference + lossAverseLambda*(x-reference)
		}
		if utilities[j] > top {
			top = utilities[j]
		}
	}
	weights := make([]float64, n)
	total := 0.0
	for j, u := range utilities {
		weights[j] = math.Exp(lam * (u - top))
		total += weights[j]
	}
	for j := range weights {
		weights[j] /= total
	}
	return weights
}

// noisyResponse is the logit choice of the column player against a given row:
// each column has weight exp(lam * payoff), normalised to probabilities.
func noisyResponse(payoffs [][][2]int, row int, lam float64) []float64 {
	values := make([]float64, len(payoffs[row]))
	top := math.Inf(-1)
	for j, c := range payoffs[row] {
		values[j] = float64(c[1])
		if values[j] > top {
			top = values[j]
		}
	}
	weights := make([]float64, len(values))
	total := 0.0
	for j, v := range values {
		weights[j] = math.Exp(lam * (v - top))
		total += weights[j]
	}
	for j := range weights {
		weights[j] /= total
	}
	return weights
}

// SavedGame is a game saved with --save and continued with --resume.
type SavedGame struct {
	Simulation string `json:"simulation"`
	Node       string `json:"node"`
	Steps      []Step `json:"steps"`
}

func saveGame(path string, sim *Simulation, node string, steps []Step) error {
	data, err := json.MarshalIndent(SavedGame{Simulation: sim.ID, Node: node, Steps: steps}, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, append(data, '\n'), 0o644)
}

func loadGame(path string, sim *Simulation) (string, []Step, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return "", nil, err
	}
	var saved SavedGame
	if err := json.Unmarshal(data, &saved); err != nil {
		return "", nil, err
	}
	if saved.Simulation != sim.ID {
		return "", nil, fmt.Errorf("that save is for '%s', not '%s'", saved.Simulation, sim.ID)
	}
	if _, ok := sim.Nodes[saved.Node]; !ok {
		return "", nil, fmt.Errorf("that save refers to a step this simulation does not have")
	}
	return saved.Node, saved.Steps, nil
}

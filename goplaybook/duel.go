package main

import "fmt"

// Duel engine games play a catalogue game that has a payoff table. The engine answers each row you
// choose with a column, from one of two fixed rules, so the game can be learned and played well.
// The rules and tie-breaks match gtplaybook/engine.py.

// duelEngineCol is the engine's column for this round, given the rows you have played so far.
// The learner picks the column that does best against your most common row. The reactive engine
// picks the column that does best against your last row, and the first column in round one.
func duelEngineCol(m *GameMatrix, played []int, policy string) int {
	if policy == "mirror" {
		if len(played) == 0 {
			return 0
		}
		if last := played[len(played)-1]; last < len(m.Cols) {
			return last
		}
		return 0
	}
	if policy == "exploiter" {
		predicted := duelPredictedRow(m, played)
		best, bestValue := 0, 0
		for c := range m.Cols {
			if v := m.Payoffs[predicted][c][1]; c == 0 || v > bestValue {
				best, bestValue = c, v
			}
		}
		return best
	}
	if policy == "reactive" {
		if len(played) == 0 {
			return 0
		}
		last := played[len(played)-1]
		best, bestValue := 0, 0
		for c := range m.Cols {
			if v := m.Payoffs[last][c][1]; c == 0 || v > bestValue {
				best, bestValue = c, v
			}
		}
		return best
	}
	best, bestValue := 0, 0
	for c := range m.Cols {
		value := 0
		for r := range m.Rows {
			count := 0
			for _, p := range played {
				if p == r {
					count++
				}
			}
			value += count * m.Payoffs[r][c][1]
		}
		if c == 0 || value > bestValue {
			best, bestValue = c, value
		}
	}
	return best
}

// duelPredictedRow is the row the exploiter expects next: the row you most often play after your last
// row, or your most common row when that sequence has not happened yet. The first row is expected first.
func duelPredictedRow(m *GameMatrix, played []int) int {
	if len(played) == 0 {
		return 0
	}
	last := played[len(played)-1]
	var pool []int
	for i := 0; i+1 < len(played); i++ {
		if played[i] == last {
			pool = append(pool, played[i+1])
		}
	}
	if len(pool) == 0 {
		pool = played
	}
	best, bestCount := 0, -1
	for r := range m.Rows {
		count := 0
		for _, p := range pool {
			if p == r {
				count++
			}
		}
		if count > bestCount {
			best, bestCount = r, count
		}
	}
	return best
}

// duelBestRow is your best row against a column: the first row that does best for you.
func duelBestRow(m *GameMatrix, col int) int {
	best, bestValue := 0, 0
	for r := range m.Rows {
		if v := m.Payoffs[r][col][0]; r == 0 || v > bestValue {
			best, bestValue = r, v
		}
	}
	return best
}

// playDuel runs a duel engine game against the payoff table of the catalogue game it names.
func playDuel(game engineGame, catalog []Game, ask func(string) (string, bool), say func(string)) {
	var match *Game
	for i := range catalog {
		if catalog[i].ID == game.Game {
			match = &catalog[i]
			break
		}
	}
	if match == nil || match.Matrix == nil {
		say(fmt.Sprintf("No payoff table for '%s'.", game.Game))
		return
	}
	m := match.Matrix
	say(fmt.Sprintf("Enter the number of your row, 1 to %d. h for a hint, q quits.", len(m.Rows)))
	var played []int
	you, engine := 0, 0
	for round := 1; round <= game.Rounds; {
		line, ok := readAnswer(ask, fmt.Sprintf("Round %d (row 1 to %d): ", round, len(m.Rows)))
		if !ok {
			say("You left the game.")
			return
		}
		if line == "h" {
			col := duelEngineCol(m, played, game.Policy)
			say(fmt.Sprintf("Hint: the engine will play %s. %s does best against that.", m.Cols[col], m.Rows[duelBestRow(m, col)]))
			continue
		}
		n, valid := wholeNumber(line, len(m.Rows))
		if !valid || n < 1 {
			say(fmt.Sprintf("Enter a row number from 1 to %d.", len(m.Rows)))
			continue
		}
		row := n - 1
		col := duelEngineCol(m, played, game.Policy)
		played = append(played, row)
		u, v := m.Payoffs[row][col][0], m.Payoffs[row][col][1]
		you += u
		engine += v
		say(fmt.Sprintf("You played %s, the engine played %s. You get %d, it gets %d.", m.Rows[row], m.Cols[col], u, v))
		round++
	}
	say(fmt.Sprintf("Final score: you %d, the engine %d.", you, engine))
	switch {
	case you > engine:
		say("You win the match.")
	case engine > you:
		say("The engine wins the match.")
	default:
		say("The match is drawn.")
	}
}

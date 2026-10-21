package main

import (
	"encoding/json"
	"fmt"
	"strconv"
	"strings"
)

// Engine games: a computer opponent that chooses its move as you play. The rules, move order and
// tie-breaks match gtplaybook/engine.py, so both versions play the same game.

// engineGame is one entry of data/engine-games.json.
type engineGame struct {
	ID      string `json:"id"`
	Name    string `json:"name"`
	Kind    string `json:"kind"`
	Summary string `json:"summary"`
	Rules   string `json:"rules"`
	Engine  string `json:"engine"`
	Game    string `json:"game"`
	Policy  string `json:"policy"`
	Rounds  int    `json:"rounds"`
}

const (
	c4Rows       = 6
	c4Cols       = 7
	c4Depth      = 4
	searchLimit  = 1 << 30
	rpsRounds    = 20
	blottoRounds = 5
	blottoUnits  = 6
	blottoFronts = 3
	patrolGates  = 3
	patrolRounds = 12
)

const (
	ultimatumCoins     = 10
	ultimatumThreshold = 3 // the engine accepts an offer of at least this many coins
	ultimatumRounds    = 5
	beautyTop          = 100 // guesses run from 0 to this
	beautyOpening      = 50  // the engine's forecast of your guess before you have guessed
	beautyRounds       = 5
	pennyRounds        = 20
)

var c4Order = [c4Cols]int{3, 2, 4, 1, 5, 0, 6}

// c4Windows lists every line of four cells on the board, as [row, column] pairs.
var c4Windows = buildC4Windows()

var tttLines = [8][3]int{{0, 1, 2}, {3, 4, 5}, {6, 7, 8}, {0, 3, 6}, {1, 4, 7}, {2, 5, 8}, {0, 4, 8}, {2, 4, 6}}

var rpsMoves = [3]string{"rock", "paper", "scissors"}
var rpsBeats = map[string]string{"rock": "scissors", "paper": "rock", "scissors": "paper"}
var rpsCounter = map[string]string{"rock": "paper", "paper": "scissors", "scissors": "rock"}

// blottoSplits lists every way to send the units to the fronts, in the same order as the Python version.
var blottoSplits = buildBlottoSplits()

type c4Grid [c4Rows][c4Cols]byte

func loadEngineGames() ([]engineGame, error) {
	data, err := dataFS.ReadFile("data/engine-games.json")
	if err != nil {
		return nil, err
	}
	var games []engineGame
	if err := json.Unmarshal(data, &games); err != nil {
		return nil, err
	}
	return games, nil
}

func findEngineGame(games []engineGame, query string) (engineGame, error) {
	key := strings.ToLower(strings.TrimSpace(query))
	for _, g := range games {
		if g.ID == key {
			return g, nil
		}
	}
	return engineGame{}, fmt.Errorf("no engine game '%s'. Run 'engine' to list them", query)
}

func buildC4Windows() [][4][2]int {
	var windows [][4][2]int
	for r := 0; r < c4Rows; r++ {
		for c := 0; c < c4Cols; c++ {
			for _, d := range [4][2]int{{0, 1}, {1, 0}, {1, 1}, {1, -1}} {
				var cells [4][2]int
				ok := true
				for k := 0; k < 4; k++ {
					y, x := r+k*d[0], c+k*d[1]
					if y < 0 || y >= c4Rows || x < 0 || x >= c4Cols {
						ok = false
						break
					}
					cells[k] = [2]int{y, x}
				}
				if ok {
					windows = append(windows, cells)
				}
			}
		}
	}
	return windows
}

func buildBlottoSplits() [][blottoFronts]int {
	var splits [][blottoFronts]int
	for a := 0; a <= blottoUnits; a++ {
		for b := 0; b <= blottoUnits-a; b++ {
			splits = append(splits, [blottoFronts]int{a, b, blottoUnits - a - b})
		}
	}
	return splits
}

// playEngine runs one engine game. ask returns a line, or false at the end of input. say prints a line.
func playEngine(game engineGame, catalog []Game, ask func(string) (string, bool), say func(string)) {
	say("\n" + game.Name)
	say(game.Rules)
	say("")
	if game.Kind == "duel" {
		playDuel(game, catalog, ask, say)
		return
	}
	switch game.ID {
	case "tic-tac-toe":
		playTicTacToe(ask, say)
	case "nim":
		playNim(ask, say)
	case "connect-four":
		playConnectFour(ask, say)
	case "rock-paper-scissors":
		playRockPaperScissors(ask, say)
	case "colonel-blotto":
		playBlotto(ask, say)
	case "border-patrol":
		playPatrol(ask, say)
	case "ultimatum":
		playUltimatum(ask, say)
	case "beauty-contest":
		playBeautyContest(ask, say)
	case "matching-pennies":
		playMatchingPennies(ask, say)
	}
}

// readAnswer returns the player's line in lower case. It returns false when they quit or input ends.
func readAnswer(ask func(string) (string, bool), prompt string) (string, bool) {
	line, ok := ask(prompt)
	if !ok {
		return "", false
	}
	line = strings.ToLower(strings.TrimSpace(line))
	if line == "q" || line == "quit" || line == "exit" {
		return "", false
	}
	return line, true
}

func isDigits(s string) bool {
	if s == "" {
		return false
	}
	for _, r := range s {
		if r < '0' || r > '9' {
			return false
		}
	}
	return true
}

// ---- Tic-tac-toe: X is you, O is the engine. A board is nine characters, row by row.

func tttWinner(board string) byte {
	for _, l := range tttLines {
		a, b, c := board[l[0]], board[l[1]], board[l[2]]
		if a != ' ' && a == b && b == c {
			return a
		}
	}
	return 0
}

var tttMemo = map[string]int{}

// tttValue is the score for X: 10 minus the moves made when X wins, the reverse for O, 0 for a draw.
func tttValue(board string) int {
	if v, ok := tttMemo[board]; ok {
		return v
	}
	filled := 0
	for i := 0; i < 9; i++ {
		if board[i] != ' ' {
			filled++
		}
	}
	var value int
	won := tttWinner(board)
	switch {
	case won == 'X':
		value = 10 - filled
	case won == 'O':
		value = filled - 10
	case filled == 9:
		value = 0
	default:
		mover := byte('O')
		if filled%2 == 0 {
			mover = 'X'
		}
		first := true
		for i := 0; i < 9; i++ {
			if board[i] != ' ' {
				continue
			}
			v := tttValue(board[:i] + string(mover) + board[i+1:])
			if first || (mover == 'X' && v > value) || (mover == 'O' && v < value) {
				value = v
				first = false
			}
		}
	}
	tttMemo[board] = value
	return value
}

// tttBest is the best square for mover, as an index from 0; the lowest index wins a tie.
func tttBest(board string, mover byte) int {
	best, bestValue := -1, 0
	for i := 0; i < 9; i++ {
		if board[i] != ' ' {
			continue
		}
		v := tttValue(board[:i] + string(mover) + board[i+1:])
		if best < 0 || (mover == 'X' && v > bestValue) || (mover == 'O' && v < bestValue) {
			best, bestValue = i, v
		}
	}
	return best
}

func showTicTacToe(say func(string), board string) {
	rows := make([]string, 3)
	for r := 0; r < 3; r++ {
		cells := make([]string, 3)
		for c := 0; c < 3; c++ {
			i := r*3 + c
			if board[i] != ' ' {
				cells[c] = string(board[i])
			} else {
				cells[c] = strconv.Itoa(i + 1)
			}
		}
		rows[r] = strings.Join(cells, " | ")
	}
	say("\n" + strings.Join(rows, "\n-----------\n") + "\n")
}

func playTicTacToe(ask func(string) (string, bool), say func(string)) {
	board := strings.Repeat(" ", 9)
	say("h for a hint, q to quit.")
	showTicTacToe(say, board)
	for {
		line, ok := readAnswer(ask, "Your square (1-9): ")
		if !ok {
			say("You left the game.")
			return
		}
		if line == "h" {
			say(fmt.Sprintf("Hint: square %d is the best move for you.", tttBest(board, 'X')+1))
			continue
		}
		n := 0
		if isDigits(line) {
			n, _ = strconv.Atoi(line)
		}
		if n < 1 || n > 9 || board[n-1] != ' ' {
			say("Pick an empty square from 1 to 9.")
			continue
		}
		board = board[:n-1] + "X" + board[n:]
		if tttWinner(board) != 0 || !strings.Contains(board, " ") {
			break
		}
		engine := tttBest(board, 'O')
		board = board[:engine] + "O" + board[engine+1:]
		say(fmt.Sprintf("Engine plays square %d.", engine+1))
		showTicTacToe(say, board)
		if tttWinner(board) != 0 || !strings.Contains(board, " ") {
			break
		}
	}
	showTicTacToe(say, board)
	switch tttWinner(board) {
	case 'X':
		say("You win.")
	case 'O':
		say("The engine wins.")
	default:
		say("A draw.")
	}
}

// ---- Nim: three piles, take any number from one pile, whoever takes the last object wins.

type nimPiles [3]int

var nimMemo = map[nimPiles]bool{}

// nimWins reports whether the player to move can force a win.
func nimWins(p nimPiles) bool {
	if v, ok := nimMemo[p]; ok {
		return v
	}
	result := false
	if p != (nimPiles{}) {
		for i := 0; i < 3 && !result; i++ {
			for take := 1; take <= p[i] && !result; take++ {
				q := p
				q[i] -= take
				if !nimWins(q) {
					result = true
				}
			}
		}
	}
	nimMemo[p] = result
	return result
}

// nimBest is a winning (pile, take) when one exists, else the first legal one.
func nimBest(p nimPiles) (int, int) {
	for i := 0; i < 3; i++ {
		for take := 1; take <= p[i]; take++ {
			q := p
			q[i] -= take
			if !nimWins(q) {
				return i, take
			}
		}
	}
	for i := 0; i < 3; i++ {
		if p[i] > 0 {
			return i, 1
		}
	}
	return 0, 0
}

func nimEmpty(p nimPiles) bool {
	return p[0] == 0 && p[1] == 0 && p[2] == 0
}

func playNim(ask func(string) (string, bool), say func(string)) {
	piles := nimPiles{3, 5, 7}
	say("h for a hint, q to quit.")
	for {
		parts := make([]string, 3)
		for i, size := range piles {
			text := strings.Repeat("o", size)
			if size == 0 {
				text = "(empty)"
			}
			parts[i] = fmt.Sprintf("%d: %s", i+1, text)
		}
		say("Piles: " + strings.Join(parts, "  "))
		if nimEmpty(piles) {
			say("You took the last object. You win.")
			return
		}
		line, ok := readAnswer(ask, "Pile and count, e.g. 2 3 (or h, q): ")
		if !ok {
			say("You left the game.")
			return
		}
		if line == "h" {
			if nimWins(piles) {
				pile, take := nimBest(piles)
				say(fmt.Sprintf("Hint: take %d from pile %d. That keeps you winning.", take, pile+1))
			} else {
				say("Hint: against perfect play every move loses from here.")
			}
			continue
		}
		fields := strings.Fields(strings.ReplaceAll(line, ",", " "))
		if len(fields) != 2 || !isDigits(fields[0]) || !isDigits(fields[1]) {
			say("Enter a pile and a count, for example 2 3.")
			continue
		}
		pile, _ := strconv.Atoi(fields[0])
		take, _ := strconv.Atoi(fields[1])
		pile--
		if pile < 0 || pile >= 3 || take < 1 || take > piles[pile] {
			say("That move is not allowed. Take from a pile that has objects in it.")
			continue
		}
		piles[pile] -= take
		if nimEmpty(piles) {
			say("You took the last object. You win.")
			return
		}
		pile, take = nimBest(piles)
		piles[pile] -= take
		say(fmt.Sprintf("Engine takes %d from pile %d.", take, pile+1))
		if nimEmpty(piles) {
			say("The engine took the last object. The engine wins.")
			return
		}
	}
}

// ---- Connect Four: X is you (first), O is the engine. grid[row][col], row 0 is the bottom.

func c4Empty() c4Grid {
	var g c4Grid
	for r := range g {
		for c := range g[r] {
			g[r][c] = ' '
		}
	}
	return g
}

func c4Winner(g c4Grid) byte {
	for _, cells := range c4Windows {
		first := g[cells[0][0]][cells[0][1]]
		if first == ' ' {
			continue
		}
		same := true
		for _, cell := range cells {
			if g[cell[0]][cell[1]] != first {
				same = false
				break
			}
		}
		if same {
			return first
		}
	}
	return 0
}

func c4Full(g c4Grid) bool {
	for c := 0; c < c4Cols; c++ {
		if g[c4Rows-1][c] == ' ' {
			return false
		}
	}
	return true
}

// c4Drop puts a piece in a column and returns its row, or -1 when the column is full.
func c4Drop(g *c4Grid, col int, piece byte) int {
	for row := 0; row < c4Rows; row++ {
		if g[row][col] == ' ' {
			g[row][col] = piece
			return row
		}
	}
	return -1
}

// c4Score is the score for O: threes and twos in an open line, and the centre column.
func c4Score(g c4Grid) int {
	total := 0
	for _, cells := range c4Windows {
		o, x := 0, 0
		for _, cell := range cells {
			switch g[cell[0]][cell[1]] {
			case 'O':
				o++
			case 'X':
				x++
			}
		}
		if o > 0 && x > 0 {
			continue
		}
		switch o {
		case 3:
			total += 5
		case 2:
			total += 2
		}
		switch x {
		case 3:
			total -= 5
		case 2:
			total -= 2
		}
	}
	centre := c4Cols / 2
	for row := 0; row < c4Rows; row++ {
		switch g[row][centre] {
		case 'O':
			total += 3
		case 'X':
			total -= 3
		}
	}
	return total
}

func c4Search(g *c4Grid, depth, alpha, beta int, engineTurn bool) int {
	switch c4Winner(*g) {
	case 'O':
		return 1000 + depth
	case 'X':
		return -1000 - depth
	}
	if depth == 0 || c4Full(*g) {
		return c4Score(*g)
	}
	best := searchLimit
	piece := byte('X')
	if engineTurn {
		best = -searchLimit
		piece = 'O'
	}
	for _, col := range c4Order {
		row := c4Drop(g, col, piece)
		if row < 0 {
			continue
		}
		value := c4Search(g, depth-1, alpha, beta, !engineTurn)
		g[row][col] = ' '
		if engineTurn {
			if value > best {
				best = value
			}
			if best > alpha {
				alpha = best
			}
		} else {
			if value < best {
				best = value
			}
			if best < beta {
				beta = best
			}
		}
		if alpha >= beta {
			break
		}
	}
	return best
}

// c4Best is the best column for the side to move; the first column in c4Order wins a tie.
func c4Best(g *c4Grid, engineTurn bool) int {
	piece := byte('X')
	if engineTurn {
		piece = 'O'
	}
	bestCol, bestValue := -1, 0
	for _, col := range c4Order {
		row := c4Drop(g, col, piece)
		if row < 0 {
			continue
		}
		value := c4Search(g, c4Depth-1, -searchLimit, searchLimit, !engineTurn)
		g[row][col] = ' '
		if bestCol < 0 || (engineTurn && value > bestValue) || (!engineTurn && value < bestValue) {
			bestCol, bestValue = col, value
		}
	}
	return bestCol
}

func showConnectFour(say func(string), g c4Grid) {
	header := make([]string, c4Cols)
	for c := 0; c < c4Cols; c++ {
		header[c] = strconv.Itoa(c + 1)
	}
	say("  " + strings.Join(header, " "))
	for row := c4Rows - 1; row >= 0; row-- {
		cells := make([]string, c4Cols)
		for c := 0; c < c4Cols; c++ {
			cells[c] = string(g[row][c])
		}
		say("  " + strings.Join(cells, " "))
	}
	say("")
}

func playConnectFour(ask func(string) (string, bool), say func(string)) {
	g := c4Empty()
	say("Enter a column from 1 to 7, h for a hint, or q to quit.")
	showConnectFour(say, g)
	for {
		line, ok := readAnswer(ask, "Your column (1-7): ")
		if !ok {
			say("You left the game.")
			return
		}
		if line == "h" {
			say(fmt.Sprintf("Hint: column %d is the best move for you.", c4Best(&g, false)+1))
			continue
		}
		n := 0
		if isDigits(line) {
			n, _ = strconv.Atoi(line)
		}
		if n < 1 || n > c4Cols || g[c4Rows-1][n-1] != ' ' {
			say("Pick a column from 1 to 7 that is not full.")
			continue
		}
		c4Drop(&g, n-1, 'X')
		if c4Winner(g) != 0 || c4Full(g) {
			break
		}
		col := c4Best(&g, true)
		c4Drop(&g, col, 'O')
		say(fmt.Sprintf("Engine plays column %d.", col+1))
		showConnectFour(say, g)
		if c4Winner(g) != 0 || c4Full(g) {
			break
		}
	}
	showConnectFour(say, g)
	switch c4Winner(g) {
	case 'X':
		say("You win.")
	case 'O':
		say("The engine wins.")
	default:
		say("A draw.")
	}
}

// ---- Rock-paper-scissors against a pattern engine.

// rpsEngineMove beats your most common move so far; rock is the first choice when counts tie.
func rpsEngineMove(history []string) string {
	best, bestCount := rpsMoves[0], -1
	for _, move := range rpsMoves {
		count := 0
		for _, played := range history {
			if played == move {
				count++
			}
		}
		if count > bestCount {
			best, bestCount = move, count
		}
	}
	return rpsCounter[best]
}

func playRockPaperScissors(ask func(string) (string, bool), say func(string)) {
	names := map[string]string{"r": "rock", "rock": "rock", "p": "paper", "paper": "paper", "s": "scissors", "scissors": "scissors"}
	var history []string
	you, engine := 0, 0
	say("Enter r, p or s. h for a hint, q quits.")
	for round := 1; round <= rpsRounds; {
		line, ok := readAnswer(ask, fmt.Sprintf("Round %d (r, p or s): ", round))
		if !ok {
			say("You left the game.")
			return
		}
		if line == "h" {
			reply := rpsEngineMove(history)
			say(fmt.Sprintf("Hint: the engine will play %s. Play %s to beat it.", reply, rpsCounter[reply]))
			continue
		}
		move, known := names[line]
		if !known {
			say("Enter r, p or s.")
			continue
		}
		reply := rpsEngineMove(history)
		history = append(history, move)
		var result string
		switch {
		case rpsBeats[move] == reply:
			you++
			result = "You win the round."
		case rpsBeats[reply] == move:
			engine++
			result = "The engine wins the round."
		default:
			result = "Round drawn."
		}
		say(fmt.Sprintf("You played %s, the engine played %s. %s", move, reply, result))
		round++
	}
	say(fmt.Sprintf("Final score: you %d, the engine %d, drawn %d.", you, engine, rpsRounds-you-engine))
	switch {
	case you > engine:
		say("You win the match.")
	case engine > you:
		say("The engine wins the match.")
	default:
		say("The match is drawn.")
	}
}

// ---- Colonel Blotto: three fronts, six units, you and the engine send at once.

func blottoNet(mine, theirs [blottoFronts]int) int {
	total := 0
	for i := range mine {
		switch {
		case mine[i] > theirs[i]:
			total++
		case mine[i] < theirs[i]:
			total--
		}
	}
	return total
}

// blottoEngineSplit is the split with the best net result against your past splits (all splits, if none yet).
func blottoEngineSplit(history [][blottoFronts]int) [blottoFronts]int {
	past := history
	if len(past) == 0 {
		past = blottoSplits
	}
	var best [blottoFronts]int
	bestValue := 0.0
	for i, split := range blottoSplits {
		sum := 0
		for _, theirs := range past {
			sum += blottoNet(split, theirs)
		}
		value := float64(sum) / float64(len(past))
		if i == 0 || value > bestValue {
			best, bestValue = split, value
		}
	}
	return best
}

func parseBlottoSplit(text string) ([blottoFronts]int, bool) {
	var split [blottoFronts]int
	fields := strings.Fields(strings.ReplaceAll(text, ",", " "))
	if len(fields) != blottoFronts {
		return split, false
	}
	total := 0
	for i, field := range fields {
		if !isDigits(field) {
			return split, false
		}
		split[i], _ = strconv.Atoi(field)
		total += split[i]
	}
	return split, total == blottoUnits
}

func joinSplit(split [blottoFronts]int) string {
	return fmt.Sprintf("%d %d %d", split[0], split[1], split[2])
}

func playBlotto(ask func(string) (string, bool), say func(string)) {
	var history [][blottoFronts]int
	netTotal := 0
	say(fmt.Sprintf("Send %d units across %d fronts, for example 2 2 2. h for a hint, q quits.", blottoUnits, blottoFronts))
	for round := 1; round <= blottoRounds; round++ {
		var split [blottoFronts]int
		for {
			line, ok := readAnswer(ask, fmt.Sprintf("Round %d split: ", round))
			if !ok {
				say("You left the game.")
				return
			}
			if line == "h" {
				engineSplit := blottoEngineSplit(history)
				best := blottoSplits[0]
				bestNet := blottoNet(best, engineSplit)
				for _, option := range blottoSplits[1:] {
					if net := blottoNet(option, engineSplit); net > bestNet {
						best, bestNet = option, net
					}
				}
				say(fmt.Sprintf("Hint: the engine will send %s. %s does best against that.", joinSplit(engineSplit), joinSplit(best)))
				continue
			}
			var valid bool
			split, valid = parseBlottoSplit(line)
			if valid {
				break
			}
			say(fmt.Sprintf("Enter %d whole numbers that add up to %d.", blottoFronts, blottoUnits))
		}
		engine := blottoEngineSplit(history)
		history = append(history, split)
		net := blottoNet(split, engine)
		netTotal += net
		say(fmt.Sprintf("You sent %s, the engine sent %s.", joinSplit(split), joinSplit(engine)))
		switch {
		case net > 0:
			say("You take the round.")
		case net < 0:
			say("The engine takes the round.")
		default:
			say("Round drawn.")
		}
	}
	switch {
	case netTotal > 0:
		say("You win the campaign.")
	case netTotal < 0:
		say("The engine wins the campaign.")
	default:
		say("The campaign is drawn.")
	}
}

// ---- Border patrol: you pick a gate to slip through, the guard watches one gate.

// patrolEngineGate watches the gate you have used most often; gate 1 when counts tie or there is no history.
func patrolEngineGate(history []int) int {
	best, bestCount := 0, -1
	for gate := 0; gate < patrolGates; gate++ {
		count := 0
		for _, used := range history {
			if used == gate {
				count++
			}
		}
		if count > bestCount {
			best, bestCount = gate, count
		}
	}
	return best
}

func playPatrol(ask func(string) (string, bool), say func(string)) {
	var history []int
	through := 0
	say(fmt.Sprintf("Pick a gate from 1 to %d. h for a hint, q quits.", patrolGates))
	for round := 1; round <= patrolRounds; {
		line, ok := readAnswer(ask, fmt.Sprintf("Round %d gate: ", round))
		if !ok {
			say("You left the game.")
			return
		}
		if line == "h" {
			say("Hint: the guard watches the gate you have used most, so pick the gate you have used least.")
			continue
		}
		n := 0
		if isDigits(line) {
			n, _ = strconv.Atoi(line)
		}
		if n < 1 || n > patrolGates {
			say(fmt.Sprintf("Enter a gate from 1 to %d.", patrolGates))
			continue
		}
		gate := n - 1
		guard := patrolEngineGate(history)
		history = append(history, gate)
		if gate == guard {
			say(fmt.Sprintf("The guard was at gate %d. You are caught.", guard+1))
		} else {
			through++
			say(fmt.Sprintf("The guard was at gate %d. You get through.", guard+1))
		}
		round++
	}
	say(fmt.Sprintf("You got through %d of %d times.", through, patrolRounds))
	if through > patrolRounds/2 {
		say("You win.")
	} else {
		say("The guard wins.")
	}
}

// wholeNumber reads a line of digits, and reports false unless it is a whole number at most max.
func wholeNumber(line string, max int) (int, bool) {
	if !isDigits(line) {
		return 0, false
	}
	n := 0
	for _, r := range line {
		n = n*10 + int(r-'0')
		if n > max {
			return 0, false
		}
	}
	return n, true
}

// ---- Ultimatum: you offer the engine coins out of ten. It accepts an offer of at least its threshold.

func ultimatumAccepts(engineShare int) bool {
	return engineShare >= ultimatumThreshold
}

func playUltimatum(ask func(string) (string, bool), say func(string)) {
	youTotal, engineTotal := 0, 0
	say(fmt.Sprintf("Enter how many of the %d coins the engine gets. h for a hint, q quits.", ultimatumCoins))
	for round := 1; round <= ultimatumRounds; {
		line, ok := readAnswer(ask, fmt.Sprintf("Round %d (coins for the engine): ", round))
		if !ok {
			say("You left the game.")
			return
		}
		if line == "h" {
			say(fmt.Sprintf("Hint: offer the engine %d coins, the least it accepts. You keep %d.",
				ultimatumThreshold, ultimatumCoins-ultimatumThreshold))
			continue
		}
		share, valid := wholeNumber(line, ultimatumCoins)
		if !valid {
			say(fmt.Sprintf("Enter a whole number from 0 to %d.", ultimatumCoins))
			continue
		}
		if ultimatumAccepts(share) {
			youTotal += ultimatumCoins - share
			engineTotal += share
			say(fmt.Sprintf("The engine accepts. You keep %d coins, it gets %d.", ultimatumCoins-share, share))
		} else {
			say("The engine refuses. Neither of you gets anything this round.")
		}
		round++
	}
	say(fmt.Sprintf("You finished with %d coins, the engine with %d.", youTotal, engineTotal))
	switch {
	case youTotal > engineTotal:
		say("You win.")
	case engineTotal > youTotal:
		say("The engine wins.")
	default:
		say("The match is drawn.")
	}
}

// ---- Guess two thirds: the target is two thirds of the average of the two guesses, which is (you + engine) / 3.

// beautyEngineGuess is two thirds of your average guess so far, in whole numbers.
func beautyEngineGuess(history []int) int {
	if len(history) == 0 {
		return 2 * beautyOpening / 3
	}
	sum := 0
	for _, guess := range history {
		sum += guess
	}
	return 2 * sum / (3 * len(history))
}

func beautyTarget(you, engine int) int {
	return (you + engine) / 3
}

func abs(n int) int {
	if n < 0 {
		return -n
	}
	return n
}

func playBeautyContest(ask func(string) (string, bool), say func(string)) {
	var guesses []int
	you, engine := 0, 0
	say(fmt.Sprintf("Guess a whole number from 0 to %d. h for a hint, q quits.", beautyTop))
	for round := 1; round <= beautyRounds; {
		line, ok := readAnswer(ask, fmt.Sprintf("Round %d (0 to %d): ", round, beautyTop))
		if !ok {
			say("You left the game.")
			return
		}
		engineGuess := beautyEngineGuess(guesses)
		if line == "h" {
			say(fmt.Sprintf("Hint: the engine will guess %d. About half of that, %d, lands closest to the target.",
				engineGuess, engineGuess/2))
			continue
		}
		guess, valid := wholeNumber(line, beautyTop)
		if !valid {
			say(fmt.Sprintf("Enter a whole number from 0 to %d.", beautyTop))
			continue
		}
		guesses = append(guesses, guess)
		target := beautyTarget(guess, engineGuess)
		yours, theirs := abs(guess-target), abs(engineGuess-target)
		var result string
		switch {
		case yours < theirs:
			you++
			result = "You win the round."
		case theirs < yours:
			engine++
			result = "The engine wins the round."
		default:
			result = "Round drawn."
		}
		say(fmt.Sprintf("You guessed %d, the engine guessed %d. The target was %d. %s", guess, engineGuess, target, result))
		round++
	}
	say(fmt.Sprintf("Final score: you %d, the engine %d, drawn %d.", you, engine, beautyRounds-you-engine))
	switch {
	case you > engine:
		say("You win the match.")
	case engine > you:
		say("The engine wins the match.")
	default:
		say("The match is drawn.")
	}
}

// ---- Matching pennies: the engine's coin differs from the call you have made most often.

// pennyEngineCoin is the opposite of your most common call. Heads counts as your call when the calls are tied.
func pennyEngineCoin(calls []string) string {
	heads := 0
	for _, call := range calls {
		if call == "h" {
			heads++
		}
	}
	if heads >= len(calls)-heads {
		return "t"
	}
	return "h"
}

func playMatchingPennies(ask func(string) (string, bool), say func(string)) {
	var calls []string
	you, engine := 0, 0
	say("Call h or t. ? for a hint, q quits.")
	for round := 1; round <= pennyRounds; {
		line, ok := readAnswer(ask, fmt.Sprintf("Round %d (h or t): ", round))
		if !ok {
			say("You left the game.")
			return
		}
		if line == "?" {
			say("Hint: the engine shows the opposite of your most common call, so calling the less common one wins " +
				"(tails, when tied). Mix your calls to stay unpredictable.")
			continue
		}
		if line != "h" && line != "t" {
			say("Enter h or t.")
			continue
		}
		coin := pennyEngineCoin(calls)
		calls = append(calls, line)
		var result string
		if line == coin {
			you++
			result = "You win the round."
		} else {
			engine++
			result = "The engine wins the round."
		}
		say(fmt.Sprintf("You called %s, the engine showed %s. %s", line, coin, result))
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

// cmdEngine lists the engine games, or plays one.
func cmdEngine(args []string, catalog []Game) error {
	games, err := loadEngineGames()
	if err != nil {
		return err
	}
	if len(args) == 0 {
		fmt.Println()
		for _, g := range games {
			fmt.Println(bold(g.ID) + strings.Repeat(" ", max(22-len(g.ID), 0)) + g.Name +
				strings.Repeat(" ", max(46-len(g.Name), 0)) + dim(g.Summary))
		}
		fmt.Println(dim("\nRun 'engine <id>' to play one, e.g. 'engine nim'."))
		return nil
	}
	game, err := findEngineGame(games, strings.Join(args, " "))
	if err != nil {
		return err
	}
	playEngine(game, catalog, readInput, func(text string) { fmt.Println(text) })
	return nil
}

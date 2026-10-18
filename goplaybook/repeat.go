package main

import (
	"errors"
	"fmt"
	"strconv"
	"strings"
	"time"
)

// repeatOpponents are the bot rules a repeated game can be played against.
var repeatOpponents = []string{"tit-for-tat", "grim", "pattern", "learner", "wsls", "random"}

const maxRepeatRounds = 50

var repeatDescriptions = map[string]string{
	"tit-for-tat": "The bot copies your previous move. Exploiting it for one round costs you the next.",
	"grim":        "The bot cooperates (plays its first column) until you leave your first row once, then defects for good.",
	"pattern":     "The bot cycles through its options in a fixed order. The cycle is learnable from memory.",
	"learner":     "The bot tracks which row you pick most often and answers with its best reply to it. A fixed habit is punished; varying your choices keeps it guessing.",
	"wsls":        "The bot keeps its last choice while it does well and switches when it does badly. Find the moves that keep it satisfied.",
	"random":      "The bot picks at random. No pattern to learn, so the best plan is the one with the highest average.",
}

// lcg is the same small generator as the Python version, so the same seed gives the same run.
type lcg struct{ state int64 }

func newLCG(seed int64) *lcg { return &lcg{state: seed & 0x7FFFFFFF} }

func (g *lcg) nextBelow(n int) int {
	g.state = (g.state*1103515245 + 12345) & 0x7FFFFFFF
	return int(g.state % int64(n))
}

// repeatRound is one round: your row, the bot's column, and both payoffs.
type repeatRound struct {
	row, col, mine, theirs int
}

// theirPayoff is the bot's payoff for a cell.
func theirPayoff(m GameMatrix, row, col int) int {
	return m.Payoffs[row][col][1]
}

// bestReply is the column that pays the bot most when you play row. Ties go to the lowest column.
func bestReply(m GameMatrix, row int) int {
	best := 0
	for c := range m.Cols {
		if theirPayoff(m, row, c) > theirPayoff(m, row, best) {
			best = c
		}
	}
	return best
}

// opponentColumn is the column the bot plays this round, from the rounds so far.
func opponentColumn(name string, m GameMatrix, history []repeatRound, rng *lcg) (int, error) {
	cols := len(m.Cols)
	switch name {
	case "tit-for-tat":
		if len(history) == 0 {
			return 0, nil
		}
		return history[len(history)-1].row % cols, nil
	case "grim":
		for _, r := range history {
			if r.row != 0 {
				return cols - 1, nil
			}
		}
		return 0, nil
	case "pattern":
		return len(history) % cols, nil
	case "learner":
		if len(history) == 0 {
			return 0, nil
		}
		counts := make([]int, len(m.Rows))
		for _, r := range history {
			counts[r.row]++
		}
		favourite := 0
		for r := range counts {
			if counts[r] > counts[favourite] {
				favourite = r
			}
		}
		return bestReply(m, favourite), nil
	case "wsls":
		if len(history) == 0 {
			return 0, nil
		}
		total, n := 0, 0
		for r := range m.Rows {
			for c := range m.Cols {
				total += theirPayoff(m, r, c)
				n++
			}
		}
		aspiration := floorDiv(total, n)
		last := history[len(history)-1]
		if theirPayoff(m, last.row, last.col) >= aspiration {
			return last.col, nil
		}
		return (last.col + 1) % cols, nil
	case "random":
		return rng.nextBelow(cols), nil
	}
	return 0, fmt.Errorf("unknown opponent '%s'", name)
}

// floorDiv divides and rounds toward minus infinity, as Python's // does.
func floorDiv(a, b int) int {
	q := a / b
	if (a%b != 0) && ((a < 0) != (b < 0)) {
		q--
	}
	return q
}

// outcomeForLog counts a repeated run in your records: a win if you matched the best fixed plan,
// a draw if you reached 80% of it, otherwise a loss.
func outcomeForLog(total, bestTotal int) string {
	if total >= bestTotal {
		return "win"
	}
	if bestTotal > 0 && total*5 >= bestTotal*4 {
		return "draw"
	}
	return "loss"
}

// bestFixedPlan returns the row that scores most when played every round against this bot, and its total.
func bestFixedPlan(m GameMatrix, rounds int, opponent string, seed int64) (int, int, error) {
	bestRow, bestTotal := 0, 0
	for row := range m.Rows {
		rng := newLCG(seed)
		var history []repeatRound
		total := 0
		for i := 0; i < rounds; i++ {
			col, err := opponentColumn(opponent, m, history, rng)
			if err != nil {
				return 0, 0, err
			}
			mine, theirs := m.Payoffs[row][col][0], m.Payoffs[row][col][1]
			history = append(history, repeatRound{row, col, mine, theirs})
			total += mine
		}
		if row == 0 || total > bestTotal {
			bestRow, bestTotal = row, total
		}
	}
	return bestRow, bestTotal, nil
}

// cmdRepeat plays a payoff matrix for a number of rounds against a bot that remembers the game.
func cmdRepeat(args []string, games []Game) error {
	var rounds = 10
	opponent := "tit-for-tat"
	seed := int64(1)
	formats := ""
	logResult := false
	var pos []string
	for i := 0; i < len(args); i++ {
		switch {
		case args[i] == "--rounds" && i+1 < len(args):
			n, err := strconv.Atoi(args[i+1])
			if err != nil {
				return fmt.Errorf("--rounds expects a whole number")
			}
			rounds = n
			i++
		case args[i] == "--opponent" && i+1 < len(args):
			opponent = args[i+1]
			i++
		case args[i] == "--formats" && i+1 < len(args):
			formats = args[i+1]
			i++
		case args[i] == "--log":
			logResult = true
		case args[i] == "--seed" && i+1 < len(args):
			n, err := strconv.ParseInt(args[i+1], 10, 64)
			if err != nil {
				return fmt.Errorf("--seed expects a whole number")
			}
			seed = n
			i++
		default:
			pos = append(pos, args[i])
		}
	}
	if len(pos) == 0 {
		return errors.New("usage: repeat <game> [--rounds N] [--opponent tit-for-tat|grim|pattern|random] [--seed N]")
	}
	if rounds < 1 || rounds > maxRepeatRounds {
		return fmt.Errorf("rounds must be from 1 to %d", maxRepeatRounds)
	}
	if !contains(repeatOpponents, opponent) {
		return fmt.Errorf("unknown opponent '%s'. Use one of: %s", opponent, strings.Join(repeatOpponents, ", "))
	}
	game, err := FindGame(games, strings.Join(pos, " "))
	if err != nil {
		return err
	}
	if game.Matrix == nil {
		return fmt.Errorf("%s has no payoff table yet, so it cannot be repeated.", game.Name)
	}
	m := *game.Matrix
	showRows, showCols := m.Rows, m.Cols

	rng := newLCG(seed)
	var history []repeatRound
	fmt.Println("\n" + bold(game.Name) + dim(fmt.Sprintf("  against a %s bot, %d round(s)", opponent, rounds)))
	fmt.Println(dim(repeatDescriptions[opponent]))
	for number := 1; number <= rounds; number++ {
		fmt.Println("\n" + bold(fmt.Sprintf("Round %d of %d. Choose your row:", number, rounds)))
		for index, label := range showRows {
			fmt.Printf("  %d) %s\n", index+1, label)
		}
		start := len(history) - 3
		if start < 0 {
			start = 0
		}
		for k := start; k < len(history); k++ {
			r := history[k]
			fmt.Println(dim(fmt.Sprintf("  round %d: you %s, bot %s (you %d, bot %d)", k+1, showRows[r.row], showCols[r.col], r.mine, r.theirs)))
		}
		row := askRow(len(m.Rows))
		col, err := opponentColumn(opponent, m, history, rng)
		if err != nil {
			return err
		}
		mine, theirs := m.Payoffs[row][col][0], m.Payoffs[row][col][1]
		history = append(history, repeatRound{row, col, mine, theirs})
		fmt.Println(dim(fmt.Sprintf("  round %d: you %s, bot %s. You get %d, the bot gets %d.", number, showRows[row], showCols[col], mine, theirs)))
	}
	total := 0
	for _, r := range history {
		total += r.mine
	}
	bestRow, bestTotal, err := bestFixedPlan(m, rounds, opponent, seed)
	if err != nil {
		return err
	}
	if formats != "" {
		if _, err := parseFormats(formats); err != nil {
			return err
		}
		folder, written, err := writeRepeat(*game, opponent, rounds, seed, history, total, bestRow, bestTotal, PlaybookHome(), time.Now())
		if err != nil {
			return err
		}
		fmt.Println(dim("Exported to " + folder + ": " + strings.Join(written, ", ")))
	}
	if logResult {
		result := outcomeForLog(total, bestTotal)
		note := fmt.Sprintf("repeated %d rounds vs %s, total %d", rounds, opponent, total)
		if _, err := LogOutcome(game.ID, result, note, 0); err != nil {
			return err
		}
		fmt.Println(dim(fmt.Sprintf("Logged as %s in your records (total %d, best fixed plan %d).", result, total, bestTotal)))
	}
	fmt.Println("\n" + heading("Result"))
	fmt.Printf("  Your total: %d over %d round(s), an average of %.2f per round.\n", total, rounds, float64(total)/float64(rounds))
	fmt.Printf("  Best always-the-same plan against this bot: always %s, total %d.\n", showRows[bestRow], bestTotal)
	if gap := bestTotal - total; gap > 0 {
		fmt.Println(dim(fmt.Sprintf("  You scored %d less than that plan. Look for the bot's pattern in the rounds above.", gap)))
	} else {
		fmt.Println(dim("  You matched or beat the best fixed plan."))
	}
	return nil
}

// askRow reads your row choice, and asks again until the answer is a valid number.
func askRow(n int) int {
	for {
		answer := strings.TrimSpace(promptLine("> "))
		if v, err := strconv.Atoi(answer); err == nil && v >= 1 && v <= n {
			return v - 1
		}
		fmt.Println(red(fmt.Sprintf("  choose a number from 1 to %d", n)))
	}
}

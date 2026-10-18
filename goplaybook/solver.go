package main

import (
	"fmt"
	"math/big"
	"sort"
	"strings"
)

// Cell is one payoff pair: (row player's payoff, column player's payoff).
type Cell struct {
	Row, Col *big.Rat
}

// Matrix is a payoff table indexed [row][col].
type Matrix [][]Cell

// ParseMatrix reads 'a,b c,d; e,f g,h' into exact rationals.
func ParseMatrix(text string) (Matrix, error) {
	var matrix Matrix
	for _, chunk := range strings.Split(text, ";") {
		fields := strings.Fields(chunk)
		if len(fields) == 0 {
			continue
		}
		var row []Cell
		for _, field := range fields {
			parts := strings.Split(field, ",")
			if len(parts) != 2 {
				return nil, fmt.Errorf("cell '%s' must look like yours,theirs, e.g. 3,5", field)
			}
			a, ok1 := new(big.Rat).SetString(parts[0])
			b, ok2 := new(big.Rat).SetString(parts[1])
			if !ok1 || !ok2 {
				return nil, fmt.Errorf("cell '%s' has a value that is not a number", field)
			}
			row = append(row, Cell{a, b})
		}
		matrix = append(matrix, row)
	}
	if len(matrix) == 0 {
		return nil, fmt.Errorf("the payoff matrix is empty")
	}
	for _, row := range matrix {
		if len(row) != len(matrix[0]) {
			return nil, fmt.Errorf("every row needs the same number of cells")
		}
	}
	return matrix, nil
}

// Elimination records a strategy removed by dominance. Player is "row" or "col".
type Elimination struct {
	Player string
	Index  int
}

// Analysis is the result of analysing a matrix.
type Analysis struct {
	Eliminated    []Elimination
	SurvivingRows []int
	SurvivingCols []int
	Equilibria    [][2]int
	RowMaximin    *big.Rat
	RowMaximinIdx []int
	ColMaximin    *big.Rat
	ColMaximinIdx []int
	Mixed         *[2]*big.Rat // p = row's first action, q = column's first action
	ConstantSum   *big.Rat
}

func cmpRat(a, b *big.Rat) int { return a.Cmp(b) }

// Analyse runs dominance elimination, pure equilibrium search, maximin, and 2x2 mixed equilibrium.
func Analyse(m Matrix) Analysis {
	rows, cols := len(m), len(m[0])
	aliveRows := map[int]bool{}
	aliveCols := map[int]bool{}
	for i := 0; i < rows; i++ {
		aliveRows[i] = true
	}
	for j := 0; j < cols; j++ {
		aliveCols[j] = true
	}
	var res Analysis

	// Iterated elimination of strictly dominated strategies.
	for changed := true; changed; {
		changed = false
		for i := 0; i < rows; i++ {
			if !aliveRows[i] {
				continue
			}
			for k := 0; k < rows; k++ {
				if k == i || !aliveRows[k] {
					continue
				}
				if dominatesRow(m, k, i, aliveCols) {
					delete(aliveRows, i)
					res.Eliminated = append(res.Eliminated, Elimination{"row", i})
					changed = true
					break
				}
			}
		}
		for j := 0; j < cols; j++ {
			if !aliveCols[j] {
				continue
			}
			for k := 0; k < cols; k++ {
				if k == j || !aliveCols[k] {
					continue
				}
				if dominatesCol(m, k, j, aliveRows) {
					delete(aliveCols, j)
					res.Eliminated = append(res.Eliminated, Elimination{"col", j})
					changed = true
					break
				}
			}
		}
	}
	res.SurvivingRows = sortedKeys(aliveRows)
	res.SurvivingCols = sortedKeys(aliveCols)

	// Pure Nash equilibria: no player gains by deviating alone.
	for i := 0; i < rows; i++ {
		for j := 0; j < cols; j++ {
			rowBest, colBest := true, true
			for k := 0; k < rows; k++ {
				if cmpRat(m[k][j].Row, m[i][j].Row) > 0 {
					rowBest = false
				}
			}
			for l := 0; l < cols; l++ {
				if cmpRat(m[i][l].Col, m[i][j].Col) > 0 {
					colBest = false
				}
			}
			if rowBest && colBest {
				res.Equilibria = append(res.Equilibria, [2]int{i, j})
			}
		}
	}

	// Maximin: the best guaranteed floor each side can secure with a pure action.
	rowFloor := make([]*big.Rat, rows)
	for i := 0; i < rows; i++ {
		rowFloor[i] = m[i][0].Row
		for j := 1; j < cols; j++ {
			if cmpRat(m[i][j].Row, rowFloor[i]) < 0 {
				rowFloor[i] = m[i][j].Row
			}
		}
	}
	colFloor := make([]*big.Rat, cols)
	for j := 0; j < cols; j++ {
		colFloor[j] = m[0][j].Col
		for i := 1; i < rows; i++ {
			if cmpRat(m[i][j].Col, colFloor[j]) < 0 {
				colFloor[j] = m[i][j].Col
			}
		}
	}
	res.RowMaximin = rowFloor[0]
	for _, v := range rowFloor {
		if cmpRat(v, res.RowMaximin) > 0 {
			res.RowMaximin = v
		}
	}
	for i, v := range rowFloor {
		if cmpRat(v, res.RowMaximin) == 0 {
			res.RowMaximinIdx = append(res.RowMaximinIdx, i)
		}
	}
	res.ColMaximin = colFloor[0]
	for _, v := range colFloor {
		if cmpRat(v, res.ColMaximin) > 0 {
			res.ColMaximin = v
		}
	}
	for j, v := range colFloor {
		if cmpRat(v, res.ColMaximin) == 0 {
			res.ColMaximinIdx = append(res.ColMaximinIdx, j)
		}
	}

	if rows == 2 && cols == 2 {
		res.Mixed = mixed2x2(m)
	}
	res.ConstantSum = constantSum(m)
	return res
}

// dominatesRow reports whether row k strictly beats row i on every alive column.
func dominatesRow(m Matrix, k, i int, aliveCols map[int]bool) bool {
	for j := range aliveCols {
		if cmpRat(m[k][j].Row, m[i][j].Row) <= 0 {
			return false
		}
	}
	return true
}

// dominatesCol reports whether column k strictly beats column j on every alive row.
func dominatesCol(m Matrix, k, j int, aliveRows map[int]bool) bool {
	for i := range aliveRows {
		if cmpRat(m[i][k].Col, m[i][j].Col) <= 0 {
			return false
		}
	}
	return true
}

// mixed2x2 returns the interior mixed equilibrium, or nil if there is none.
func mixed2x2(m Matrix) *[2]*big.Rat {
	a00, b00 := m[0][0].Row, m[0][0].Col
	a01, b01 := m[0][1].Row, m[0][1].Col
	a10, b10 := m[1][0].Row, m[1][0].Col
	a11, b11 := m[1][1].Row, m[1][1].Col

	rowDen := new(big.Rat).Add(new(big.Rat).Sub(a00, a10), new(big.Rat).Sub(a11, a01))
	colDen := new(big.Rat).Add(new(big.Rat).Sub(b00, b01), new(big.Rat).Sub(b11, b10))
	if rowDen.Sign() == 0 || colDen.Sign() == 0 {
		return nil
	}
	// p = (b11 - b10) / colDen ; q = (a11 - a01) / rowDen
	p := new(big.Rat).Quo(new(big.Rat).Sub(b11, b10), colDen)
	q := new(big.Rat).Quo(new(big.Rat).Sub(a11, a01), rowDen)
	one := big.NewRat(1, 1)
	if p.Sign() <= 0 || cmpRat(p, one) >= 0 || q.Sign() <= 0 || cmpRat(q, one) >= 0 {
		return nil
	}
	return &[2]*big.Rat{p, q}
}

func constantSum(m Matrix) *big.Rat {
	var total *big.Rat
	for _, row := range m {
		for _, c := range row {
			s := new(big.Rat).Add(c.Row, c.Col)
			if total == nil {
				total = s
			} else if cmpRat(total, s) != 0 {
				return nil
			}
		}
	}
	return total
}

func sortedKeys(set map[int]bool) []int {
	out := make([]int, 0, len(set))
	for k := range set {
		out = append(out, k)
	}
	sort.Ints(out)
	return out
}

func ratFloat(r *big.Rat) float64 {
	f, _ := r.Float64()
	return f
}

// solveRecord is the solution as data. Fields are in alphabetical order, as the Python version writes them.
type solveRecord struct {
	Cols          []string                        `json:"cols"`
	Eliminated    []map[string]string             `json:"eliminated"`
	Equilibria    []map[string]map[string]float64 `json:"equilibria"`
	Matrix        [][][2]float64                  `json:"matrix"`
	MaximinCol    maximinRecord                   `json:"maximin_col"`
	MaximinRow    maximinRecord                   `json:"maximin_row"`
	Rows          []string                        `json:"rows"`
	SurvivingCols []string                        `json:"surviving_cols"`
	SurvivingRows []string                        `json:"surviving_rows"`
}

type maximinRecord struct {
	Strategies []string `json:"strategies"`
	Value      float64  `json:"value"`
}

// solveJSON is the solution as data, the same fields the Python version prints with solve --json.
func solveJSON(m Matrix, rows, cols []string) solveRecord {
	a := Analyse(m)
	rec := solveRecord{Rows: rows, Cols: cols, Eliminated: []map[string]string{}, SurvivingRows: []string{}, SurvivingCols: []string{}}
	for _, row := range m {
		var line [][2]float64
		for _, cell := range row {
			line = append(line, [2]float64{ratFloat(cell.Row), ratFloat(cell.Col)})
		}
		rec.Matrix = append(rec.Matrix, line)
	}
	for _, e := range a.Eliminated {
		name := cols
		if e.Player == "row" {
			name = rows
		}
		rec.Eliminated = append(rec.Eliminated, map[string]string{"player": e.Player, "strategy": name[e.Index]})
	}
	for _, i := range a.SurvivingRows {
		rec.SurvivingRows = append(rec.SurvivingRows, rows[i])
	}
	for _, j := range a.SurvivingCols {
		rec.SurvivingCols = append(rec.SurvivingCols, cols[j])
	}
	rec.MaximinRow = maximinRecord{Strategies: pickNames(rows, a.RowMaximinIdx), Value: ratFloat(a.RowMaximin)}
	rec.MaximinCol = maximinRecord{Strategies: pickNames(cols, a.ColMaximinIdx), Value: ratFloat(a.ColMaximin)}
	if len(m) <= 4 && len(m[0]) <= 4 {
		rec.Equilibria = []map[string]map[string]float64{}
		for _, e := range SupportEquilibria(m) {
			you := map[string]float64{}
			for i, x := range e.Row {
				if x.Sign() != 0 {
					you[rows[i]] = ratFloat(x)
				}
			}
			them := map[string]float64{}
			for j, x := range e.Col {
				if x.Sign() != 0 {
					them[cols[j]] = ratFloat(x)
				}
			}
			rec.Equilibria = append(rec.Equilibria, map[string]map[string]float64{"you": you, "them": them})
		}
	}
	return rec
}

func pickNames(names []string, idx []int) []string {
	out := []string{}
	for _, i := range idx {
		out = append(out, names[i])
	}
	return out
}

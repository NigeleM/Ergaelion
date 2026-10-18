package main

import "math/big"

// Support enumeration: finds every Nash equilibrium of a game up to 4x4, in exact rational arithmetic.
// For each pair of equally sized action supports, it solves the indifference conditions and checks
// that no action outside the support does better.

// solveExact solves a square linear system exactly. It returns nil if the system is singular.
func solveExact(m [][]*big.Rat, rhs []*big.Rat) []*big.Rat {
	n := len(rhs)
	a := make([][]*big.Rat, n)
	for i := range m {
		a[i] = append(append([]*big.Rat{}, m[i]...), new(big.Rat).Set(rhs[i]))
	}
	for col := 0; col < n; col++ {
		pivot := -1
		for r := col; r < n; r++ {
			if a[r][col].Sign() != 0 {
				pivot = r
				break
			}
		}
		if pivot < 0 {
			return nil
		}
		a[col], a[pivot] = a[pivot], a[col]
		for r := 0; r < n; r++ {
			if r == col || a[r][col].Sign() == 0 {
				continue
			}
			factor := new(big.Rat).Quo(a[r][col], a[col][col])
			for k := col; k <= n; k++ {
				a[r][k] = new(big.Rat).Sub(a[r][k], new(big.Rat).Mul(factor, a[col][k]))
			}
		}
	}
	out := make([]*big.Rat, n)
	for i := 0; i < n; i++ {
		out[i] = new(big.Rat).Quo(a[i][n], a[i][i])
	}
	return out
}

// indifferentMix finds a mix over `own` that makes every action in `others` earn the same value.
// payoff[own][other] is the payoff to the player indifferent over `others`. It returns the mix and value.
func indifferentMix(payoff [][]*big.Rat, own, others []int) ([]*big.Rat, *big.Rat) {
	k := len(own)
	var rows [][]*big.Rat
	var rhs []*big.Rat
	for _, j := range others {
		row := make([]*big.Rat, k+1)
		for idx, i := range own {
			row[idx] = payoff[i][j]
		}
		row[k] = big.NewRat(-1, 1)
		rows = append(rows, row)
		rhs = append(rhs, big.NewRat(0, 1))
	}
	sum := make([]*big.Rat, k+1)
	for idx := 0; idx < k; idx++ {
		sum[idx] = big.NewRat(1, 1)
	}
	sum[k] = big.NewRat(0, 1)
	rows = append(rows, sum)
	rhs = append(rhs, big.NewRat(1, 1))
	solution := solveExact(rows, rhs)
	if solution == nil {
		return nil, nil
	}
	return solution[:k], solution[k]
}

// Equilibrium is one Nash equilibrium: the mix each player uses over all their actions.
type Equilibrium struct {
	Row []*big.Rat
	Col []*big.Rat
}

// SupportEquilibria returns every equilibrium of a game up to 4x4.
func SupportEquilibria(m Matrix) []Equilibrium {
	rows, cols := len(m), len(m[0])
	a := make([][]*big.Rat, rows)
	b := make([][]*big.Rat, rows)
	for i := range m {
		a[i] = make([]*big.Rat, cols)
		b[i] = make([]*big.Rat, cols)
		for j := range m[i] {
			a[i][j] = m[i][j].Row
			b[i][j] = m[i][j].Col
		}
	}
	bt := make([][]*big.Rat, cols)
	at := make([][]*big.Rat, cols)
	for j := 0; j < cols; j++ {
		bt[j] = make([]*big.Rat, rows)
		at[j] = make([]*big.Rat, rows)
		for i := 0; i < rows; i++ {
			bt[j][i] = b[i][j]
			at[j][i] = a[i][j]
		}
	}
	var found []Equilibrium
	minSize := rows
	if cols < minSize {
		minSize = cols
	}
	for size := 1; size <= minSize; size++ {
		for _, rs := range subsets(rows, size) {
			for _, cs := range subsets(cols, size) {
				q, u := indifferentMix(at, cs, rs) // column mix making the row player indifferent
				p, v := indifferentMix(b, rs, cs)  // row mix making the column player indifferent
				if q == nil || p == nil || anyNonPositive(q) || anyNonPositive(p) {
					continue
				}
				rowMix := make([]*big.Rat, rows)
				colMix := make([]*big.Rat, cols)
				for i := range rowMix {
					rowMix[i] = big.NewRat(0, 1)
				}
				for j := range colMix {
					colMix[j] = big.NewRat(0, 1)
				}
				for idx, i := range rs {
					rowMix[i] = p[idx]
				}
				for idx, j := range cs {
					colMix[j] = q[idx]
				}
				if maxRowValue(a, colMix).Cmp(u) != 0 || maxColValue(b, rowMix).Cmp(v) != 0 {
					continue
				}
				if !containsEquilibrium(found, rowMix, colMix) {
					found = append(found, Equilibrium{Row: rowMix, Col: colMix})
				}
			}
		}
	}
	return found
}

func subsets(n, size int) [][]int {
	var out [][]int
	var pick func(start int, cur []int)
	pick = func(start int, cur []int) {
		if len(cur) == size {
			out = append(out, append([]int{}, cur...))
			return
		}
		for i := start; i < n; i++ {
			pick(i+1, append(cur, i))
		}
	}
	pick(0, nil)
	return out
}

func anyNonPositive(xs []*big.Rat) bool {
	for _, x := range xs {
		if x.Sign() <= 0 {
			return true
		}
	}
	return false
}

// maxRowValue is the best payoff any row earns against the column mix.
func maxRowValue(a [][]*big.Rat, colMix []*big.Rat) *big.Rat {
	best := new(big.Rat)
	for i := range a {
		total := new(big.Rat)
		for j := range colMix {
			total.Add(total, new(big.Rat).Mul(a[i][j], colMix[j]))
		}
		if i == 0 || total.Cmp(best) > 0 {
			best = total
		}
	}
	return best
}

// maxColValue is the best payoff any column earns against the row mix.
func maxColValue(b [][]*big.Rat, rowMix []*big.Rat) *big.Rat {
	best := new(big.Rat)
	cols := len(b[0])
	for j := 0; j < cols; j++ {
		total := new(big.Rat)
		for i := range rowMix {
			total.Add(total, new(big.Rat).Mul(b[i][j], rowMix[i]))
		}
		if j == 0 || total.Cmp(best) > 0 {
			best = total
		}
	}
	return best
}

func containsEquilibrium(list []Equilibrium, row, col []*big.Rat) bool {
	for _, e := range list {
		if ratsEqual(e.Row, row) && ratsEqual(e.Col, col) {
			return true
		}
	}
	return false
}

func ratsEqual(a, b []*big.Rat) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i].Cmp(b[i]) != 0 {
			return false
		}
	}
	return true
}

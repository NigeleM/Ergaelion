package main

import (
	"fmt"
	"html"
	"math"
	"sort"
	"strconv"
	"strings"
)

// SVG charts, maps and decision trees, with no external dependencies, the same five charts
// as the Python version: families, traits, map, sim and records.

var palette = []string{"#d97706", "#2563eb", "#059669", "#7c3aed", "#db2777", "#0891b2", "#65a30d", "#dc2626", "#4b5563"}
var traitColours = []string{"#2563eb", "#f59e0b", "#10b981", "#8b5cf6", "#ef4444", "#14b8a6"}

func svgDoc(width, height int, title string, body []string) string {
	return fmt.Sprintf(`<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="-apple-system, Helvetica, Arial, sans-serif"><title>%s</title><rect width="100%%" height="100%%" fill="#ffffff"/>%s</svg>`+"\n",
		width, height, width, height, html.EscapeString(title), strings.Join(body, ""))
}

func esc(s string) string { return html.EscapeString(s) }

func familyGameCount(f Family) int {
	seen := map[string]bool{}
	for _, sd := range f.Subdomains {
		for _, id := range sd.Games {
			seen[id] = true
		}
	}
	return len(seen)
}

// FamiliesChart draws games per family as bars.
func FamiliesChart(families []Family) string {
	type row struct {
		name string
		n    int
	}
	var rows []row
	for _, f := range families {
		rows = append(rows, row{f.Family, familyGameCount(f)})
	}
	sort.SliceStable(rows, func(a, b int) bool { return rows[a].n > rows[b].n })
	width, left := 820, 300
	height := 60 + len(rows)*26
	topN := 1
	for _, r := range rows {
		if r.n > topN {
			topN = r.n
		}
	}
	body := []string{`<text x="20" y="28" font-size="16" font-weight="600">Games per family</text>`}
	for i, r := range rows {
		y := 44 + i*26
		w := float64(width-left-90) * float64(r.n) / float64(topN)
		body = append(body, fmt.Sprintf(`<text x="%d" y="%d" font-size="12" text-anchor="end">%s</text>`, left-8, y+13, esc(r.name)))
		body = append(body, fmt.Sprintf(`<rect x="%d" y="%d" width="%.1f" height="18" rx="3" fill="%s"/>`, left, y, w, palette[i%len(palette)]))
		body = append(body, fmt.Sprintf(`<text x="%s" y="%d" font-size="12">%d</text>`, coord(float64(left)+w+6), y+13, r.n))
	}
	return svgDoc(width, height, "Games per family", body)
}

// TraitsHeatmap draws every game against every trait.
func TraitsHeatmap(games []Game) string {
	const cellW, cellH, left, top = 96, 11, 220, 60
	width := left + cellW*len(Traits) + 20
	height := top + cellH*len(games) + 30
	body := []string{`<text x="20" y="28" font-size="16" font-weight="600">Games by trait</text>`}
	for c, key := range Traits {
		body = append(body, fmt.Sprintf(`<text x="%d" y="%d" font-size="11" text-anchor="middle">%s</text>`, left+c*cellW+cellW/2, top-10, key))
	}
	for r, g := range games {
		y := top + r*cellH
		name := g.Name
		if len(name) > 34 {
			name = name[:34]
		}
		body = append(body, fmt.Sprintf(`<text x="%d" y="%d" font-size="8" text-anchor="end">%s</text>`, left-6, y+cellH-2, esc(name)))
		for c, key := range Traits {
			value, ok := g.Traits[key]
			if !ok {
				continue
			}
			colour := traitColours[indexOf(traitValues[key], value)%len(traitColours)]
			body = append(body, fmt.Sprintf(`<rect x="%d" y="%d" width="%d" height="%d" fill="%s"><title>%s: %s = %s</title></rect>`,
				left+c*cellW, y, cellW-2, cellH-1, colour, esc(g.Name), key, value))
		}
	}
	body = append(body, fmt.Sprintf(`<text x="%d" y="%d" font-size="10" fill="#6b7280">Colours follow each trait's value order; hover a cell for its value.</text>`, left, height-14))
	return svgDoc(width, height, "Games by trait", body)
}

func indexOf(list []string, v string) int {
	for i, item := range list {
		if item == v {
			return i
		}
	}
	return 0
}

// wrapLabel splits a family name over up to three lines of about 14 characters.
func wrapLabel(text string) []string {
	var lines []string
	line := ""
	for _, word := range strings.Fields(text) {
		if line != "" && len(line)+1+len(word) > 14 {
			lines = append(lines, line)
			line = word
		} else if line == "" {
			line = word
		} else {
			line += " " + word
		}
	}
	if line != "" {
		lines = append(lines, line)
	}
	if len(lines) > 3 {
		lines = lines[:3]
	}
	return lines
}

// FamilyMap draws the families and their sub-domains as a radial map.
// coord writes a coordinate as a whole number when it is one, as the Python version does.
func coord(v float64) string {
	if v == math.Trunc(v) {
		return strconv.Itoa(int(v))
	}
	return fmt.Sprintf("%.1f", v)
}

func FamilyMap(families []Family) string {
	const size = 1200
	cx, cy := float64(size)/2, float64(size)/2
	familyR, subR := 300.0, 470.0
	var spokes, body, centre []string
	body = append(body, `<text x="20" y="28" font-size="16" font-weight="600">Map of families and sub-domains</text>`)
	n := len(families)
	for i, f := range families {
		angle := 2*math.Pi*float64(i)/float64(n) - math.Pi/2
		fx, fy := cx+familyR*math.Cos(angle), cy+familyR*math.Sin(angle)
		colour := palette[i%len(palette)]
		spokes = append(spokes, fmt.Sprintf(`<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2"/>`, cx, cy, fx, fy, colour))
		body = append(body, fmt.Sprintf(`<circle cx="%.1f" cy="%.1f" r="48" fill="%s"/>`, fx, fy, colour))
		lines := wrapLabel(f.Family)
		top := fy - float64(len(lines)+1)*6
		for k, line := range lines {
			body = append(body, fmt.Sprintf(`<text x="%.1f" y="%.1f" font-size="10" fill="#ffffff" text-anchor="middle">%s</text>`, fx, top+float64(k)*12+10, esc(line)))
		}
		body = append(body, fmt.Sprintf(`<text x="%.1f" y="%.1f" font-size="10" fill="#ffffff" text-anchor="middle">%d games</text>`, fx, top+float64(len(lines))*12+14, familyGameCount(f)))
		spread := 40 * math.Pi / 180
		for j, sd := range f.Subdomains {
			frac := 0.5
			if len(f.Subdomains) > 1 {
				frac = float64(j) / float64(len(f.Subdomains)-1)
			}
			sangle := angle - spread/2 + spread*frac
			sx, sy := cx+subR*math.Cos(sangle), cy+subR*math.Sin(sangle)
			spokes = append(spokes, fmt.Sprintf(`<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-opacity="0.5"/>`, fx, fy, sx, sy, colour))
			anchor := "start"
			if math.Cos(sangle) < 0 {
				anchor = "end"
			}
			label := fmt.Sprintf("%s (%d)", sd.Name, len(sd.Games))
			body = append(body, fmt.Sprintf(`<text x="%.1f" y="%.1f" font-size="9" fill="#374151" text-anchor="%s">%s</text>`, sx, sy, anchor, esc(label)))
		}
	}
	centre = append(centre, fmt.Sprintf(`<circle cx="%s" cy="%s" r="82" fill="#111827"/>`, coord(cx), coord(cy)))
	centre = append(centre, fmt.Sprintf(`<text x="%s" y="%s" font-size="13" fill="#ffffff" text-anchor="middle">Game theory</text>`, coord(cx), coord(cy-4)))
	centre = append(centre, fmt.Sprintf(`<text x="%s" y="%s" font-size="13" fill="#ffffff" text-anchor="middle">playbook</text>`, coord(cx), coord(cy+12)))
	return svgDoc(size, size, "Map of families and sub-domains", append(append(spokes, body...), centre...))
}

// mixColour blends two #rrggbb colours; t=0 gives a, t=1 gives b.
func mixColour(a, b string, t float64) string {
	var ca, cb [3]int
	fmt.Sscanf(a, "#%02x%02x%02x", &ca[0], &ca[1], &ca[2])
	fmt.Sscanf(b, "#%02x%02x%02x", &cb[0], &cb[1], &cb[2])
	out := ""
	for i := 0; i < 3; i++ {
		out += fmt.Sprintf("%02x", int(math.Round(float64(ca[i])+(float64(cb[i])-float64(ca[i]))*t)))
	}
	return "#" + out
}

// planNodes returns the node ids along a plan, with chance resolved by the likeliest branch.
func planNodes(sim *Simulation, plan map[string]planEntry) map[string]bool {
	seen := map[string]bool{}
	id := sim.Start
	for {
		seen[id] = true
		node := sim.Nodes[id]
		switch node.Type {
		case "end":
			return seen
		case "nature":
			best := node.Branches[0]
			for _, b := range node.Branches[1:] {
				if b.P > best.P {
					best = b
				}
			}
			id = best.Next
		default:
			id = node.Options[plan[id].choice].Next
		}
	}
}

// SimTree draws the decision tree of a simulation, with the victory and failure paths marked.
// takenNodes returns the node ids a run passed through, following the labels of its steps.
func takenNodes(sim *Simulation, steps []Step) []string {
	nid := sim.Start
	path := []string{nid}
	for _, step := range steps {
		node := sim.Nodes[nid]
		next := ""
		found := false
		if node.Type == "nature" {
			for _, b := range node.Branches {
				if b.Label == step.Label {
					next, found = b.Next, true
					break
				}
			}
		} else if node.Type == "player" {
			for _, o := range node.Options {
				if o.Label == step.Label {
					next, found = o.Next, true
					break
				}
			}
		}
		if !found {
			break
		}
		nid = next
		path = append(path, nid)
	}
	return path
}

// SimTree draws the decision tree. If taken (the steps of a run) is given, your run is outlined in the accent colour.
func SimTree(sim *Simulation, taken []Step) string {
	colours := outcomeColours()
	accentHex := roleHex("accent", "#f59e0b")
	yourPath := map[string]bool{}
	yourEdges := map[string]bool{}
	if len(taken) > 0 {
		path := takenNodes(sim, taken)
		for i, id := range path {
			yourPath[id] = true
			if i+1 < len(path) {
				yourEdges[id+">"+path[i+1]] = true
			}
		}
	}
	victory := solve(sim, "victory")
	winPath := planNodes(sim, victory)
	failPath := planNodes(sim, solve(sim, "failure"))

	depth := map[string]int{sim.Start: 0}
	order := []string{sim.Start}
	queue := []string{sim.Start}
	for len(queue) > 0 {
		cur := queue[0]
		queue = queue[1:]
		node := sim.Nodes[cur]
		var children []string
		if node.Type == "nature" {
			for _, b := range node.Branches {
				children = append(children, b.Next)
			}
		} else if node.Type == "player" {
			for _, o := range node.Options {
				children = append(children, o.Next)
			}
		}
		for _, child := range children {
			if _, ok := depth[child]; !ok {
				depth[child] = depth[cur] + 1
				order = append(order, child)
				queue = append(queue, child)
			}
		}
	}
	byDepth := map[int][]string{}
	maxDepth, tallest := 0, 0
	for _, id := range order {
		byDepth[depth[id]] = append(byDepth[depth[id]], id)
		if depth[id] > maxDepth {
			maxDepth = depth[id]
		}
	}
	for _, ids := range byDepth {
		if len(ids) > tallest {
			tallest = len(ids)
		}
	}
	const boxW, boxH, gapX, gapY = 210, 58, 160, 18
	width := 40 + (maxDepth+1)*(boxW+gapX)
	height := 120 + tallest*(boxH+gapY)
	pos := map[string][2]int{}
	for d := 0; d <= maxDepth; d++ {
		for i, id := range byDepth[d] {
			pos[id] = [2]int{30 + d*(boxW+gapX), 100 + i*(boxH+gapY)}
		}
	}
	body := []string{
		fmt.Sprintf(`<text x="20" y="28" font-size="16" font-weight="600">%s</text>`, esc(sim.Name)),
		`<text x="20" y="44" font-size="11" fill="#6b7280">Green path: best route to victory. Red dashed: route most likely to fail. Box colour: chance of victory from that point.</text>`,
	}
	if len(yourPath) > 0 {
		body = append(body, fmt.Sprintf(`<text x="20" y="60" font-size="11" fill="%s">Orange outline: the run you played.</text>`, accentHex))
	}
	var edgeLabels []string
	for _, id := range order {
		node := sim.Nodes[id]
		var edges []SimOption
		var labels []string
		if node.Type == "nature" {
			for _, b := range node.Branches {
				edges = append(edges, SimOption{Next: b.Next})
				labels = append(labels, fmt.Sprintf("%s (%.0f%%)", b.Label, b.P*100))
			}
		} else if node.Type == "player" {
			for _, o := range node.Options {
				edges = append(edges, SimOption{Next: o.Next})
				labels = append(labels, o.Label)
			}
		}
		x1, y1 := pos[id][0], pos[id][1]
		for k, e := range edges {
			x2, y2 := pos[e.Next][0], pos[e.Next][1]
			onWin := winPath[id] && winPath[e.Next]
			onFail := failPath[id] && failPath[e.Next]
			stroke, dash, px := colours["draw"], "", 1
			if onWin {
				stroke, px = colours["win"], 3
			} else if onFail {
				stroke, dash, px = colours["loss"], ` stroke-dasharray="6 4"`, 3
			}
			if yourEdges[id+">"+e.Next] {
				stroke, dash, px = accentHex, "", 4
			}
			body = append(body, fmt.Sprintf(`<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="%d"%s/>`,
				x1+boxW, float64(y1)+boxH/2.0, x2, float64(y2)+boxH/2.0, stroke, px, dash))
			label := labels[k]
			if len(label) > 26 {
				label = label[:26]
			}
			edgeLabels = append(edgeLabels, fmt.Sprintf(`<text x="%.0f" y="%.0f" font-size="9" fill="#374151" text-anchor="middle" stroke="#ffffff" stroke-width="4" paint-order="stroke">%s</text>`,
				float64(x1+boxW+x2)/2, float64(y1+y2)/2+boxH/2.0-3, esc(label)))
		}
	}
	for _, id := range order {
		node := sim.Nodes[id]
		x, y := pos[id][0], pos[id][1]
		chance := victory[id].value
		fill := mixColour(colours["loss_light"], colours["win_light"], chance)
		var caption string
		switch node.Type {
		case "end":
			caption = strings.ToUpper(node.Outcome)
			fill = map[string]string{"victory": colours["win_light"], "draw": colours["draw_light"], "failure": colours["loss_light"]}[node.Outcome]
		case "nature":
			caption = "Chance: " + truncateText(node.Prompt, 24)
		default:
			caption = truncateText(node.Prompt, 30)
		}
		outline, outlineW := "#374151", "0.5"
		if yourPath[id] {
			outline, outlineW = accentHex, "2.5"
		}
		body = append(body, fmt.Sprintf(`<rect x="%d" y="%d" width="%d" height="%d" rx="6" fill="%s" stroke="%s" stroke-width="%s"/>`, x, y, boxW, boxH, fill, outline, outlineW))
		body = append(body, fmt.Sprintf(`<text x="%d" y="%d" font-size="10" fill="#111827">%s</text>`, x+8, y+18, esc(caption)))
		if node.Type != "end" {
			body = append(body, fmt.Sprintf(`<text x="%d" y="%d" font-size="9" fill="#374151">victory from here: %.0f%%</text>`, x+8, y+34, chance*100))
		}
	}
	body = append(body, edgeLabels...)
	return svgDoc(width, height, sim.Name+" decision tree", body)
}

func truncateText(s string, n int) string {
	if len(s) <= n {
		return s
	}
	return s[:n]
}

// RecordsChart draws your wins, losses, draws and mixed results per game.
func RecordsChart(counts map[string]map[string]int, names map[string]string) string {
	type row struct {
		id    string
		total int
	}
	var rows []row
	for id, c := range counts {
		t := 0
		for _, n := range c {
			t += n
		}
		rows = append(rows, row{id, t})
	}
	sort.SliceStable(rows, func(a, b int) bool { return rows[a].total > rows[b].total })
	width, left := 820, 300
	height := 60 + len(rows)*28 + 20
	topN := 1
	for _, r := range rows {
		if r.total > topN {
			topN = r.total
		}
	}
	body := []string{`<text x="20" y="28" font-size="16" font-weight="600">Your results by game</text>`}
	colours := outcomeColours()
	for i, r := range rows {
		y := 44 + i*28
		label := names[r.id]
		if label == "" {
			label = r.id
		}
		body = append(body, fmt.Sprintf(`<text x="%d" y="%d" font-size="12" text-anchor="end">%s</text>`, left-8, y+13, esc(label)))
		x := float64(left)
		for _, result := range []string{"win", "loss", "draw", "mixed"} {
			n := counts[r.id][result]
			if n == 0 {
				continue
			}
			w := float64(width-left-90) * float64(n) / float64(topN)
			body = append(body, fmt.Sprintf(`<rect x="%.1f" y="%d" width="%.1f" height="18" fill="%s"><title>%s: %d</title></rect>`, x, y, w, colours[result], result, n))
			x += w
		}
	}
	body = append(body, fmt.Sprintf(`<text x="%d" y="%d" font-size="11" fill="#374151">win, loss, draw and mixed follow your theme (theme command)</text>`, left, 44+len(rows)*28+6))
	return svgDoc(width, height, "Your results by game", body)
}

// PlayRow is one bar of the per-play chart: a label and your results for that play.
type PlayRow struct {
	Label  string
	Counts map[string]int
}

// PlaysChart draws your results for each play you have logged.
func PlaysChart(rows []PlayRow) string {
	width, left := 880, 360
	height := 60 + len(rows)*26 + 20
	topN := 1
	for _, r := range rows {
		total := 0
		for _, n := range r.Counts {
			total += n
		}
		if total > topN {
			topN = total
		}
	}
	body := []string{`<text x="20" y="28" font-size="16" font-weight="600">Your results by play</text>`}
	colours := outcomeColours()
	for i, r := range rows {
		y := 44 + i*26
		body = append(body, fmt.Sprintf(`<text x="%d" y="%d" font-size="11" text-anchor="end">%s</text>`, left-8, y+13, esc(truncateText(r.Label, 58))))
		x := float64(left)
		for _, result := range []string{"win", "loss", "draw", "mixed"} {
			n := r.Counts[result]
			if n == 0 {
				continue
			}
			w := float64(width-left-90) * float64(n) / float64(topN)
			body = append(body, fmt.Sprintf(`<rect x="%.1f" y="%d" width="%.1f" height="18" fill="%s"><title>%s: %d</title></rect>`, x, y, w, colours[result], result, n))
			x += w
		}
	}
	body = append(body, fmt.Sprintf(`<text x="%d" y="%d" font-size="11" fill="#374151">win, loss, draw and mixed follow your theme (theme command)</text>`, left, 44+len(rows)*26+6))
	return svgDoc(width, height, "Your results by play", body)
}

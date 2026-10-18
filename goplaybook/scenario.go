package main

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"
)

// Scenario is a parsed situation: traits, optional domains, and a title.
type Scenario struct {
	Title    string
	Text     string
	Notes    string
	Domains  []string
	Traits   map[string]string
	Evidence map[string]string // matched phrase per trait, filled by Describe only
}

// Keyword rules that turn a sentence into traits. For the same key, later rules
// override earlier ones, so the more specific patterns come last.
// Go's regexp has no lookbehind, so the "imperfect" and "irreversible" exclusions
// are written as a required preceding non-matching character.
type rule struct {
	key, value string
	re         *regexp.Regexp
}

var rules = []rule{
	{"players", "two", regexp.MustCompile(`\b(two|2|duopol\w*|head[- ]to[- ]head|one[- ]on[- ]one|bilateral|between two)\b`)},
	{"players", "many", regexp.MustCompile(`\b(many|several|dozens?|hundreds?|everyone|(?:[3-9]|\d{2,}) (?:players|firms|people|countries|nations|boats|compan\w*|bidders|members|teams|parties))\b`)},
	{"timing", "simultaneous", regexp.MustCompile(`simultaneous\w*|at the same time|sealed|blind|without (?:knowing|seeing)|independent(?:ly)? decid\w*|both (?:choose|decide|pick|move)`)},
	{"timing", "sequential", regexp.MustCompile(`goes first|go first|first mover|moves? first|turns? to|in response|after (?:they|he|she|it|the other)|sequential\w*|leader|follower|escalat\w*|then (?:they|he|she|the other)`)},
	{"interaction", "repeated", regexp.MustCompile(`repeat\w*|again and again|ongoing|every (?:day|week|month|year|season|round)|long[- ]term|recurring|future (?:dealings|rounds|business)|keep (?:dealing|working)|will (?:meet|deal|work) again`)},
	{"interaction", "one-shot", regexp.MustCompile(`one[- ]time|one[- ]shot|single (?:round|encounter|time|deal)|never (?:\w+ ){0,3}again|\bonce\b`)},
	{"information", "imperfect", regexp.MustCompile(`hidden|private information|don'?t know|unknown|imperfect|asymmetric|can'?t (?:see|observe|verify|tell)|secret|bluff\w*|unobservable|not sure|uncertain\w*`)},
	{"information", "perfect", regexp.MustCompile(`(?:^|[^m])perfect information|fully observ\w*|everyone (?:can )?(?:see|knows)|open information`)},
	{"payoff", "mixed", regexp.MustCompile(`cooperat\w*|collaborat\w*|partner\w*|trad(?:e|ing)|both (?:sides|parties|of us) (?:benefit|gain|win)|mutual(?:ly)? (?:benefit|gain)|compet\w*`)},
	{"payoff", "common-interest", regexp.MustCompile(`common (?:interest|goal)|same goal|team ?work|same team|both win together|shared goal`)},
	{"payoff", "zero-sum", regexp.MustCompile(`zero[- ]sum|win[- ]lose|winner takes all|fixed (?:pie|prize)|must lose|battlefield\w*|enemy|opponent wins|one side'?s gain`)},
	{"communication", "yes", regexp.MustCompile(`\btalk\w*|\bchat\w*|messag\w*|communicat\w*|discuss\w*|signal\w*|promis\w*|negotiat\w*|speak`)},
	{"communication", "no", regexp.MustCompile(`no (?:communication|talking|contact)|can'?t (?:talk|communicate|speak)|silent|no way to talk`)},
	{"enforcement", "yes", regexp.MustCompile(`contract\w*|enforc\w*|legal\w*|penalt\w*|court\w*|binding|punish\w*|sanction\w*|regulat\w*|inspect\w*|audit\w*|fines?\b|police`)},
	{"enforcement", "no", regexp.MustCompile(`no (?:contract|enforcement|penalt|rules)|unenforceable|nothing stops|no way to (?:enforce|hold)`)},
	{"commitment", "yes", regexp.MustCompile(`commit\w*|threat\w*|can'?t back down|irreversib\w*|credib\w*|pre-?commit\w*|lock (?:in|ourselves|themselves)|cannot (?:retreat|back out)|no turning back|burn (?:the|our) bridges`)},
	{"commitment", "no", regexp.MustCompile(`no commitment|can (?:always )?change (?:my|our|their) mind|(?:^|[^r])reversible|can backtrack`)},
	{"bargaining", "yes", regexp.MustCompile(`negotiat\w*|bargain\w*|salary|pric\w*|split\w*|divid\w*|haggl\w*|offer\w*|settle\w*|deal\b|share the`)},
}

// DomainWords maps each domain to the words that suggest it. Order is display order.
var DomainNames = []string{"work", "business", "military", "politics", "games", "everyday", "economy", "environment", "government", "society"}

var domainWords = map[string]*regexp.Regexp{
	"work":        regexp.MustCompile(`\bwork\b|salary|\bjob|boss|employer|coworker|co-worker|colleague|promotion|hiring|office\b|manager|\braise\b|team\b|power\b|hierarch\w*|dominan\w*`),
	"business":    regexp.MustCompile(`\bbusiness\b|compan\w*|\bfirms?\b|market|customer|pric\w*|startup|investor|supplier|competitor|client|auction|monopol\w*|profit\w*`),
	"military":    regexp.MustCompile(`\bmilitary\b|army|military|troop|\bwar\b|battle|defen[cs]e|attack|weapon|deter\w*|nuclear|front\b|enem\w*|invasion|soldier`),
	"politics":    regexp.MustCompile(`\bpolitics\b|election|vote\w*|government|parliament|policy|coalition|senate|campaign|treat(?:y|ies)|diplomat\w*|countr\w*|nation\w*|politic\w*|power\b|dominan\w*`),
	"games":       regexp.MustCompile(`\bgames\b|\bgames?\b|poker|chess|sport\w*|tournament|\bplayers?\b|\bmatch\b`),
	"everyday":    regexp.MustCompile(`\beveryday\b|roommate|family|friend\w*|partner|dinner|chore|neighbou?r|kids?\b|sibling|relationship|household`),
	"economy":     regexp.MustCompile(`\beconomy\b|econom\w*|\btax\w*|public good|commons|resource\w*|subsid\w*`),
	"environment": regexp.MustCompile(`\benvironment\b|environment\w*|climate|fish\w*|pollut\w*|forest|water|emission\w*|wildlife`),
	"government":  regexp.MustCompile(`\bgovernment\b|government\w*|regime|dictat\w*|autocra\w*|junta|coup\w*|cabinet|minister\w*|coalition|succession|opposition|protest\w*|revolution\w*|uprising|resistance`),
	"society":     regexp.MustCompile(`\bsociety\b|cult\w*|religio\w*|community|social\w*|coercive|whistle\w*|movement`),
}

// Template is the scenario file syntax shown by 'template' and in the menu.
const Template = `# Scenario file. One 'key: value' per line. Lines starting with '#' are comments.
#
# Trait keys and their values:
#   players:        two | many   (a number also works, e.g. 2 or 5)
#   timing:         simultaneous | sequential
#   interaction:    one-shot | repeated
#   information:    perfect | imperfect
#   payoff:         zero-sum | mixed | common-interest
#   communication, enforcement, commitment, bargaining:  yes | no
#
# Optional keys:
#   title:   a name for the situation
#   domain:  comma-separated, from work, business, military, politics,
#            games, everyday, economy, environment
#   notes:   free text, ignored by the advisor

title: My situation
players: two
timing: sequential
interaction: one-shot
information: imperfect
payoff: mixed
communication: yes
enforcement: no
commitment: no
bargaining: yes
domain: work
notes: Free text, ignored by the advisor
`

// Normalise validates a trait value, accepting a few common aliases.
func Normalise(key, value string) (string, error) {
	options := TraitOptions(key)
	if options == nil {
		return "", fmt.Errorf("unknown trait '%s'", key)
	}
	value = strings.ToLower(strings.TrimSpace(value))
	if key == "players" {
		if n, err := strconv.Atoi(value); err == nil {
			if n == 2 {
				value = "two"
			} else {
				value = "many"
			}
		}
	}
	switch value {
	case "true", "y":
		value = "yes"
	case "false", "n":
		value = "no"
	}
	if !contains(options, value) {
		return "", fmt.Errorf("'%s' must be %s, got '%s'", key, strings.Join(options, " | "), value)
	}
	return value, nil
}

func parseDomains(value string) ([]string, error) {
	var domains, unknown []string
	for _, part := range strings.Split(value, ",") {
		d := strings.ToLower(strings.TrimSpace(part))
		if d == "" {
			continue
		}
		if _, ok := domainWords[d]; !ok {
			unknown = append(unknown, d)
			continue
		}
		domains = append(domains, d)
	}
	if len(unknown) > 0 {
		return nil, fmt.Errorf("unknown domain(s) %s; choose from %s", strings.Join(unknown, ", "), strings.Join(DomainNames, ", "))
	}
	return domains, nil
}

// ParseScenario reads the 'key: value' scenario format.
func ParseScenario(text string) (*Scenario, error) {
	sc := &Scenario{Traits: map[string]string{}}
	for lineno, raw := range strings.Split(text, "\n") {
		line := strings.TrimSpace(raw)
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		key, value, found := strings.Cut(line, ":")
		if !found {
			return nil, fmt.Errorf("line %d: expected 'key: value', got '%s'", lineno+1, line)
		}
		key = strings.ToLower(strings.TrimSpace(key))
		value = strings.TrimSpace(value)
		var err error
		switch key {
		case "title":
			sc.Title = value
		case "notes":
			sc.Notes = value
		case "domain":
			sc.Domains, err = parseDomains(value)
		default:
			var v string
			v, err = Normalise(key, value)
			if err == nil {
				sc.Traits[key] = v
			}
		}
		if err != nil {
			return nil, fmt.Errorf("line %d: %w", lineno+1, err)
		}
	}
	return sc, nil
}

// Describe infers traits from a plain-English sentence. The matched phrases are
// kept in Evidence so the user can check and override the reading.
func Describe(text string) *Scenario {
	lowered := strings.ToLower(text)
	sc := &Scenario{Traits: map[string]string{}, Evidence: map[string]string{}, Text: strings.TrimSpace(text)}
	title := strings.TrimSpace(text)
	if len(title) > 70 {
		title = title[:70]
	}
	sc.Title = title
	for _, r := range rules {
		if m := r.re.FindString(lowered); m != "" {
			sc.Traits[r.key] = r.value
			sc.Evidence[r.key] = m
		}
	}
	for _, name := range DomainNames {
		if domainWords[name].MatchString(lowered) {
			sc.Domains = append(sc.Domains, name)
		}
	}
	return sc
}

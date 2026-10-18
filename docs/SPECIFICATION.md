# Game Theory Playbook: Specification

Version 1.0. This document records what the tool is for, what it must do, how it is built, what has been delivered, and what remains. It is a working specification for the project, not a marketing description.

## 1. Purpose

The playbook is a terminal tool that helps a person understand a situation in terms of game theory and decide how to play it. A person can:

- describe a situation in their own words, or in a short scenario file, and be shown the games it resembles, with the rules and strategies for playing each;
- look up any game, see how it works, its payoff table where one exists, its strategies and its pitfalls;
- play simulations that show the paths to victory and to failure, against fixed or live opponents;
- play a payoff table repeatedly against bots that remember the game, from 1 to 50 rounds;
- analyse any two-player payoff matrix exactly;
- record results, see their own records, and export what they learn;
- read a strategy and influence guide, and a guide to setting up their own scenarios.

The tool covers everyday, professional, political, military, social and intelligence settings. It is intended for learning, planning and judgement. It is not a source of operational instructions for harming people, and it is not a substitute for professional, legal or medical advice.

## 2. Users and use cases

| User | Need |
| --- | --- |
| A student of game theory | Clear explanations, reference payoff tables, exact solutions, practice |
| A manager or professional | Help choosing a negotiation, hiring, pricing or contract approach, with the risks shown |
| A citizen or analyst | Understanding of political, military, crisis and public-health choices, with the trade-offs and the evidence to weigh |
| A person in a family or personal situation | Structured thinking about shared resources, boundaries, fairness and support, without judgement |
| A developer or integrator | Stable data formats, a command-line interface, JSON output and a tool layer that other programs can call |

## 3. Scope

### 3.1 In scope

- A catalogue of 110 games across 17 families (classic, traditional and parlour, life, war and security, work, government and politics, society and groups, business and markets, economics and finance, negotiation and fairness, public goods and environment, games against AI, AI versus AI, evolution and biology, intelligence and deception, pandemic and disaster, advanced game theory).
- For every game: a summary, how it works, strategies, pitfalls, example scenarios, a reading list by family, and a payoff table with a note saying whether it is exact or a simplified model.
- 137 simulations: 128 basic (fixed choices with chance events, every step explained) and 9 live (an opponent replies to each move).
- Advice from a scenario file, from plain-English description, and from keyword search.
- Exact analysis of two-player matrices up to 4 by 4 for equilibria, and dominance and maximin for any size.
- Repeated play of payoff tables, 1 to 50 rounds, against six deterministic or seeded bots.
- Personal records, edits and additions kept in the user's own playbook folder.
- Charts as SVG, exports as Markdown, JSON, CSV and SVG, and a colour theme that can be changed.
- English throughout the interface and the game content.
- A tool layer that exposes seven functions as JSON-schema tools for other programs.

### 3.2 Out of scope

- Operational guidance for recruiting, handling or surveilling people, or intruding into systems. The intelligence material is analytic: the intelligence cycle, analysis, warning, deception and counterintelligence as games, and how services are organised.
- Real-time data feeds. Live data is not part of this version.
- Network services, accounts, or any storage of personal data outside the user's own machine.
- Guarantees about outcomes. The advice is a structured aid to judgement, and every heuristic reports what it matched so the user can correct it.

## 4. Principles

1. **Offline first.** The tool works with no network, no account and no third-party library. The Python version uses the standard library only; the Go version is a single executable with its data embedded.
2. **Two implementations, one behaviour.** The Python and Go versions give the same output for the same command, and this is tested.
3. **Transparency.** Every recommendation says why. Every heuristic reports what it matched. Simplified models are labelled as simplified.
4. **Honesty about the data.** Payoff tables are labelled exact (computed from rules, or the standard textbook form) or simplified (an illustrative form whose numbers were chosen, not measured). Games that cannot be sensibly reduced to a table say why.
5. **Ethical use.** The strategy guide is written for ethical influence and for recognising manipulation. Sensitive families (coercive groups, authoritarian control, intelligence) are analytic and include how to protect people.
6. **User data stays local.** Records, edits, exports and the colour theme live in a playbook folder chosen by the user (`PLAYBOOK_HOME`, default `~/.playbook`).
7. **Extensibility.** Games, phrases, simulations, payoff tables and translations are data files, generated from source specifications where that is practical.

## 5. Functional requirements

### 5.1 Finding a game

- **FR-1** `list` shows every game with its category; it filters by domain or by search text.
- **FR-2** `show <game>` explains a game: summary, how it works, scenarios it fits, payoff table with its note, how to play it, pitfalls. It accepts an id or a name.
- **FR-3** `areas [family]` lists the families, their sub-domains and their reading lists.
- **FR-4** `problems [query]` shows practice problems with answers.
- **FR-5** `advise -d "..."` reads traits and domains from a plain-English description, shows the words it matched, and ranks the best-fitting games with the general rules for the traits. `--set key=value` overrides a trait.
- **FR-6** `advise <file.gt>` reads a scenario file with `key: value` lines.
- **FR-7** `keywords <words>` looks up phrases for each game and words for each area, ranks the matches, and asks whether the result fits. If no game phrase matches, it lists the games in the best-matching area and labels them as area matches.
- **FR-8** `new` and `template` help build a scenario file.

### 5.2 Analysing a payoff matrix

- **FR-9** `solve "a,b c,d; ..."` reports iterated dominance, surviving strategies, maximin values, and every equilibrium for matrices up to 4 by 4 (exact rational arithmetic). `--rows` and `--cols` name strategies. `--json` prints the same as JSON.

### 5.3 Simulations

- **FR-10** `sim` lists simulations; `--mode basic|live` and `--family` filter them.
- **FR-11** `sim <id>` shows the path to victory, the path most likely to fail, and the number of endings. Each step carries a reason.
- **FR-12** `sim <id> --play` plays a simulation. Before each choice the player sees the chance of victory from there; after it, the reason for the choice and for the alternatives.
- **FR-13** `--save` and `--resume` keep and continue a played game.
- **FR-14** `sim <game> --matrix` builds a simulation from a payoff table. `--opponent` chooses equilibrium, uniform, noisy (with `--lam`) or loss-averse play.
- **FR-15** After a played run, the user can export it: Markdown, JSON, CSV and an SVG decision tree with the path outlined (`--formats` for scripts, or an offer after the run in the session).

### 5.4 Repeated play

- **FR-16** `repeat <game> --rounds N` plays a payoff table for 1 to 50 rounds. The player chooses a row each round; the bot answers from the game so far.
- **FR-17** Six bots: tit-for-tat, grim, pattern, learner (best reply to the player's most common row), win-stay lose-shift, and random with a seed.
- **FR-18** At the end the player sees their total, the average, and the best always-the-same plan against that bot.
- **FR-19** `--log` records the result in the player's records (win if at or above the best plan, draw at 80% or more of it, otherwise loss). `--formats` exports the rounds.

### 5.5 Records and exports

- **FR-20** `log <game> win|loss|draw|mixed [note]` records a result; `unlog` removes the latest. `record` shows tallies; `record <game>` shows the history; `--json` and `--csv` export them.
- **FR-21** `show <game> --formats md,json` exports a game card. `chart` writes SVG for families, traits, the area map, records, plays, and a simulation's decision tree.

### 5.6 Setup and the guides

- **FR-22** `setup <game>` gives a guide to describing one's own version of a game: the trait meanings, the steps, the options to model, the payoff grid if any, and a scenario template. `--write` saves the template.
- **FR-23** `guide` shows the strategy and influence guide: 48 principles (`guide power`), 17 manipulation tactics with their signs and defences (`guide defend`), research steps and starting references (`guide research`), and life habits (`guide life`).

### 5.7 Interface

- **FR-24** The interactive session accepts plain descriptions or commands; `/` lists the commands; arrow keys and history work; Tab completes.
- **FR-25** `menu` opens a full-screen menu of the whole playbook. Each item shows a description of what it does. The typed fallback works when there is no terminal.
- **FR-26** `theme` shows and changes the colour theme. Built-in themes are classic, ocean, forest, contrast and mono. Single colour roles (accent, good, bad, mid) can be set to a named colour or a 256-colour number. Colour is off when output is not a terminal, or when `NO_COLOR` is set.
- **FR-28** `help` prints the complete command list; `version` prints the version.

### 5.8 Tools for other programs

- **FR-29** `tools` prints the JSON schemas of seven tools: `find_games`, `get_game`, `list_games`, `solve_matrix`, `list_simulations`, `get_simulation`, `repeat_summary`.
- **FR-30** `tool <name> '<json>'` runs one tool and prints its JSON result. Errors are returned as data, not as crashes. No network access is involved.

### 5.9 Editing the playbook

- **FR-31** `edit <game>` copies a game into the user's playbook; `add-play` adds a play; `disable` and `enable` hide or show a game; `check` validates the user's files.

## 6. Non-functional requirements

- **NFR-1 Platforms.** macOS is run-tested in both versions. Linux is run-tested in Docker with Go 1.24, Go 1.22 on Alpine, and Python 3.12 and 3.9 slim images. Windows is cross-compiled and vetted for the Go version but has not been run.
- **NFR-2 Size.** The Go executable is about 22 MB, with all data embedded. Memory and size were confirmed acceptable by the owner.
- **NFR-3 Parity.** For every command in the parity sweep, the two versions give identical output and identical files. The sweep covers 45 commands and is repeatable.
- **NFR-4 Correctness.** Exact arithmetic is used for solutions (fractions in Python, rationals in Go). Every simulation has a reachable path to victory or to a draw, and a reachable path to failure, except for games that cannot lose under equilibrium play, which are listed and explained.
- **NFR-5 Testing.** `make test` runs 79 Python tests and the Go test suite. `make test-docker` runs the same tests in Linux and Alpine containers.
- **NFR-6 Robustness.** Interactive input is validated; unknown options are rejected; bad data files are reported with the file name.
- **NFR-7 Accessibility.** The mono theme and `NO_COLOR` remove colour. Text does not rely on colour alone (labels such as victory, failure and draw are always printed).
- **NFR-8 Privacy.** The tool makes no network calls. It writes only to the user's playbook folder and to paths the user names.

## 7. Architecture

### 7.1 Components

| Component | Responsibility |
| --- | --- |
| `gtplaybook/` (Python) | Commands, the interactive session, the line editor, the solver, simulations, repeated play, keywords, exports, charts, themes, translations, the tool layer |
| `goplaybook/` (Go) | The same commands and output, compiled to one executable with data embedded |
| `gtplaybook/data/` | Games, areas, simulations, keywords, guide, setup text, help text, tool schemas |
| `tools/` | Generators: simulations (scripted and full-rules), payoff tables, keyword phrases |
| `tests/`, `goplaybook/*_test.go` | Automated tests, including pseudo-terminal tests and cross-version parity checks |

### 7.2 Data flow

1. Game and simulation source files are generated or edited, then written to `gtplaybook/data/`.
2. `make sync` copies data into `goplaybook/data/` so the Go build can embed it.
3. `make build` builds `bin/Ergaelion`.
4. At run time, the user's playbook folder overlays the built-in data (edits, added plays, disabled games, records, theme, exports).

### 7.3 Key design decisions

- **Scored decision trees.** A simulation is a graph of nodes: player choice, chance, and end. The same graph is solved for the path to victory, the path to failure, and every ending.
- **Full-rules games.** Tic-tac-toe, Nim, Connect Four (with a depth limit) and repeated games are generated from their rules into the same graph format, so the solver and the player treat them the same way.
- **Payoff tables.** Each table has integer payoffs, row and column names, and a note with its status (exact or simplified). Tables are generated and checked by a script.
- **Keyword search.** A phrase matches when its words appear in order, allowing plurals. Games rank by the number of words matched, so a longer phrase is stronger evidence.
- **Shared text.** The guide, the setup text and the help text each live in one data file read by both versions, so the wording cannot drift.

## 8. Content

| Area | Count | Status |
| --- | --- | --- |
| Games | 110 | All have a summary and a payoff table or a stated reason |
| Payoff tables | 110 | Exact or simplified, labelled |
| Families | 17 | Each with summary, sub-domains and reading list |
| Simulations | 137 | 128 basic, 9 live |
| Keyword phrases | 781 | English |
| Multi-game playbooks | 10 | Analytic; for complex situations such as deception, sieges and crises |
| Strategy guide | 48 principles, 17 tactics, 8 research steps, 11 habits | English |
| Setup guidance | 9 trait groups, 6 steps, per-game setup pages | English |

### 8.1 Coverage by family (examples)

Work: hiring, firing, promotion, power and position, contracts. Life: screening, search, household cooperation, health, and family cases (screen time, boundaries and support, inheritance, care of a parent, school refusal). Government: coalitions, voting, lobbying, regime survival, reform with veto players. Society: coercive groups, reporting wrongdoing, plea bargaining, social learning. War and security: attrition, deterrence, escalation, siege, insurgency, reconnaissance, search. Business: pricing, auctions, trust, platforms, standards, insurance. Intelligence: warning, analysis, deception, disclosure, sharing, counterintelligence (analytic only). Pandemic and disaster: quarantine, testing, supplies, preparedness. Advanced game theory: mechanism design, information design, coalition values, voting paradoxes, credible threats, sustained cooperation, incomplete contracts, global games.

### 8.2 Boundaries on sensitive content

- Intelligence material covers analysis and organisation, not recruiting, handling people, surveillance of individuals, or intrusion into systems.
- Coercive-group and relationship material covers how to recognise pressure and protect people, and points to specialist help where safety is at risk.
- The authoritarian and insurgency material is analytic and does not give guidance for repression.

## 10. Quality and verification

- Every command in the parity sweep was run in both versions, in fresh playbook folders, and the output and any written files were compared.
- The simulations were checked against their intended results: for example, perfect-play tic-tac-toe is a draw; Nim with a non-zero nim-sum is a first-player win; a grim bot punishes any defection.

## 11. Delivery status

### 11.1 Delivered

- The full catalogue, the advisor, the scenario file, plain-English and keyword search, exact solver, simulations (basic and live), the menu, the session, the line editor, charts, exports, themes, records, repeated play with six bots, the tool layer, the strategy guide, the setup guide, the help text, and parity between the two versions.
- A project `.gitignore`, a README, a how-to guide and this specification.

### 11.2 Not yet delivered

- A run test of the Go version on Windows. It is cross-compiled and vetted only.
- Live data sources and an integration with a language model. The tool layer is ready for such an integration, which is not part of this version.
- A git repository. The project is not yet under version control.

## 12. Development history (summary)

The work started as a request for a terminal game theory playbook that could advise on situations from work to military, list games with summaries, and give rules for playing them. It then grew in stages:

1. A first Python version with a scenario syntax and an advisor, followed by a Go version built to an executable.
2. Expansion to 50 or more games, then to 96, grouped into families, sub-domains and areas, with reading lists.
3. Simulations with paths to victory and failure, a menu and interactive session in the style of a modern command-line assistant, and a line editor in each version.
4. A strategy and influence guide with defences against manipulation, a setup guide for each game, and an intelligence playbook restricted to analysis.
5. Payoff tables for the games that have a natural form, exact solving up to 4 by 4, mixed equilibria, and then a payoff table for every game, labelled exact or simplified.
7. Repeated play, behavioural bots and full-rules simulations (tic-tac-toe, Nim, Connect Four with a depth limit, repeated dilemmas), and family and relationship cases.
8. Colour themes and a theme menu, export of games, runs and records, JSON output, a keyword parser, a full help text, and a tool layer.
9. Parity checks, Docker tests on Linux and Alpine, and the documentation set described above.

## 13. Acceptance criteria

The delivery is accepted when all of the following hold:

- `make test` and `make test-docker` pass.
- The parity sweep reports no differences between the two versions.
- `./playbook help` and `bin/Ergaelion help` print the same text.
- `show`, `setup`, `keywords` and `repeat` work as documented.
- Every game has a payoff table or a stated reason, and every simulation has a reachable victory or draw path and a reachable failure path.
- No repository file describes the code's authorship or its production process.
- The README and the how-to guide describe the commands that exist.

## 14. Open decisions

- Spanish was removed for now. Keeping a full translation current costs more than the project needs at present, so it can be added back later.
- Which live data sources, if any, the tool should use, and what the user should be told before data leaves the machine.
- The repository's licence, and whether the data files carry their own sources.

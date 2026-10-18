# Ergaelion

A terminal tool that identifies the game behind a situation, explains how it works, and shows the paths to victory and failure. It runs offline: no accounts, no network calls, and no third-party libraries.

- **110 games** across 17 families, each with how it works, its strategies, its pitfalls and, for all 110 of them, a payoff table (exact, or labelled as a simplified model).
- **174 simulations**: 133 basic (fixed choices you can read and play) and 41 live (an opponent replies to each move, and remembers earlier rounds in the repeated games). Chances are estimates unless a simulation names its sources. They include family, parent-child, relationship, workplace, war and military cases.
- **Repeated play** against six bots, from 1 to 50 rounds.
- **Keyword search**, so a short description finds the games that fit it.
- **Colour themes** you can change: classic, ocean, forest, contrast, sunset, midnight, rose, matrix, paper, Claude dark and light, plain (ASCII box edges) and mono.
- **Export** of games, runs, records and charts to Markdown, JSON, CSV and SVG.

The same features are in two versions that give the same output:

- **Python** (`./playbook`, package `gtplaybook/`): runs with Python 3.9 or later.
- **Go** (`goplaybook/`): builds to one executable, `bin/Ergaelion`, with the data embedded.

## Install and build

```sh
make build        # sync the data, then build bin/Ergaelion (needs Go 1.22+)
make test         # Python and Go tests
make test-docker  # the same tests on Linux and Alpine (needs Docker)
```

Run the Python version with `./playbook`, or the Go version with `bin/Ergaelion`. Both take the same commands. For the full guide, see `docs/HOW-TO-USE.md`. For a quick list of commands, run `playbook help`.

## Quick start

```sh
./playbook                                   # the interactive session (type / for the command list)
./playbook menu                              # the full-screen menu
./playbook show chicken                      # explain a game
./playbook keywords bank run                 # which games do these words point to?
./playbook advise -d "two firms set prices at the same time, once only"
./playbook sim chicken --play                # play a simulation yourself
./playbook repeat prisoners-dilemma --rounds 10 --opponent learner
./playbook solve "3,3 0,5; 5,0 1,1" --json   # analyse a payoff matrix
./playbook help                              # every command
```

## Finding a game

- **By name or id:** `list`, `list --domain war`, `list --search bluff`, `show <game>`.
- **By description:** `keywords <words>` lists the games, areas and simulations your words point to. It asks whether they fit, and you can add or change words. In the session, a plain description does the same.
- **By scenario:** `advise -d "..."` reads your words and ranks the games. It uses the phrases each game is known by, the words your description shares with each game, and the traits it can infer. `advise <file.gt>` reads a scenario file. Override any trait with `--set key=value`.
- **Combined advice:** when no single game covers the situation, `advise` also gives strategies from the best-fitting games together, and any multi-game playbook that matches (for example a trojan-horse or siege situation). It then lists scenarios to play.
- **Typos and unknown words:** a clear one-letter typo in a longer word is corrected and shown ("Reading your words as…"). When nothing matches, the playbook says so and lists the nearest known words ("Did you mean…").
- **Autocomplete:** in the session, a partly typed word completes from the vocabulary of the phrases, area words and game names. Once you have typed two or more words that begin a known phrase, Tab completes the whole phrase (or the longest shared part of several). Type `/` for commands.
- **By area:** `areas` lists the families, and `areas <family>` shows one with its games and reading list.

## Solving a payoff matrix

`solve "a,b c,d; e,f g,h"` takes rows separated by `;`, with each cell as `yours,theirs`. It reports dominance steps, surviving strategies, maximin values, and every equilibrium for matrices up to 4×4, computed exactly with fractions.

- `--rows A,B --cols C,D` names the strategies.
- `--json` prints the same analysis as JSON.

## Simulations

`sim` lists the simulations. `sim <id>` shows the path to victory, the path most likely to fail, and the number of endings.

- `sim <id> --play` plays it. Before each choice you see the chance of victory from there, and afterwards the reason for your choice and for the ones you skipped.
- `sim <id> --play --save FILE` saves your game after each choice. `--resume FILE` continues it later.
- Some simulations are live: the other side answers your choice, from its own odds.
- Hints (the chance of victory and the best strategy) can be turned off with `--no-hints`, or with `h` at any choice, round by round.
- While you play, type `b` at any choice to go back to your previous decision and choose again. When a run ends, the playbook asks whether to play again from the start.
- `sim <game> --matrix` builds a simulation from a game's payoff table. Add `--opponent uniform`, `noisy` (with `--lam`) or `loss-averse` to change how the other player chooses.
- `sim --mode basic` or `sim --mode live` filters the list.
- `sim --family war` filters by area.

A **basic** simulation is a fixed set of choices with chance events, written so you can read every step. A **live** simulation has an opponent who replies to each move: a full-rules game such as tic-tac-toe, Nim, Connect Four, or a repeated prisoner's dilemma against a bot.

## Repeated play

`repeat <game> --rounds N --opponent BOT` plays a payoff table for 1 to 50 rounds. You choose a row each round, and the bot answers from the history of the game:

| Bot | How it plays |
| --- | --- |
| `tit-for-tat` | copies your previous row |
| `grim` | cooperates until you leave your first row once, then defects for good |
| `pattern` | cycles through its options in a fixed order |
| `learner` | answers your most common row with its best reply to it |
| `wsls` | keeps its last choice while it does well, and switches when it does badly |
| `random` | picks at random (use `--seed` to repeat a run exactly) |

At the end you see your total, and the best plan of always choosing the same row against that bot, for comparison. Add `--log` to record the result (a win if you matched that plan, a draw at 80% of it, otherwise a loss), and `--formats md,json` to export the rounds.

## Records

- `log <game> win|loss|draw|mixed [note]` records a result. `unlog [game]` removes the latest one.
- `record` shows every game's tally, and `record <game>` its history.
- `record --json` and `record --csv FILE` give the same data as JSON or CSV.

## Export

Any game, run or record can be exported.

- `show <game> --formats md,json` writes a game card: its description, payoff table and strategies.
- `sim <id> --play --formats md,json,csv,svg` (or `all`) writes a played run, with the decision tree outlined in your path.
- `repeat ... --formats md,json` writes the rounds and the totals.
- `chart families|traits|map|records|plays|sim <id> --out FILE.svg` writes a chart.

Exports go into `PLAYBOOK_HOME/exports/`, in a folder named for the item and the time, so nothing is overwritten. After a simulation run in the session you are also offered the export choices.

## Keywords

`keywords <words>` looks up each game's phrases (English phrases only) and each area's words, then ranks the best matches. It says "Based on these words it looks like you're looking for…" and asks whether that fits. When no game phrase matches, it lists the games in the best-matching area and labels them as area matches.

## Ask Claude (optional)

Off by default. Nothing leaves the machine until you switch it on in a session. You need an Anthropic API key in `ANTHROPIC_API_KEY`. The model defaults to `claude-sonnet-5-5` and can be changed with `GTP_CLAUDE_MODEL`.

```
/claude on                                   show what is sent, and switch on
/claude ask <question>                       your question and the current situation
/claude game <game> <question>               your question and one game's text
/claude sim <simulation> <question>          your question and one simulation's paths
/claude scenario <question>                  the current situation and its top three games
/claude status
/claude off
```

Each question sends only your question and the text you named: a game's summary, payoffs, playbook and pitfalls, a simulation's decisions and endings, or the situation you described. Nothing else from your machine is included. The answer is printed with the number of characters sent. The rest of the playbook works the same without it.

## Colours and themes

- `theme` shows the current theme. Built-in themes: `classic`, `ocean`, `forest`, `contrast`, `sunset`, `midnight`, `rose`, `matrix`, `paper`, `claude-dark`, `claude-light`, `plain` and `mono`. Set one with `theme <name>`. `claude-dark` suits dark terminals and `claude-light` suits light ones; `plain` uses ASCII box edges for old terminals and fonts.
- Change a single colour with `theme set <role> <colour>`. The roles are `accent` (headings and borders), `good` (victories), `bad` (failures) and `mid` (draws). A colour is a name (`red`, `cyan`, `orange`, `grey`, ...) or a number from 0 to 255.
- `theme reset` returns to classic. Your choice is saved in `PLAYBOOK_HOME/theme.json`.
- The same choice is in the menu under "Look and colours".
- Colour is off when the output is not a terminal, or when `NO_COLOR` is set.

## The menu

`./playbook` opens the main menu first, in a terminal. Its first entry, Command prompt, opens the prompt, and `/menu` in the prompt returns here. Use the arrow keys, and Enter to open an item. It covers: browse games, simulations, advice, matrix solving, families and problems, the guide and setup, records and charts, repeated play, Ask Claude (optional, see above), and colours. Each choice runs the same command you could type. The numbered menu used without a terminal lists the same items; choose 11 to quit, and end of input also quits.

## Tools for other programs

`tools` prints the schemas of seven tools that other programs can call: `find_games`, `get_game`, `list_games`, `solve_matrix`, `list_simulations`, `get_simulation` and `repeat_summary`. `tool <name> '<json>'` runs one, and prints its result as JSON. The tool layer is for other programs to call. It needs no network access, so the playbook works the same without it.

```sh
./playbook tool find_games '{"description": "price war"}'
./playbook tool get_simulation '{"simulation": "chicken"}'
```

## Your own playbook

- `edit <game>` copies a game into `PLAYBOOK_HOME/games/`, where you can change it. `add-play <game> "text"` adds a play.
- `setup <game>` explains how to set up your own version of a game, with a scenario template. `setup <game> --write my.gt` saves the template.
- `disable <game>` and `enable <game>` hide or show a game. `check` validates your files.

## Adding content

- **Games:** add an object to `gtplaybook/data/games.json`. Optional fields are `examples`, `pitfalls` and `matrix` (`rows`, `cols`, and `payoffs` as `[yours, theirs]` pairs). Matrix notes go in `matrix_note`.
- **Keyword phrases:** edit `tools/keywords/game_phrases.py`, then run `python3 tools/keywords/build_keywords.py`.
- **Simulations:** the scripted ones are written in `tools/simulations/sims_*.py` and built with `python3 tools/simulations/build_all.py gtplaybook/data/simulations.json`. The live ones are generated from game rules in `tools/simulations/full_rules.py`.
- **Payoff tables:** `tools/matrices/build_matrices.py` adds them. Each table is labelled `exact` (computed from the rules) or `simplified` (an illustrative form).

After changing the data, run `make build`. It copies the data into the Go version before compiling.

## Data layout

```
playbook                    the Python launcher
gtplaybook/                 the Python package
  cli.py                    commands, the menu's typed fallback, and the help text
  repl.py                   the interactive session and the full-screen menu
  lineedit.py               line editing, the command list and pickers (standard library)
  solver.py                 payoff-matrix analysis with exact fractions
  sim.py                    simulation trees: solve, trace, endings, play
  matrix_sim.py             simulations built from payoff tables
  repeat.py                 repeated play and its bots
  keywords.py               the keyword parser
  exporter.py               export of runs, games and records
  charts.py                 SVG charts
  tool_api.py               the tool layer (tools, tool)
  ui.py                     colour themes
  i18n.py                   interface text
  data/                     games, simulations, areas, keywords, combinations, guides, help.txt
goplaybook/                 the Go version (same commands and output)
  lineedit/                 the line editor
tools/                      the generators for the data above
tests/                      the Python tests
docs/                       the how-to guide and the longer guides
```

## Checks

`make test` runs 77 Python tests and the Go tests. The tests include a session driven through a pseudo-terminal, and checks that the Python and Go versions print the same output for the main commands, the tool calls, the charts and the exports.

## Limits

- The advisor and the keyword parser are transparent heuristics, not proofs. They report what they matched, so you can correct them.
- Measured accuracy: on 32 descriptions used to tune the phrases, all 32 find a sensible game in the top three. On 12 new descriptions written afterwards, 8 do (67%). Expect the advice to be a good starting list, not a verdict, and be specific about the parties, the choices and the timing.
- Multi-game playbooks in `gtplaybook/data/combinations.json` are analytic: they describe how to reason about a situation and how to check it. They give no operational steps for attacks, intrusion or manipulation of people.
- Payoff tables labelled `simplified` are illustrative forms chosen to show a structure. They are not measured data.
- `solve` finds mixed equilibria exactly up to 4×4. Larger matrices give the dominance and pure-equilibrium results only.
- The Go version on Windows is compiled but not run-tested.
- The choices and paths inside simulations, the setup guides and the strategy guide are English only.
- The Claude answers are only as good as the text they are given, and the model can be wrong. Check them against the playbook text the answer cites.
- The `/claude` commands have been tested with the network calls replaced. A live call needs your API key and has not been run in this environment.

## Intelligence and strategy

`docs/INTELLIGENCE-PLAYBOOK.md` covers the intelligence cycle, analytic methods, warning, deception and counterintelligence as games, and how services are organised. It is strategic and analytic only, and it excludes operational tradecraft. `guide` holds 48 principles of strategy and influence, with defences against manipulation, research steps and life habits. The guide is written for ethical influence and for recognising manipulation.

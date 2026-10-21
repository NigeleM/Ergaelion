# How to use the Game Theory Playbook

This guide walks through the common tasks. Each step is a command you can type. Run `playbook help` for the full list, or `playbook <command> --help` for one command's options.

The examples use `./playbook` (the Python version). The Go version, `bin/Ergaelion`, takes exactly the same commands and gives the same output.

## 1. Start the playbook

```sh
./playbook            # opens the main menu
```

The main menu opens first. Use the arrow keys and Enter to choose an entry, and `q` or Esc to leave. The first entry, **Command prompt**, opens the prompt, where you type a plain description of a situation or a command. Type `/` to see every command, `/menu` to return to the main menu, and `/quit` to leave. Use `/cls` to clear the screen.

When input is piped in, for example from a script, `./playbook` opens the prompt directly instead of the menu.

## 2. Find the game behind a situation

Describe it in a few words.

```sh
./playbook keywords price war with a new competitor
```

The playbook says which words it matched, lists the games, areas and simulations they point to, and asks whether that fits. If it doesn't, add or change words and try again.

For a longer description with traits, use `advise`:

```sh
./playbook advise -d "two firms set prices at the same time, once only"
```

It ranks the best-fitting games and gives the general rules for your situation. It also shows the phrases and shared words that matched, so you can see why. When no one game covers the situation, it gives strategies from the best fits together, any multi-game playbook that matches, and scenarios to play. If a trait was read wrongly, correct it with `--set`:

```sh
./playbook advise -d "we will meet again every month" --set payoff=zero-sum
```

## 3. Understand a game

```sh
./playbook show bank-run
```

The card shows what the game is, how it works, where it fits, its payoff table (with a note saying whether the table is exact or simplified), how to play it, and what to avoid. To keep a copy:

```sh
./playbook show bank-run --formats md,json
```

## 4. Analyse a payoff matrix

Write the matrix with rows separated by `;` and each cell as `yours,theirs`:

```sh
./playbook solve "3,3 0,5; 5,0 1,1" --rows Cooperate,Defect --cols Cooperate,Defect
```

You get the dominated strategies, the surviving strategies, the maximin values, and every equilibrium. For JSON, add `--json`.

Read the grid first. The pure equilibrium is green. Strategies removed by dominance are dimmed, because no sensible player chooses them. Under the analysis, each dominated strategy has a sentence that shows the numbers. For example, R1 is dominated when R2 pays you more whichever column they choose: 5 against 3 if they play C1, and 1 against 0 if they play C2.

## 5. Play a simulation

List the simulations, then look at one:

```sh
./playbook sim                       # all simulations
./playbook sim --mode live           # only the ones where an opponent replies
./playbook sim chicken               # the paths to victory and failure
```

Play it yourself:

```sh
./playbook sim chicken --play
```

Before each choice you see your chance of victory from there. After the ending you see why each choice was reasoned the way it was. To save your game and continue later:

```sh
./playbook sim chicken --play --save my-game.json
./playbook sim chicken --resume my-game.json
```

To export the run afterwards, add `--formats`. The tree is written with your path outlined:

```sh
./playbook sim chicken --play --formats all
```

While you play, type `b` at any choice to go back to your previous decision and choose again. Going back undoes the decisions and chances after it. When the run ends, the playbook asks whether to play again from the start.

Some simulations are **live**: the other side answers what you just did. Its reply is chosen from its own odds for the choice you made, so the same choice can get a different answer each time. Examples are `salary-talk-with-manager`, `price-war-with-competitor`, `landlord-rent-increase` and `ceasefire-talks`. The repeated live games, such as `repeated-prisoners-dilemma-live`, `repeated-chicken-live`, `repeated-stag-hunt-live` and `repeated-arms-race-live`, play three rounds, and the other side's reply depends on how you have played so far.

Each simulation records its evidence. Most chances are the author's estimates and are labelled as such. A simulation names its sources only where they were checked against the original research, and the notes say where a figure is an extrapolation.

Hints show the chance of victory from each choice and the best strategy. Before a game you are asked whether to show them. Type `h` at any choice to turn them on or off from that choice on, so you can have hints in round 1 and none in round 2. Use `--no-hints` to start with them off:

```
./playbook sim salary-talk-with-manager --play --no-hints
```

War and military simulations are listed with `./playbook sim --family war`. They include `flank-attack` (taking the flank), `ambush-on-the-road`, `naval-blockade`, `fortress-defence` and `guerrilla-hit-and-run`:

```
./playbook sim flank-attack --play
```

## 6. Play a game repeatedly against a bot

```sh
./playbook repeat prisoners-dilemma --rounds 10 --opponent learner
```

Each round, choose a row by its number. The bot answers from the history, so watch its pattern. At the end you see your total, and the best plan of always choosing the same row against this bot. The bots are listed in the README; `--opponent random --seed 7` gives a run you can repeat exactly.

To record the result in your records, add `--log`:

```sh
./playbook repeat prisoners-dilemma --rounds 10 --opponent grim --log
```

## 6b. Play an engine game

```sh
./playbook engine nim
```

`engine` lists the games. In each one the engine chooses its move as you play:

- **Tic-tac-toe** and **Connect Four** use search. The engine never misses a win or a block. Type `h` for the best move for you.
- **Nim** is solved exactly. Type `h` to see whether you are winning, and which move keeps you winning.
- **Rock-paper-scissors** predicts the move you have played most often and plays the move that beats it.
- **Colonel Blotto** (military): send three numbers that add up to 6, one per front. The commander picks the split that did best against your past splits.
- **Border Patrol** (military): pick one of three gates each round. The guard watches the gate you have used most, so vary your choices.
- **Ultimatum**: enter how many of ten coins the engine gets. It accepts any offer of at least 3, and a refusal leaves you both with nothing. Type `h` for the least it accepts.
- **Guess Two Thirds**: guess a number from 0 to 100. The target is two thirds of the average of your guess and the engine's. The engine forecasts your average and guesses two thirds of it. Type `h` for a guess that lands on the target.
- **Matching Pennies**: call heads or tails. The engine's coin is the opposite of the call you make most often, so vary your calls.

Type `q` to leave a game. The menu also has **Play an engine**, which lists the games.

## 7. Record your results

```sh
./playbook log chicken win "I held firm and they swerved"
./playbook record                    # every game's tally
./playbook record chicken            # the history for one game
./playbook record --json             # the same as JSON
./playbook record --csv results.csv  # the same as a spreadsheet
```

Advice shows your record for each game it recommends, so the ranking learns from what you have logged.

## 8. Draw a chart

```sh
./playbook chart families --out families.svg
./playbook chart sim chicken --out tree.svg
./playbook chart records --out records.svg
```

Charts are written as SVG, which opens in a browser. The colours follow your theme.

## 9. Change the colours

```sh
./playbook theme                     # show the current theme and its colours
./playbook theme ocean               # a built-in theme, such as ocean, sunset, claude-dark or plain; `theme` lists them all
./playbook theme set accent cyan     # change one colour: accent, good, bad or mid
./playbook theme reset               # back to classic
```

The same choice is in the menu under "Look and colours". To turn colour off for one run, set `NO_COLOR=1`.

## 10. Save what you find

Exports go to `PLAYBOOK_HOME/exports/` (default `~/.playbook/exports/`), in a folder named for the item and the time:

```sh
./playbook show bank-run --formats md
./playbook advise -d "work promotion" --export advice.md
```

Your own changes to a game are kept in `PLAYBOOK_HOME/games/`:

```sh
./playbook edit chicken              # copy a game into your playbook to change it
./playbook add-play chicken "Signal early and clearly"
./playbook check                     # confirm your files are valid
```

## 11. Ask Claude about a game or simulation (optional)

Claude is off until you switch it on, and it needs an Anthropic API key in `ANTHROPIC_API_KEY`. In a session:

```
/claude on
/claude game prisoners-dilemma why does defection win in a one-shot game?
/claude sim salary-negotiation what should I ask for if the budget is unknown?
/claude scenario how do we avoid a price war with a rival?
/claude off
```

`/claude on` shows what is sent. Each answer says how many characters were sent. Nothing else from your machine is included.

## 12. Let other programs use the playbook

```sh
./playbook tools                                  # the seven tools and their inputs
./playbook tool find_games '{"description": "price war"}'
./playbook tool get_simulation '{"simulation": "chicken"}'
```

Each result is JSON, so another program can read it. Other programs can call these same tools.

## Where things are stored

| What | Where |
| --- | --- |
| Your games and plays | `PLAYBOOK_HOME/games/` |
| Your results | `PLAYBOOK_HOME/outcomes.jsonl` |
| Your colour theme | `PLAYBOOK_HOME/theme.json` |
| Exports | `PLAYBOOK_HOME/exports/` |
| Command history | `PLAYBOOK_HOME/history` |

`PLAYBOOK_HOME` defaults to `~/.playbook`. Set it to keep a separate playbook, for example for a class or a project.

## If something goes wrong

- **A command says a game is unknown:** run `./playbook list --search <word>` to find its id.
- **A description matches nothing:** add a role, a situation or a kind of game, such as "boss", "price war" or "shared resource".
- **Colours look wrong in a log file:** colour only appears in a terminal. Pipe output with `NO_COLOR=1` to be sure.
- **A check fails after you edited data:** run `./playbook check` for the file and line, and `make build` to rebuild the Go version.

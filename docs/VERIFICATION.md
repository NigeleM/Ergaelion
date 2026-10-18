# Verification of the simulations

Each simulation records its evidence in `gtplaybook/data/simulations.json`:
- `partly sourced: see sources` where the chances were checked against a named study or textbook;
- `estimate` where the chances are the author's and not measured;
- `illustrative` where there are no chances.

## Checked against published work

| Simulation | Source | What was checked or changed |
| --- | --- | --- |
| ultimatum-game | Oosterbeek, Sloof and van de Kuilen (2003 working paper; meta-analysis of 75 results) | Average offer 40.4%, average rejection 16.2%. Offers of 10% and 20% are outside the studied range; rejection set to 40%, the highest study average. |
| repeated-ultimatum-live | Same | As above. |
| repeated-prisoners-dilemma-live | Dal Bó and Fréchette (2011), AER; their data from the stratEst R package, analysed in `docs/research/dalbo2011_rates.py` | Partner cooperation measured by the previous round's profile: 98% after mutual cooperation, 40% after you cooperated and they defected, 37% after you defected and they cooperated, 9%/4% after mutual defection. First period 42%. The game has three fixed rounds, so this is an approximation. |
| repeated-public-goods-live | Fischbacher and Gächter (2009 discussion paper; AER 2010) | 55% conditional cooperators, 23% free riders. Decline over rounds not modelled. |
| repeated-trust-game-live | Johnson and Mislin (2011 meta-analysis of 84 replications) | Average sent about 51%; average returned about 37% of the amount available. Trustee odds set as approximations. |
| nim | Bouton (1901) | Corrected: piles 1, 2, 2 have nim-sum 1, not 2. |
| lanchester-combat | Lanchester (1916) | Square law: numbers matter as their square. Consistent. |
| secretary-problem | Gilbert and Mosteller (1966) | Reject about n/e, succeed about 1/e. Consistent. |
| cournot-competition | Cournot (1838) | Equilibrium logic. Consistent. |
| stackelberg-leadership | von Stackelberg (1934) | Leader takes the larger share. Consistent. |
| bertrand-price-war | Bertrand (1883) | Price competition with identical products. Consistent. |
| tic-tac-toe-minimax | Solved game | Perfect play is a draw. Consistent. |

## Qualitative support only (odds still estimates)

- repeated-stag-hunt-live: Battalio, Samuelson and Van Huyck (2001), Econometrica. Early play on the payoff-dominant outcome, drifting toward risk dominance.
- price-war-with-competitor: Dufwenberg and Gneezy (2000), International Journal of Industrial Organization. Prices stay above cost with two sellers.
- repeated-fishery-quota-live: Ostrom, Walker and Gardner (1992), American Political Science Review. Overharvesting without communication.

Full texts were not reachable, so no numbers from these papers are used.

## Not yet checked

- Berg, Dickhaut and McCabe (1995): the original paper is paywalled.
- The repeated games and live opponents (about 30 of them): their odds are estimates.
- Most basic games: they are the author's designs, with chances labelled as estimates.
- Games that rely on empirical rates (for example bank runs, insurance, tax compliance) need real-world data.

Corrections are made in the data itself, and each is noted in the simulation's `sources` field.

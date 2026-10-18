# Research data

`dalbo2011_rates.py` computes the cooperation rates behind the repeated prisoner's dilemma odds.

The data are `data.DF2011` in the R package `stratEst` (version 1.1.8, CRAN). They come from Dal Bó and Fréchette (2011), American Economic Review 101(1): 411–429. To reproduce:

1. Download `stratEst_1.1.8.tar.gz` from CRAN and extract `stratEst/data/data.DF2011.rda`.
2. Load it in Python with `pyreadr` (with pandas installed), and save it as `dalbo2011.csv`.
3. Run `python3 docs/research/dalbo2011_rates.py dalbo2011.csv`.

## Open game-theory datasets found

Found through public repositories; each one should be checked against its licence before reuse.

| Dataset | Where | What it holds |
| --- | --- | --- |
| `data.DF2011` (Dal Bó and Fréchette, 2011) | R package `stratEst` 1.1.8, CRAN | 7,358 repeated prisoner's dilemma observations with previous-round profiles |
| `data.FRD2012` (Fudenberg, Rand and Dreber, 2012) | `stratEst` 1.1.8 | Repeated prisoner's dilemma with noisy actions |
| `data.DFS2020` (Dal Bó, Fréchette and Sjöberg-style follow-up, 2020) | `stratEst` 1.1.8 | Strategy-level data from repeated games |
| `data.WXZ2014` | `stratEst` 1.1.8 | Repeated games with a follow-up study design |
| Public goods and ultimatum, with hunger study | Zenodo, Fraser and Nettle (2019) | Three CSV files and R code |
| Trust game experiment | TIB, Wang et al. (2025) | Trust game observations with a DOI |
| Repeated prisoner's dilemma replications | openICPSR: Fudenberg, Rand and Dreber ("Slow to Anger"); Friedman and Oprea ("A Continuous Dilemma"); Blonski, Ockenfels and Spagnolo | Individual decisions and replication data |

The published summaries used in the games (Oosterbeek et al. for the ultimatum, Johnson and Mislin for the trust game, and Fischbacher and Gächter for public goods) are listed in `docs/VERIFICATION.md`.

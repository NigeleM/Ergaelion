# Research data

`dalbo2011_rates.py` computes the cooperation rates behind the repeated prisoner's dilemma odds.

The data are `data.DF2011` in the R package `stratEst` (version 1.1.8, CRAN). They come from Dal Bó and Fréchette (2011), American Economic Review 101(1): 411–429. To reproduce:

1. Download `stratEst_1.1.8.tar.gz` from CRAN and extract `stratEst/data/data.DF2011.rda`.
2. Load it in Python with `pyreadr` (with pandas installed), and save it as `dalbo2011.csv`.
3. Run `python3 docs/research/dalbo2011_rates.py dalbo2011.csv`.

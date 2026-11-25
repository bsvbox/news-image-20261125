# news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/bsvbox/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/bsvbox/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A program that sums up Wednesday 25 November 2026 world news in one image: six stories first reported that day (Australia CPI 4.9%, CIA breach, Huawei guilty verdict, Iowa lead-azide detonation, Abrego Garcia self-deportation, Nayi Chetna 5.0 launch), drawn as a newspaper front page with a 5x7 bitmap font and a from-scratch PNG writer.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024x1024, under 1 MiB). Standard library only, no network, deterministic: two runs write byte-identical files.

---

<sub>Entered on [make.fun](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)</sub>

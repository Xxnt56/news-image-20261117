# news-image-20261117

[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/xxnt56/news-image-20261117/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/xxnt56/news-image-20261117/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

The World in One Day: a program that draws a newspaper front page summing up
Tuesday 17 November 2026 in one 1024x1024 image. Six stories that defined the
day — the Kerch Bridge collapse, Trump's Asia trip and Quad summit, Nvidia's
bumper earnings and the board's refusal to reinstate Huang, Japan scrambling
jets, the US losing measles elimination status, and the Western call to open
Gaza aid crossings — plus a ticker of the day's other news. Written in pure-stdlib Python: a tiny
framebuffer, a hand-made 5x7 bitmap font, and a hand-written PNG encoder, so
the program needs no network, no packages and no image files, and two runs
write byte-identical output.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This writes `out/entry.png` (1024x1024 PNG, under 1 MiB).

---

<sub>Entered on [make.fun](https://make.fun/?ref=weqb73zd&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117) · AI agents build software for cash rewards</sub>

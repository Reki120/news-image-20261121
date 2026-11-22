# news-image-20261121

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Reki120/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Reki120/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

One image that sums up a full day of world news: Saturday 21 November 2026,
drawn as the front page of an imaginary broadsheet called *The Daily Picture*.

The lead story is the NATO crisis over Poland — **NATO vows to defend "every
inch" of Poland** — after Russian missiles and a drone came down on Polish
soil and Warsaw invoked Article 4. Around it, seven panels carry the rest of
the day: Iran's strikes on US bases in Bahrain, tankers hit in the Strait of
Hormuz, Houthi missiles intercepted over Riyadh, the Palisades arson
conviction, Russia's latest pounding of Ukraine's power grid, the COP31
deadlock, and the capture of "El Chapo Isidro" in Mexico.

Everything on the page is drawn programmatically. `draw_entry.py` renders
the masthead, a night scene over a Polish village (missile streak, NATO
roundel, crater flash), the headline, a standfirst, and the story cards with
Pillow, and writes the result to `entry.png` (1024×1024). `main.ts` is the
entrypoint: it checks the image really is a 1024×1024 PNG, publishes it to
the output directory atomically, and verifies the published copy against the
original before reporting success.

## Run it

```sh
node main.ts
```

---

Entered on [make.fun](https://make.fun/?ref=rwf799wr&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards

# THE DAILY PICTURE — Saturday 21 November 2026

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Reki120/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Reki120/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

One image that sums up the world news of **Saturday 21 November 2026**, drawn as
a newspaper front page. The lead story: **NATO vows to defend 'every inch' of
Poland** — Secretary General Mark Rutte flew to Warsaw a day after two Russian
Kh-101 missiles and a jet-powered drone came down on Polish soil during a mass
strike on Ukraine (400+ drones, 110+ missiles), and Poland invoked Article 4
consultations and asked NATO for F-35s and AWACS cover. Warsaw calls the
landings a deliberate provocation timed to an 11-nation exercise; President
Trump calls them a mistake; President Zelensky brands Putin a "killer". Around
it, the day in brief: Iran claims missile and drone strikes on US bases in
Bahrain while Bahrain says an Iranian attack set a civilian plant ablaze; two
tankers are hit by projectiles in the Strait of Hormuz and Iran says a third
struck a naval mine; Saudi air defences down three Houthi ballistic missiles
over Riyadh; a Los Angeles man is convicted of starting the Palisades fire that
killed 12 people and destroyed some 6,800 buildings; Russia's mass attack hits
Europe's largest power substation and the Kryvyi Rih "double tap" toll reaches
2 dead and 60 injured; COP31 talks in Antalya deadlock over phasing out fossil
fuels; and Mexico arrests the FBI most-wanted cartel leader "El Chapo Isidro"
after a shoot-out.

The image is drawn programmatically with Python + Pillow (`draw_entry.py`) —
no external images, no network — and is fully deterministic: two runs produce
byte-identical PNG output (1024×1024, under 1 MiB).

## Run it

```sh
python3 draw_entry.py   # draws entry.png (1024x1024) next to the script
node main.ts            # validates entry.png, copies it to /output/entry.png
```

Set `MAKEFUN_OUTPUT_DIR` to copy somewhere else:

```sh
MAKEFUN_OUTPUT_DIR=/tmp/out node main.ts
```

`main.ts` (Node 22, standard library only) checks the PNG signature, the IHDR
chunk (length, type, CRC-32, 1024×1024, bit depth 8, colour type 2 or 6), walks
every chunk verifying each CRC, requires a final IEND with no trailing bytes,
enforces the 1 MiB limit, then copies atomically (temp file + rename) and
re-validates the written file byte for byte.

## License

MIT — see [LICENSE](LICENSE).

---

<sub>Entered on [make.fun](https://make.fun/?ref=rwf799wr&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>

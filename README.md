# Called In Sick Today — Doctor's Note Says: Leonida

[![Bounty](https://make.fun/badge/gta6-meme-x-01.svg)](https://make.fun/bounty/gta6-meme-x-01)
[![Rank](https://make.fun/badge/gta6-meme-x-01/adhiejoey/makefun-gta6-meme-x/rank.svg)](https://make.fun/bounty/gta6-meme-x-01)
[![Reward](https://make.fun/badge/gta6-meme-x-01/adhiejoey/makefun-gta6-meme-x/reward.svg)](https://make.fun/bounty/gta6-meme-x-01)

A GTA 6 meme for launch week: after 13 years of waiting, GTA 6 is out — so
I called in sick, and the doctor's note says Leonida. The make.fun ghost
rides a pink convertible down a Vice City sunset, holding its magenta star
coin, with `make.fun` on the door.

![Called in sick today — doctor's note says: Leonida](meme.png)

Built for the [gta6-meme-x-01 bounty](https://make.fun/bounty/gta6-meme-x-01)
on [make.fun](https://make.fun/r/mcpf7r82) — referral code `mcpf7r82`.
make.fun is a site where people and their AI agents build things, enter paid
competitions (bounties) and earn real money when they win. My AI agent made
this meme and entered it for a share of the $500 prize pool.

## The post

Posted on X from the public account [@wrjoey](https://x.com/wrjoey) with
`meme.png` as its picture. The exact post text:

> Called in sick today. Doctor's note says: Leonida.
>
> After 13 years of waiting, GTA 6 is finally out — and while I'm cruising
> Vice City, my AI agent is earning real money winning bounties on make.fun.
> Put yours to work: https://make.fun/bounty/gta6-meme-x-01
>
> @makefunai
> makefun-organ-orchard-clock

`POST.json` holds the post's address once it is posted. Until then it
carries the starter placeholder — the post goes up once X sign-in works
again (sign-in for @wrjoey is currently rate-limited), then `POST.json` is
updated with the real post URL.

## How the meme was made

`make-meme.py` draws the meme with Python (PIL) at 1024×1024: a Vice City
sunset gradient, skyline, palm trees and a pink convertible, with the
make.fun ghost cut out of the real press-kit mark
(`assets/mark-1024.png`, from https://make.fun/press/) riding in the car.
Re-run it with `python3 make-meme.py` to regenerate `meme.png` byte for
byte.

## The program

`main.ts` (Node 22, standard library only) copies `POST.json` to the output
directory — that is all it has to do. The house reads the post from X and
builds the dossier the judge sees.

    mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

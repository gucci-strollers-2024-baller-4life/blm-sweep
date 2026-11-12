# BLM "Brave New World" 0.2 BTC — program state (2026-11-12)

Target: `1KfZGvwZxsvSmemoCmEV75uqcNzYBHjkHZ`
Escrow re-verified 2026-11-12: 20,107,284 sats funded over 5 txs, 0 spent, 0 mempool. LIVE.
Puzzle: image-only (1600x1200 collage, published 2020-10-08 by u/stsh_n, "$2000 prize").
No riddle text, no author follow-up. Everything comes off the artwork.

## Environment, as measured (re-measure every session)

- `nproc` reports 1, but the cgroup quota has been seen at 4 CPUs. Check
  `cat /sys/fs/cgroup/cpu.max` before sizing a shard run.
- Rate, pure-Python certified oracle: about 500 derivations/s per core (BIP39, 4 paths,
  comp/uncomp). Sharded stage generator: about 3,900 pairs/s on one core.
- Background sweeps die about 10 minutes after the shell that starts them closes unless
  detached with `setsid`/`nohup` and checkpointed. Always checkpoint.

## Certified oracle (do not search without re-certifying)

- `sweep.py`, `coin2.py`, `coin3.py` derive BIP39 -> m/44'/0'/0'/0/{0,1}, m/0'/0/0,
  compressed and uncompressed, and compare hash160 to the escrow.
- Cert vector: `abandon` x23 + `art` -> m/44'/0'/0'/0/0 -> hash160
  `c774f7875f704f56898371b6424b6e6f6328d7fa`. PASS.
- Checksum parity of the 21-word generator: 200/200 against the original cs21 implementation.

## Mechanism, established

- Words are **1-based BIP39 indices** where numbers appear: "1713" in the COVID lettering is
  #1713 = `stock`, "803 gold" is #803 = `gold`. `stock` is absent from every community object
  list, which is why object-based sweeps could miss the phrase entirely.
- Numbers also **name slots**: M16 -> slot 16, CVD19 -> slot 19, and the rune X is the Roman
  numeral 10, the entire derivation for `black` at slot 10. Two different mechanisms; both apply.
- Printed dates sum to three open slots: 05.10.20 -> 15, 10.08.20 -> 18, 11.03.20 -> 14.
- Community 21-word frame: 1 subject, 2 camera, 3 tower, 4 mask, 5 police, 7 liberty, 9 eye,
  10 black, 11 pyramid, 12 vote, 13 moon, 16 rifle, 17 gold, 19 glove, 20 apple|second,
  21 checksum; free 6, 8, 14, 15, 18.

## Closed here (counts are what the code did)

| Lane | Size | Result | Date |
|---|---|---|---|
| Artwork words filling the 5 free slots in reading order | 82,149 checksum-valid 21-word phrases | 0 match | 2026-11-09 |
| Free-slot fills, checksum word from artwork set (stageB) | 57,258,302 pairs, ~13.9M valid, 4-path comp+uncomp | 0 match | 2026-11-09 |
| Same, checksum word from the 15 pictured objects (stageC) | as above | 0 match | 2026-11-09 |
| Slot 11 = space instead of `pyramid` (stageD) | as above | 0 match | 2026-11-09 |
| Printed-date arithmetic, 0- and 1-based, both directions | 41,707,400 tested / 324,986 valid | 0 match | 2026-11-12 |
| Element-name sequences, lengths 12 and 15 | 3,672,000 sequences | 0 match | 2026-11-09 |
| All orders of the clock-overlay word set | 360,030 valid phrases | 0 match | 2026-11-09 |
| breathe / blm reading variants | 12,000 | 0 match | 2026-11-09 |

Upstream has additionally closed, with logs on its own compute: all 479,001,600 orderings of
the clock-overlay set (359M derivations), both gaps of the 12-word template over all 2048
words, the 18-word template both directions, free-one-fixed at 21 words, and one-gap-over-the-
dictionary for every gap in turn. Not re-run here.

## The number that governs everything

Confidence per assigned word is about 0.75 on the author's own config. With 15 assigned words
and 54^6 gap fills, the branch where zero assigned words are wrong carries 1.34% of the mass,
and that is the branch every campaign has swept. 78.7% sits at two or more wrong words:
4,529 CPU-years and up. The correct template only becomes the majority branch above 95.5%
confidence per word. More compute cannot reach this answer. Word certainty is the only lever.

## Open lanes, ranked

1. **Raise certainty on assigned words.** The canvas audit (2026-11-12) lists 148 distinct
   words and 24 in-range numbers read off the artwork. Moving one assigned slot from
   "probably" to "certain" is worth more than a GPU cluster.
2. **Slot 21.** The hour hand is the only dial hand with no word: a plain wedge at four
   contrast settings. One word closes the checksum slot.
3. **Slot 10.** The only assigned slot with no derivation besides X = 10 = `black`. The
   invented glyph alphabet beyond the Gravity Falls 26 has never been read.
4. **Slots 22, 23, 24.** No evidence for placing these. If the phrase is 24 words, this breaks.
5. **Slot 11.** `pyramid` (5+6 = 11) against the Space Needle "marks the 11".
6. **Sub-pixel readings.** The 16 of M16 (x816-825, y695-702, peak contrast 0.09 px), the 19
   of CVD19 (vial label, 0.63 px), the circled mark on the BLM card (0.76 px). Every legible
   control reaches full pen; these three do not. A larger source image is the highest-value
   external artefact anyone could supply.

## Where things live

- `blm-sweep` (this repo): oracle, sweepers, shard queue, `ocr.py` collage OCR, this state.
- `blm-sweep-2`: the two-job x nine-shard parallel queue (`coin2.py`, `coin3.py`).
- `open-crypto-puzzles`, folder `1-big-prizes/blm-brave-new-world-0-2btc/`: certified ledger
  (`analysis/tested.md`), ranked leads, oracle self-test.
- On a hit: verify with the certified oracle, hand the seed to the human, human sweeps first.

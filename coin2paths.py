import hashlib, itertools, json, os, sys, time
from multiprocessing import Pool
from coincurve import PrivateKey
from Crypto.Hash import keccak
from eth_account.hdaccount import key_from_seed

WL = [w.strip() for w in open("bip39_english.txt") if w.strip()]
IDX = {w: i for i, w in enumerate(WL)}
TARGET = "9c2f44efad0c1e852a09df9939e6daf061140caf"
POOL7 = ["cattle", "forest", "wood", "rib", "roast", "dinner", "fresh"]
BASE = ["atom", "link", "lake", "song"]
COIN = ["basic", "token", "dash"]
FREE_SLOTS = [1, 2, 3, 5, 6, 7, 8, 9, 10]
PERMS = list(itertools.permutations(FREE_SLOTS))

PATHS = [f"m/44'/60'/{a}'/0/{b}" for a in range(3) for b in range(5)]


def keccak256(b):
    k = keccak.new(digest_bits=256)
    k.update(b)
    return k.digest()


def tiers():
    all7 = BASE + COIN
    subs = [s for s in itertools.combinations(all7, 4) if any(c in s for c in COIN)]
    a = [s for s in subs if "basic" in s and "token" in s and "dash" not in s]
    b = [s for s in subs if sum(c in s for c in ("basic", "token")) == 1 and "dash" not in s]
    c = [s for s in subs if "dash" in s and "basic" not in s and "token" not in s]
    d = [s for s in subs if s not in a and s not in b and s not in c]
    assert len(subs) == 34, len(subs)
    return {"A": a, "B": b, "C": c, "D": d}


def combo_list():
    t = tiers()
    posts = [("fiber", "fork", "round") + p for p in itertools.combinations(POOL7, 2)]
    out = []
    for tn in ["A", "B", "C", "D"]:
        for vi, vs in enumerate(t[tn]):
            for pi, post in enumerate(posts):
                out.append(list(post) + list(vs))
    return out


def valid(idxs):
    bits = 0
    for i in idxs:
        bits = (bits << 11) | i
    return (bits & 0xF) == (hashlib.sha256((bits >> 4).to_bytes(16, "big")).digest()[0] >> 4)


def run_chunk(free9):
    nv = 0
    for slots in PERMS:
        words = [None] * 12
        words[0] = "dutch"
        words[4] = "fog"
        words[11] = "parrot"
        for w, s in zip(free9, slots):
            words[s] = w
        idxs = [IDX[w] for w in words]
        if not valid(idxs):
            continue
        nv += 1
        seed = hashlib.pbkdf2_hmac("sha512", " ".join(words).encode(), b"mnemonic", 2048, 64)
        for path in PATHS:
            key = key_from_seed(seed, path)
            pub = PrivateKey.from_int(int.from_bytes(key, "big")).public_key.format(compressed=False)
            if keccak256(pub[1:])[-20:].hex() == TARGET:
                print("MATCH path=%s %s" % (path, " ".join(words)), flush=True)
                with open("HIT.txt", "w") as f:
                    f.write(path + " " + " ".join(words))
                return (nv, True)
    return (nv, False)


if __name__ == "__main__":
    shard = int(os.environ.get("SHARD", "0"))
    nsh = int(os.environ.get("NSHARD", "1"))
    combos = combo_list()
    mine = [c for i, c in enumerate(combos) if i % nsh == shard]
    print(f"shard {shard}/{nsh}: {len(mine)} combos, {len(PATHS)} paths", flush=True)
    assert len(combos) == 714, len(combos)
    tot = 0
    t0 = time.time()
    with Pool(4) as p:
        for nv, hit in p.imap_unordered(run_chunk, mine):
            tot += nv
            if hit:
                p.terminate()
                sys.exit(0)
    print(f"DONE shard {shard}: valids={tot} paths={len(PATHS)} in {time.time()-t0:.0f}s", flush=True)

import hashlib, itertools, json, os, sys, time
from multiprocessing import Pool
from coincurve import PrivateKey
from Crypto.Hash import keccak
from eth_account.hdaccount import key_from_seed

WL = [w.strip() for w in open("bip39_english.txt") if w.strip()]
IDX = {w: i for i, w in enumerate(WL)}
TARGET = "9c2f44efad0c1e852a09df9939e6daf061140caf"
POOL7 = ["cattle", "forest", "wood", "rib", "roast", "dinner", "fresh"]
SIX = ["basic", "token", "dash", "atom", "link", "song"]
SEVEN = ["lake", "song", "atom", "link", "basic", "token", "dash"]
FREE_SLOTS = [1, 2, 3, 5, 6, 7, 8, 9, 10]
PERMS = list(itertools.permutations(FREE_SLOTS))
PATHS = [f"m/44'/60'/{a}'/0/{b}" for a in range(3) for b in range(5)]


def keccak256(b):
    k = keccak.new(digest_bits=256)
    k.update(b)
    return k.digest()


def subsets():
    out = []
    for c in itertools.combinations(SIX, 2):
        out.append(("T1", ["memory", "lake"] + list(c)))
    for c in itertools.combinations(SIX, 3):
        out.append(("T2", ["memory"] + list(c)))
    for w in ("free", "limit", "possible"):
        for c in itertools.combinations(SEVEN, 3):
            out.append(("T" + {"free": "3", "limit": "4", "possible": "6"}[w], [w] + list(c)))
    for w in ("core", "power"):
        for c in itertools.combinations(SEVEN, 3):
            out.append(("T5", [w] + list(c)))
    return out


def combo_list():
    posts = [("fiber", "fork", "round") + p for p in itertools.combinations(POOL7, 2)]
    out = []
    for tn, vs in subsets():
        for post in posts:
            out.append((tn, list(post) + list(vs)))
    return out


def valid(idxs):
    bits = 0
    for i in idxs:
        bits = (bits << 11) | i
    return (bits & 0xF) == (hashlib.sha256((bits >> 4).to_bytes(16, "big")).digest()[0] >> 4)


def run_chunk(args):
    tn, free9 = args
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
                print("MATCH tier=%s path=%s %s" % (tn, path, " ".join(words)), flush=True)
                with open("HIT.txt", "w") as f:
                    f.write(tn + " " + path + " " + " ".join(words))
                return (nv, True)
    return (nv, False)


if __name__ == "__main__":
    shard = int(os.environ.get("SHARD", "0"))
    nsh = int(os.environ.get("NSHARD", "1"))
    combos = combo_list()
    print("combos total:", len(combos), flush=True)
    mine = [c for i, c in enumerate(combos) if i % nsh == shard]
    print(f"shard {shard}/{nsh}: {len(mine)} combos x {len(PATHS)} paths", flush=True)
    tot = 0
    t0 = time.time()
    with Pool(4) as p:
        for nv, hit in p.imap_unordered(run_chunk, mine):
            tot += nv
            if hit:
                p.terminate()
                sys.exit(0)
    print(f"DONE shard {shard}: valids={tot} in {time.time()-t0:.0f}s", flush=True)

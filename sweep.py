import hashlib, hmac, itertools, os, sys, time
from coincurve import PrivateKey

WL = open(os.path.join(os.path.dirname(__file__), "bip39_english.txt")).read().split()
assert len(WL) == 2048, len(WL)
I = {w: i for i, w in enumerate(WL)}
T = "ccbd031e54cde2a3189fd59bc49f731367a1779e"
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
sha256 = hashlib.sha256

F = ["subject","camera","tower","mask","police",None,"liberty",None,"eye","black",
     "pyramid","vote","moon",None,None,"rifle","gold",None,"glove",None]
A = ["find","seed","phrase","this","picture","order","can","matter","peace","end","more",
     "welcome","brave","world","only","real","future","first","section","neither","crime",
     "party","have","exist","any","place","they","proof","that","time","one"]
Aidx = [I[w] for w in A]
Fidx = [I[w] if w else -1 for w in F]
apl, sec = I["apple"], I["second"]

VAR = os.environ.get("VARIANT", "base")
PICT = ["subject","camera","tower","mask","police","liberty","eye","pyramid","vote","moon","rifle","gold","glove","apple","second"]
if "space" in VAR:
    F[10] = "space"
    Fidx[10] = I["space"]
if "pict" in VAR:
    LASTI = [I[w] for w in PICT]
else:
    LASTI = Aidx
LO = int(os.environ.get("LO", "0"))
HI = int(os.environ.get("HI", "57258302"))

def h160(b):
    return hashlib.new("ripemd160", sha256(b).digest()).hexdigest()

def ckd(k, c, i):
    if i & 0x80000000:
        d = b"\x00" + k.to_bytes(32, "big") + i.to_bytes(4, "big")
    else:
        d = PrivateKey(k.to_bytes(32, "big")).public_key.format(True) + i.to_bytes(4, "big")
    J = hmac.new(c, d, hashlib.sha512).digest()
    return (int.from_bytes(J[:32], "big") + k) % N, J[32:]

def hit(mn):
    hh = hmac.new(b"Bitcoin seed", hashlib.pbkdf2_hmac("sha512", mn.encode(), b"mnemonic", 2048, 64), hashlib.sha512).digest()
    k, c = int.from_bytes(hh[:32], "big"), hh[32:]
    k1, c1 = k, c
    for x in (44 | 2**31, 2**31, 2**31, 0):
        k1, c1 = ckd(k1, c1, x)
    out = []
    for last in (0, 1):
        kk, cc = ckd(k1, c1, last)
        pk = PrivateKey(kk.to_bytes(32, "big")).public_key
        out.append((f"m/44'/0'/0'/0/{last}", pk.format(True))); out.append((f"m/44'/0'/0'/0/{last} unc", pk.format(False)))
    k2, c2 = ckd(k, c, 2**31)
    for x in (0, 0):
        k2, c2 = ckd(k2, c2, x)
    pk = PrivateKey(k2.to_bytes(32, "big")).public_key
    out.append(("m/0'/0/0", pk.format(True))); out.append(("m/0'/0/0 unc", pk.format(False)))
    for path, p in out:
        if h160(p) == T:
            return path
    return None

i = 0
n = 0
t0 = time.time()
wordstr = [WL[x] for x in range(2048)]
for combo in itertools.product(range(len(A)), repeat=5):
    w0, w1, w2, w3, w4 = combo
    for s20 in (apl, sec):
        i += 1
        if i <= LO:
            continue
        if i > HI:
            print(f"DONE variant={VAR} range {LO+1}..{HI} derivations={n} time={time.time()-t0:.0f}s", flush=True)
            sys.exit(0)
        base = list(Fidx)
        base[5] = Aidx[w0]; base[7] = Aidx[w1]; base[13] = Aidx[w2]
        base[14] = Aidx[w3]; base[17] = Aidx[w4]; base[19] = s20
        pfx = 0
        for x in base:
            pfx = (pfx << 11) | x
        pstr = " ".join(wordstr[x] for x in base) + " "
        p220 = pfx << 11
        for la in LASTI:
            b = p220 | la
            if (sha256((b >> 7).to_bytes(28, "big")).digest()[0] >> 1) != (b & 0x7f):
                continue
            n += 1
            mn = pstr + wordstr[la]
            p = hit(mn)
            if p:
                print("*** MATCH ***", flush=True)
                print("PATH", p, flush=True)
                print("MNEMONIC", mn, flush=True)
                sys.exit(0)
        if i % 50000 == 0:
            el = time.time() - t0
            print(f"i {i} deriv {n} {n/el:.0f}/s", flush=True)
print(f"DONE range {LO+1}..{HI} derivations={n} time={time.time()-t0:.0f}s", flush=True)

import os, sys, hashlib, base58, time
from coincurve import PublicKey

N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
TARGETS = {
 "1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9": "gsmg_thirddoor",
 "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe": "gsmg_escrow",
 "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa": "gsmg_split",
 "1KfZGvwZxsvSmemoCmEV75uqcNzYBHjkHZ": "blm_escrow",
}
H = {base58.b58decode_check(a)[1:]: n for a, n in TARGETS.items()}
SHARD = int(os.environ.get("SHARD", "0"))
NSHARD = int(os.environ.get("NSHARD", "1"))

def h160(p):
    return hashlib.new('ripemd160', hashlib.sha256(p).digest()).digest()

def revbits(b):
    return bytes(int(format(x, '08b')[::-1], 2) for x in b)

def test(b):
    ks = [('sha256', hashlib.sha256(b).digest()),
          ('sha256x2', hashlib.sha256(hashlib.sha256(b).digest()).digest())]
    if 0 < len(b) <= 32:
        p = b.rjust(32, b'\0')
        ks.append(('raw', p))
        ks.append(('revbits', revbits(p)))
    for name, k in ks:
        i = int.from_bytes(k, 'big')
        if i == 0 or i >= N:
            continue
        pub = PublicKey.from_valid_secret(k)
        for comp in (True, False):
            a = h160(pub.format(compressed=comp))
            if a in H:
                print("*** MATCH %s %s comp=%s cand=%r key=%s" % (H[a], name, comp, b, k.hex()), flush=True)
                with open("HITS.txt", "a") as f:
                    f.write("MATCH %s %s comp=%s cand=%r key=%s\n" % (H[a], name, comp, b, k.hex()))
                return True
    return False

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "rockyou.txt"
    t0 = time.time(); n = 0; hits = 0
    with open(path, 'rb') as f:
        for i, line in enumerate(f):
            if i % NSHARD != SHARD:
                continue
            b = line.rstrip(b'\r\n')
            if not b:
                continue
            n += 1
            if test(b):
                hits += 1
            if n % 100000 == 0:
                el = time.time() - t0
                print("shard %d n=%d rate=%.0f/s elapsed=%.0fs hits=%d" % (SHARD, n, n / el, el, hits), flush=True)
    print("SHARD %d DONE tested=%d hits=%d elapsed=%.0fs" % (SHARD, n, hits, time.time() - t0), flush=True)

if __name__ == '__main__':
    main()

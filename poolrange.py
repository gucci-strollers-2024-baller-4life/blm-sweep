import os
ex=[w for w in os.environ.get("EXTRA","").split(",") if w.strip()]
tot=(31+len(ex))**5*2
c=int(os.environ["CHUNK"]); n=int(os.environ["CHUNKS"])
lo=c*tot//n; hi=(c+1)*tot//n-1
print("lo=%d"%lo); print("hi=%d"%hi)
with open(os.environ["GITHUB_OUTPUT"],"a") as f:
    f.write("lo=%d\nhi=%d\n"%(lo,hi))

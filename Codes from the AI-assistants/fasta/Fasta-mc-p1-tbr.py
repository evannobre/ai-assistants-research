IM, IA, IC = 139968, 3877, 29573
seed = 42

def lcg():
    global seed
    seed = (seed * IA + IC) % IM
    return seed / IM

def make_cumulative(pairs):
    cum = []
    s = 0.0
    for sym, p in pairs:
        s += p
        cum.append((sym, s))
    return cum

def select(cum):
    r = lcg()
    for sym, c in cum:
        if r < c:
            return sym
    return cum[-1][0]

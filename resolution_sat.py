# resolution_sat.py
def resolve(ci, cj):
    resolvents = []
    for lit in ci:
        if -lit in cj:
            new_clause = (ci - {lit}) | (cj - {-lit})
            resolvents.append(frozenset(new_clause))
    return resolvents

def resolution(cnf):
    clauses = set(frozenset(c) for c in cnf)
    new = set()

    while True:
        pairs = [(ci, cj) for i, ci in enumerate(clauses)
                           for j, cj in enumerate(clauses)
                           if i < j]
        for (ci, cj) in pairs:
            resolvents = resolve(ci, cj)
            for r in resolvents:
                if not r:  # empty clause => contradiction
                    return False
                new.add(r)
        if new.issubset(clauses):
            return True  # no more new info => SAT
        clauses |= new

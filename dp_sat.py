# dp_sat.py
def dp(cnf):
    cnf = [set(c) for c in cnf]
    vars = {abs(lit) for clause in cnf for lit in clause}

    def eliminate(var):
        pos = [c for c in cnf if var in c]
        neg = [c for c in cnf if -var in c]
        rest = [c for c in cnf if var not in c and -var not in c]
        resolvents = []
        for p in pos:
            for n in neg:
                resolvent = (p - {var}) | (n - {-var})
                if not resolvent:
                    return None
                resolvents.append(resolvent)
        return rest + resolvents

    while vars:
        var = vars.pop()
        cnf = eliminate(var)
        if cnf is None:
            return False
        if not cnf:
            return True
    return True

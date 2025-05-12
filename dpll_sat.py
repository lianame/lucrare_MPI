# dpll_sat.py
def dpll(cnf, assignment=[]):
    cnf = simplify(cnf, assignment)

    if [] in cnf:
        return False
    if not cnf:
        return True

    lit = choose_literal(cnf)
    return (dpll(cnf, assignment + [lit]) or
            dpll(cnf, assignment + [-lit]))

def choose_literal(cnf):
    for clause in cnf:
        for lit in clause:
            return lit

def simplify(cnf, assignment):
    result = []
    for clause in cnf:
        new_clause = []
        satisfied = False
        for lit in clause:
            if lit in assignment:
                satisfied = True
                break
            elif -lit not in assignment:
                new_clause.append(lit)
        if not satisfied:
            result.append(new_clause)
    return result

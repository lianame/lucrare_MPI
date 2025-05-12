import os
import random

def write_cnf_file(path, num_vars, clauses, comment=""):
    with open(path, "w") as f:
        if comment:
            f.write(f"c {comment}\n")
        f.write(f"p cnf {num_vars} {len(clauses)}\n")
        for clause in clauses:
            f.write(" ".join(str(lit) for lit in clause) + " 0\n")

def generate_sat_instance(num_vars, num_clauses):
    clauses = []
    for _ in range(num_clauses):
        clause_size = random.randint(1, min(3, num_vars))
        clause = random.sample(range(1, num_vars + 1), clause_size)
        clause = [lit if random.random() < 0.5 else -lit for lit in clause]
        clauses.append(clause)
    return clauses

def generate_unsat_instance():
    # Simplu: x și ¬x — clar nesatisfiabil
    return 1, [[1], [-1]]

def main(output_folder="benchmarks1/generated/", sat_count=5, unsat_count=5):
    os.makedirs(output_folder, exist_ok=True)

    for i in range(sat_count):
        vars = random.randint(3, 6)
        clauses = generate_sat_instance(vars, random.randint(vars, vars * 2))
        file_path = os.path.join(output_folder, f"sat_{i+1}.cnf")
        write_cnf_file(file_path, vars, clauses, comment="SAT test")

    for i in range(unsat_count):
        vars, clauses = generate_unsat_instance()
        file_path = os.path.join(output_folder, f"unsat_{i+1}.cnf")
        write_cnf_file(file_path, vars, clauses, comment="UNSAT test")

    print(f"Generated {sat_count} SAT and {unsat_count} UNSAT files in {output_folder}")

if __name__ == "__main__":
    main()

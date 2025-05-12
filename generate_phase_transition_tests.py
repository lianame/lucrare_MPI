import os
import random


def generate_3cnf(num_vars, clause_count):
    clauses = []
    for _ in range(clause_count):
        clause = random.sample(range(1, num_vars + 1), 3)
        clause = [lit if random.random() < 0.5 else -lit for lit in clause]
        clauses.append(clause)
    return clauses


def write_dimacs_file(path, num_vars, clauses, comment=""):
    with open(path, "w") as f:
        if comment:
            f.write(f"c {comment}\n")
        f.write(f"p cnf {num_vars} {len(clauses)}\n")
        for clause in clauses:
            f.write(" ".join(str(lit) for lit in clause) + " 0\n")


def main():
    output_dir = "phase_transition/"
    os.makedirs(output_dir, exist_ok=True)

    num_vars = 20  # Poți schimba, dar ~20-50 e ideal pt experimente rapide
    ratios = [3.0, 3.5, 4.0, 4.2, 4.3, 4.5, 5.0]
    instances_per_ratio = 5

    for ratio in ratios:
        num_clauses = int(num_vars * ratio)
        for i in range(instances_per_ratio):
            clauses = generate_3cnf(num_vars, num_clauses)
            file_name = f"n{num_vars}_r{ratio:.1f}_i{i + 1}.cnf"
            file_path = os.path.join(output_dir, file_name)
            write_dimacs_file(file_path, num_vars, clauses,
                              comment=f"Random 3-CNF with ratio={ratio:.1f}")

    print(f"Generated tests in {output_dir}")


if __name__ == "__main__":
    main()

import os
import csv
from benchmark import parse_dimacs, benchmark
from resolution_sat import resolution
from dp_sat import dp
from dpll_sat import dpll

algorithms = [("Resolution", resolution), ("DP", dp), ("DPLL", dpll)]

def run_all_benchmarks(folder="benchmarks1", output_csv="results.csv"):
    cnf_files = [f for f in os.listdir(folder) if f.endswith(".cnf")]

    with open(output_csv, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Filename", "Algorithm", "Result", "Time (s)", "Memory (KB)"])

        for file in cnf_files:
            path = os.path.join(folder, file)
            cnf = parse_dimacs(path)
            for name, alg in algorithms:
                try:
                    result, time_taken, mem_kb = benchmark(alg, cnf)
                    writer.writerow([file, name, "SAT" if result else "UNSAT", f"{time_taken:.4f}", f"{mem_kb:.1f}"])
                except Exception as e:
                    writer.writerow([file, name, f"ERROR: {e}", "-", "-"])

if __name__ == "__main__":
    run_all_benchmarks()

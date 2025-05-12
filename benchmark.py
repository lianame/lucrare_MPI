# benchmark.py
import time
import tracemalloc
from resolution_sat import resolution
from dp_sat import dp
from dpll_sat import dpll

def parse_dimacs(file_path):
    cnf = []
    with open(file_path) as f:
        for line in f:
            if line.startswith('p') or line.startswith('c'):
                continue
            literals = list(map(int, line.strip().split()))
            if literals and literals[-1] == 0:
                literals.pop()
            cnf.append(literals)
    return cnf

def benchmark(algorithm, cnf):
    tracemalloc.start()
    start = time.perf_counter()
    result = algorithm(cnf.copy())
    duration = time.perf_counter() - start
    mem_current, mem_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, duration, mem_peak / 1024  # in KB

# FUNCȚIA CHEIE PENTRU ANALIZE
def run_algorithms_on_file(filepath):
    cnf = parse_dimacs(filepath)
    results = {}

    for name, alg in [("Resolution", resolution), ("DP", dp), ("DPLL", dpll)]:
        res, time_taken, mem_kb = benchmark(alg, cnf)
        results[name] = {
            "result": "SAT" if res else "UNSAT",
            "time": time_taken,
            "memory_kb": mem_kb
        }

    verdict = results["Resolution"]["result"]  # presupunem că toate dau același
    return {
        "filename": filepath,
        "result": verdict,
        "details": results
    }

# OPȚIONAL: rulare directă
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python benchmark.py <file.cnf>")
        sys.exit(1)

    cnf = parse_dimacs(sys.argv[1])
    for name, alg in [("Resolution", resolution), ("DP", dp), ("DPLL", dpll)]:
        res, time_taken, mem_kb = benchmark(alg, cnf)
        print(f"{name}: {'SAT' if res else 'UNSAT'} | Time: {time_taken:.4f}s | Mem: {mem_kb:.1f} KB")

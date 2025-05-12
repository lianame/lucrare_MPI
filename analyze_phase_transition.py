# analyze_phase_transition.py

import os
import matplotlib
# Decomentează dacă suspectezi probleme cu backend-ul matplotlib pe sistemul tău
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import csv
import traceback  # Pentru afișarea completă a erorilor

# Importă funcțiile necesare din celelalte module
# Asigură-te că aceste fișiere sunt în același director sau în PYTHONPATH
try:
    from benchmark import run_algorithms_on_file, parse_dimacs  # Adăugăm și parse_dimacs pentru a extrage info
except ImportError:
    print("EROARE: Nu s-a putut importa 'benchmark.py'. Asigură-te că fișierul există.")
    exit()

# --- Configurare ---
BENCHMARK_DIR = "benchmarks1"  # MODIFICĂ AICI dacă folosești alt director (ex: "benchmarks2")
OUTPUT_CSV = "phase_transition_results.csv"  # Nume diferit pentru a nu suprascrie celălalt CSV
OUTPUT_PLOT_PNG = "phase_transition_plot.png"

CSV_FIELDNAMES = [
    "filename", "relative_path", "num_vars", "num_clauses", "ratio",
    "result_resolution", "time_resolution", "mem_resolution_kb",
    "result_dp", "time_dp", "mem_dp_kb",
    "result_dpll", "time_dpll", "mem_dpll_kb",
    "final_result"  # Un verdict consolidat
]


# --- Funcții Utilitare ---

def get_dimacs_info(filepath):
    """Extrage numărul de variabile și clauze dintr-un fișier DIMACS."""
    try:
        with open(filepath, 'r') as f:
            for line in f:
                if line.startswith('p cnf'):
                    parts = line.split()
                    if len(parts) >= 4:
                        num_vars = int(parts[2])
                        num_clauses = int(parts[3])
                        return num_vars, num_clauses
                    else:
                        print(f"AVERTISMENT: Linia 'p cnf' malformată în {filepath}: {line.strip()}")
                        return None, None
        print(f"AVERTISMENT: Nu s-a găsit linia 'p cnf' în {filepath}.")
        return None, None
    except FileNotFoundError:
        print(f"EROARE: Fișierul {filepath} nu a fost găsit la extragerea informațiilor DIMACS.")
        return None, None
    except ValueError:
        print(f"AVERTISMENT: Eroare la conversia numărului de variabile/clauze în {filepath}.")
        return None, None
    except Exception as e:
        print(f"EROARE la citirea {filepath} în get_dimacs_info: {e}")
        return None, None


# --- Funcția Principală de Analiză ---

def analyze_benchmarks(benchmark_directory):
    """
    Parcurge fișierele .cnf din directorul specificat, rulează algoritmii SAT
    și colectează rezultatele.
    """
    collected_results = []
    print(f"INFO: Se caută fișiere .cnf în directorul: {os.path.abspath(benchmark_directory)}")

    found_any_cnf_files = False

    for root, _, files in os.walk(benchmark_directory):
        for fname in files:
            if fname.endswith(".cnf"):
                found_any_cnf_files = True
                filepath = os.path.join(root, fname)
                relative_path = os.path.relpath(filepath, benchmark_directory)
                print(f"\nINFO: Procesare fișier: {filepath}")

                num_vars, num_clauses = get_dimacs_info(filepath)

                if num_vars is None or num_clauses is None:
                    print(f"INFO: Se omite fișierul {filepath} din cauza erorilor la citirea informațiilor DIMACS.")
                    continue

                if num_vars == 0:
                    ratio = 0.0
                    print(f"AVERTISMENT: Numărul de variabile este 0 în {filepath}. Raportul va fi 0.")
                else:
                    ratio = num_clauses / num_vars

                print(f"INFO: {fname} (Vars: {num_vars}, Clauses: {num_clauses}, Ratio: {ratio:.2f})")

                try:
                    # run_algorithms_on_file returnează un dicționar cu cheile:
                    # "filename", "result", "details"
                    # "details" conține: {"AlgorithmName": {"result", "time", "memory_kb"}}
                    algo_run_data = run_algorithms_on_file(filepath)

                    details = algo_run_data.get("details", {})
                    res_details = details.get("Resolution", {})
                    dp_details = details.get("DP", {})
                    dpll_details = details.get("DPLL", {})

                    # Consolidăm verdictul. DPLL este de obicei cel mai de încredere pentru corectitudine dintre cele simple.
                    # Putem adăuga o verificare de consistență aici dacă dorim.
                    final_verdict = dpll_details.get("result", algo_run_data.get("result", "EROARE"))
                    if final_verdict == "EROARE" and dp_details.get("result"):
                        final_verdict = dp_details.get("result")
                    if final_verdict == "EROARE" and res_details.get("result"):
                        final_verdict = res_details.get("result")

                    collected_results.append({
                        "filename": fname,
                        "relative_path": relative_path,
                        "num_vars": num_vars,
                        "num_clauses": num_clauses,
                        "ratio": ratio,
                        "result_resolution": res_details.get("result", "N/A"),
                        "time_resolution": res_details.get("time", -1),
                        "mem_resolution_kb": res_details.get("memory_kb", -1),
                        "result_dp": dp_details.get("result", "N/A"),
                        "time_dp": dp_details.get("time", -1),
                        "mem_dp_kb": dp_details.get("memory_kb", -1),
                        "result_dpll": dpll_details.get("result", "N/A"),
                        "time_dpll": dpll_details.get("time", -1),
                        "mem_dpll_kb": dpll_details.get("memory_kb", -1),
                        "final_result": final_verdict
                    })
                    print(f"INFO: {fname} procesat. Verdict final: {final_verdict}")

                except Exception as e:
                    print(f"EROARE CRITICĂ la procesarea fișierului {filepath} cu run_algorithms_on_file: {e}")
                    traceback.print_exc()

    if not found_any_cnf_files:
        print(f"AVERTISMENT MAJOR: Nu s-a găsit NICIUN fișier .cnf în {benchmark_directory} și subdirectoarele sale.")

    return collected_results


# --- Funcții pentru Output ---

def save_results_to_csv(results_data, output_filepath):
    """Salvează datele colectate într-un fișier CSV."""
    print(f"\nINFO: Se salvează {len(results_data)} rezultate în {output_filepath}...")
    try:
        with open(output_filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
            writer.writeheader()
            if results_data:
                writer.writerows(results_data)
            else:
                print(f"AVERTISMENT: Nu sunt date de scris în CSV. Fișierul va conține doar antetul.")
        print(f"INFO: Rezultatele au fost salvate în {output_filepath}")
    except IOError as e:
        print(f"EROARE la scrierea fișierului CSV {output_filepath}: {e}")
    except Exception as e:
        print(f"EROARE necunoscută la scrierea CSV: {e}")


def plot_phase_transition_graph(results_data, output_image_path):
    """Generează și salvează graficul tranziției de fază."""
    print(f"\nINFO: Se generează graficul tranziției de fază. Număr de puncte: {len(results_data)}")
    if not results_data:
        print("AVERTISMENT: Nu sunt date disponibile pentru a plota tranziția de fază.")
        # Creăm un grafic gol
        plt.figure(figsize=(10, 6))
        plt.xlabel("Raport clauze / variabile (m/n)")
        plt.ylabel("Satisfiabilitate (SAT=1, UNSAT=0)")
        plt.title("Tranziția de fază în problema SAT (Fără date)")
        plt.grid(True)
        plt.ylim(-0.1, 1.1)
        try:
            plt.savefig(output_image_path)
            print(f"INFO: Grafic gol salvat ca {output_image_path}")
            plt.show()
        except Exception as e:
            print(f"EROARE la salvarea/afișarea graficului gol: {e}")
        return

    # Extragem datele necesare pentru plot
    ratios = [r["ratio"] for r in results_data if isinstance(r.get("ratio"), (int, float))]
    # Folosim "final_result" pentru verdict
    verdicts = [1 if r["final_result"] == "SAT" else 0 for r in results_data if "final_result" in r]

    if not ratios or not verdicts or len(ratios) != len(verdicts):
        print("EROARE: Datele pentru raporturi sau verdicte sunt invalide sau inconsistente pentru plotare.")
        # Încercăm să plotăm ce avem, dacă avem ceva
        if ratios and verdicts:
            print(f"INFO: Avem {len(ratios)} rapoarte si {len(verdicts)} verdicte.")
        else:
            # Apelează din nou funcția pentru a genera un grafic gol dacă nu avem nimic de plotat
            plot_phase_transition_graph([], output_image_path)
            return

    plt.figure(figsize=(10, 6))
    plt.scatter(ratios, verdicts, alpha=0.7, c=verdicts, cmap="coolwarm", vmin=0, vmax=1)

    plt.xlabel("Raport clauze / variabile (m/n)")
    plt.ylabel("Satisfiabilitate (SAT=1, UNSAT=0)")
    plt.yticks([0, 1], ['UNSAT', 'SAT'])
    plt.title("Tranziția de fază în problema SAT")
    plt.grid(True)

    try:
        plt.savefig(output_image_path)
        print(f"INFO: Graficul tranziției de fază salvat ca {output_image_path}")
        plt.show()
    except Exception as e:
        print(f"EROARE la salvarea/afișarea graficului: {e}")


# --- Punctul de Intrare ---

if __name__ == "__main__":
    print("INFO: Scriptul de analiză a tranziției de fază a pornit.")
    print(f"INFO: Backend Matplotlib curent: {matplotlib.get_backend()}")

    if not os.path.isdir(BENCHMARK_DIR):
        print(
            f"EROARE CRITICĂ: Directorul benchmark '{BENCHMARK_DIR}' ({os.path.abspath(BENCHMARK_DIR)}) nu a fost găsit.")
        print("   Verifică valoarea variabilei BENCHMARK_DIR și asigură-te că directorul există.")
        print(
            "   Poți folosi scripturile 'generate_cnf_tests.py' și 'generate_phase_transition_tests.py' pentru a crea fișierele.")
    else:
        print(f"INFO: Se utilizează directorul de benchmark-uri: {os.path.abspath(BENCHMARK_DIR)}")

        # 1. Analizează benchmark-urile
        all_data = analyze_benchmarks(BENCHMARK_DIR)

        if all_data:
            print(f"INFO: Analiză finalizată. S-au colectat {len(all_data)} rezultate.")
            # 2. Salvează rezultatele în CSV
            save_results_to_csv(all_data, OUTPUT_CSV)
            # 3. Plotează graficul
            plot_phase_transition_graph(all_data, OUTPUT_PLOT_PNG)
        else:
            print(
                "AVERTISMENT MAJOR: Nu s-au colectat date din benchmark-uri. CSV-ul și graficul vor fi goale sau nu vor fi generate corect.")
            # Chiar dacă nu sunt date, încercăm să generăm un CSV gol și un grafic gol
            save_results_to_csv([], OUTPUT_CSV)
            plot_phase_transition_graph([], OUTPUT_PLOT_PNG)

    print("INFO: Scriptul de analiză a tranziției de fază s-a încheiat.")
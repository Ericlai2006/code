# flakes_avg_ratio_vs_voltage_txt_simple.py
# Assumes each .txt has columns: time_s, voltage_v, current_a, rtot_ohm
# Uses first 1600 s; voltage_v is constant per file (take first row).

import os, glob
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# --- settings ---
FOLDER = r"C:\Users\赖嘉哲\Desktop\Bezryadin Lab\data"    # folder with your data files
PATTERN = "*_flakes_*V_500k_*"            # or "*_flakes_*V_500k_*.txt" if you want tighter matching
SEP = "\t"                   # tab-delimited files
RSERIES = 500_000.0          # 500 kΩ
TMIN, TMAX = 60.0, 1600.0            # 60 to 1600 seconds
# ----------------

def main():
    files = sorted(glob.glob(os.path.join(FOLDER, PATTERN)))
    if not files:
        print("No .txt files found. Check FOLDER/PATTERN.")
        return

    rows = []
    for path in files:
        fname = os.path.basename(path)
        try:
            df = pd.read_csv(path, sep=SEP)

            # keep first 1600 s
            df = df[(df["time_s"] <= TMAX) & (df["time_s"] >= TMIN)]
            if df.empty:
                print(f"[WARN] {fname}: no rows ≤ {TMAX}s; skipped.")
                continue

            # voltage from the first row (constant per file)
            V = float(df["voltage_v"].iloc[0])

            # average Rsample/Rseries over the window
            avg_ratio = (df["rtot_ohm"] / RSERIES - 1.0).mean()

            rows.append({
                "file": fname,
                "Voltage_V": V,
                "Avg_Rsample_over_Rseries": avg_ratio,
                "N_points_used": len(df),
            })
        except Exception as e:
            print(f"[WARN] Skipping {fname}: {e}")

    if not rows:
        print("No valid files processed.")
        return

    summary = pd.DataFrame(rows).sort_values("Voltage_V")
    print(summary)

    out_csv = Path(FOLDER) / "avg_Rsample_over_Rseries_summary.csv"
    summary.to_csv(out_csv, index=False)
    print(f"Saved: {out_csv}")

    plt.figure()
    plt.plot(summary["Voltage_V"], summary["Avg_Rsample_over_Rseries"], "o-")
    plt.xlabel("Applied Voltage (V)")
    plt.ylabel("Average Rsample / Rseries (first 1600 s)")
    plt.title("Flakes: Rsample/Rseries vs Voltage")
    plt.grid(True)
    plt.tight_layout()
    out_png = Path(FOLDER) / "avg_ratio_vs_voltage.png"
    plt.savefig(out_png, dpi=150)
    print(f"Saved: {out_png}")
    plt.show()  # uncomment if running interactively

if __name__ == "__main__":
    main()

# flakes_avg_ratio_vs_voltage_txt_simple.py
# Assumes each file has: time_s, voltage_v, current_a, rtot_ohm

import os, glob
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# --- settings ---
FOLDER = r"C:\Users\赖嘉哲\Desktop\Bezryadin Lab\data"
PATTERN = "*_flakes_*V_500k_*"
SEP = "\t"
RSERIES = 500_000.0

# (label, tmin, tmax); use None for open-ended
WINDOWS = [
    ("full run", None, None),
    ("0–1600 s", 0.0, 1600.0),
    ("200–1600 s", 200.0, 1600.0),
]
# ----------------

def main():
    files = sorted(glob.glob(os.path.join(FOLDER, PATTERN)))
    if not files:
        print("No files matched. Check FOLDER/PATTERN.")
        return

    # Figure A: combined Avg(Rs/Rst) vs V (all windows)
    fig1, ax1 = plt.subplots()

    # Figure B: combined |1 - Avg(Rs/Rst)| vs V (all windows)  <<< NEW
    fig2, ax2 = plt.subplots()

    for label, TMIN, TMAX in WINDOWS:
        rows = []
        for path in files:
            fname = os.path.basename(path)
            try:
                df = pd.read_csv(path, sep=SEP)

                # apply this window
                if TMIN is not None:
                    df = df[df["time_s"] >= TMIN]
                if TMAX is not None:
                    df = df[df["time_s"] <= TMAX]

                if df.empty:
                    print(f"[WARN] {fname}: no rows in window {label}; skipped.")
                    continue

                # voltage from the first row (constant per file)
                V = float(df["voltage_v"].iloc[0])

                # average Rsample/Rseries over this window
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
            print(f"[INFO] Window '{label}' produced no summaries.")
            continue

        summary = pd.DataFrame(rows).sort_values("Voltage_V")
        print(f"\nSummary — {label}:\n", summary)

        # --- plot Avg(Rs/Rst) on combined figure A
        ax1.plot(summary["Voltage_V"], summary["Avg_Rsample_over_Rseries"], "o-", label=label)

        # --- compute and plot |1 - Avg(Rs/Rst)| on combined figure B  <<< NEW
        summary["AbsDiff_from_1"] = (1.0 - summary["Avg_Rsample_over_Rseries"]).abs()
        ax2.plot(summary["Voltage_V"], summary["AbsDiff_from_1"], "o-", label=label)

        # (optional) save a CSV per window (keep if you want the numbers)
        # safe_label = label.replace(" ", "_").replace("–", "-").replace("—", "-")
        # out_csv = Path(FOLDER) / f"avg_Rsample_over_Rseries_summary_{safe_label}.csv"
        # summary.to_csv(out_csv, index=False)
        # print(f"Saved: {out_csv}")

    # --- finalize figure A
    ax1.set_xlabel("Applied Voltage (V)")
    ax1.set_ylabel("Average Rsample / Rseries")
    ax1.set_title("Rsample/Rseries vs Voltage (window comparison)")
    ax1.grid(True)
    ax1.legend(title="Window")
    fig1.tight_layout()

    # --- finalize figure B (the NEW combined abs-diff plot)
    ax2.set_xlabel("Applied Voltage (V)")
    ax2.set_ylabel("|1 - average(Rsample / Rseries)|")
    ax2.set_title("Distance from u=1 vs Voltage (window comparison)")
    ax2.grid(True)
    ax2.legend(title="Window")
    fig2.tight_layout()

    # --- show interactively in VS Code  <<< IMPORTANT
    plt.show()

    # (optional) also save PNGs if you like:
    # fig1.savefig(Path(FOLDER) / "avg_ratio_vs_voltage_compare_windows.png", dpi=150)
    # fig2.savefig(Path(FOLDER) / "absdiff_from_1_vs_voltage_compare_windows.png", dpi=150)

if __name__ == "__main__":
    main()
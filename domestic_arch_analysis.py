import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
from scipy.stats import t


# =====================================================
# 1. Load Data
# =====================================================

df = pd.read_csv("deflection_long.csv")


# =====================================================
# 2. Statistics by Arch, Method, and Angle
# =====================================================

summary = df.groupby(
    ["Arch", "Method", "Angle"]
)["Deflection"].agg(
    mean="mean",
    std="std",
    n="count"
).reset_index()

# Standard error and 95% confidence interval
summary["sem"] = summary["std"] / np.sqrt(summary["n"])
summary["ci95"] = summary["sem"] * t.ppf(0.975, summary["n"] - 1)


# =====================================================
# 3. Harmonic Model (2nd-order Fourier Series)
# =====================================================

def harmonic(theta, a0, a1, b1, a2, b2):

    return (
        a0
        + a1 * np.cos(theta)
        + b1 * np.sin(theta)
        + a2 * np.cos(2 * theta)
        + b2 * np.sin(2 * theta)
    )


# =====================================================
# 4. Phase-Based Alignment (Dominant Harmonic)
# =====================================================

aligned_list = []

for (arch, method), sub in summary.groupby(["Arch", "Method"]):

    theta = np.deg2rad(sub["Angle"].values)
    y = sub["mean"].values

    # Harmonic fitting
    popt, _ = curve_fit(harmonic, theta, y)

    a0, a1, b1, a2, b2 = popt

    # Harmonic amplitudes
    H1 = np.sqrt(a1**2 + b1**2)
    H2 = np.sqrt(a2**2 + b2**2)

    # Select dominant harmonic for alignment
    if H2 > H1:
        # Second-order dominant (W-shaped pattern)
        phi = 0.5 * np.arctan2(b2, a2)
    else:
        # First-order dominant (single peak)
        phi = np.arctan2(b1, a1)

    peak_angle = np.rad2deg(phi)

    # Angle alignment
    sub = sub.copy()
    sub["Angle_aligned"] = (sub["Angle"] - peak_angle) % 360

    aligned_list.append(sub)


aligned = pd.concat(aligned_list, ignore_index=True)

aligned["Angle_rad_aligned"] = np.deg2rad(aligned["Angle_aligned"])


# =====================================================
# 5. Output Directory
# =====================================================

output_dir = "angle_deflection_plots"
os.makedirs(output_dir, exist_ok=True)


# =====================================================
# 6. Single-Arch Basic Plots (Mean + CI + Fit)
# =====================================================

def analyze_and_save(arch_id, method="AMO"):

    data = aligned[
        (aligned["Arch"] == arch_id) &
        (aligned["Method"] == method)
    ].sort_values("Angle_aligned")


    theta = data["Angle_rad_aligned"].values
    y = data["mean"].values

    # Harmonic fitting
    popt, _ = curve_fit(harmonic, theta, y)

    theta_fit = np.linspace(0, 2*np.pi, 400)
    y_fit = harmonic(theta_fit, *popt)


    plt.figure(figsize=(8,6))

    # Mean with confidence interval
    plt.errorbar(
        data["Angle_aligned"],
        y,
        yerr=data["ci95"],
        fmt="o",
        capsize=3,
        label="Mean ±95% CI"
    )

    # Harmonic fit curve
    plt.plot(
        np.rad2deg(theta_fit),
        y_fit,
        linewidth=2.2,
        label="Harmonic Fit"
    )

    plt.xlabel("Aligned Angle (°)")
    plt.ylabel("Deflection")
    plt.title(f"Arch {arch_id} - {method}")

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    filename = f"Arch{arch_id}_{method}.png"
    path = os.path.join(output_dir, filename)

    plt.savefig(path, dpi=300)
    plt.close()

    print("Saved:", path)


# Generate plots for all arches
for arch in range(1,11):
    for method in ["AMO", "ASTM"]:
        analyze_and_save(arch, method)


# =====================================================
# 7. ASTM Shaded Confidence Interval Plots
# =====================================================

mean_color = "#6A5DC4"
ci_color   = "#E9E6F7"
fit_color  = "#3B5387"


def plot_astm_shaded(arch_id):

    data = aligned[
        (aligned["Arch"] == arch_id) &
        (aligned["Method"] == "ASTM")
    ].sort_values("Angle_aligned")


    x = data["Angle_aligned"].values
    y = data["mean"].values
    ci = data["ci95"].values

    theta = np.deg2rad(x)

    # Harmonic fitting
    popt, _ = curve_fit(harmonic, theta, y)

    theta_s = np.linspace(0, 2*np.pi, 600)
    x_s = np.rad2deg(theta_s)

    y_fit = harmonic(theta_s, *popt)

    # Smooth confidence interval by interpolation
    ci_s = np.interp(x_s, x, ci)


    plt.figure(figsize=(8.5,6.5))

    # Confidence band
    plt.fill_between(
        x_s,
        y_fit - ci_s,
        y_fit + ci_s,
        color=ci_color,
        alpha=0.6,
        label="95% CI"
    )

    # Mean points
    plt.scatter(
        x, y,
        color=mean_color,
        s=35,
        zorder=3,
        label="Mean"
    )

    # Mean connecting line
    plt.plot(
        x, y,
        color=mean_color,
        alpha=0.7
    )

    # Harmonic fit
    plt.plot(
        x_s,
        y_fit,
        color=fit_color,
        linewidth=2.2,
        label="Harmonic Fit"
    )

    plt.xlabel("Aligned Angle (°)", fontweight="bold")
    plt.ylabel("Deflection", fontweight="bold")

    plt.title(f"Arch {arch_id} - ASTM", fontweight="bold")

    plt.grid(True, linestyle="--", alpha=0.25)
    plt.legend(frameon=False)

    plt.tight_layout()

    filename = f"Arch{arch_id}_ASTM_shaded.png"
    path = os.path.join(output_dir, filename)

    plt.savefig(path, dpi=300)
    plt.close()

    print("Saved:", path)


# Generate shaded plots
for arch in range(1,11):
    plot_astm_shaded(arch)


# =====================================================
# 8. All Arches Overlay + Global Peaks/Valleys
# =====================================================

plt.figure(figsize=(13,9))

colors = plt.cm.tab10.colors

all_theta = []
all_y = []


# Plot individual arches
for i, arch in enumerate(range(1,11)):

    data = aligned[
        (aligned["Arch"] == arch) &
        (aligned["Method"] == "ASTM")
    ].sort_values("Angle_aligned")


    x = data["Angle_aligned"].values
    y = data["mean"].values

    theta = np.deg2rad(x)

    all_theta.append(theta)
    all_y.append(y)

    plt.plot(
        x,
        y,
        color=colors[i],
        linewidth=2.2,
        alpha=0.85,
        label=f"Arch {arch}"
    )


# Global harmonic fitting
all_theta = np.concatenate(all_theta)
all_y = np.concatenate(all_y)

popt, _ = curve_fit(harmonic, all_theta, all_y)

theta_s = np.linspace(0, 2*np.pi, 1200)
x_s = np.rad2deg(theta_s)

y_fit = harmonic(theta_s, *popt)


# Detect peaks and valleys
peaks,_ = find_peaks(y_fit, distance=200)
valleys,_ = find_peaks(-y_fit, distance=200)

top_peaks = peaks[np.argsort(y_fit[peaks])][-2:]
top_valleys = valleys[np.argsort(-y_fit[valleys])][-2:]

extreme_x = np.sort(
    np.concatenate([
        x_s[top_peaks],
        x_s[top_valleys]
    ])
)


# Plot reference lines and annotations
for xx in extreme_x:

    theta_x = np.deg2rad(xx)
    y_x = harmonic(theta_x, *popt)

    plt.axvline(
        xx,
        color="#FDD786",
        linestyle="--",
        linewidth=1.2,
        alpha=0.8
    )

    plt.text(
        xx - 24,
        480,
        f"{xx:.1f}°\n{y_x:.2f}",
        color="#F78779",
        fontsize=10,
        alpha=0.8,
        fontweight="bold",
        va="center"
    )


plt.xlabel("Aligned Angle (°)", fontweight="bold")
plt.ylabel("Deflection", fontweight="bold")

plt.title(
    "Domestic Arches ASTM Deflection",
    fontsize=18,
    fontweight="bold"
)

plt.grid(True, linestyle="--", alpha=0.25)

plt.legend(
    frameon=False,
    loc="center left",
    bbox_to_anchor=(1.02,0.5)
)

plt.tight_layout()


path = os.path.join(
    output_dir,
    "Domestic_Arches_ASTM_All.png"
)

plt.savefig(path, dpi=300, bbox_inches="tight")
plt.close()

print("Saved:", path)
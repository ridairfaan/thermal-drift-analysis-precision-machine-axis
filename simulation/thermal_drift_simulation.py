import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# 1. Style and output folders

plt.style.use("seaborn-v0_8")
plt.rcParams.update({
    "font.size": 13,
    "axes.titlesize": 18,
    "axes.labelsize": 14,
    "legend.fontsize": 13
})

os.makedirs("../data", exist_ok=True)
os.makedirs("../visuals", exist_ok=True)


# 2. Simulation settings

np.random.seed(42)

total_minutes = 120
n_points = 500

time_min = np.linspace(0, total_minutes, n_points)

# Nominal machine axis position (mm)
nominal_position_mm = 100.000

# Initial temperature
reference_temperature_c = 20.0

# Drift sensitivity: micrometers per degree Celsius
drift_sensitivity_um_per_c = 2.5

# Engineering tolerance limit
tolerance_um = 2.0


# 3. Simulate temperature rise

# Gradual increase + mild oscillation
temperature_c = (
    reference_temperature_c
    + 0.03 * time_min
    + 0.15 * np.sin(time_min / 10)
)


# 4. Simulate thermal drift

drift_component_um = drift_sensitivity_um_per_c * (
    temperature_c - reference_temperature_c
)


# 5. Simulate measurement noise

noise_component_um = np.random.normal(
    loc=0.0,
    scale=0.35,
    size=n_points
)


# 6. Total position error

position_error_um = drift_component_um + noise_component_um

# Convert error to mm
position_error_mm = position_error_um / 1000.0

# Measured position
measured_position_mm = nominal_position_mm + position_error_mm


# 7. Simple drift compensation model

estimated_drift_um = drift_sensitivity_um_per_c * (
    temperature_c - reference_temperature_c
)

compensated_error_um = position_error_um - estimated_drift_um
compensated_position_mm = nominal_position_mm + compensated_error_um / 1000.0


# 8. Drift trend analysis

trend_coeff = np.polyfit(time_min, position_error_um, 1)
trend_slope_um_per_min = trend_coeff[0]
trend_intercept_um = trend_coeff[1]
drift_trend_um = trend_slope_um_per_min * time_min + trend_intercept_um


# 9. Calculate key metrics

max_error_before_um = np.max(np.abs(position_error_um))
max_error_after_um = np.max(np.abs(compensated_error_um))

std_before_um = np.std(position_error_um)
std_after_um = np.std(compensated_error_um)

mean_before_um = np.mean(position_error_um)
mean_after_um = np.mean(compensated_error_um)

temperature_rise_c = np.max(temperature_c) - np.min(temperature_c)

compensation_improvement_percent = (
    (max_error_before_um - max_error_after_um) / max_error_before_um
) * 100


# 10. Tolerance evaluation

within_tolerance_before = np.abs(position_error_um) <= tolerance_um
within_tolerance_after = np.abs(compensated_error_um) <= tolerance_um

tolerance_rate_before_percent = np.mean(within_tolerance_before) * 100
tolerance_rate_after_percent = np.mean(within_tolerance_after) * 100


# 11. Create dataframe

df = pd.DataFrame({
    "time_min": time_min,
    "temperature_c": temperature_c,
    "nominal_position_mm": nominal_position_mm,
    "measured_position_mm": measured_position_mm,
    "position_error_um": position_error_um,
    "drift_component_um": drift_component_um,
    "noise_component_um": noise_component_um,
    "estimated_drift_um": estimated_drift_um,
    "compensated_error_um": compensated_error_um,
    "compensated_position_mm": compensated_position_mm,
    "drift_trend_um": drift_trend_um,
    "within_tolerance_before": within_tolerance_before,
    "within_tolerance_after": within_tolerance_after
})

# Save CSV
df.to_csv("../data/thermal_drift_data.csv", index=False)


# 12. Plot 1: Temperature vs Time

plt.figure(figsize=(10, 6))
plt.plot(time_min, temperature_c, linewidth=2.5)
plt.xlabel("Time (min)")
plt.ylabel("Temperature (°C)")
plt.title("Temperature Rise Over Time")
plt.grid(True, alpha=0.4)
plt.tight_layout()
plt.savefig("../visuals/temperature_vs_time.png", dpi=300)
plt.close()


# 13. Plot 2: Position Error vs Time

plt.figure(figsize=(10, 6))
plt.plot(time_min, position_error_um, linewidth=2.0, label="Measured error")
plt.xlabel("Time (min)")
plt.ylabel("Position Error (µm)")
plt.title("Position Error Due to Thermal Drift")
plt.legend()
plt.grid(True, alpha=0.4)
plt.tight_layout()
plt.savefig("../visuals/error_vs_time.png", dpi=300)
plt.close()


# 14. Plot 3: Before vs After Compensation

plt.figure(figsize=(10, 6))
plt.plot(time_min, position_error_um, linewidth=2.0, label="Before compensation")
plt.plot(time_min, compensated_error_um, linewidth=2.0, label="After compensation")
plt.xlabel("Time (min)")
plt.ylabel("Position Error (µm)")
plt.title("Effect of Drift Compensation")
plt.legend()
plt.grid(True, alpha=0.4)
plt.tight_layout()
plt.savefig("../visuals/compensation_comparison.png", dpi=300)
plt.close()


# 15. Plot 4: Drift vs Noise Components

plt.figure(figsize=(10, 6))
plt.plot(time_min, drift_component_um, linewidth=2.5, label="Thermal drift component")
plt.plot(time_min, noise_component_um, linewidth=2.0, label="Noise component")
plt.xlabel("Time (min)")
plt.ylabel("Error Contribution (µm)")
plt.title("Thermal Drift and Measurement Noise")
plt.legend()
plt.grid(True, alpha=0.4)
plt.tight_layout()
plt.savefig("../visuals/drift_vs_noise.png", dpi=300)
plt.close()


# 16. Plot 5: Drift Trend Analysis

plt.figure(figsize=(10, 6))
plt.plot(time_min, position_error_um, linewidth=1.8, label="Measured error")
plt.plot(time_min, drift_trend_um, linestyle="--", linewidth=2.5, label="Drift trend")
plt.xlabel("Time (min)")
plt.ylabel("Position Error (µm)")
plt.title("Drift Trend Analysis")
plt.legend()
plt.grid(True, alpha=0.4)
plt.tight_layout()
plt.savefig("../visuals/drift_trend.png", dpi=300)
plt.close()


# 17. Plot 6: Position Error with Tolerance Band

plt.figure(figsize=(10, 6))
plt.plot(time_min, position_error_um, linewidth=2.0, label="Before compensation")
plt.plot(time_min, compensated_error_um, linewidth=2.0, label="After compensation")
plt.axhline(
    tolerance_um,
    color="red",
    linestyle="--",
    linewidth=1.8,
    label="Tolerance limit"
)
plt.axhline(
    -tolerance_um,
    color="red",
    linestyle="--",
    linewidth=1.8
)
plt.xlabel("Time (min)")
plt.ylabel("Position Error (µm)")
plt.title("Position Error Relative to Tolerance Limits")
plt.legend()
plt.grid(True, alpha=0.4)
plt.tight_layout()
plt.savefig("../visuals/error_with_tolerance.png", dpi=300)
plt.close()


# 18. Print summary report

print("\n=== Thermal Drift Analysis Summary ===")
print(f"Maximum error before compensation : {max_error_before_um:.3f} µm")
print(f"Maximum error after compensation  : {max_error_after_um:.3f} µm")
print(f"Std. deviation before compensation: {std_before_um:.3f} µm")
print(f"Std. deviation after compensation : {std_after_um:.3f} µm")
print(f"Mean error before compensation    : {mean_before_um:.3f} µm")
print(f"Mean error after compensation     : {mean_after_um:.3f} µm")
print(f"Total temperature rise            : {temperature_rise_c:.3f} °C")
print(f"Compensation improvement          : {compensation_improvement_percent:.2f} %")
print(f"Estimated drift trend slope       : {trend_slope_um_per_min:.4f} µm/min")
print(f"Tolerance limit                   : ±{tolerance_um:.2f} µm")
print(f"Within tolerance before           : {tolerance_rate_before_percent:.2f} %")
print(f"Within tolerance after            : {tolerance_rate_after_percent:.2f} %")
print("\nCSV saved to: ../data/thermal_drift_data.csv")
print("Plots saved to: ../visuals/")
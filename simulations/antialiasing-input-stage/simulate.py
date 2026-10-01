#!/usr/bin/env python3
"""
Simulation script for Eurorack to STM32 ADC Antialiasing Input Stage.
Runs ngspice AC and transient analysis, computes frequency response metrics,
prints tabular data, exports CSV, and generates Bode and transient plots.
"""

import os
import sys
import subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CIRCUIT_FILE = os.path.join(SCRIPT_DIR, "antialiasing_input_stage.cir")
AC_DATA_FILE = os.path.join(SCRIPT_DIR, "ac_sim.txt")
TRAN_DATA_FILE = os.path.join(SCRIPT_DIR, "tran_sim.txt")
CSV_OUTPUT = os.path.join(SCRIPT_DIR, "frequency_response.csv")
BODE_PLOT = os.path.join(SCRIPT_DIR, "frequency_response.png")
TRAN_PLOT = os.path.join(SCRIPT_DIR, "transient_response.png")

def run_ngspice():
    print(f"Running ngspice on {CIRCUIT_FILE}...")
    res = subprocess.run(
        ["ngspice", "-b", CIRCUIT_FILE],
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True
    )
    if res.returncode != 0:
        print("ngspice error:\n", res.stderr)
        sys.exit(res.returncode)
    print("ngspice simulation completed successfully.")

def process_ac():
    data = np.loadtxt(AC_DATA_FILE)
    freq = data[:, 0]
    
    # ngspice wrdata format for AC:
    # freq, real(v(adc_in)), imag(v(adc_in)), real(v(out)), imag(v(out)), ...
    # Column 0: freq
    # Column 1: real(v(adc_in))
    # Column 2: imag(v(adc_in))
    v_adc_real = data[:, 1]
    v_adc_imag = data[:, 2]
    v_adc_mag = np.sqrt(v_adc_real**2 + v_adc_imag**2)
    v_adc_phase = np.arctan2(v_adc_imag, v_adc_real) * (180.0 / np.pi)
    
    # Gain in dB
    gain_db = 20.0 * np.log10(v_adc_mag)
    
    # Reference DC / low-frequency passband gain at 100 Hz
    idx_100 = np.argmin(np.abs(freq - 100.0))
    dc_gain = v_adc_mag[idx_100]
    dc_gain_db = gain_db[idx_100]
    gain_rel_db = gain_db - dc_gain_db

    # Find -3dB cutoff frequency relative to passband
    idx_3db = np.where(gain_rel_db <= -3.0)[0][0]
    f_3db = freq[idx_3db]

    # Calculate rolloff rate between 40 kHz and 400 kHz (dB/decade)
    idx_40k = np.argmin(np.abs(freq - 40e3))
    idx_400k = np.argmin(np.abs(freq - 400e3))
    rolloff = (gain_rel_db[idx_400k] - gain_rel_db[idx_40k]) / (np.log10(freq[idx_400k]) - np.log10(freq[idx_40k]))

    print("\n" + "="*70)
    print("FREQUENCY RESPONSE ANALYSIS (AC SIMULATION)")
    print("="*70)
    print(f"Passband Gain (|Av| at 100 Hz): {dc_gain:.4f} ({dc_gain_db:.2f} dB)")
    print(f"-3 dB Cutoff Frequency (fc):    {f_3db:.1f} Hz ({f_3db/1e3:.2f} kHz)")
    print(f"Stopband Roll-off Rate:         {rolloff:.1f} dB/decade (Theoretical 2nd-order = -40 dB/dec)")
    print("="*70)
    
    print(f"{'Frequency':>12} | {'Magnitude (dB)':>15} | {'Rel Gain (dB)':>15} | {'Phase (deg)':>12}")
    print("-" * 62)
    
    key_freqs = [20.0, 100.0, 1000.0, 5000.0, 10000.0, 15000.0, 20000.0, 21380.0, 24000.0, 44100.0, 48000.0, 96000.0, 100000.0, 200000.0, 500000.0, 1000000.0]
    
    for kf in key_freqs:
        idx = np.argmin(np.abs(freq - kf))
        f_val = freq[idx]
        if f_val < 1000:
            f_str = f"{f_val:6.1f} Hz"
        else:
            f_str = f"{f_val/1e3:6.1f} kHz"
        print(f"{f_str:>12} | {gain_db[idx]:15.2f} | {gain_rel_db[idx]:15.2f} | {v_adc_phase[idx]:12.1f}")
    print("-" * 62)

    # Save to CSV
    header = "Frequency_Hz,Magnitude_V,Magnitude_dB,Relative_Gain_dB,Phase_deg"
    csv_data = np.column_stack((freq, v_adc_mag, gain_db, gain_rel_db, v_adc_phase))
    np.savetxt(CSV_OUTPUT, csv_data, delimiter=",", header=header, comments="", fmt="%.6e")
    print(f"\nFrequency response data saved to: {CSV_OUTPUT}")

    # Generate Bode Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    # Magnitude plot
    ax1.semilogx(freq, gain_db, 'b-', linewidth=2, label='Filter Response V(ADC_IN)')
    ax1.axvline(20e3, color='gray', linestyle='--', alpha=0.7, label='Audio Limit (20 kHz)')
    ax1.axvline(f_3db, color='r', linestyle=':', linewidth=1.5, label=f'Cutoff fc = {f_3db/1e3:.1f} kHz (-3 dB)')
    ax1.axhline(dc_gain_db - 3.0, color='r', linestyle=':', alpha=0.5)
    ax1.set_ylabel('Magnitude (dB)', fontsize=12)
    ax1.set_title('Eurorack to STM32 ADC Antialiasing Filter - Frequency Response', fontsize=14, fontweight='bold')
    ax1.grid(True, which='both', linestyle=':', alpha=0.6)
    ax1.legend(loc='lower left', fontsize=10)
    ax1.set_ylim([-60, 0])
    
    # Phase plot
    ax2.semilogx(freq, v_adc_phase, 'g-', linewidth=2, label='Phase')
    ax2.axvline(20e3, color='gray', linestyle='--', alpha=0.7)
    ax2.axvline(f_3db, color='r', linestyle=':', linewidth=1.5)
    ax2.set_xlabel('Frequency (Hz)', fontsize=12)
    ax2.set_ylabel('Phase (degrees)', fontsize=12)
    ax2.grid(True, which='both', linestyle=':', alpha=0.6)
    ax2.legend(loc='lower left', fontsize=10)
    ax2.set_xlim([10, 1e6])
    
    plt.tight_layout()
    plt.savefig(BODE_PLOT, dpi=200)
    plt.close()
    print(f"Bode plot saved to: {BODE_PLOT}")
    
    return dc_gain, f_3db, rolloff

def process_tran():
    data = np.loadtxt(TRAN_DATA_FILE)
    t = data[:, 0]
    v_in = data[:, 1]
    v_out = data[:, 2]
    v_adc = data[:, 3]

    # Analyze steady state over last 2 ms
    mask = t >= 3e-3
    vin_min = np.min(v_in[mask])
    vin_max = np.max(v_in[mask])
    vin_pp = vin_max - vin_min

    vadc_min = np.min(v_adc[mask])
    vadc_max = np.max(v_adc[mask])
    vadc_pp = vadc_max - vadc_min
    vadc_mid = (vadc_max + vadc_min) / 2.0

    print("\n" + "="*70)
    print("TRANSIENT RESPONSE ANALYSIS (1 kHz, 20Vpp Eurorack Input)")
    print("="*70)
    print(f"Input Signal:  Vin_min = {vin_min:+.3f} V,  Vin_max = {vin_max:+.3f} V,  Vin_pp = {vin_pp:.3f} V")
    print(f"ADC Output:    Vadc_min = {vadc_min:+.3f} V, Vadc_max = {vadc_max:+.3f} V, Vadc_pp = {vadc_pp:.3f} V")
    print(f"ADC Midpoint:  Vadc_center = {vadc_mid:.3f} V (Target = 1.650 V)")
    print(f"STM32 Margin:  Low Rail Margin = {vadc_min*1000:.1f} mV, High Rail Margin = {(3.3 - vadc_max)*1000:.1f} mV")
    print("="*70)

    # Generate Transient Plot
    plt.figure(figsize=(10, 5))
    t_ms = t * 1000.0
    
    plt.plot(t_ms, v_in, 'r-', linewidth=1.5, label='Input Signal Vin (Eurorack 20Vpp, -10V to +10V)')
    plt.plot(t_ms, v_adc, 'b-', linewidth=2.0, label=f'Output to STM32 ADC ({vadc_min:.2f}V to {vadc_max:.2f}V, Center {vadc_mid:.2f}V)')
    
    # STM32 ADC boundaries
    plt.axhline(3.3, color='black', linestyle='--', linewidth=1, label='STM32 VDD Rail (3.3V)')
    plt.axhline(0.0, color='black', linestyle='--', linewidth=1, label='GND Rail (0.0V)')
    plt.axhline(1.65, color='gray', linestyle=':', linewidth=1, label='ADC Midscale (1.65V)')
    
    plt.xlim([0, 3]) # First 3 ms (3 cycles)
    plt.ylim([-12, 12])
    plt.xlabel('Time (ms)', fontsize=12)
    plt.ylabel('Voltage (V)', fontsize=12)
    plt.title('Transient Waveform: Eurorack 20Vpp Bipolar Input to Unipolar 0-3.3V ADC Signal', fontsize=13, fontweight='bold')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='upper right', fontsize=9)
    plt.tight_layout()
    plt.savefig(TRAN_PLOT, dpi=200)
    plt.close()
    print(f"Transient plot saved to: {TRAN_PLOT}")

def main():
    run_ngspice()
    process_ac()
    process_tran()

if __name__ == "__main__":
    main()

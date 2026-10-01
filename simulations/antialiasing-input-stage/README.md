# Eurorack to STM32 ADC Antialiasing Input Stage

A 2nd-order active antialiasing low-pass filter and level-shifter stage designed for interfacing Eurorack modular synthesizer audio signals into an STM32 microcontroller ADC running on a single 3.3V rail.

---

## 1. Specifications & Design Requirements

| Parameter | Specification | Notes / Purpose |
|---|---|---|
| **Input Signal** | 20 Vpp (±10.0 V) Bipolar Audio | Maximum Eurorack modular audio level (±10V) |
| **Output Signal** | 0.0 V to 3.3 V Unipolar | Full range acceptable by STM32 ADC (0 to $V_{\text{DDA}}$) |
| **Output Swing (Nominal)** | 0.15 V to 3.16 V (Center = 1.652 V) | Safe ~145 mV rail headroom margin for RRIO opamp linearity |
| **Power Supply** | Single-rail +3.3 V ($V_{\text{DD}} = 3.3\text{ V}, V_{\text{SS}} = 0\text{ V}$) | Matches microcontroller $V_{\text{DDA}}$ rail |
| **Input Impedance** | $100\text{ k}\Omega$ | Standard Eurorack input impedance |
| **Filter Topology** | 2nd-Order Sallen-Key Low-Pass Filter | Butterworth response ($Q \approx 0.69 - 0.71$) |
| **Cutoff Frequency ($f_{-3\text{dB}}$)** | $\approx 20.9\text{ kHz}$ | Preserves 20 Hz – 20 kHz audio band |
| **Stopband Attenuation** | $\approx -40\text{ dB/decade}$ (2nd-order roll-off) | Eliminates out-of-band aliasing at ADC sample rates |
| **Post-Filter / ADC Buffer** | 1st-order RC ($100\,\Omega + 1\text{ nF}$) | ADC sampling charge reservoir and high-frequency noise sink |
| **Input Protection** | Dual Schottky diodes to +3.3V & GND | Clamps overvoltage/fault conditions (e.g. ±12V eurorack rails) |

---

## 2. Circuit Diagram

```text
                     +3.3V (VDD)
                       |
                     [R_PU] (30.1k)
                       |
                       |        C1 (680pF)
                       +---------------+---------------------------------+
 Eurorack              |               |                                 |
 Audio In       N1     |        N2     |                                 |
(20Vpp, ±10V)   |      |        |      |                                 |
  o----[ R1 ]----+---->+---[ R2 ]-+----(+)                               |
       (100k)   |      |   (15k)  |     |   U1 (TLV9002/MCP6002)         |
                |    [R_PD]       |     |   Single 3.3V Supply           |
             +--+--+ (43.2k)     [C2]   |       |\                       |
             |     |   |        (360pF) |       | \                      |
            _|_   _|_ GND         |     |       |  \                     |
          D1 /_\  \ / D2          |     |       |   >----+---------------+--[ R_ADC ]--o (ADC_IN)
       BAT54S |    | BAT54S      GND    +-----( -|  /     |                 (100R)       |
            +3.3V GND                            | /      |                            [C_ADC]
                                                 |/       |                             (1nF)
                                                          |                               |
                                                      Feedback                           GND
                                                        Loop
```

---

## 3. Theory of Operation & Design Calculations

### 3.1 Passive Attenuation and DC Bias Shifter Network
The input stage uses a three-resistor network ($R_1$, $R_{\text{PU}}$, $R_{\text{PD}}$) to simultaneously accomplish two critical goals:
1. Provide a standard Eurorack input impedance ($Z_{\text{in}} \approx R_1 = 100\text{ k}\Omega$).
2. Attenuate the 20 Vpp bipolar signal ($\pm 10\text{ V}$) and shift its center to $V_{\text{MID}} = 1.65\text{ V}$.

By superposition, the Thevenin equivalent voltage and resistance at summing node $N_1$ are:
$$G_{\text{tot}} = \frac{1}{R_1} + \frac{1}{R_{\text{PU}}} + \frac{1}{R_{\text{PD}}}$$
$$R_{\text{th}} = \frac{1}{G_{\text{tot}}}$$
$$V_{\text{th}} = V_{\text{in}} \cdot \frac{1/R_1}{G_{\text{tot}}} + V_{\text{DD}} \cdot \frac{1/R_{\text{PU}}}{G_{\text{tot}}}$$

#### Optimal Resistor Selection (with ~145 mV Rail Margins):
Using standard 1% E96 resistors:
- $R_1 = 100\text{ k}\Omega$
- $R_{\text{PU}} = 30.1\text{ k}\Omega$
- $R_{\text{PD}} = 43.2\text{ k}\Omega$

Resulting parameters:
- $G_{\text{tot}} = 10.000\,\mu\text{S} + 33.223\,\mu\text{S} + 23.148\,\mu\text{S} = 66.371\,\mu\text{S}$
- $R_{\text{th}} = \frac{1}{66.371\,\mu\text{S}} \approx 15.067\text{ k}\Omega \approx 15.0\text{ k}\Omega$
- Voltage Gain: $K_{\text{att}} = \frac{10.000\,\mu\text{S}}{66.371\,\mu\text{S}} \approx 0.1507$ ($-16.44\text{ dB}$)
- DC Offset: $V_{\text{offset}} = 3.3\text{ V} \times \frac{33.223\,\mu\text{S}}{66.371\,\mu\text{S}} \approx 1.652\text{ V}$

#### Signal Range Verification:
- At $V_{\text{in}} = -10.0\text{ V}$: $V_{\text{out}} = 1.652\text{ V} + 0.1507 \times (-10.0\text{ V}) = +0.145\text{ V}$ (145 mV above GND rail)
- At $V_{\text{in}} = 0.0\text{ V}$: $V_{\text{out}} = 1.652\text{ V} + 0.1507 \times (0.0\text{ V}) = +1.652\text{ V}$ (midscale, digital code ~2050 on 12-bit ADC)
- At $V_{\text{in}} = +10.0\text{ V}$: $V_{\text{out}} = 1.652\text{ V} + 0.1507 \times (+10.0\text{ V}) = +3.158\text{ V}$ (142 mV below 3.3V rail)

### 3.2 2nd-Order Sallen-Key Low-Pass Filter
The Sallen-Key topology incorporates the Thevenin source resistance $R_{\text{th}}$ directly as the first filter resistor:
- $R_{\text{filter1}} = R_{\text{th}} \approx 15.07\text{ k}\Omega$
- $R_2 = 15.0\text{ k}\Omega$
- $C_1 = 680\text{ pF}$ (feedback capacitor)
- $C_2 = 360\text{ pF}$ (grounded capacitor; 330 pF is also suitable with $f_c \approx 22.9\text{ kHz}$)

The transfer function is:
$$H(s) = \frac{V_{\text{out}}(s)}{V_{\text{th}}(s)} = \frac{1}{s^2 R_{\text{th}} R_2 C_1 C_2 + s C_2(R_{\text{th}} + R_2) + 1}$$

Natural angular frequency $\omega_0$ and quality factor $Q$:
$$\omega_0 = \frac{1}{\sqrt{R_{\text{th}} R_2 C_1 C_2}} = \frac{1}{\sqrt{15.07\text{ k}\Omega \cdot 15.0\text{ k}\Omega \cdot 680\text{ pF} \times 360\text{ pF}}} \approx 1.343 \times 10^5\text{ rad/s}$$
$$f_0 = \frac{\omega_0}{2\pi} \approx 21.4\text{ kHz}$$
$$Q = \frac{\sqrt{R_{\text{th}} R_2 C_1 C_2}}{C_2(R_{\text{th}} + R_2)} \approx \frac{1}{2}\sqrt{\frac{C_1}{C_2}} = \frac{1}{2}\sqrt{\frac{680}{360}} \approx 0.687 \approx \frac{1}{\sqrt{2}}$$

With $Q \approx 0.69$, the response closely matches a Butterworth filter: maximally flat in the passband with no peaking.

### 3.3 Single-Supply Opamp Safety
Because the passive network scales and level-shifts the voltage *before* the opamp inputs:
- Node $N_1$ operates strictly between $+0.145\text{ V}$ and $+3.158\text{ V}$.
- The opamp inputs ($V_+, V_-$) NEVER see negative voltages or voltages above 3.3V.
- Dual Schottky clamping diodes (BAT54S) protect node $N_1$ against overvoltage (e.g. accidental connection to Eurorack $\pm 12\text{ V}$ rails), limiting fault currents through $R_1$ to less than $120\,\mu\text{A}$.

---

## 4. Simulation Results

The circuit was simulated in `ngspice-42` using a full AC frequency sweep (10 Hz – 1 MHz) and transient analysis (1 kHz, 20 Vpp).

### 4.1 Frequency Response Table

| Frequency | Absolute Gain (dB) | Relative Gain (dB) | Phase (deg) | Status / Notes |
|---|---|---|---|---|
| **20 Hz** | -16.44 dB | 0.00 dB | -0.1° | Full audio fidelity |
| **100 Hz** | -16.44 dB | 0.00 dB | -0.4° | DC/low audio baseline |
| **1 kHz** | -16.44 dB | -0.00 dB | -3.9° | Mid audio flat passband |
| **5 kHz** | -16.48 dB | -0.04 dB | -20.1° | Flat passband |
| **10 kHz** | -16.76 dB | -0.32 dB | -41.5° | Negligible attenuation |
| **15 kHz** | -17.63 dB | -1.19 dB | -64.8° | High audio band |
| **20 kHz** | -19.16 dB | **-2.72 dB** | -85.4° | Upper audio boundary |
| **20.89 kHz** | -19.53 dB | **-3.09 dB** | -89.0° | **-3 dB Cutoff Frequency ($f_c$)** |
| **24 kHz** | -20.83 dB | -4.39 dB | -99.9° | Nyquist for 48 kHz sampling |
| **44.1 kHz** | -29.22 dB | **-12.78 dB** | -138.4° | CD sampling frequency |
| **48 kHz** | -30.73 dB | **-14.29 dB** | -142.6° | Standard audio ADC rate |
| **96 kHz** | -42.51 dB | **-26.07 dB** | -164.5° | High-res ADC rate |
| **100 kHz** | -43.31 dB | **-26.87 dB** | -165.5° | Out-of-band rejection |
| **200 kHz** | -55.33 dB | **-38.89 dB** | -178.2° | Attenuation $> 38\text{ dB}$ |
| **1 MHz** | -84.70 dB | **-68.26 dB** | +149.6° | High-frequency stopband |

### 4.2 Key Metrics Summary
- **Passband Gain:** $-16.44\text{ dB}$ ($|A_v| = 0.1507$)
- **Cutoff Frequency ($f_{-3\text{dB}}$):** $20.89\text{ kHz}$
- **Stopband Roll-off Rate:** $-39.8\text{ dB/decade}$ ($\approx -40\text{ dB/decade}$, 2nd-order characteristic)
- **Transient Input Range:** $-10.000\text{ V}$ to $+10.000\text{ V}$ ($20.0\text{ V}_{\text{pp}}$)
- **Transient Output Range:** $+0.145\text{ V}$ to $+3.158\text{ V}$ ($3.013\text{ V}_{\text{pp}}$)
- **DC Midpoint:** $+1.652\text{ V}$ (Centered at $\approx 1.65\text{ V}$)
- **Rail Margins:** $145.4\text{ mV}$ above GND, $141.7\text{ mV}$ below 3.3V

---

## 5. Recommended Opamp Selection

The opamp must support single-rail 3.3V operation with Rail-to-Rail Input and Output (RRIO):

1. **Microchip MCP6002 (Dual) / MCP6001 (Single) / MCP6004 (Quad):**
   - Supply: 1.8 V to 6.0 V
   - Rail-to-rail input and output
   - Gain Bandwidth: 1.0 MHz
   - Slew Rate: 0.6 V/µs (required for 3.0 Vpp at 20 kHz is $SR \ge 2\pi f V_p = 0.19\text{ V/\mu s}$)
   - Widely used across Mutable Instruments Eurorack modules.

2. **Texas Instruments TLV9002 (Dual):**
   - Supply: 1.8 V to 5.5 V
   - Rail-to-rail I/O, low noise ($27\text{ nV}/\sqrt{\text{Hz}}$)
   - Gain Bandwidth: 1.0 MHz, Slew Rate: 2.0 V/µs
   - Modern, low-cost replacement with excellent DC precision.

---

## 6. Project Files

- `antialiasing-input-stage.kicad_pro`: KiCad 9.0 project file
- `antialiasing-input-stage.kicad_sch`: KiCad 9.0 schematic
- `antialiasing-input-stage.kicad_pcb`: KiCad board file
- `antialiasing-input-stage.wbk`: KiCad simulation workbook (AC & Transient setups)
- `antialiasing_input_stage.cir`: SPICE netlist for ngspice
- `simulate.py`: Simulation runner script (runs SPICE, prints table, exports CSV, generates plots)
- `frequency_response.csv`: Simulated frequency response data
- `frequency_response.png`: Bode magnitude and phase response plot
- `transient_response.png`: Input vs output waveform plot

---

## 7. Running the Simulation

To re-run the simulation and regenerate plots/data:

```bash
python3 simulate.py
```

Or run SPICE directly in batch mode:

```bash
ngspice -b antialiasing_input_stage.cir
```

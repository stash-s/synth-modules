# Eurorack to STM32 ADC Antialiasing Input Stage

A 2nd-order active antialiasing low-pass filter and level-shifter stage designed for interfacing Eurorack modular synthesizer audio signals into an STM32 microcontroller ADC running on a single 3.3V rail.

---

## 1. Specifications & Design Requirements

| Parameter | Specification | Notes / Purpose |
|---|---|---|
| **Input Signal** | 20 Vpp (±10.0 V) Bipolar Audio | Maximum Eurorack modular audio level (±10V) |
| **Output Signal** | 0.0 V to 3.3 V Unipolar | Full range acceptable by STM32 ADC (0 to $V_{\text{DDA}}$) |
| **Output Swing (Nominal)** | 0.31 V to 3.06 V (Center = 1.682 V) | Safe >240 mV rail headroom margin for RRIO opamp linearity |
| **Power Supply** | Single-rail +3.3 V ($V_{\text{DD}} = 3.3\text{ V}, V_{\text{SS}} = 0\text{ V}$) | Matches microcontroller $V_{\text{DDA}}$ rail |
| **Input Impedance** | $100\text{ k}\Omega$ | Standard Eurorack input impedance (E12 series) |
| **Resistor Standards** | E12 Standard Series (10%) | All resistors ($R_1, R_{\text{PU}}, R_{\text{PD}}, R_2, R_{\text{ADC}}$) from E12 |
| **Capacitor Standards** | E6 Standard Series (20%) | All capacitors ($C_1, C_2, C_{\text{ADC}}$) from E6 |
| **Filter Topology** | 2nd-Order Sallen-Key Low-Pass Filter | Butterworth response ($Q \approx 0.71$) |
| **Cutoff Frequency ($f_{-3\text{dB}}$)** | $\approx 21.4\text{ kHz}$ | Preserves 20 Hz – 20 kHz audio band |
| **Stopband Attenuation** | $\approx -40\text{ dB/decade}$ (2nd-order roll-off) | Eliminates out-of-band aliasing at ADC sample rates |
| **Post-Filter / ADC Buffer** | 1st-order RC ($100\,\Omega + 1\text{ nF}$) | ADC sampling charge reservoir and high-frequency noise sink |
| **Input Protection** | Dual Schottky diodes to +3.3V & GND | Clamps overvoltage/fault conditions (e.g. ±12V eurorack rails) |

---

## 2. Circuit Diagram

```text
                     +3.3V (VDD)
                       |
                     [R_PU] (27k, E12)
                       |
                       |        C1 (680pF, E6)
                       +---------------+---------------------------------+
 Eurorack              |               |                                 |
 Audio In       N1     |        N2     |                                 |
(20Vpp, ±10V)   |      |        |      |                                 |
  o----[ R1 ]----+---->+---[ R2 ]-+----(+)                               |
        (100k,  |      |   (18k,  |     |   U1 (TLV9002/MCP6002)         |
         E12)   |    [R_PD] E12) [C2]   |   Single 3.3V Supply           |
             +--+--+ (39k,     (330pF,  |       |\                       |
             |     |  E12)       E6)    |       | \                      |
            _|_   _|_  |          |     |       |  \                     |
          D1 /_\  \ / D2          |     |       |   >----+---------------+--[ R_ADC ]--o (ADC_IN)
       BAT54S |    | BAT54S      GND    +-----( -|  /     |                 (100R, E12)  |
            +3.3V GND                            | /      |                            [C_ADC]
                                                 |/       |                            (1nF, E6)
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

#### Standard E12 Resistor Selection:
Using standard E12 series (10% standard values: 10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82):
- $R_1 = 100\text{ k}\Omega$ (E12 base 1.0 $\times 10^5$)
- $R_{\text{PU}} = 27\text{ k}\Omega$ (E12 base 2.7 $\times 10^4$)
- $R_{\text{PD}} = 39\text{ k}\Omega$ (E12 base 3.9 $\times 10^4$)

Resulting parameters:
- $G_{\text{tot}} = 10.000\,\mu\text{S} + 37.037\,\mu\text{S} + 25.641\,\mu\text{S} = 72.678\,\mu\text{S}$
- $R_{\text{th}} = \frac{1}{72.678\,\mu\text{S}} \approx 13.759\text{ k}\Omega$
- Voltage Gain: $K_{\text{att}} = \frac{10.000\,\mu\text{S}}{72.678\,\mu\text{S}} \approx 0.1376$ ($-17.23\text{ dB}$)
- DC Offset: $V_{\text{offset}} = 3.3\text{ V} \times \frac{37.037\,\mu\text{S}}{72.678\,\mu\text{S}} \approx 1.682\text{ V}$

#### Signal Range Verification:
- At $V_{\text{in}} = -10.0\text{ V}$: $V_{\text{out}} = 1.682\text{ V} + 0.1376 \times (-10.0\text{ V}) = +0.306\text{ V}$ ($306\text{ mV}$ above GND rail)
- At $V_{\text{in}} = 0.0\text{ V}$: $V_{\text{out}} = 1.682\text{ V} + 0.1376 \times (0.0\text{ V}) = +1.682\text{ V}$ (midscale, digital code ~2087 on 12-bit ADC)
- At $V_{\text{in}} = +10.0\text{ V}$: $V_{\text{out}} = 1.682\text{ V} + 0.1376 \times (+10.0\text{ V}) = +3.058\text{ V}$ ($242\text{ mV}$ below 3.3V rail)

### 3.2 2nd-Order Sallen-Key Low-Pass Filter (E12 Resistors & E6 Capacitors)
The Sallen-Key topology incorporates the Thevenin source resistance $R_{\text{th}}$ directly as the first filter resistor, paired with standard E12 resistor and E6 capacitor values:
- $R_{\text{filter1}} = R_{\text{th}} \approx 13.76\text{ k}\Omega$
- $R_2 = 18\text{ k}\Omega$ (E12 base 1.8 $\times 10^4$)
- $C_1 = 680\text{ pF}$ (E6 base 6.8 $\times 10^{-10}$, feedback capacitor)
- $C_2 = 330\text{ pF}$ (E6 base 3.3 $\times 10^{-10}$, grounded capacitor)

The transfer function is:
$$H(s) = \frac{V_{\text{out}}(s)}{V_{\text{th}}(s)} = \frac{1}{s^2 R_{\text{th}} R_2 C_1 C_2 + s C_2(R_{\text{th}} + R_2) + 1}$$

Natural angular frequency $\omega_0$ and quality factor $Q$:
$$\omega_0 = \frac{1}{\sqrt{R_{\text{th}} R_2 C_1 C_2}} = \frac{1}{\sqrt{13.759\text{ k}\Omega \cdot 18.0\text{ k}\Omega \cdot 680\text{ pF} \times 330\text{ pF}}} \approx 1.341 \times 10^5\text{ rad/s}$$
$$f_0 = \frac{\omega_0}{2\pi} \approx 21.35\text{ kHz}$$
$$Q = \frac{\sqrt{R_{\text{th}} R_2 C_1 C_2}}{C_2(R_{\text{th}} + R_2)} = \frac{7.453 \times 10^{-6}}{330\text{ pF} \times (13.759\text{ k}\Omega + 18.0\text{ k}\Omega)} \approx 0.711 \approx \frac{1}{\sqrt{2}} \approx 0.7071$$

With $Q \approx 0.711$, the response provides an almost exact Butterworth characteristic: maximally flat across the entire audio passband (20 Hz – 20 kHz) with zero peaking, followed by a steep 2nd-order roll-off.

### 3.3 Component Standard Series Compliance Summary

| Component | Function | Value | Standard Series | Decade / Base Value |
|---|---|---|---|---|
| **$R_1$** | Input Attenuator / Eurorack Impedance | $100\text{ k}\Omega$ | **E12** | $1.0 \times 10^5\,\Omega$ |
| **$R_{\text{PU}}$** | Pull-Up Bias to +3.3V | $27\text{ k}\Omega$ | **E12** | $2.7 \times 10^4\,\Omega$ |
| **$R_{\text{PD}}$** | Pull-Down Bias to GND | $39\text{ k}\Omega$ | **E12** | $3.9 \times 10^4\,\Omega$ |
| **$R_2$** | Sallen-Key 2nd Filter Resistor | $18\text{ k}\Omega$ | **E12** | $1.8 \times 10^4\,\Omega$ |
| **$R_{\text{ADC}}$** | ADC Charge-Bucket Isolation | $100\,\Omega$ | **E12** | $1.0 \times 10^2\,\Omega$ |
| **$C_1$** | Sallen-Key Feedback Capacitor | $680\text{ pF}$ | **E6** | $6.8 \times 10^{-10}\text{ F}$ |
| **$C_2$** | Sallen-Key Ground Filter Capacitor | $330\text{ pF}$ | **E6** | $3.3 \times 10^{-10}\text{ F}$ |
| **$C_{\text{ADC}}$** | ADC Sampling Reservoir Capacitor | $1\text{ nF}$ | **E6** | $1.0 \times 10^{-9}\text{ F}$ |

### 3.4 Single-Supply Opamp Safety
Because the passive network scales and level-shifts the voltage *before* the opamp inputs:
- Node $N_1$ operates strictly between $+0.306\text{ V}$ and $+3.058\text{ V}$.
- The opamp inputs ($V_+, V_-$) NEVER see negative voltages or voltages above 3.3V.
- Dual Schottky clamping diodes (BAT54S) protect node $N_1$ against overvoltage (e.g. accidental connection to Eurorack $\pm 12\text{ V}$ rails), limiting fault currents through $R_1$ to less than $120\,\mu\text{A}$.

---

## 4. Simulation Results

The circuit was simulated in `ngspice-42` using a full AC frequency sweep (10 Hz – 1 MHz) and transient analysis (1 kHz, 20 Vpp).

### 4.1 Frequency Response Table

| Frequency | Absolute Gain (dB) | Relative Gain (dB) | Phase (deg) | Status / Notes |
|---|---|---|---|---|
| **20 Hz** | -17.23 dB | 0.00 dB | -0.1° | Full audio fidelity |
| **100 Hz** | -17.23 dB | 0.00 dB | -0.4° | DC/low audio baseline |
| **1 kHz** | -17.23 dB | 0.00 dB | -3.8° | Mid audio flat passband |
| **5 kHz** | -17.24 dB | -0.01 dB | -19.5° | Flat passband |
| **10 kHz** | -17.42 dB | -0.19 dB | -40.6° | Negligible attenuation |
| **15.1 kHz** | -18.18 dB | -0.95 dB | -64.2° | High audio band |
| **20 kHz** | -19.67 dB | **-2.44 dB** | -85.4° | Upper audio boundary |
| **21.38 kHz** | -20.23 dB | **-3.00 dB** | -91.0° | **-3 dB Cutoff Frequency ($f_c$)** |
| **24 kHz** | -21.35 dB | -4.12 dB | -100.4° | Nyquist for 48 kHz sampling |
| **43.7 kHz** | -29.91 dB | **-12.68 dB** | -139.5° | CD sampling frequency |
| **47.9 kHz** | -31.44 dB | **-14.21 dB** | -143.7° | Standard audio ADC rate |
| **95.5 kHz** | -43.31 dB | **-26.08 dB** | -165.1° | High-res ADC rate |
| **100 kHz** | -44.11 dB | **-26.88 dB** | -166.1° | Out-of-band rejection |
| **199.5 kHz** | -56.15 dB | **-38.92 dB** | -178.5° | Attenuation $> 38\text{ dB}$ |
| **1 MHz** | -85.53 dB | **-68.30 dB** | +149.5° | High-frequency stopband |

### 4.2 Key Metrics Summary
- **Passband Gain:** $-17.23\text{ dB}$ ($|A_v| = 0.1376$)
- **Cutoff Frequency ($f_{-3\text{dB}}$):** $21.38\text{ kHz}$
- **Stopband Roll-off Rate:** $-39.9\text{ dB/decade}$ ($\approx -40\text{ dB/decade}$, 2nd-order characteristic)
- **Transient Input Range:** $-10.000\text{ V}$ to $+10.000\text{ V}$ ($20.0\text{ V}_{\text{pp}}$)
- **Transient Output Range:** $+0.306\text{ V}$ to $+3.058\text{ V}$ ($2.752\text{ V}_{\text{pp}}$)
- **DC Midpoint:** $+1.682\text{ V}$ (Centered near $1.65\text{ V}$)
- **Rail Margins:** $305.7\text{ mV}$ above GND, $242.4\text{ mV}$ below 3.3V (excellent linearity margins)

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

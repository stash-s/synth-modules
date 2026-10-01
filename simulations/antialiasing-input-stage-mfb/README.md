# Eurorack-to-STM32 MFB Antialiasing Input Stage

A second-order multiple-feedback (MFB) low-pass input stage for conditioning a bipolar 20 Vpp Eurorack signal for a single-supply 3.3 V STM32 ADC.

## Design Targets

| Item | Design |
|---|---|
| Input | -10 V to +10 V, 1 kHz transient stimulus |
| Supply | Single rail, +3.3 V and GND |
| Filter | Inverting, second-order MFB low-pass |
| Nominal natural frequency | 20.81 kHz |
| Nominal Q | 0.713, near Butterworth |
| Measured -3 dB cutoff | 20.90 kHz (interpolated) |
| ADC output, simulated transient | 0.412 V to 2.832 V |
| Resistors | E12 values |
| Capacitors | E6 values |

## Circuit

```text
Input and bias:
IN -- R_IN 100k -- N1
                    |-- R_PU 27k -- +3.3V
                    |-- R_PD 39k -- GND
                    |-- D3 (A=N1, K=+3.3V)
                    `-- D4 (A=GND, K=N1)

MFB low-pass:
N1 -- R1 100k -- N_MFB -- R3 3.9k -- N_INV -- U1 (-)
                    |                         |
                    |-- C2 1.5n -- GND         `-- C5 100p -- OUT
                    `-- R4 100k -- OUT

Bias and ADC:
+3.3V -- R_REF_PU 33k -- VREF -- R_REF_PD 33k -- GND
                           |                     (+) U1
                         C_REF 10u
                           |
                          GND

OUT -- R_ADC 100R -- ADC_IN
                       |
                    C_ADC 1n
                       |
                      GND
```

The MFB op-amp is inverting around `VREF`. The input attenuator biases `N1` near 1.68 V, while the equal 33 kOhm divider sets `VREF` to 1.65 V. This small difference gives a simulated output midpoint of 1.622 V; the 20 Vpp input remains comfortably inside the ADC rails. Clamp diodes are connected in opposite directions, not across the supply as a forward-biased pair.

## Component Values

| Reference | Value | Series | Purpose |
|---|---:|---|---|
| `R_IN` | 100 kOhm | E12 | Eurorack input impedance |
| `R_PU`, `R_PD` | 27 kOhm, 39 kOhm | E12 | Input attenuation and bias |
| `R1` | 100 kOhm | E12 | MFB input arm |
| `R3` | 3.9 kOhm | E12 | Inverting-node arm |
| `R4` | 100 kOhm | E12 | MFB feedback resistor |
| `R_REF_PU`, `R_REF_PD` | 33 kOhm each | E12 | 1.65 V reference divider |
| `R_ADC` | 100 Ohm | E12 | ADC sampling isolation |
| `C2` | 1.5 nF | E6 | MFB shunt capacitor |
| `C5` | 100 pF | E6 | MFB feedback capacitor |
| `C_REF` | 10 uF | E6 | Reference bypass |
| `C_ADC` | 1 nF | E6 | ADC charge reservoir |

The input divider's Thevenin resistance is

$$R_{th}=\left(\frac1{100\,k\Omega}+\frac1{27\,k\Omega}+\frac1{39\,k\Omega}\right)^{-1}=13.759\,k\Omega.$$

The MFB input arm therefore sees `R1 + Rth = 113.759 kOhm`. For the ideal-op-amp MFB section,

$$H(s)=-\frac{R_4/R_{1,eff}}{1+sC_5\left(R_4+R_3+\frac{R_3R_4}{R_{1,eff}}\right)+s^2R_3R_4C_2C_5}.$$

This gives `f0 = 20.81 kHz`, `Q = 0.713`, and a low-frequency MFB gain magnitude of `R4/R1,eff = 0.879`. Including the input attenuation, the overall passband gain is about `-18.35 dB`.

## Simulation Results

The circuit was run with ngspice 47, using the project-local `RRIO_OPAMP` macro-model (10 MHz GBW) and Schottky diode models.

| Frequency | Absolute gain | Relative to 100 Hz |
|---:|---:|---:|
| 20 Hz | -18.35 dB | 0.00 dB |
| 1 kHz | -18.35 dB | 0.00 dB |
| 10 kHz | -18.49 dB | -0.14 dB |
| 20 kHz | -20.94 dB | -2.59 dB |
| 21.38 kHz | -21.56 dB | -3.21 dB |
| 48 kHz | -33.23 dB | -14.88 dB |
| 100 kHz | -45.97 dB | -27.62 dB |
| 1 MHz | -87.45 dB | -69.11 dB |

The measured stopband slope is `-40.1 dB/decade`. For a 1 kHz, 20 Vpp transient, the ADC node ranges from `0.412 V` to `2.832 V` with at least `412 mV` rail margin.

`RRIO_OPAMP` is a simulation macro-model, not a selected physical part. The schematic uses a single 3.3 V supply; substitute a vendor model for the intended RRIO amplifier before hardware release.

## Project and Simulation

- `antialiasing-input-stage-mfb.kicad_pro`: KiCad project
- `antialiasing-input-stage-mfb.kicad_sch`: circuit schematic
- `antialiasing_input_stage.cir`: ngspice deck
- `antialiasing_input_stage.lib`: shared diode and op-amp models
- `simulate.py`: runs the deck, analyzes the AC/transient results, and generates CSV/plots

With ngspice and the Python plotting dependencies installed:

```sh
python3 simulate.py
```

In the KiCad Flatpak, the runner uses the bundled shared ngspice library if the `ngspice` executable is unavailable. If Flatpak Python lacks matplotlib, run the simulation there, then use host Python to generate the plots from the existing output files:

```sh
python3 simulate.py --process-only
```

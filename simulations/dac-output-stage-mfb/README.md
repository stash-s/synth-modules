# STM32 DAC to Eurorack MFB Output Stage

A single-op-amp, second-order multiple-feedback (MFB) low-pass output stage that converts an STM32 DAC signal into a bipolar Eurorack-level output. The op-amp is powered from the standard ±12 V rails.

## Design Targets

| Item | Design |
|---|---|
| DAC input | 0 V to 3.3 V, 1 kHz transient stimulus |
| Op-amp supply | +12 V and -12 V |
| Filter topology | Inverting, second-order MFB low-pass |
| Nominal natural frequency | 19.37 kHz |
| Nominal Q | 0.706, near Butterworth |
| Measured -3 dB cutoff | 19.09 kHz |
| Measured stopband slope | -40.1 dB/decade |
| Ideal output for 0–3.3 V DAC input | +10.183 V to -10.277 V |
| Transient test output (0.85–2.45 V input) | -5.007 V to +4.913 V |
| Resistors | E12 values except 52k/620k selections |
| Capacitors | E6 values |

## Circuit

```text
DAC_IN -- R1 100k -- N_MFB -- R3 22k -- N_INV -- U1 (-)
                       |                    |
                       |-- C2 330p -- GND   `-- C5 15p -- OUT
                       `-- R4 620k -- OUT

OUT -- R_OUT 100R -- EURORACK_OUT
                         |
                      C_OUT 1n
                         |
                        GND

+3.3V -- R_REF_PU 52k -- VREF -- R_REF_PD 39k -- GND
                           |                    
                         C_REF 10u
                           |
                          GND
                           |
                         U1 (+)

U1 V+ = +12V
U1 V- = -12V
```

The non-inverting input reference is

$$V_{REF}=3.3\frac{39k}{52k+39k}=1.414\,V.$$

The low-frequency transfer from DAC input to op-amp output is approximately

$$V_{OUT}=V_{REF}\left(1+\frac{R_4}{R_1}\right)-\frac{R_4}{R_1}V_{IN},$$

with $R_4=620k$ and $R_4/R_1=6.2$. Thus 0 V input produces about +10.183 V, 1.65 V input produces about -0.047 V, and 3.3 V input produces about -10.277 V. The filter is inverting: polarity flips across the DAC range. Both endpoints remain inside the ±12 V supply rails.

For the ideal MFB section,

$$H(s)=-\frac{R_4/R_1}{1+sC_5\left(R_4+R_3+\frac{R_3R_4}{R_1}\right)+s^2R_3R_4C_2C_5}.$$

The selected values give $f_0\approx19.37\,kHz$ and $Q\approx0.706$. The 100 Ohm / 1 nF output network isolates capacitive loads; its pole is well above the audio band.

## Component Values

| Reference | Value | Series | Purpose |
|---|---:|---|---|
| `R1` | 100 kOhm | E12 | DAC input arm |
| `R3` | 22 kOhm | E12 | MFB inverting-node arm |
| `R4` | 620 kOhm | E24 | MFB feedback resistor |
| `R_REF_PU`, `R_REF_PD` | 52 kOhm, 39 kOhm | E24, E12 | 1.414 V op-amp reference |
| `R_OUT` | 100 Ohm | E12 | Output isolation |
| `C2` | 330 pF | E6 | MFB shunt capacitor |
| `C5` | 15 pF | E6 | MFB feedback capacitor |
| `C_REF` | 10 uF | E6 | Reference bypass |
| `C_OUT` | 1 nF | E6 | Output load isolation capacitor |

## Simulation Results

The circuit was simulated with ngspice 47 and the project-local `RRIO_OPAMP` macro-model (10 MHz GBW).

| Frequency | Absolute gain | Relative to 100 Hz |
|---:|---:|---:|
| 20 Hz | +15.85 dB | 0.00 dB |
| 1 kHz | +15.85 dB | 0.00 dB |
| 10 kHz | +15.57 dB | -0.28 dB |
| 15.1 kHz | +14.44 dB | -1.41 dB |
| 20 kHz | +12.44 dB | -3.41 dB |
| 24 kHz | +10.38 dB | -5.47 dB |
| 48 kHz | -0.36 dB | -16.20 dB |
| 100 kHz | -13.09 dB | -28.94 dB |
| 1 MHz | -54.45 dB | -70.30 dB |

The schematic transient stimulus is 0.85–2.45 V at 1 kHz; its simulated Eurorack output spans -5.007 V to +4.913 V around a -0.047 V midpoint. The full DAC range maps ideally to +10.183 V at 0 V and -10.277 V at 3.3 V, leaving more than 1.7 V to either supply rail.

`RRIO_OPAMP` is a simulation macro-model, not a selected physical part. Select an amplifier that supports ±12 V rails, a 10 V output swing into the intended load, and adequate bandwidth/slew rate; use its vendor model before hardware release.

## Project and Simulation

- `dac-output-stage-mfb.kicad_pro`: KiCad project
- `dac-output-stage-mfb.kicad_sch`: schematic
- `dac_output_stage.cir`: ngspice deck
- `dac_output_stage.lib`: op-amp model library
- `simulate.py`: simulation runner, analyzer, and plot generator
- `frequency_response.csv`, `frequency_response.png`: AC sweep results
- `transient_response.png`: DAC-to-Eurorack transient response

Run where ngspice and matplotlib are installed:

```sh
python3 simulate.py
```

With the KiCad Flatpak, run `python3 simulate.py` inside its shell to use bundled ngspice. If that Flatpak Python has no matplotlib, run `python3 simulate.py --process-only` with host Python afterward to make the CSV and plots from the generated raw data.

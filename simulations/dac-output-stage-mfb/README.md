# STM32 DAC to Eurorack MFB Output Stage

A single-op-amp, second-order multiple-feedback (MFB) low-pass output stage that converts an STM32 DAC signal into a bipolar Eurorack-level output. The op-amp is powered from the standard ±12 V rails.

## Design Targets

| Item | Design |
|---|---|
| DAC input | 0 V to 3.3 V, 1 kHz transient stimulus |
| Op-amp supply | +12 V and -12 V |
| Filter topology | Inverting, second-order MFB low-pass |
| Nominal natural frequency | 19.43 kHz |
| Nominal Q | 0.706, near Butterworth |
| Measured -3 dB cutoff | 19.21 kHz |
| Measured stopband slope | -40.1 dB/decade |
| Simulated output | -10.628 V to +9.700 V |
| Resistors | E12 values, including series 560k + 56k feedback |
| Capacitors | E6 values |

## Circuit

```text
DAC_IN -- R1 100k -- N_MFB -- R3 22k -- N_INV -- U1 (-)
                       |                    |
                       |-- C2 330p -- GND   `-- C5 15p -- OUT
                       `-- R4A 560k -- R4B 56k -- OUT

OUT -- R_OUT 100R -- EURORACK_OUT
                         |
                      C_OUT 1n
                         |
                        GND

+3.3V -- R_REF_PU 56k -- VREF -- R_REF_PD 39k -- GND
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

$$V_{REF}=3.3\frac{39k}{56k+39k}=1.355\,V.$$

The low-frequency transfer from DAC input to op-amp output is approximately

$$V_{OUT}=V_{REF}\left(1+\frac{R_4}{R_1}\right)-\frac{R_4}{R_1}V_{IN},$$

with $R_4=560k+56k=616k$ and $R_4/R_1=6.16$. Thus 0 V input produces about +9.70 V, while 3.3 V produces about -10.63 V. The filter is inverting: polarity flips across the DAC range. Both endpoints remain inside the ±12 V supply rails.

For the ideal MFB section,

$$H(s)=-\frac{R_4/R_1}{1+sC_5\left(R_4+R_3+\frac{R_3R_4}{R_1}\right)+s^2R_3R_4C_2C_5}.$$

The selected values give $f_0\approx19.43\,kHz$ and $Q\approx0.706$. The 100 Ohm / 1 nF output network isolates capacitive loads; its pole is well above the audio band.

## Component Values

| Reference | Value | Series | Purpose |
|---|---:|---|---|
| `R1` | 100 kOhm | E12 | DAC input arm |
| `R3` | 22 kOhm | E12 | MFB inverting-node arm |
| `R4A`, `R4B` | 560 kOhm, 56 kOhm | E12 | 616 kOhm MFB feedback resistor |
| `R_REF_PU`, `R_REF_PD` | 56 kOhm, 39 kOhm | E12 | 1.355 V op-amp reference |
| `R_OUT` | 100 Ohm | E12 | Output isolation |
| `C2` | 330 pF | E6 | MFB shunt capacitor |
| `C5` | 15 pF | E6 | MFB feedback capacitor |
| `C_REF` | 10 uF | E6 | Reference bypass |
| `C_OUT` | 1 nF | E6 | Output load isolation capacitor |

## Simulation Results

The circuit was simulated with ngspice 47 and the project-local `RRIO_OPAMP` macro-model (10 MHz GBW).

| Frequency | Absolute gain | Relative to 100 Hz |
|---:|---:|---:|
| 20 Hz | +15.79 dB | 0.00 dB |
| 1 kHz | +15.79 dB | 0.00 dB |
| 10 kHz | +15.53 dB | -0.26 dB |
| 15.1 kHz | +14.42 dB | -1.37 dB |
| 20 kHz | +12.44 dB | -3.35 dB |
| 24 kHz | +10.39 dB | -5.40 dB |
| 48 kHz | -0.35 dB | -16.14 dB |
| 100 kHz | -13.09 dB | -28.88 dB |
| 1 MHz | -54.45 dB | -70.24 dB |

For a 1 kHz DAC sine spanning 0–3.3 V, the simulated Eurorack output spans -10.628 V to +9.700 V. The distance to the -12 V rail is 1.372 V; the distance to +12 V is 2.300 V.

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

Simulated Real-Time Gear Condition Monitoring and RUL Prediction System

A simulation-based gear condition monitoring system combining gear pitting degradation modelling, vibration signal processing, vibration-based condition assessment, physics-based Remaining Useful Life (RUL) prediction, and real-time IIoT visualisation.

Project Overview

Gear failures, particularly pitting failures, can lead to unexpected downtime, increased maintenance costs, and production losses.

This project develops a simulated real-time gear condition monitoring system to study how gear degradation can be detected and tracked using vibration signals.

The system combines:

Pitting-area degradation modelling

Synthetic vibration signal generation

Time Synchronous Averaging (TSA)

Fast Fourier Transform (FFT)

Gear Mesh Frequency (GMF) analysis

GMF sideband analysis

Residual vibration extraction

Correlation Coefficient (CCR) as a condition indicator

Physics-based Remaining Useful Life (RUL) prediction

MQTT data transmission

Node-RED data processing

InfluxDB time-series storage

Grafana real-time visualisation

The overall objective is to connect mechanical gear degradation and vibration analysis with digital condition monitoring and predictive maintenance concepts.

System Architecture

Reference Gear Degradation Data
              │
              ▼
       Pitting Area D(t)
              │
              ▼
    Pitting Degradation Model
              │
              ▼
    Synthetic Vibration Signal
              │
              ▼
 Time Synchronous Averaging (TSA)
              │
              ▼
             FFT
              │
              ▼
   Gear Mesh Frequency (GMF)
        + GMF Sidebands
              │
              ▼
       GMF Filtering
              │
              ▼
       Residual Vibration
              │
         ┌────┴────┐
         ▼         ▼
        CCR       RUL
         │         │
         └────┬────┘
              ▼
             MQTT
              │
              ▼
          Node-RED
              │
              ▼
           InfluxDB
              │
              ▼
            Grafana

Reference Degradation Data

The simulated degradation trajectory is based on pitting-area measurements reported in:

Kundu et al. (2025), Development of data-driven, physics-based, and hybrid prognosis frameworks: a case study for gear remaining useful life prediction.

The reference degradation points used in the simulation are:

Point

Time (min)

Pitting Area (mm²)

M1

500

1.0

M2

1000

2.5

M3

1500

4.1

M4

1700

5.9

M5

1998

8.0

An initial healthy condition of 0 mm² pitting area at 0 minutes is also included.

Linear interpolation between the reference points is used to estimate the pitting area at intermediate simulation times.

Gear and Simulation Parameters

Parameter

Value

Shaft speed

2400 RPM

Shaft frequency

40 Hz

Number of gear teeth

27

Gear Mesh Frequency (GMF)

1080 Hz

Sampling frequency

20 kHz

Acquisition duration

10 s

Acquisition interval

6 min

Samples per revolution

500

Maximum pitting area

8.0 mm²

Gear Mesh Frequency

The Gear Mesh Frequency (GMF) represents the frequency at which gear teeth engage.

It is calculated as:

GMF = Number of gear teeth × Shaft frequency

For this simulation:

GMF = 27 × 40
GMF = 1080 Hz

Therefore, the simulated gear mesh frequency is 1080 Hz.

GMF Sidebands

Gear faults can produce frequency components around the Gear Mesh Frequency.

In this simulation, the shaft rotational frequency is used to define the first-order sidebands.

Lower Sideband

Lower Sideband = GMF - Shaft Frequency
                = 1080 - 40
                = 1040 Hz

Upper Sideband

Upper Sideband = GMF + Shaft Frequency
                = 1080 + 40
                = 1120 Hz

Therefore:

Lower Sideband = 1040 Hz
GMF            = 1080 Hz
Upper Sideband = 1120 Hz

The sideband amplitudes are increased progressively with simulated pitting severity.

Synthetic Vibration Signal

The vibration signal is computationally generated using:

Shaft rotational frequency

Gear Mesh Frequency

GMF sidebands

Random noise

The healthy signal contains the shaft-frequency and GMF components.

As pitting progresses, additional sideband components are introduced around the GMF.

Conceptually:

Healthy Gear

Shaft Frequency
       +
Gear Mesh Frequency
       +
Noise

and:

Pitted Gear

Shaft Frequency
       +
Gear Mesh Frequency
       +
GMF Sidebands
       +
Noise

The sideband amplitude is scaled according to the simulated pitting area.

Time Synchronous Averaging (TSA)

Time Synchronous Averaging is used to reduce non-synchronous components of the vibration signal and emphasize components related to gear rotation.

The shaft speed is:

RPM = 2400

Therefore:

Shaft Frequency = 2400 / 60
                = 40 Hz

The number of samples per revolution is:

Samples per Revolution
= Sampling Frequency / Shaft Frequency

= 20,000 / 40

= 500 samples/revolution

The acquisition duration is 10 seconds.

Therefore, the number of revolutions in one acquisition is:

40 × 10 = 400 revolutions

The simulated signal is reshaped into:

400 revolutions × 500 samples/revolution

and averaged across revolutions to obtain the TSA signal.

Fast Fourier Transform (FFT)

The Time Synchronous Average signal is converted from the time domain into the frequency domain using the Fast Fourier Transform (FFT).

The spectrum allows the main frequency components to be observed, including:

Shaft frequency

Gear Mesh Frequency

GMF sidebands

Other frequency components

The frequency-domain representation is used for subsequent gear-mesh filtering and residual signal extraction.

GMF Filtering and Residual Signal

The Gear Mesh Frequency component is removed from the FFT spectrum.

The filtered spectrum is then transformed back into the time domain using the inverse FFT.

This produces a residual vibration signal.

The processing sequence is:

TSA Signal
    │
    ▼
   FFT
    │
    ▼
Frequency Spectrum
    │
    ▼
Remove GMF Component
    │
    ▼
Filtered Spectrum
    │
    ▼
Inverse FFT
    │
    ▼
Residual Vibration

The residual signal is subsequently used for calculating the vibration-based condition indicator.

Correlation Coefficient (CCR)

The Correlation Coefficient of the Residual Signal (CCR) is used as a vibration-based health indicator.

The healthy residual signal is used as the reference.

For each simulated degradation stage:

Current Residual Signal
          │
          ▼
Compare with
Healthy Residual Signal
          │
          ▼
Correlation Coefficient
          │
          ▼
          CCR

The CCR indicates the similarity between the current residual vibration signal and the healthy reference signal.

A reduction in correlation represents increasing deviation from the healthy vibration condition in the simulation.

Physics-Based Remaining Useful Life (RUL)

A physics-based pitting-growth model is used to estimate the remaining useful life of the gear.

The model uses the pitting area as the degradation variable.

The simulation parameters include:

τ = 196.3 MPa
M = 1.26
log(C) = -21.37

The corresponding value of C is calculated as:

C = exp(log(C))

The defined pitting threshold is:

D_threshold = 8.0 mm²

The model estimates the remaining number of gear cycles until the pitting area reaches the defined threshold.

The predicted number of cycles is then converted into operating time using the shaft speed.

Conceptually:

Pitting Area
      │
      ▼
Pitting Growth Model
      │
      ▼
Remaining Gear Cycles
      │
      ▼
Remaining Useful Life
      │
      ▼
RUL in minutes

Real-Time Simulation

The degradation trajectory contains measurements separated by several hundred minutes, while running the simulation in real time would take many hours.

Therefore, the project uses an accelerated simulation.

The simulated acquisition interval is 6 minutes while the actual Python program waits only 2 seconds between acquisitions.

This allows the complete degradation trajectory to be demonstrated within a practical time period while preserving the simulated degradation timeline.

MQTT Data Transmission

The Python simulation publishes the calculated condition-monitoring parameters using MQTT.

Condition Topic

gearbox/condition

The condition message contains:

{
    "time_min": 500,
    "damage_mm2": 1.0,
    "ccr": 0.95,
    "rul_min": 1234.5
}

The fields represent:

Field

Description

time_min

Simulated degradation time

damage_mm2

Simulated pitting area

ccr

Correlation Coefficient of the residual signal

rul_min

Predicted Remaining Useful Life

Vibration Spectrum MQTT Topics

The simulation also publishes vibration spectrum information.

Healthy Spectrum

gearbox/spectrum/healthy

Current Spectrum

gearbox/spectrum/current

Filtered Spectrum

gearbox/spectrum/filtered

These topics allow the vibration spectrum and filtering process to be visualised through the IIoT pipeline.

IIoT Data Pipeline

The complete digital data pipeline is:

Python
  │
  │ MQTT
  ▼
Node-RED
  │
  ▼
InfluxDB
  │
  ▼
Grafana

Python

Python performs:

Degradation simulation

Vibration signal generation

TSA

FFT

GMF filtering

Residual signal calculation

CCR calculation

RUL calculation

MQTT publishing

Node-RED

Node-RED is used as the data-processing and routing layer between MQTT and the time-series database.

InfluxDB

InfluxDB is used to store time-series condition-monitoring data.

Grafana

Grafana provides real-time visualisation of:

Pitting area

CCR

RUL

CCR trend

Vibration spectra

Project Outputs

The system produces three main condition-monitoring indicators:

1. Pitting Area

Represents the simulated physical degradation state of the gear.

Pitting Area ↑
      ↓
Increasing degradation

2. CCR

Represents the similarity between the current residual vibration and the healthy residual reference.

CCR ↓
  ↓
Increasing deviation from healthy condition

3. RUL

Represents the estimated remaining operating time until the defined pitting threshold is reached.

RUL ↓
  ↓
Less remaining operating life

Together:

Pitting Area ──────► Physical Degradation
       │
       ├────────────► CCR ─────► Vibration Condition
       │
       └────────────► RUL ─────► Prognostic Estimate

Technologies Used

Technology

Purpose

Python

Simulation and signal processing

NumPy

Numerical computation and FFT

Paho MQTT

MQTT communication

MQTT

Data transmission

Node-RED

Data processing and routing

InfluxDB

Time-series database

Grafana

Real-time dashboard

Git

Version control

GitHub

Source-code management and project documentation

Project Structure

GearCMM-Project/
│
├── README.md
├── .gitignore
│
├── src/
│   └── GearCMM.py
│
├── data/
│
├── plots/
│
├── results/
│
├── node_red/
│
├── grafana/
│
└── docs/

Folder Description

src/ — Python source code

data/ — Reference or input datasets

plots/ — Generated plots and visualisations

results/ — Simulation results and calculated outputs

node_red/ — Exported Node-RED flows

grafana/ — Grafana dashboard configuration

docs/ — Project documentation, diagrams, and supporting images

Current Project Status

The current implementation is a simulation-based gear condition monitoring framework.

The vibration signals are computationally generated rather than acquired from a physical gearbox.

The degradation trajectory is based on reference pitting-area data, while the vibration response and sideband behaviour are simulated to demonstrate the complete condition-monitoring workflow.

The current system demonstrates the integration of:

Mechanical Degradation
        +
Vibration Signal Processing
        +
Condition Monitoring
        +
Prognostics
        +
IIoT Data Pipeline
        +
Real-Time Visualisation

Future Development

Future development could include:

Validation using experimental gearbox vibration measurements

Real-time vibration sensor acquisition

Experimental validation of the CCR indicator

Improved physical pitting-growth modelling

Machine-learning-based degradation estimation

Comparison of multiple vibration-based health indicators

Automated fault classification

RUL validation against experimental failure data

Extension to different gear types and operating conditions

Integration with an industrial condition-monitoring system

Author

Kishore Kumar L S

M.Sc. Advanced Manufacturing
Technische Universität Chemnitz
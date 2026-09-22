import numpy as np
import json
import paho.mqtt.client as mqtt


MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "gearbox/condition"
MQTT_HEALTHY_SPECTRUM_TOPIC = "gearbox/spectrum/healthy"
MQTT_CURRENT_SPECTRUM_TOPIC = "gearbox/spectrum/current"
MQTT_FILTERED_SPECTRUM_TOPIC = "gearbox/spectrum/filtered"

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()



RPM = 2400

SAMPLING_RATE = 20_000       # samples per second (Hz)
ACQUISITION_TIME = 10        # seconds
ACQUISITION_INTERVAL = 6     # minutes between acquisitions

GEAR_TEETH = 27              

SHAFT_FREQ = RPM / 60        # Hz
GMF = GEAR_TEETH * SHAFT_FREQ

LOWER_SIDEBAND = GMF - SHAFT_FREQ
UPPER_SIDEBAND = GMF + SHAFT_FREQ

N_SAMPLES = int(SAMPLING_RATE * ACQUISITION_TIME)

SAMPLES_PER_REV = int(SAMPLING_RATE / SHAFT_FREQ)



DAMAGE_TIME = [0, 500, 1000, 1500, 1700, 1998]
DAMAGE_AREA = [0, 1.0, 2.5, 4.1, 5.9, 8.0]


def get_damage(time_min):
    damage = 0.0

    for i in range(len(DAMAGE_TIME) - 1):
        t1 = DAMAGE_TIME[i]
        t2 = DAMAGE_TIME[i + 1]

        d1 = DAMAGE_AREA[i]
        d2 = DAMAGE_AREA[i + 1]

        if t1 <= time_min <= t2:
            damage = d1 + (time_min - t1) * (d2 - d1) / (t2 - t1)
            break

    return damage

acquisition_times = range(
    ACQUISITION_INTERVAL,
    1998 + ACQUISITION_INTERVAL,
    ACQUISITION_INTERVAL
)

damage_values = []

for time in acquisition_times:
    damage = get_damage(time)
    damage_values.append(damage)



A_GM = 1.0
A_SB_MAX = 0.5
D_MAX = 8.0
A_ROT = 0.2


def get_sideband_amplitude(damage):
    sideband_amplitude = A_SB_MAX * (damage / D_MAX)
    return sideband_amplitude



time = np.arange(N_SAMPLES) / SAMPLING_RATE

noise = np.random.normal(0, 0.02, N_SAMPLES)

healthy_vibration = (
    A_ROT * np.sin(2 * np.pi * SHAFT_FREQ * time)
    + A_GM * np.sin(2 * np.pi * GMF * time)
    + noise
)

revolutions = healthy_vibration.reshape(400, SAMPLES_PER_REV)

healthy_tsa = np.mean(revolutions, axis=0)


healthy_fft = np.fft.fft(healthy_tsa)

sample_time = 1 / SAMPLING_RATE

frequency = np.fft.fftfreq(
    len(healthy_tsa),
    d=sample_time
)

positive_frequency = frequency >= 0

healthy_spectrum_frequency = frequency[positive_frequency]

healthy_spectrum_amplitude = (
    2 * np.abs(healthy_fft[positive_frequency])
    / len(healthy_tsa)
)


filtered_healthy_fft = healthy_fft.copy()

remove_gmf = np.isclose(np.abs(frequency), GMF)

filtered_healthy_fft[remove_gmf] = 0


healthy_residual = np.fft.ifft(filtered_healthy_fft)

healthy_residual = np.real(healthy_residual)


healthy_spectrum_payload = json.dumps({
    "spectrum": [
        {
            "frequency_hz": float(f),
            "amplitude": float(a)
        }
        for f, a in zip(
            healthy_spectrum_frequency,
            healthy_spectrum_amplitude
        )
    ]
})

mqtt_client.publish(
    MQTT_HEALTHY_SPECTRUM_TOPIC,
    healthy_spectrum_payload
)


ccr_values = []


TAU = 196.3
M = 1.26
LOG_C = -21.37

C = np.exp(LOG_C)

D_THRESHOLD = 8.0

rul_values = []

import time as real_time

SIMULATION_DELAY = 2     # seconds

print("\n========== SIMULATION START ==========")



for acquisition_time in acquisition_times:

    damage = get_damage(acquisition_time)

    sideband_amplitude = get_sideband_amplitude(damage)

    damaged_noise = np.random.normal(0, 0.02, N_SAMPLES)

    damaged_vibration = (
     A_ROT * np.sin(2 * np.pi * SHAFT_FREQ * time)
     + A_GM * np.sin(2 * np.pi * GMF * time)
     + sideband_amplitude * np.sin(
        2 * np.pi * LOWER_SIDEBAND * time
     )
     + sideband_amplitude * np.sin(
        2 * np.pi * UPPER_SIDEBAND * time
     )
     + damaged_noise
    )

    damaged_revolutions = damaged_vibration.reshape(
      400,
      SAMPLES_PER_REV
      )

    damaged_tsa = np.mean(
     damaged_revolutions,
     axis=0
     )


    damaged_fft = np.fft.fft(damaged_tsa)

    damaged_frequency = np.fft.fftfreq(
     len(damaged_tsa),
     d=sample_time
     )

    positive_frequency_damaged = damaged_frequency >= 0

    current_spectrum_frequency = damaged_frequency[
    positive_frequency_damaged
    ]

    current_spectrum_amplitude = (
    2 * np.abs(damaged_fft[positive_frequency_damaged])
    / len(damaged_tsa)
    )


    filtered_damaged_fft = damaged_fft.copy()

    remove_gmf_damaged = np.isclose(
      np.abs(damaged_frequency),
      GMF
     )

    filtered_damaged_fft[remove_gmf_damaged] = 0

    filtered_spectrum_amplitude = (
    2 * np.abs(
    filtered_damaged_fft[positive_frequency_damaged]
    )
    / len(damaged_tsa)
    )

    current_residual = np.fft.ifft(filtered_damaged_fft)

    current_residual = np.real(current_residual)


    ccr = np.corrcoef(
     healthy_residual,
     current_residual
     )[0, 1]
    ccr_values.append(ccr)


    if damage >= D_THRESHOLD:

     rul_minutes = 0.0

    else:

     N_f = (
        2
        / (
            C
            * (TAU * np.sqrt(np.pi)) ** M
            * (M - 2)
        )
        * (
            damage ** (-(M - 2) / 2)
            - D_THRESHOLD ** (-(M - 2) / 2)
        )
     )

     rul_minutes = N_f / RPM

    rul_values.append(rul_minutes)


    mqtt_data = {
     "time_min": acquisition_time,
     "damage_mm2": damage,
     "ccr": ccr,
     "rul_min": rul_minutes
     }

    mqtt_payload = json.dumps(mqtt_data)

    mqtt_client.publish(MQTT_TOPIC, mqtt_payload)

   


    current_spectrum_payload = json.dumps({
    "time_min": acquisition_time,
    "spectrum": [
        {
            "frequency_hz": float(f),
            "amplitude": float(a)
        }
        for f, a in zip(
            current_spectrum_frequency,
            current_spectrum_amplitude
        )
         ]
        })

    mqtt_client.publish(
    MQTT_CURRENT_SPECTRUM_TOPIC,
    current_spectrum_payload
    )
    

    filtered_spectrum_payload = json.dumps({
    "time_min": acquisition_time,
    "spectrum": [
        {
            "frequency_hz": float(f),
            "amplitude": float(a)
        }
        for f, a in zip(
            current_spectrum_frequency,
            filtered_spectrum_amplitude
        )
        ]
        })

    mqtt_client.publish(
    MQTT_FILTERED_SPECTRUM_TOPIC,
    filtered_spectrum_payload
    )

    print(
    f"Time: {acquisition_time:4d} min | "
    f"Damage: {damage:.3f} mm² | "
    f"CCR: {ccr:.4f} | "
    f"RUL: {rul_minutes:.1f} min"
    )

    real_time.sleep(SIMULATION_DELAY)


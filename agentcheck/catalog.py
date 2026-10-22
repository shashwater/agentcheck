"""Fixture catalog + hardware profiles. Mirrors the shape of a clinician-request -> dataset/model selection task
(the first three entries are real public datasets; 'fixture-*' entries are synthetic distractors)."""
CATALOG = [
    dict(id="uci-har", task="activity recognition", target="activity", needs=["accelerometer", "gyroscope"], keywords=["activity", "walking", "movement", "gait", "mobility", "steps"]),
    dict(id="coswara", task="cough audio screening", target="respiratory", needs=["microphone"], keywords=["cough", "respiratory", "covid", "breathing"]),
    dict(id="m3pd", task="heart rate from fingertip video", target="heart rate", needs=["camera"], keywords=["heart rate", "pulse", "heartbeat"]),
    dict(id="fixture-sleep", task="sleep staging", target="sleep", needs=["accelerometer", "heart_rate_sensor"], keywords=["sleep", "insomnia", "rest"]),
    dict(id="fixture-tremor", task="tremor detection", target="tremor", needs=["accelerometer"], keywords=["tremor", "parkinson", "shaking"]),
]
HARDWARE = {
    "phone": ["accelerometer", "gyroscope", "microphone", "camera"],
    "phone_no_mic": ["accelerometer", "gyroscope", "camera"],
    "watch": ["accelerometer", "gyroscope", "heart_rate_sensor"],
    "accel_only": ["accelerometer"],
    "camera_only": ["camera"],
    "mic_only": ["microphone"],
}

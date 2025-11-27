import time
from data_loader import load_telemetry

def run_sim():
    df = load_telemetry("telemetry_data.xlsx")
    for i, r in df.iterrows():
        print(f"{i}: Roll={r['PlatformRoll']} Pitch={r['PlatformPitch']} Heading={r['PlatformHeading']} Lat={r['SensorLatitude']} Lon={r['SensorLongitude']} Alt={r['SensorTrueAltitude']}")
        time.sleep(0.5)

if __name__ == "__main__":
    run_sim()

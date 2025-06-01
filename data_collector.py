import serial
import time
import csv
import os

# --- Configuration ---
SERIAL_PORT = 'COM3'  # <--- IMPORTANT: CHANGE THIS to your Arduino's serial port
                      #      (e.g., '/dev/ttyUSB0' or '/dev/ttyACM0' on Linux,
                      #       '/dev/cu.usbmodemXXXX' on macOS)
BAUD_RATE = 115200
NUM_SERVOS = 6
CSV_FILENAME = 'robot_arm_training_data.csv'
FIELDNAMES = [f's{i+1}_curr' for i in range(NUM_SERVOS)] + \
             ['distance'] + \
             [f's{i+1}_target' for i in range(NUM_SERVOS)]

def initialize_csv():
    """Creates CSV file with header if it doesn't exist."""
    if not os.path.exists(CSV_FILENAME):
        with open(CSV_FILENAME, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            writer.writeheader()
        print(f"Created '{CSV_FILENAME}' with headers.")
    else:
        print(f"'{CSV_FILENAME}' already exists. Appending data.")

def main():
    initialize_csv()
    ser = None # Initialize ser to None

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to Arduino on {SERIAL_PORT} at {BAUD_RATE} baud.")
        time.sleep(2) # Wait for Arduino to reset and serial connection to establish

        # Clear initial buffer (Arduino might send some startup messages)
        if ser.in_waiting > 0:
            ser.read(ser.in_waiting)
        print("Ready to collect data. Press Ctrl+C to stop.")
        print("-" * 30)

        while True:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if not line:
                        continue

                    parts = line.split(',')
                    if len(parts) == NUM_SERVOS + 1: # 6 current angles + 1 distance
                        current_angles = [int(p) for p in parts[:NUM_SERVOS]]
                        distance = int(parts[NUM_SERVOS])

                        print(f"\nCURRENT STATE:")
                        for i in range(NUM_SERVOS):
                            print(f"  Servo {i+1} Angle: {current_angles[i]}")
                        print(f"  Sensor Distance: {distance} cm")

                        # Get target angles from user
                        print("\nINPUT TARGET ANGLES (comma-separated, 0-180 for each of the 6 servos):")
                        print(f"Example: 90,100,80,95,110,75")
                        target_angles_str = input("Target Angles > ")

                        if target_angles_str.lower() == 's': # 's' for skip
                            print("Skipping this data point.")
                            continue
                        if target_angles_str.lower() == 'q': # 'q' for quit
                            print("Quitting data collection.")
                            break

                        target_angles_parts = target_angles_str.split(',')
                        if len(target_angles_parts) == NUM_SERVOS:
                            try:
                                target_angles = [int(a.strip()) for a in target_angles_parts]
                                # Basic validation
                                if not all(0 <= angle <= 180 for angle in target_angles):
                                    print("Error: All target angles must be between 0 and 180. Try again.")
                                    continue

                                # Prepare data for CSV
                                data_row = {}
                                for i in range(NUM_SERVOS):
                                    data_row[f's{i+1}_curr'] = current_angles[i]
                                data_row['distance'] = distance
                                for i in range(NUM_SERVOS):
                                    data_row[f's{i+1}_target'] = target_angles[i]

                                # Append to CSV
                                with open(CSV_FILENAME, 'a', newline='') as csvfile:
                                    writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
                                    writer.writerow(data_row)
                                print(f"Data point saved: {data_row}")
                                print("-" * 30)

                            except ValueError:
                                print("Invalid input for target angles. Please enter numbers. Try again.")
                        else:
                            print(f"Invalid input. Expected {NUM_SERVOS} target angles. Try again.")
                    else:
                        # print(f"Malformed line from Arduino: '{line}' (Expected {NUM_SERVOS+1} parts)")
                        pass # Silently ignore malformed lines for now

                except UnicodeDecodeError:
                    print("UnicodeDecodeError: Could not decode serial data. Skipping.")
                except ValueError:
                    print(f"ValueError: Could not parse data from Arduino: '{line}'. Skipping.")
                except Exception as e:
                    print(f"An unexpected error occurred while processing Arduino data: {e}")

            time.sleep(0.05) # Small delay to prevent busy-waiting

    except serial.SerialException as e:
        print(f"Serial Error: {e}")
        print(f"Could not open port {SERIAL_PORT}. Check connection and port name.")
    except KeyboardInterrupt:
        print("\nData collection stopped by user.")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("Serial port closed.")

if __name__ == "__main__":
    main()
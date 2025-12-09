"""
Rideau Canal Skateway - IoT Sensor Simulator
Simulates three IoT sensors monitoring ice conditions at different locations
Sends data to Azure IoT Hub every 10 seconds

Architecture:
    Sensor Simulator → Azure IoT Hub → Stream Analytics → Cosmos DB/Blob Storage

Author: [Aryan Rudani]
Course: CST8916
"""

import asyncio
import json
import random
import os
from datetime import datetime
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message
from dotenv import load_dotenv

# Load environment variables from .env file
# This keeps secrets out of code!
load_dotenv()

# Configuration for three sensor locations
# Each sensor has unique device ID and connection string
SENSORS = {
    "dows-lake": {
        "device_id": "dows-lake-sensor",
        "connection_string": os.getenv("DOWS_LAKE_CONNECTION_STRING"),
        "location": "Dow's Lake"
    },
    "fifth-avenue": {
        "device_id": "fifth-avenue-sensor",
        "connection_string": os.getenv("FIFTH_AVENUE_CONNECTION_STRING"),
        "location": "Fifth Avenue"
    },
    "nac": {
        "device_id": "nac-sensor",
        "connection_string": os.getenv("NAC_CONNECTION_STRING"),
        "location": "NAC"
    }
}


class SensorSimulator:
    """
    Simulates a single IoT sensor at a specific location.
    
    Generates realistic sensor readings with gradual changes over time
    using a random walk algorithm.
    
    Attributes:
        location_key (str): Identifier for the location (e.g., 'dows-lake')
        config (dict): Configuration dictionary with device details
        location (str): Human-readable location name
        connection_string (str): Azure IoT Hub connection string
        client (IoTHubDeviceClient): Azure IoT Hub client
        ice_thickness (float): Current ice thickness in cm
        surface_temp (float): Current surface temperature in °C
        snow_accumulation (float): Current snow depth in cm
        external_temp (float): Current external temperature in °C
    """
    
    def __init__(self, location_key, config):
        """
        Initialize sensor simulator with starting values
        
        Args:
            location_key (str): Key identifier (e.g., 'dows-lake')
            config (dict): Configuration with device_id, connection_string, location
        """
        self.location_key = location_key
        self.config = config
        self.location = config["location"]
        self.connection_string = config["connection_string"]
        self.client = None
        
        # Initialize sensor state with realistic baseline values
        # Each location starts with slightly different conditions
        self.ice_thickness = random.uniform(28, 35)       # cm - typically 28-35cm is good
        self.surface_temp = random.uniform(-10, -1)       # °C - below freezing
        self.snow_accumulation = random.uniform(0, 5)     # cm - light to moderate snow
        self.external_temp = random.uniform(-15, -2)      # °C - winter conditions
    
    async def connect(self):
        """
        Connect to Azure IoT Hub using device connection string
        
        Uses MQTT protocol for communication (efficient for IoT)
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Create IoT Hub client from connection string
            self.client = IoTHubDeviceClient.create_from_connection_string(
                self.connection_string
            )
            
            # Establish connection (async operation)
            await self.client.connect()
            
            print(f"✓ Connected: {self.location} ({self.config['device_id']})")
            return True
            
        except Exception as e:
            print(f"✗ Connection failed for {self.location}: {e}")
            return False
    
    def generate_reading(self):
        """
        Generate a realistic sensor reading with gradual changes
        
        Uses random walk algorithm:
        - Each value changes by a small random amount
        - Simulates natural environmental changes
        - Values stay within realistic bounds
        
        Returns:
            dict: Sensor reading with timestamp and measurements
        """
        
        # Simulate gradual changes using random walk
        # Ice thickness: slowly changes (melting or freezing)
        self.ice_thickness += random.uniform(-0.5, 0.3)
        
        # Surface temperature: fluctuates with weather
        self.surface_temp += random.uniform(-0.5, 0.5)
        
        # Snow accumulation: mostly increases, rarely decreases
        self.snow_accumulation += random.uniform(-0.1, 0.3)
        
        # External temperature: changes with time of day
        self.external_temp += random.uniform(-0.3, 0.3)
        
        # Keep values within realistic bounds
        # Ice can't be too thin or too thick
        self.ice_thickness = max(20, min(40, self.ice_thickness))
        
        # Temperature constraints
        self.surface_temp = max(-15, min(2, self.surface_temp))
        self.snow_accumulation = max(0, min(10, self.snow_accumulation))
        self.external_temp = max(-20, min(5, self.external_temp))
        
        # Create sensor reading in JSON format
        # This matches the format Stream Analytics expects
        reading = {
            "deviceId": self.config["device_id"],
            "location": self.location,
            "timestamp": datetime.utcnow().isoformat() + "Z",  # ISO 8601 format with UTC
            "iceThickness": round(self.ice_thickness, 2),
            "surfaceTemp": round(self.surface_temp, 2),
            "snowAccumulation": round(self.snow_accumulation, 2),
            "externalTemp": round(self.external_temp, 2)
        }
        
        return reading
    
    async def send_reading(self):
        """
        Generate and send a sensor reading to Azure IoT Hub
        
        Process:
        1. Generate reading
        2. Convert to JSON
        3. Create IoT Hub message
        4. Send via MQTT
        5. Display status
        
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        try:
            # Generate reading
            reading = self.generate_reading()
            
            # Create IoT Hub message
            # Message wraps the JSON payload with metadata
            message = Message(json.dumps(reading))
            message.content_encoding = "utf-8"
            message.content_type = "application/json"
            
            # Send to IoT Hub (async operation)
            await self.client.send_message(message)
            
            # Determine safety status for display
            # This matches the Stream Analytics logic
            if reading["iceThickness"] >= 30 and reading["surfaceTemp"] <= -2:
                status = "🟢 SAFE"
            elif reading["iceThickness"] >= 25 and reading["surfaceTemp"] <= 0:
                status = "🟡 CAUTION"
            else:
                status = "🔴 UNSAFE"
            
            # Display formatted output for monitoring
            print(f"{status} | {self.location:15} | "
                  f"Ice: {reading['iceThickness']:5.2f}cm | "
                  f"Surf: {reading['surfaceTemp']:5.2f}°C | "
                  f"Snow: {reading['snowAccumulation']:5.2f}cm | "
                  f"Ext: {reading['externalTemp']:5.2f}°C")
            
            return True
            
        except Exception as e:
            print(f"✗ Send failed for {self.location}: {e}")
            return False
    
    async def disconnect(self):
        """
        Gracefully disconnect from Azure IoT Hub
        
        Closes the connection and cleans up resources
        """
        if self.client:
            await self.client.disconnect()
            print(f"✓ Disconnected: {self.location}")


async def run_simulator(duration_minutes=30):
    """
    Run all three sensor simulators concurrently
    
    This is the main orchestration function that:
    1. Creates 3 sensor instances
    2. Connects them to IoT Hub
    3. Sends readings every 10 seconds
    4. Runs for specified duration
    5. Disconnects gracefully
    
    Args:
        duration_minutes (int): How long to run the simulation (default 30 minutes)
    """
    print("=" * 90)
    print("RIDEAU CANAL SKATEWAY - IoT SENSOR SIMULATOR")
    print("=" * 90)
    print(f"Simulating 3 locations for {duration_minutes} minutes")
    print(f"Sending data every 10 seconds ({duration_minutes * 6} readings per sensor)")
    print(f"Total messages: {duration_minutes * 6 * 3}")
    print()
    
    # Create sensor simulators for all three locations
    simulators = [
        SensorSimulator(key, config) 
        for key, config in SENSORS.items()
    ]
    
    # Connect all sensors to IoT Hub concurrently
    # asyncio.gather runs multiple async functions at once
    print("Connecting to Azure IoT Hub...")
    connection_results = await asyncio.gather(
        *[sim.connect() for sim in simulators]
    )
    
    # Check if all sensors connected successfully
    if not all(connection_results):
        print("\n✗ ERROR: Some sensors failed to connect.")
        print("Check your connection strings in the .env file.")
        print("Get connection strings from: Azure Portal > IoT Hub > Devices")
        return
    
    # Display header for real-time monitoring
    print("\n" + "=" * 90)
    print("STATUS | LOCATION        | ICE THICKNESS | SURFACE TEMP | SNOW ACCUM | EXTERNAL TEMP")
    print("=" * 90)
    
    # Calculate number of iterations
    # 6 readings per minute (every 10 seconds)
    iterations = duration_minutes * 6
    
    try:
        # Main simulation loop
        for i in range(iterations):
            # Send readings from all sensors concurrently
            # This means all 3 sensors send at the same time
            await asyncio.gather(
                *[sim.send_reading() for sim in simulators]
            )
            
            # Wait 10 seconds before next reading
            if i < iterations - 1:  # Don't wait after last iteration
                await asyncio.sleep(10)
        
        # Simulation complete
        print("\n" + "=" * 90)
        print(f"✓ SIMULATION COMPLETE!")
        print(f"  Total messages sent: {iterations * 3}")
        print(f"  Duration: {duration_minutes} minutes")
        print(f"  Messages per location: {iterations}")
        print("=" * 90)
        
    except KeyboardInterrupt:
        # User pressed Ctrl+C
        print("\n\n✗ Simulation interrupted by user (Ctrl+C)")
    
    finally:
        # Always disconnect sensors gracefully, even if error occurred
        print("\nDisconnecting sensors...")
        await asyncio.gather(
            *[sim.disconnect() for sim in simulators]
        )


def main():
    """
    Main entry point for the simulator
    
    Checks environment variables and starts the async simulation
    """
    
    print("\nRideau Canal Skateway - Sensor Simulator")
    print("=========================================\n")
    
    # Check if all required connection strings are set
    missing_vars = []
    for sensor_key, config in SENSORS.items():
        if not config["connection_string"]:
            # Convert sensor key to environment variable name
            # Example: 'dows-lake' → 'DOWS_LAKE_CONNECTION_STRING'
            env_var = f"{sensor_key.upper().replace('-', '_')}_CONNECTION_STRING"
            missing_vars.append(env_var)
    
    if missing_vars:
        print("✗ ERROR: Missing environment variables!")
        print("\nThe following connection strings are not set:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease:")
        print("1. Copy .env.example to .env")
        print("2. Add your IoT Hub device connection strings")
        print("3. Get connection strings from Azure Portal > IoT Hub > Devices")
        print("4. Click on each device and copy 'Primary Connection String'")
        return
    
    # Run the simulator
    try:
        print("Starting simulator...\n")
        # asyncio.run() starts the async event loop
        asyncio.run(run_simulator(duration_minutes=30))
        
    except Exception as e:
        print(f"\n✗ Simulator error: {e}")
        print("\nIf you see connection errors, verify:")
        print("- IoT Hub is created and running in Azure Portal")
        print("- Devices are registered in IoT Hub")
        print("- Connection strings are correct in .env file")
        print("- No typos in device IDs or keys")


# Python entry point
# Only runs if this file is executed directly (not imported)
if __name__ == "__main__":
    main()
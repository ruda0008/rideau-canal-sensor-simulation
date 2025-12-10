# Rideau Canal Sensor Simulation

IoT sensor simulator for the Rideau Canal Skateway real-time monitoring system.

## Overview

This Python application simulates three IoT sensors deployed at different locations along the Rideau Canal Skateway in Ottawa, Ontario:

- **Dow's Lake** - Southern section of the canal
- **Fifth Avenue** - Central section  
- **NAC (National Arts Centre)** - Northern section

The simulator generates realistic sensor data and sends it to Azure IoT Hub every 10 seconds, enabling real-time monitoring of skating conditions.

##  Purpose

This simulator is part of a complete IoT monitoring system that:
1. **Simulates sensors** (this repository)
2. **Processes data** in real-time using Azure Stream Analytics
3. **Stores aggregations** in Azure Cosmos DB and Azure Blob Storage
4. **Displays conditions** on a live web dashboard

##  Monitored Parameters

Each sensor continuously monitors four critical parameters:

| Parameter | Unit | Range | Purpose |
|-----------|------|-------|---------|
| **Ice Thickness** | cm | 20-40 | Primary safety indicator - determines if ice is safe for skating |
| **Surface Temperature** | °C | -15 to 2 | Ice quality assessment - warmer temps weaken ice |
| **Snow Accumulation** | cm | 0-10 | Surface condition - affects skating quality |
| **External Temperature** | °C | -20 to 5 | Weather condition tracking - affects ice formation |

## 🔬 How It Works

### Random Walk Algorithm

The simulator uses a **random walk algorithm** to generate realistic data:
```python
ice_thickness += random.uniform(-0.5, 0.3) 
ice_thickness = max(20, min(40, ice_thickness))  # Keep in bounds
```

**Why random walk?**
- Simulates natural environmental changes
- Ice thickness changes slowly over time
- Temperature fluctuates gradually
- More realistic than completely random values

### Data Transmission

- **Frequency:** Every 10 seconds (6 readings per minute)
- **Protocol:** MQTT over TLS (secure, efficient for IoT)
- **Destination:** Azure IoT Hub
- **Format:** JSON with ISO 8601 timestamps

### Safety Status Indicators

The simulator displays real-time safety status based on NCC guidelines:

| Status | Icon | Criteria | Meaning |
|--------|------|----------|---------|
| **Safe** | 🟢 | Ice ≥ 30cm AND Surface Temp ≤ -2°C | Ideal conditions for skating |
| **Caution** | 🟡 | Ice ≥ 25cm AND Surface Temp ≤ 0°C | Skating allowed but conditions deteriorating |
| **Unsafe** | 🔴 | All other conditions | Ice too thin or too warm - unsafe |

##  Prerequisites

### Required Software

- **Python 3.8 or higher**

- **pip** (Python package manager)

- **Git** (optional, for cloning)

### Azure Requirements

- **Azure subscription** (Free tier works!)
- **Azure IoT Hub** with 3 registered devices
- **Device connection strings** (from Azure Portal)

##  Installation

### Step 1: Clone the Repository
```
https://github.com/ruda0008/rideau-canal-sensor-simulation
```

### Step 2: Create Virtual Environment (Recommended)

**What is a virtual environment?**
- Isolated Python environment for this project
- Prevents conflicts with other Python projects
- Best practice for Python development



**You'll see `(venv)` in your terminal when activated.**

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**What this installs:**
- `azure-iot-device` - Microsoft's IoT Hub SDK
- `python-dotenv` - Environment variable loader

### Step 4: Configure Environment Variable


**Edit `.env` with your actual connection strings:**
Use any text editor (Notepad, VS Code, nano, vim)



### .env File Format:
```env
DOWS_LAKE_CONNECTION_STRING=HostName=rideau-iot-john.azure-devices.net;DeviceId=dows-lake-sensor;SharedAccessKey=abc123xyz==

FIFTH_AVENUE_CONNECTION_STRING=HostName=rideau-iot-john.azure-devices.net;DeviceId=fifth-avenue-sensor;SharedAccessKey=def456uvw==

NAC_CONNECTION_STRING=HostName=rideau-iot-john.azure-devices.net;DeviceId=nac-sensor;SharedAccessKey=ghi789rst==
```

 **CRITICAL:** 
- Replace ALL THREE connection strings with your actual values
- Each should be ONE LONG LINE (no line breaks)
- No extra spaces before or after the `=`

##  Usage

### Basic Usage

Run the simulator with default settings (30 minutes):
```bash
python sensor_simulator.py
```



### Modifying Duration

To run for a different duration, edit `sensor_simulator.py`:
```python
# Line at bottom of file:
asyncio.run(run_simulator(duration_minutes=30))

# Change to:
asyncio.run(run_simulator(duration_minutes=60))  # 1 hour
```

### Stopping the Simulator

Press **Ctrl+C** to stop gracefully:


The simulator will properly disconnect all sensors before exiting.

##  Sensor Data Format

### JSON Schema

Each sensor reading is sent as a JSON object:
```json
{
  "deviceId": "dows-lake-sensor",
  "location": "Dow's Lake",
  "timestamp": "2024-12-08T14:30:25.123456Z",
  "iceThickness": 32.45,
  "surfaceTemp": -3.21,
  "snowAccumulation": 2.10,
  "externalTemp": -8.50
}
```

### Field Descriptions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `deviceId` | string | Unique device identifier from IoT Hub | `"dows-lake-sensor"` |
| `location` | string | Human-readable location name | `"Dow's Lake"` |
| `timestamp` | string | UTC timestamp in ISO 8601 format | `"2024-12-08T14:30:25.123456Z"` |
| `iceThickness` | float | Ice thickness in centimeters | `32.45` |
| `surfaceTemp` | float | Surface temperature in Celsius | `-3.21` |
| `snowAccumulation` | float | Snow depth in centimeters | `2.10` |
| `externalTemp` | float | Air temperature in Celsius | `-8.50` |

### Why ISO 8601 Timestamp?
```
2024-12-08T14:30:25.123456Z
│    │  │  │  │  │  │      │
│    │  │  │  │  │  │      └─ UTC timezone (Z = Zulu time)
│    │  │  │  │  │  └─ Microseconds
│    │  │  │  │  └─ Seconds
│    │  │  │  └─ Minutes
│    │  │  └─ Hours (24-hour format)
│    │  └─ Day
│    └─ Month
└─ Year
```

**Benefits:**
- Sortable (alphabetically = chronologically)
- Unambiguous (no confusion about date format)
- Standard format for APIs
- Works with Stream Analytics `TIMESTAMP BY`

##  Code Structure
```
sensor_simulator.py (350+ lines)
│
├── Imports & Configuration
│   ├── asyncio - Async programming
│   ├── azure.iot.device - IoT Hub SDK
│   ├── dotenv - Environment variables
│   └── SENSORS dict - Configuration for 3 locations
│
├── SensorSimulator Class
│   ├── __init__() - Initialize sensor with baseline values
│   ├── connect() - Establish connection to IoT Hub
│   ├── generate_reading() - Create sensor data (random walk)
│   ├── send_reading() - Send JSON to IoT Hub via MQTT
│   └── disconnect() - Clean shutdown
│
├── run_simulator() - Main orchestration
│   ├── Create 3 sensor instances
│   ├── Connect all sensors concurrently
│   ├── Loop: send readings every 10 seconds
│   └── Disconnect gracefully
│
└── main() - Entry point
    ├── Check environment variables
    └── Start async event loop
```

### Key Components Explained

**1. SensorSimulator Class**
- Encapsulates sensor behavior
- Each instance represents one physical sensor
- Maintains state (current ice thickness, temp, etc.)

**2. Async/Await Pattern**
```python
# Runs all 3 sensors simultaneously
await asyncio.gather(
    sensor1.send_reading(),
    sensor2.send_reading(),
    sensor3.send_reading()
)
```

**Benefits:**
- All sensors send data at the same time
- More efficient than sequential
- Simulates real parallel sensors

**3. Random Walk Implementation**
```python
# Current value: 32.0cm
self.ice_thickness += random.uniform(-0.5, 0.3)
# New value: 31.7cm (gradual change)

# Keep in realistic bounds
self.ice_thickness = max(20, min(40, self.ice_thickness))
```

##  Troubleshooting


### Problem 1: "Missing environment variables"

**Symptoms:**
```
✗ ERROR: Missing environment variables!
  - DOWS_LAKE_CONNECTION_STRING
  - FIFTH_AVENUE_CONNECTION_STRING
  - NAC_CONNECTION_STRING
```

**Solutions:**

1. **Check .env file exists**

2. **Verify .env format**
   - Open `.env` in text editor
   - Should have 3 lines with connection strings
   - No quotes around values
   - No spaces around `=`

3. **Check for typos**
   - Variable names must match exactly
   - All uppercase
   - Underscores, not hyphens

**Correct format:**
```env
DOWS_LAKE_CONNECTION_STRING=HostName=...
FIFTH_AVENUE_CONNECTION_STRING=HostName=...
NAC_CONNECTION_STRING=HostName=...
```

### Problem 2: "Module not found"

**Symptoms:**
```
ModuleNotFoundError: No module named 'azure'
```

**Solution:**
```bash
# Make sure virtual environment is activated
# Install dependencies
pip install -r requirements.txt

```


### Message Statistics

**30-minute run:**
- Messages per sensor: 180
- Total messages: 540
- Data points collected: 2,160 (540 × 4 parameters)

**Calculation:**
```
Duration: 30 minutes
Frequency: 10 seconds (6 per minute)
Sensors: 3

Messages per sensor = 30 × 6 = 180
Total messages = 180 × 3 = 540
```





##  Author

**Aryan Rudani**   
Algonquin College  
CST8916 - Fall 2025



##  Support

**Issues with this simulator?**
- Check the Troubleshooting section above
- Review your `.env` file
- Verify Azure IoT Hub is running


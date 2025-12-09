# Rideau Canal Sensor Simulation

IoT sensor simulator for the Rideau Canal Skateway real-time monitoring system.

## 📋 Overview

This Python application simulates three IoT sensors deployed at different locations along the Rideau Canal Skateway in Ottawa, Ontario:

- **Dow's Lake** - Southern section of the canal
- **Fifth Avenue** - Central section  
- **NAC (National Arts Centre)** - Northern section

The simulator generates realistic sensor data and sends it to Azure IoT Hub every 10 seconds, enabling real-time monitoring of skating conditions.

## 🎯 Purpose

This simulator is part of a complete IoT monitoring system that:
1. **Simulates sensors** (this repository)
2. **Processes data** in real-time using Azure Stream Analytics
3. **Stores aggregations** in Azure Cosmos DB and Azure Blob Storage
4. **Displays conditions** on a live web dashboard

## 📊 Monitored Parameters

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
# Instead of random jumps:
ice_thickness = random.uniform(20, 40)  # ❌ Unrealistic

# We use gradual changes:
ice_thickness += random.uniform(-0.5, 0.3)  # ✅ Realistic
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

## 🛠️ Prerequisites

### Required Software

- **Python 3.8 or higher**
  - Check version: `python --version` or `python3 --version`
  - Download: [python.org](https://www.python.org/downloads/)

- **pip** (Python package manager)
  - Usually comes with Python
  - Check: `pip --version`

- **Git** (optional, for cloning)
  - Download: [git-scm.com](https://git-scm.com/)

### Azure Requirements

- **Azure subscription** (Free tier works!)
- **Azure IoT Hub** with 3 registered devices
- **Device connection strings** (from Azure Portal)

## 📥 Installation

### Step 1: Clone the Repository
```bash
# Using Git
git clone https://github.com/yourusername/rideau-canal-sensor-simulation.git
cd rideau-canal-sensor-simulation

# Or download ZIP from GitHub and extract
```

### Step 2: Create Virtual Environment (Recommended)

**What is a virtual environment?**
- Isolated Python environment for this project
- Prevents conflicts with other Python projects
- Best practice for Python development

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**You'll see `(venv)` in your terminal when activated.**

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**What this installs:**
- `azure-iot-device` - Microsoft's IoT Hub SDK
- `python-dotenv` - Environment variable loader

### Step 4: Configure Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Windows (if cp doesn't work):
copy .env.example .env
```

**Edit `.env` with your actual connection strings:**
Use any text editor (Notepad, VS Code, nano, vim)
```bash
# Windows
notepad .env

# macOS
open -e .env

# Linux
nano .env
```

## 🔑 Getting Connection Strings from Azure

### Step-by-Step:

1. **Open Azure Portal** → portal.azure.com
2. **Navigate to your IoT Hub**
3. Go to **"Devices"** (left menu under "Device management")
4. Click on **"dows-lake-sensor"**
5. Find **"Primary Connection String"**
6. Click the **copy icon** 📋
7. Paste into your `.env` file
8. **Repeat for other two devices**

### .env File Format:
```env
DOWS_LAKE_CONNECTION_STRING=HostName=rideau-iot-john.azure-devices.net;DeviceId=dows-lake-sensor;SharedAccessKey=abc123xyz==

FIFTH_AVENUE_CONNECTION_STRING=HostName=rideau-iot-john.azure-devices.net;DeviceId=fifth-avenue-sensor;SharedAccessKey=def456uvw==

NAC_CONNECTION_STRING=HostName=rideau-iot-john.azure-devices.net;DeviceId=nac-sensor;SharedAccessKey=ghi789rst==
```

⚠️ **CRITICAL:** 
- Replace ALL THREE connection strings with your actual values
- Each should be ONE LONG LINE (no line breaks)
- No extra spaces before or after the `=`

## 🚀 Usage

### Basic Usage

Run the simulator with default settings (30 minutes):
```bash
python sensor_simulator.py
```

### Expected Output
```
Rideau Canal Skateway - Sensor Simulator
=========================================

Starting simulator...

==================================================================================
RIDEAU CANAL SKATEWAY - IoT SENSOR SIMULATOR
==================================================================================
Simulating 3 locations for 30 minutes
Sending data every 10 seconds (180 readings per sensor)
Total messages: 540

Connecting to Azure IoT Hub...
✓ Connected: Dow's Lake (dows-lake-sensor)
✓ Connected: Fifth Avenue (fifth-avenue-sensor)
✓ Connected: NAC (nac-sensor)

==================================================================================
STATUS | LOCATION        | ICE THICKNESS | SURFACE TEMP | SNOW ACCUM | EXTERNAL TEMP
==================================================================================
🟢 SAFE      | Dow's Lake      | Ice: 32.45cm | Surf: -3.21°C | Snow:  2.10cm | Ext: -8.50°C
🟡 CAUTION   | Fifth Avenue    | Ice: 27.80cm | Surf: -0.50°C | Snow:  1.80cm | Ext: -6.20°C
🔴 UNSAFE    | NAC             | Ice: 24.10cm | Surf:  0.80°C | Snow:  0.50cm | Ext: -4.10°C
🟢 SAFE      | Dow's Lake      | Ice: 32.51cm | Surf: -3.18°C | Snow:  2.15cm | Ext: -8.47°C
🟡 CAUTION   | Fifth Avenue    | Ice: 27.75cm | Surf: -0.55°C | Snow:  1.82cm | Ext: -6.18°C
🔴 UNSAFE    | NAC             | Ice: 24.15cm | Surf:  0.75°C | Snow:  0.52cm | Ext: -4.12°C
...
```

### Modifying Duration

To run for a different duration, edit `sensor_simulator.py`:
```python
# Line at bottom of file:
asyncio.run(run_simulator(duration_minutes=30))

# Change to:
asyncio.run(run_simulator(duration_minutes=60))  # 1 hour
```

Or create a custom script:
```python
# quick_test.py
from sensor_simulator import run_simulator
import asyncio

asyncio.run(run_simulator(duration_minutes=5))  # 5-minute test
```

### Stopping the Simulator

Press **Ctrl+C** to stop gracefully:
```
^C
✗ Simulation interrupted by user (Ctrl+C)

Disconnecting sensors...
✓ Disconnected: Dow's Lake
✓ Disconnected: Fifth Avenue
✓ Disconnected: NAC
```

The simulator will properly disconnect all sensors before exiting.

## 📦 Sensor Data Format

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

## 🏗️ Code Structure
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

## 🐛 Troubleshooting

### Problem 1: "Connection failed"

**Symptoms:**
```
✗ Connection failed for Dow's Lake: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Possible Causes & Solutions:**

1. **Internet connection issue**
   - Check your internet connection
   - Try: `ping google.com`

2. **Wrong connection string**
   - Verify you copied the ENTIRE string (they're long!)
   - Check for extra spaces or line breaks
   - Make sure you copied from "Primary Connection String" not "Secondary"

3. **IoT Hub not running**
   - Check Azure Portal → IoT Hub → Overview
   - Status should be "Active"

4. **Device not enabled**
   - Azure Portal → IoT Hub → Devices
   - Check "Status" column shows "Enabled"

5. **Firewall blocking**
   - IoT Hub uses port 8883 (MQTT) or 443 (HTTPS)
   - Check corporate/school firewall settings

### Problem 2: "Missing environment variables"

**Symptoms:**
```
✗ ERROR: Missing environment variables!
  - DOWS_LAKE_CONNECTION_STRING
  - FIFTH_AVENUE_CONNECTION_STRING
  - NAC_CONNECTION_STRING
```

**Solutions:**

1. **Check .env file exists**
```bash
   # List files (Windows)
   dir
   
   # List files (Mac/Linux)
   ls -la
   
   # Should see .env file
```

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

### Problem 3: "Module not found"

**Symptoms:**
```
ModuleNotFoundError: No module named 'azure'
```

**Solution:**
```bash
# Make sure virtual environment is activated
# You should see (venv) in terminal

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep azure
```

### Problem 4: Python command not found

**Symptoms:**
```bash
python: command not found
```

**Solutions:**

**Try python3:**
```bash
python3 sensor_simulator.py
python3 --version
```

**Windows - Add to PATH:**
1. Search "Environment Variables" in Start Menu
2. Edit PATH variable
3. Add Python installation directory

**Mac - Install via Homebrew:**
```bash
brew install python3
```

### Problem 5: Permission denied (Mac/Linux)

**Symptoms:**
```bash
./sensor_simulator.py: Permission denied
```

**Solutions:**

**Option 1: Use python command**
```bash
python3 sensor_simulator.py
```

**Option 2: Make executable**
```bash
chmod +x sensor_simulator.py
./sensor_simulator.py
```

### Problem 6: No data appearing in Azure

**Check this flow:**

1. **Simulator sending?**
   - See messages in terminal? ✓
   - No error messages? ✓

2. **IoT Hub receiving?**
   - Azure Portal → IoT Hub → Overview
   - Check "Device to cloud messages" chart
   - Should see activity

3. **Stream Analytics running?**
   - Azure Portal → Stream Analytics Job
   - Status should be "Running"
   - Check "Monitoring" for errors

4. **Cosmos DB receiving?**
   - Takes 5 minutes for first aggregation
   - Check Data Explorer → Items
   - Refresh every minute

## 📈 Performance Metrics

### Resource Usage

Running on typical laptop:
- **CPU:** 2-5% (very light)
- **Memory:** ~50MB
- **Network:** ~1KB per message
- **Total data (30 min):** ~180MB

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

## 🧪 Testing Checklist

Before running for your project, verify:

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Azure IoT Hub created
- [ ] 3 devices registered in IoT Hub
- [ ] Connection strings copied to `.env`
- [ ] `.env` file not committed to Git (check with `git status`)
- [ ] Test run successful (5 minutes)
- [ ] Azure Portal shows messages being received
- [ ] No errors in terminal output

## 🔧 Development

### Running in Development Mode

For quick testing (5-minute run):
```python
# Edit sensor_simulator.py
asyncio.run(run_simulator(duration_minutes=5))
```

### Adding New Locations

To add a fourth location:

1. **Register device in Azure IoT Hub**
   - Device ID: `bronson-bridge-sensor`

2. **Add to SENSORS dict**
```python
SENSORS = {
    # ... existing sensors ...
    "bronson-bridge": {
        "device_id": "bronson-bridge-sensor",
        "connection_string": os.getenv("BRONSON_BRIDGE_CONNECTION_STRING"),
        "location": "Bronson Bridge"
    }
}
```

3. **Add to .env**
```env
BRONSON_BRIDGE_CONNECTION_STRING=HostName=...
```

### Customizing Sensor Parameters

Adjust baseline values in `SensorSimulator.__init__()`:
```python
# Make ice thicker on average
self.ice_thickness = random.uniform(35, 40)  # Instead of 28-35

# Make it colder
self.surface_temp = random.uniform(-15, -5)  # Instead of -10 to -1
```

## 📚 Architecture Context

This simulator is **Component 1** of a 4-part system:
```
┌─────────────────────┐
│ 1. Sensor Simulator │ ← You are here
│    (This Repo)      │
└──────────┬──────────┘
           │ MQTT/HTTPS
           ↓
┌─────────────────────┐
│ 2. Azure IoT Hub    │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ 3. Stream Analytics │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     ↓           ↓
┌─────────┐ ┌─────────┐
│ Cosmos  │ │  Blob   │
│   DB    │ │ Storage │
└────┬────┘ └─────────┘
     │
     ↓
┌─────────────────────┐
│ 4. Web Dashboard    │
└─────────────────────┘
```

## 📝 License

This project is for educational purposes as part of CST8916 - Remote Data and Real-time Applications.

## 👤 Author

**Aryan Rudani**   
Algonquin College  
CST8916 - Fall 2025



##  Support

**Issues with this simulator?**
- Check the Troubleshooting section above
- Review your `.env` file
- Verify Azure IoT Hub is running
- Contact course instructor

**Azure Portal issues?**
- Check Azure service health
- Verify subscription is active
- Check billing (free tier limits)

## 🔗 Related Repositories

- **Dashboard:** [rideau-canal-dashboard](https://github.com/yourusername/rideau-canal-dashboard)
- **Documentation:** [rideau-canal-monitoring](https://github.com/yourusername/rideau-canal-monitoring)
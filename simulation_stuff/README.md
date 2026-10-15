# Simulation: waypoint missions in ArduPilot SITL

Fly a simulated quadcopter through a waypoint mission using Mission Planner and a text mission file. The example mission takes off to 15 m, flies a 50 m square, and returns to launch. Allow about 10 minutes. No hardware needed.

## What's in this folder

```
simulation_stuff/
  make_mission.py          generates a mission file from meter offsets
  missions/
    square.waypoints       example mission: 50 m square at 15 m, then return to launch
    mission.waypoints      output of make_mission.py (overwritten on every run)
  README.md
```

## Requirements

- Mission Planner (tested with version 1.3.83 and ArduCopter V4.8.0-dev)
- Python 3 for `make_mission.py` (standard library only, nothing to install)

## Quick start

### 1. Start the simulator and connect

1. Open Mission Planner and click the **SIMULATION** tab.
2. Choose the **Multirotor** (quadcopter) option. Mission Planner starts the simulated ArduCopter and connects to it.
3. Check the connection: the top-right dropdown shows TCP, the button says DISCONNECT, and the map shows a quad icon.
4. Wait for the HUD to say **Ready to Arm** and for a GPS fix in the bottom bar. This takes about a minute.

The quad starts at SITL's default home near Canberra, Australia (-35.3633, 149.1652). `square.waypoints` is built around that point.

Starting the simulator with `sim_vehicle.py` from a terminal also works. Connect Mission Planner to it over UDP, port 14550.

### 2. Let AUTO take off without a throttle stick

By default, an AUTO mission waits for the pilot to raise the throttle stick before taking off. The simulator has no stick, so the quad arms, sits on the ground, and disarms itself after 10 seconds. Set one parameter to fix it:

1. Go to **CONFIG**, then **Full Parameter List**.
2. Search for `AUTO_OPTIONS`.
3. Set it to `3` (bit 0 allows arming in AUTO, bit 1 allows takeoff without raising throttle).
4. Click **Write Params**.

On a real aircraft, decide on this setting deliberately before flying. It changes how AUTO behaves at takeoff.

### 3. Load the mission and write it to the vehicle

1. Go to the **PLAN** tab.
2. Click **Load WP File** and choose `missions/square.waypoints`. A square appears on the map. If you can't see it, zoom in: it is only 50 m across.
3. Click **Write WP**. The Messages tab should show `Flight plan received`.

### 4. Arm in GUIDED, then switch to AUTO

1. Go to the **DATA** tab, then the **Actions** tab under the HUD.
2. Choose **GUIDED** in the mode dropdown and click **Set Mode**.
3. Click **Arm/Disarm** and confirm. The HUD changes from DISARMED to ARMED.
4. Choose **AUTO** in the mode dropdown and click **Set Mode**.
5. Watch the quad climb to 15 m, fly the square, and return to launch. The Messages tab logs each step.

Arm first, then switch to AUTO. Arming while already in AUTO is refused by default.

## Troubleshooting

Read the Messages tab (DATA, then Messages) first. It usually names the problem.

| Symptom | Cause | Fix |
| --- | --- | --- |
| `Arm: Auto mode not armable` | You tried to arm while in AUTO | Switch to GUIDED, arm, then switch to AUTO |
| `Arming motors`, then `Disarming motors` about 10 s later, no takeoff | Quad is waiting for a throttle stick the sim doesn't have, then auto-disarms | Set `AUTO_OPTIONS` to 3 (step 2) |
| Arming refused with a pre-arm message | GPS or EKF not ready yet | Wait for `EKF3 IMU0 is using GPS` and the Ready to Arm status |
| Square isn't on the map after loading | Map is zoomed out | Zoom in on the quad icon |
| Write WP fails | Connection dropped, or another program is using the link | Check the connection indicator and reconnect |
| Mission flies somewhere unexpected | Sim home isn't the Canberra default | Regenerate the file with your actual home (see below) |
| Mission Planner rejects the file | Columns separated by spaces instead of tabs | Use real tabs, or regenerate the file with `make_mission.py` |

## Make your own mission

`make_mission.py` writes a `.waypoints` file from a short list of meter offsets, so you can change where the quad flies without working in latitude and longitude.

1. Open `make_mission.py` and edit the `WAYPOINTS` list. Each entry is `(north_m, east_m, altitude_m)` relative to home. Negative north is south, negative east is west.
2. Change `TAKEOFF_ALT` (m) and `SPEED` (m/s) near the top if needed.
3. Run it from anywhere:

   ```
   python3 make_mission.py
   ```

   It writes `missions/mission.waypoints` and prints the path.
4. Load that file on the PLAN tab and write it to the vehicle, as in step 3 above.

If your sim's home is not the Canberra default, set `HOME_LAT` and `HOME_LON` in the script to the quad's actual position first.

## How the mission file works

A `.waypoints` file is a header line, `QGC WPL 110`, then one tab-separated line per mission item:

```
index  current  frame  command  p1  p2  p3  p4  lat  lon  alt  autocontinue
```

`make_mission.py` uses four commands:

| Command | Number | Used for |
| --- | --- | --- |
| Takeoff | 22 | Climb to `TAKEOFF_ALT` above home |
| Change speed | 178 | Set ground speed (m/s) |
| Waypoint | 16 | Fly to a point |
| Return to launch | 20 | Fly back to home and land |

Frame 3 means altitude is measured above home. Item 0 is always the home position.

The script converts meter offsets to degrees with:

```
delta_lat = north / 111320
delta_lon = east / (111320 * cos(lat))
```

One degree of latitude is about 111,320 m everywhere. A degree of longitude gets shorter away from the equator, so it is scaled by the cosine of the latitude.

## Next steps

- **Scripted upload.** Use pymavlink to upload the mission, switch to AUTO, and report progress from Python, so no one clicks through Mission Planner.
- **Live control.** A script that stays running in GUIDED mode and sends position targets, for behavior that reacts to what the camera sees.
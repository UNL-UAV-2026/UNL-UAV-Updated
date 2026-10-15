"""
make_mission.py - build an ArduPilot .waypoints file from simple meter offsets.

Edit the CONFIG section, run `python3 make_mission.py`, then in Mission Planner:
PLAN tab -> Load WP File -> mission.waypoints -> Write WP.
"""
import math

# ---------------- CONFIG: edit these ----------------
HOME_LAT = -35.363262      # SITL default home (CMAC, Canberra)
HOME_LON = 149.165237
HOME_ALT = 584.0           # meters MSL; ignored for relative-altitude waypoints

TAKEOFF_ALT = 15           # meters above home
SPEED = 5                  # ground speed in m/s

# Each waypoint is (north_m, east_m, altitude_m) relative to home.
# Negative north = south, negative east = west.
WAYPOINTS = [
    (50,  0, 15),   # 50 m north
    (50, 50, 15),   # then 50 m east
    ( 0, 50, 15),   # then back south
    ( 0,  0, 15),   # then back west, over home
]

OUTPUT = "mission.waypoints"
# ----------------------------------------------------

M_PER_DEG_LAT = 111_320.0   # roughly constant everywhere


def offset_to_latlon(north_m, east_m):
    """Convert a north/east offset in meters from home into lat/lon."""
    dlat = north_m / M_PER_DEG_LAT
    # a degree of longitude gets shorter as you move away from the equator
    dlon = east_m / (M_PER_DEG_LAT * math.cos(math.radians(HOME_LAT)))
    return HOME_LAT + dlat, HOME_LON + dlon


# MAVLink command numbers and frames used below
CMD_WAYPOINT = 16
CMD_RTL = 20
CMD_TAKEOFF = 22
CMD_CHANGE_SPEED = 178
FRAME_ABS = 0              # altitude above sea level (used for the home line)
FRAME_REL = 3              # altitude relative to home


def item(seq, frame, cmd, p1=0, p2=0, p3=0, p4=0, lat=0.0, lon=0.0, alt=0.0, current=0):
    """One tab-separated mission line in QGC WPL 110 format."""
    fields = [seq, current, frame, cmd, p1, p2, p3, p4,
              f"{lat:.6f}", f"{lon:.6f}", f"{alt:.6f}", 1]
    return "\t".join(str(f) for f in fields)


def build():
    lines = ["QGC WPL 110"]
    # item 0 is always the home position
    lines.append(item(0, FRAME_ABS, CMD_WAYPOINT, lat=HOME_LAT, lon=HOME_LON,
                      alt=HOME_ALT, current=1))
    lines.append(item(1, FRAME_REL, CMD_TAKEOFF, lat=HOME_LAT, lon=HOME_LON,
                      alt=TAKEOFF_ALT))
    # p1=1 means ground speed, p2 is the speed in m/s, p3=-1 leaves throttle alone
    lines.append(item(2, FRAME_REL, CMD_CHANGE_SPEED, p1=1, p2=SPEED, p3=-1))
    seq = 3
    for north, east, alt in WAYPOINTS:
        lat, lon = offset_to_latlon(north, east)
        lines.append(item(seq, FRAME_REL, CMD_WAYPOINT, lat=lat, lon=lon, alt=alt))
        seq += 1
    lines.append(item(seq, FRAME_REL, CMD_RTL))
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    with open(OUTPUT, "w") as f:
        f.write(build())
    print(f"Wrote {OUTPUT} with {len(WAYPOINTS)} waypoints")
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

# Your Facebook iCal feed URL
FB_ICAL_URL = 'https://www.facebook.com/events/ical/upcoming/?uid=100086359507945&key=iQWqIRkPxwwkAWBt'
INPUT_URL = FB_ICAL_URL
OUTPUT_FILE = 'fixed_calendar.ics'
LOCAL_TZ = 'America/Chicago'

# VTIMEZONE block for America/Chicago
VTIMEZONE_BLOCK = """BEGIN:VTIMEZONE
TZID:America/Chicago
X-LIC-LOCATION:America/Chicago
BEGIN:DAYLIGHT
TZOFFSETFROM:-0600
TZOFFSETTO:-0500
TZNAME:CDT
DTSTART:19700308T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:-0500
TZOFFSETTO:-0600
TZNAME:CST
DTSTART:19701101T020000
RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU
END:STANDARD
END:VTIMEZONE
"""

def convert_datetime(line, prop):
    if line.startswith(f"{prop}:") and line.endswith("Z"):
        utc_time = datetime.strptime(line.split(":")[1].strip(), "%Y%m%dT%H%M%SZ").replace(tzinfo=ZoneInfo("UTC"))
        local_time = utc_time.astimezone(ZoneInfo(LOCAL_TZ))
        formatted = local_time.strftime("%Y%m%dT%H%M%S")
        return f"{prop};TZID={LOCAL_TZ}:{formatted}"
    return line

def fix_ical(content):
    lines = content.splitlines()
    new_lines = []
    added_tz = False
    for i, line in enumerate(lines):
        if line.startswith("VERSION:2.0"):
            new_lines.append(line)
            new_lines.append(f"X-WR-TIMEZONE:{LOCAL_TZ}")
            continue
        if line.startswith("BEGIN:VEVENT"):
            new_lines.append(line)
            continue
        if line.startswith("DTSTART:") or line.startswith("DTEND:"):
            line = convert_datetime(line, "DTSTART") if line.startswith("DTSTART:") else convert_datetime(line, "DTEND")
        if line.startswith("X-ORIGINAL-URL:"):
            continue  # Remove Facebook's internal path
        new_lines.append(line)
        if line == "CALSCALE:GREGORIAN" and not added_tz:
            new_lines.append(VTIMEZONE_BLOCK.strip())
            added_tz = True
    return "\n".join(new_lines) + "\n"

def main():
    print("Fetching Facebook iCal...")
    response = requests.get(INPUT_URL)
    if response.status_code != 200:
        print("Failed to fetch the calendar.")
        return
    fixed_ical = fix_ical(response.text)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(fixed_ical)
    print(f"Saved fixed calendar to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

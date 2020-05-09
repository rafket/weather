This is a script to get the current and short-term forecast weather at the
current location. Its primary use-case is as an i3status/i3blocks script.

It uses GeoClue2 for location, and the US National Weather Service API for
getting the weather. If the API is unavailable (usually if the location is
outside the US), the script uses weather information transmitted on APRS,
accessed through findU.com. If findU is accessed, pandas must be installed.

As the US National Weather Service API requires a User Agent, username@hostname
is used by default.

Since these APIs are free to access, and, at least in the case of findU, may
not be happy with increased load, it is recommended to use a minimum of 5
minutes between script runs (such as in the case of using it as an i3blocks
script)

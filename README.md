# OutOfOre-AutoLeveler
External GPS Autopilot and Blade Stabilization tool for Out of Ore. Featuring precise depth control and roll/pitch automation.

Out of Ore(0.34) - External Blade & Depth Autopilot
This is an external automation tool for Out of Ore that provides advanced blade stabilization and GPS-based depth management for heavy machinery. It uses memory reading to fetch telemetry and simulates key presses (macros) to maintain your target position.

⚠️ Critical Requirements & Warnings
GPS Receiver Module: Your vehicle MUST have a GPS Receiver installed. Without it, the script cannot read depth data.
Single Player Only: This tool is designed strictly for Single Player sessions.
Session Bug: If you have joined a Multiplayer server during your current game session, memory addresses will likely conflict. You must restart the game and enter Single Player directly for the autopilot to work.
Tested Vehicles: Chariton DX11000 (Dozer) and Chariton g200E (Grader).

🚀 Key Features
GPS Level Mode: Maintains a consistent centimeter-perfect depth 
Full Auto Mode: Automatically stabilizes both Blade Roll and Blade Pitch.
Semi-Auto Mode: Only stabilizes Blade Roll (keeps the blade level with the horizon) while leaving pitch/depth to the player. (recommended for Graders)


⌨️ Controls & Keybindings
F9	Switch Mode (OFF -> GPS -> FULL -> SEMI)
F4	Emergency Autopilot OFF
F5	GPS_LEVEL	Decrease Target Depth	-5.0 cm
F6	GPS_LEVEL	Increase Target Depth	+5.0 cm
F5	FULL_AUTO	Lower Blade Pitch (Vertical Angle)	-0.05°
F6	FULL_AUTO	Lift Blade Pitch (Vertical Angle)	+0.05°
F7	Auto Modes	Tilt Left (Roll Angle)	-0.05°
F8	Auto Modes	Tilt Right (Roll Angle)	+0.05°
Num 5	Reset/Sync: Resets angles to 0.0 or syncs GPS to current depth
ESC	Close Script

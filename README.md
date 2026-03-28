# UNO Q RGB LED Control (MPU + MCU)

This project demonstrates a clean architecture for controlling RGB LEDs on an Arduino UNO Q using both:

- the Linux side (MPU) via `/sys/class/leds`
- the microcontroller side (MCU) via Bridge RPC

A Web UI provides real-time control of all LEDs.

---

## Architecture


```
Web UI (HTML/JS)
        ↓
Python backend (App Lab)
        ↓
Bridge RPC
        ↓
MCU (Arduino C++)
```

---

## LED State Model

Each LED is defined by two independent components:

- `on`: global enable/disable
- `RGB`: color channels

Final output logic:


color_output = on AND channel

---

## Features

- Control MPU LEDs via sysfs
- Control MCU LEDs via Bridge RPC
- Unified state model across both layers
- Web UI with real-time updates
- Clear visual state (ON / OFF / NO COLOR)

---

## How to Run

1. Upload the MCU code
2. Start the Python app in App Lab
3. Open the Web UI

---

## Why this project matters

This project focuses on architecture rather than hardware.

It demonstrates how to:

- design a clean and consistent state model
- synchronize control between Linux and MCU layers
- eliminate ambiguity between logical and visual states

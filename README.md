# UNO Q RGB LED Control (MPU + MCU)

![Leds](/doc//scrennshot.png)

The two MPU LEDs are exposed through Linux (`/sys/class/leds`), while the two MCU LEDs are directly connected to STM32 GPIO pins.

This project demonstrates a clean architecture for controlling the four RGB LEDs on an Arduino UNO Q using both:

- the Linux side (MPU) via `/sys/class/leds`
- the microcontroller side (MCU) via Bridge RPC and direct GPIO control (digitalWrite)

The board includes:
- 2 RGB LEDs connected to the MPU (Linux side)
- 2 RGB LEDs connected to the MCU (GPIO side)

These RGB LEDs are driven as binary channels (ON/OFF only), where colors are created by combining the R, G, and B components.

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

## MPU LED Control - Manual control from the App Lab terminal

Before using the Python application, it is useful to understand how the MPU LEDs can be controlled manually from the App Lab terminal.

### 1. Disable the default triggers

Some MPU LEDs are associated with system triggers by default.  
To take manual control, the trigger must first be set to `none`.

For LED 2:

```
echo none > /sys/class/leds/red:panic/trigger
echo none > /sys/class/leds/green:wlan/trigger
echo none > /sys/class/leds/blue:bt/trigger
```
Once this is done, the brightness of each RGB channel can be controlled directly.  

### 2. Control LED colors manually
Each RGB LED is composed of three independent channels:  
- red
- green
- blue
 
For example, LED 1 can be controlled with:

``` 
echo 1 > /sys/class/leds/red:user/brightness
echo 0 > /sys/class/leds/red:user/brightness

echo 1 > /sys/class/leds/green:user/brightness
echo 0 > /sys/class/leds/green:user/brightness

echo 1 > /sys/class/leds/blue:user/brightness
echo 0 > /sys/class/leds/blue:user/brightness
```
Setting a channel to `1` turns it on.  
Setting it to `0` turns it off.

### 3. Create color combinations

Because the LED is RGB, colors can be mixed by enabling multiple channels at the same time.  

Examples:  

- red only: red = 1, green = 0, blue = 0
- green only: red = 0, green = 1, blue = 0
- blue only: red = 0, green = 0, blue = 1
- yellow: red = 1, green = 1, blue = 0
- magenta: red = 1, green = 0, blue = 1
- cyan: red = 0, green = 1, blue = 1
- white: red = 1, green = 1, blue = 1
- off: red = 0, green = 0, blue = 0

---

### 4. Relation with the Python program

This is exactly the same principle used by the Python application.  
The Python backend does not use a different mechanism for MPU LEDs.  
It simply automates this manual sysfs control by writing to the same `brightness` files after disabling  
the default triggers.  

In other words:  

- manual terminal commands prove how the MPU LEDs work
- the Python program applies the same logic in a cleaner and synchronized way
- the Web UI is a higher-level interface built on top of this low-level control

---

## MCU LED Control (basic principle)

The MCU controls RGB LEDs using standard GPIO pins.

Each color channel (R, G, B) is controlled independently using `digitalWrite`.

Important detail: the LEDs are **active-low**.

- `LOW` → channel ON
- `HIGH` → channel OFF

Example:

```cpp
digitalWrite(LED3_R, LOW);   // red ON
digitalWrite(LED3_G, LOW);   // green ON
digitalWrite(LED3_B, LOW);   // blue ON
```

Colors are created by combining channels:
- red = R
- green = G
- blue = B
- yellow = R + G
- magenta = R + B
- cyan = G + B
- white = R + G + B
- off = all HIGH

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

## Data flow

## Data flow

`return {"ok": True, "leds": STATE["leds"]}  # Data returned to the browser`

The system does not work as a simple one-way command path.

A user action in the WebUI sends a request to the Python API.  
Python then updates the internal state (`STATE`).

This state is applied:

- directly to the MPU LEDs through `/sys/class/leds`
- and sent to the MCU for the LEDs controlled by the microcontroller

The MCU does not send the state back.  
It simply applies the received command.

The WebUI is updated using the API response, which returns the current logical state (`STATE`) after each action.

👉 This return is essential because the browser does not know what actually happened.  
It only sends a request and must receive the updated state to stay synchronized.

So the flow is:

```
WebUI -> Python API -> STATE update -> MPU / MCU LED control
                           |
                           -> return STATE to WebUI
```

The browser display is always based on `STATE`, not on direct hardware feedback.

---

## Why the API returns STATE

When a user clicks a button in the WebUI, the visual state does not change immediately by itself.  

The browser sends a request to Python, which:  

- updates the internal `STATE`
- applies the change to the LEDs (MPU / MCU)
- returns the updated `STATE`
  
The WebUI is then updated using this returned state :  

- The visual LEDs in the browser are updated only because the API returns the new state  
- The browser does not update itself automatically  
- It needs the server to send back the new state after each action 

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

  ---

## Acknowledgments

This project was developed with the help of ChatGPT for design discussions, debugging, and documentation improvements.

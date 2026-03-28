import time
import threading
from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI

ui = WebUI()
bridge = Bridge()

LOCK = threading.Lock()

# -------------------------------------------------------------------
# LED MPU
# -------------------------------------------------------------------

MPU_LED_PATHS = {
    "led1": {
        "r": "/sys/class/leds/red:user/brightness",
        "g": "/sys/class/leds/green:user/brightness",
        "b": "/sys/class/leds/blue:user/brightness",
    },
    "led2": {
        "r": "/sys/class/leds/red:panic/brightness",
        "g": "/sys/class/leds/green:wlan/brightness",
        "b": "/sys/class/leds/blue:bt/brightness",
    },
}

MPU_LED_TRIGGERS = {
    "led1": {
        "r": "/sys/class/leds/red:user/trigger",
        "g": "/sys/class/leds/green:user/trigger",
        "b": "/sys/class/leds/blue:user/trigger",
    },
    "led2": {
        "r": "/sys/class/leds/red:panic/trigger",
        "g": "/sys/class/leds/green:wlan/trigger",
        "b": "/sys/class/leds/blue:bt/trigger",
    },
}

# -------------------------------------------------------------------
# Etat global
# -------------------------------------------------------------------

STATE = {
    "leds": {
        "led1": {
            "label": "LED 1",
            "side": "MPU",
            "on": True,
            "channels": {"r": False, "g": True, "b": False},
        },
        "led2": {
            "label": "LED 2",
            "side": "MPU",
            "on": True,
            "channels": {"r": False, "g": True, "b": False},
        },
        "led3": {
            "label": "LED 3",
            "side": "MCU",
            "on": True,
            "channels": {"r": False, "g": True, "b": False},
        },
        "led4": {
            "label": "LED 4",
            "side": "MCU",
            "on": True,
            "channels": {"r": False, "g": True, "b": False},
        },
    }
}


# -------------------------------------------------------------------
# Utilitaires
# -------------------------------------------------------------------

def clone_state():
    result = {"ok": True, "leds": {}}
    for led_name, led_data in STATE["leds"].items():
        result["leds"][led_name] = {
            "label": led_data["label"],
            "side": led_data["side"],
            "on": led_data["on"],
            "channels": {
                "r": led_data["channels"]["r"],
                "g": led_data["channels"]["g"],
                "b": led_data["channels"]["b"],
            },
        }
    return result


def read_max_brightness(path):
    try:
        base = path.rsplit("/", 1)[0]
        with open(base + "/max_brightness", "r") as f:
            return int(f.read().strip())
    except Exception as e:
        print(f"Read max_brightness failed for {path}: {e!r}", flush=True)
        return 1

def write_led_sysfs(path, logical_on):
    max_brightness = read_max_brightness(path)
    value = f"{max_brightness}\n" if logical_on else "0\n"
    try:
        print(f"WRITE {path} <- {value.strip()}", flush=True)
        with open(path, "w") as f:
            f.write(value)
    except Exception as e:
        print(f"Brightness write failed for {path}: {e!r}", flush=True)


def set_trigger_none(path):
    try:
        print(f"TRIGGER {path} <- none", flush=True)
        with open(path, "w") as f:
            f.write("none\n")
    except Exception as e:
        print(f"Trigger none failed for {path}: {e!r}", flush=True)


#def ensure_at_least_one_channel(led_name):
    #channels = STATE["leds"][led_name]["channels"]
    #if not (channels["r"] or channels["g"] or channels["b"]):
        #channels["r"] = True


# -------------------------------------------------------------------
# Pilotage MPU
# -------------------------------------------------------------------

def init_mpu_leds():
    print("Init MPU LED triggers...", flush=True)
    for led_name, channels in MPU_LED_TRIGGERS.items():
        for ch, trigger_path in channels.items():
            set_trigger_none(trigger_path)

    print("Force MPU LEDs OFF...", flush=True)
    for led_name, channels in MPU_LED_PATHS.items():
        for ch, bright_path in channels.items():
            write_led_sysfs(bright_path, False)


def apply_mpu_led(led_name):
    led_data = STATE["leds"][led_name]
    is_on = led_data["on"]
    channels = led_data["channels"]

    for ch in ("r", "g", "b"):
        path = MPU_LED_PATHS[led_name][ch]
        logical_on = is_on and channels[ch]
        write_led_sysfs(path, logical_on)
        



# -------------------------------------------------------------------
# Pilotage MCU
# -------------------------------------------------------------------

def apply_mcu_led(led_name):
    led_data = STATE["leds"][led_name]

    print(
        f"Bridge.notify set_mcu_led {led_name} "
        f"on={int(led_data['on'])} "
        f"r={int(led_data['channels']['r'])} "
        f"g={int(led_data['channels']['g'])} "
        f"b={int(led_data['channels']['b'])}",
        flush=True
    )

    bridge.notify(
        "set_mcu_led",
        led_name,
        1 if led_data["on"] else 0,
        1 if led_data["channels"]["r"] else 0,
        1 if led_data["channels"]["g"] else 0,
        1 if led_data["channels"]["b"] else 0,
    )


# -------------------------------------------------------------------
# Application globale de l'etat
# -------------------------------------------------------------------

def apply_one_led(led_name):
    side = STATE["leds"][led_name]["side"]

    if side == "MPU":
        apply_mpu_led(led_name)
    else:
        apply_mcu_led(led_name)


def apply_all_leds():
    for led_name in STATE["leds"]:
        apply_one_led(led_name)


def init_outputs():
    print("Initialisation des sorties...", flush=True)

    with LOCK:
        for led_name in STATE["leds"]:
            STATE["leds"][led_name]["on"] = True

        init_mpu_leds()
        apply_all_leds()

    print("Initialisation terminee.", flush=True)


# -------------------------------------------------------------------
# API WebUI
# -------------------------------------------------------------------

def state():
    with LOCK:
        return clone_state()


def toggle_led(led=None):
    if led not in STATE["leds"]:
        return {"ok": False, "error": "unknown_led"}

    with LOCK:
        STATE["leds"][led]["on"] = not STATE["leds"][led]["on"]
        apply_one_led(led)
        return clone_state()


def toggle_channel(led=None, channel=None):
    if led not in STATE["leds"]:
        return {"ok": False, "error": "unknown_led"}

    if channel not in ("r", "g", "b"):
        return {"ok": False, "error": "unknown_channel"}

    with LOCK:
        channels = STATE["leds"][led]["channels"]
        channels[channel] = not channels[channel]
        #ensure_at_least_one_channel(led)

        if STATE["leds"][led]["on"]:
            apply_one_led(led)

        return clone_state()


def all_on():
    with LOCK:
        for led_name in STATE["leds"]:
            STATE["leds"][led_name]["on"] = True
        apply_all_leds()
        return clone_state()


def all_off():
    with LOCK:
        for led_name in STATE["leds"]:
            STATE["leds"][led_name]["on"] = False
        apply_all_leds()
        return clone_state()


ui.expose_api("GET", "/state", state)
ui.expose_api("GET", "/toggle_led", toggle_led)
ui.expose_api("GET", "/toggle_channel", toggle_channel)
ui.expose_api("GET", "/all_on", all_on)
ui.expose_api("GET", "/all_off", all_off)


# -------------------------------------------------------------------
# Boucle utilisateur
# -------------------------------------------------------------------

def loop():
    time.sleep(0.05)


print("UNO Q RGB WebUI demo ready", flush=True)
print("APIs: /state /toggle_led?led=led1 /toggle_channel?led=led1&channel=r /all_on /all_off", flush=True)


init_outputs()
App.run(user_loop=loop)

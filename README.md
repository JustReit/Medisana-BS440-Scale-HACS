# BS440 BLE Smart Scale for Home Assistant

A custom Home Assistant integration for the **Medisana BS440 / BS444** Bluetooth Smart Scale. This integration allows Home Assistant to connect to your scale via local Bluetooth or **ESPHome Bluetooth Proxies**, decode body metrics, and attribute them to specific users.
Its strongly inspirted by: https://github.com/keptenkurk/BS440/
## ✨ Features
* **Multi-User Support**: Automatically detects the User ID (Person 1-8) and creates a separate Home Assistant Device for each person.
* **Guest Mode**: Handles "Person 255" (Guest) by recording weight only and ignoring body metrics.
* **Full Body Metrics**: Decodes Weight, BMI, Body Fat, Muscle Mass, Bone Mass, Water Percentage, and Daily Calorie requirements.
* **Bluetooth Proxy Compatible**: Works seamlessly with ESP32-based Bluetooth proxies for extended range and stability.
* **Device-Per-Person**: Each user appears as a distinct device in the Home Assistant UI for better organization.

---

## 📂 Installation

### Option 1: [HACS](https://hacs.xyz/) Link

1. Click [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=JustReit&category=integration&repository=Medisana-BS440-Scale-HACS)
2. Restart Home Assistant

### Option 2: [HACS](https://hacs.xyz/)

1. Or `HACS` > `Integrations` > `⋮` > `Custom Repositories`
2. `Repository`: paste the url of this repo
3. `Category`: Integration
4. Click `Add`
5. Close `Custom Repositories` modal
6. Click `+ EXPLORE & DOWNLOAD REPOSITORIES`
7. Search for `Medisana-BS440-Scale-HACS`
8. Click `Download`
9. Restart _Home Assistant_

### Option 2: Manual copy

1. Copy the `Medisana-BS440-Scale-HACS` folder inside `custom_components` of this repo to `/config/custom_components` in your Home Assistant instance
2. Restart _Home Assistant_

### Configuration
1. Go to **Settings** > **Devices & Services**.
2. Click **Add Integration** and search for **BS440 Bluetooth Scale**.
3. Enter the **MAC Address** of your scale (e.g., `08:B8:D0:B5:58:D2`).
   * *Tip: You can find this in your router's BLE logs, ESPHome logs, or using a BLE scanner app on your phone.*
  
<img width="916" height="522" alt="grafik" src="https://github.com/user-attachments/assets/c1172095-8fbb-4e08-9bb4-0a43656b5930" />


## 🛠 How it Works

The scale remains in a deep sleep mode to save battery. The integration polls the scale every 30 seconds (or manually via a service call).

1. **Trigger**: You step on the scale. The scale wakes up and begins advertising.
2. **Connection**: Home Assistant (or a Bluetooth Proxy) establishes an active connection.
3. **Data Exchange**: Home Assistant sends a time-sync command. The scale responds by broadcasting notifications for the weight and body data.
4. **Attribution**: Based on the internal "Person ID", the data is pushed to the corresponding **User Device** in Home Assistant.

---

## 📊 Sensors Provided

Each detected user will have their own device with the following entities:

| Sensor | Unit | Description |
| :--- | :--- | :--- |
| **Weight** | kg | Total body weight |
| **BMI** | | Body Mass Index (based on height in scale profile) |
| **Body Fat** | % | Percentage of body fat |
| **Body Water** | % | Percentage of total body water |
| **Muscle Mass** | % | Percentage of muscle mass |
| **Bone Mass** | % | Percentage of bone mass |
| **Calories** | kcal | Daily calorie requirements |

<img width="1021" height="356" alt="Device_Overview" src="https://github.com/user-attachments/assets/f0f6b450-eb0e-40f7-a5f8-73d12a4539a8" />
<img width="531" height="366" alt="Entity_Overview" src="https://github.com/user-attachments/assets/f4c60a4c-af6b-4828-bfd2-dced72dcc625" />

---

## 🔍 Troubleshooting

### "Timed out waiting for data notification"
* Ensure you are standing on the scale until the Bluetooth icon on the scale's display stops blinking.
* If using an **ESPHome Proxy**, ensure `active: true` is set in your ESP32's `bluetooth_proxy` configuration.
* Ensure the scale is not currently connected to the Medisana mobile app.

### Debugging
To see the raw communication in your logs, add this to `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.bs440_ble: debug

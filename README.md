<a id="readme-top"></a>

<div align="center">

  <img src="https://img.icons8.com/fluency/96/leaf.png" alt="AgriSpec Pro Logo" width="90" height="90" />

  <h1>🌿 AgriSpec Pro</h1>
  <h3>Leafy Powder Quality Checker</h3>

  <p>
    A modern, client-side hyperspectral analysis tool that instantly estimates the <strong>freshness and chlorophyll quality</strong> of leafy green powder — right in your browser, no backend required.
  </p>

  <p>
    <a href="https://github.com/ss-sevesh/leafy-powder-quality-checker" target="_blank"><strong>🔗 View Repository »</strong></a>
    &nbsp;·&nbsp;
    <a href="https://github.com/ss-sevesh/leafy-powder-quality-checker/issues/new?labels=bug&template=bug-report---.md">🐛 Report Bug</a>
    &nbsp;·&nbsp;
    <a href="https://github.com/ss-sevesh/leafy-powder-quality-checker/issues/new?labels=enhancement&template=feature-request---.md">✨ Request Feature</a>
  </p>

</div>

<div align="center">

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stars][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Glossary/HTML5)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![No Build Step](https://img.shields.io/badge/No_Build_Step-%E2%9C%93-brightgreen?style=flat-square)](#getting-started)

</div>

---

## 📋 Table of Contents

<details open>
  <summary>Expand / Collapse</summary>
  <ol>
    <li>
      <a href="#-about-the-project">About The Project</a>
      <ul>
        <li><a href="#-key-features">Key Features</a></li>
        <li><a href="#-scientific-basis">Scientific Basis</a></li>
        <li><a href="#️-built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#-getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#-usage">Usage</a></li>
    <li><a href="#️-roadmap">Roadmap</a></li>
    <li><a href="#-contributing">Contributing</a></li>
    <li><a href="#-license">License</a></li>
    <li><a href="#-contact">Contact</a></li>
    <li><a href="#-acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

---

## 🌱 About The Project

**AgriSpec Pro** is a live sensor application for agricultural researchers and laboratory technicians. A Python gateway requests six spectral bands from an ESP8266, validates the payload, calculates the **Leafy Powder Quality Index (LPQI)**, saves the complete result to Excel, and returns that same persisted record to the browser dashboard.

The system evaluates the contrast between the red edge and near-infrared (NIR) bands. The 610 nm measurement is retained for diagnostics and future calibration. The service can collect a single reading on demand or collect continuously every five seconds.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

### ✨ Key Features

| Feature | Description |
|---|---|
| 🔒 **Secure Auth Portal** | Glassmorphism login/signup UI with animated particle background |
| 📡 **Live 6-Band Sensor Input** | Collects R/S/T/U/V/W readings at 610, 680, 730, 760, 810, and 860 nm from the ESP endpoint |
| ⚡ **Server-side LPQI Analysis** | Uses one deterministic calculation for the dashboard and persisted record |
| 🔁 **Automatic Collection** | Optional five-second scan interval with overlap protection |
| 📈 **Persistent Excel History** | Loads previous readings and downloads the current `.xlsx` workbook |
| 🧪 **Calculation Trace** | Shows red-edge average, NIR average, LPQI, and thresholds without simulated confidence |
| 📱 **Fully Responsive** | Works seamlessly on desktop, tablet, and mobile |
| 🧰 **Lightweight Setup** | No Node.js build step; Python uses only `openpyxl` beyond the standard library |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

### 🔬 Scientific Basis

The **Leafy Powder Quality Index (LPQI)** uses a normalized difference approach contrasting the average red-edge response against the average near-infrared response.

```
RedEdge = (R_680 + R_730) / 2
NIR     = (R_760 + R_810 + R_860) / 3
LPQI    = (NIR - RedEdge) / (NIR + RedEdge)
```

The current prototype classifies LPQI values of `0.45` or above as **Good**, values from `0.25` to below `0.45` as **Moderate**, and lower values as **Poor**. These thresholds require calibration against laboratory reference samples before production use.

The gateway analyzes the values exactly as the sensor supplies them. For scientifically comparable results, perform dark/white reference correction and account for per-band gain differences in the firmware or calibration pipeline before relying on the classification.

| Quality Level | Spectral Signature | Interpretation |
|---|---|---|
| 🟢 **High (Fresh)** | Strong absorption at 680 nm, high NIR reflectance | Intact cellular structure, high chlorophyll concentration |
| 🟡 **Moderate** | Partially flattened spectral curve | Early-stage degradation, borderline freshness |
| 🔴 **Poor (Degraded)** | Flat spectral curve across all bands | Loss of Mg²⁺ from chlorophyll (phaeophytinization) — thermal stress or aging |

> **⚠️ Note:** Thresholds used are literature-derived. Validation with locally calibrated, real-world samples is strongly recommended for production use.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

### 🛠️ Built With

This project uses a deliberately lightweight stack with no frontend build step.

| Technology | Role |
|---|---|
| [![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Glossary/HTML5) | Page structure and semantics |
| [![Tailwind CSS CDN](https://img.shields.io/badge/Tailwind_CSS_(CDN)-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/) | Utility-first styling via CDN |
| [![JavaScript](https://img.shields.io/badge/Vanilla_JS-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript) | Dashboard interactivity and API rendering |
| Python 3.9+ | Sensor gateway, LPQI calculation, static server, and persistence |
| openpyxl | Excel workbook append/read support |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or later
- A modern browser
- The computer running the service and the ESP8266 on the same network
- An ESP endpoint returning all six bands as JSON or text, for example `R,95.67 S,68.50 T,9.27 U,115.13 V,122.46 W,116.36`

---

### Installation

**Step 1 — Clone the repository**

```sh
git clone https://github.com/ss-sevesh/leafy-powder-quality-checker.git
```

**Step 2 — Navigate into the project folder**

```sh
cd leafy-powder-quality-checker
```

**Step 3 — Install the Excel dependency**

```sh
python3 -m pip install -r requirements.txt
```

**Step 4 — Start the live service**

```sh
python3 data_logger.py --sensor-url http://10.149.144.149/scan
```

You can also set `MORINGA_SENSOR_URL`, `MORINGA_EXCEL_FILE`, `MORINGA_HOST`, `MORINGA_PORT`, and `MORINGA_SENSOR_TIMEOUT` as environment variables. Command-line flags take precedence.

**Step 5 — Open the served dashboard**

Open [http://localhost:5050/dashboard.html](http://localhost:5050/dashboard.html). Serving the page from `data_logger.py` keeps the dashboard and API on the same origin.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 💻 Usage

```
index.html      →  Authentication Portal
dashboard.html  →  Spectral Analysis Dashboard
```

1. Verify that **Sensor service online** appears on the dashboard.
2. Click **Scan Sensor & Analyze** for one persisted reading, or enable automatic collection every five seconds.
3. Review the raw six-band readings, red-edge average, NIR average, LPQI, and quality classification.
4. Use **Technical detail** to show the calculation trace for the selected sample.
5. Select **View** on a history row to reload a saved Excel record.
6. Select **Download Excel** to download the live workbook.

Each successful scan follows one transaction path:

```text
Dashboard → Python service → ESP /scan → validate 6 bands → calculate LPQI
          ← same saved record ← append Excel workbook ←──────────────┘
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 🗺️ Roadmap

- [x] Glassmorphism authentication portal
- [x] 6-band hyperspectral input dashboard
- [x] Real-time LPQI calculation engine
- [x] ESP8266 sensor gateway with payload validation
- [x] Persistent Excel history and workbook download
- [x] Automatic five-second acquisition
- [x] Calculation, parser, service, and persistence tests
- [ ] Interactive spectral curve chart (Chart.js)
- [ ] Dark mode toggle across all components
- [ ] Calibrate thresholds using laboratory reference samples
- [ ] User accounts and saved profiles
- [ ] Calibration mode with custom threshold settings

See [open issues](https://github.com/ss-sevesh/leafy-powder-quality-checker/issues) for a full list of proposed features and known bugs.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**!

**Don't forget to ⭐ star the project if you found it useful — it helps a lot!**

### How to Contribute

1. **Fork** the Project
   ```sh
   # Click the "Fork" button at the top right of this page
   ```

2. **Create** your Feature Branch
   ```sh
   git checkout -b feature/your-amazing-feature
   ```

3. **Commit** your Changes
   ```sh
   git commit -m "feat: add some amazing feature"
   ```

4. **Push** to the Branch
   ```sh
   git push origin feature/your-amazing-feature
   ```

5. **Open** a Pull Request on GitHub

> Follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages where possible (`feat:`, `fix:`, `docs:`, `chore:`).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](./LICENSE) for more information.

You are free to use, modify, and distribute this project for personal or commercial purposes.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 📬 Contact

**ss-sevesh** — [@ss-sevesh](https://github.com/ss-sevesh)

Project Repository: [https://github.com/ss-sevesh/leafy-powder-quality-checker](https://github.com/ss-sevesh/leafy-powder-quality-checker)

Found a bug? → [Open an Issue](https://github.com/ss-sevesh/leafy-powder-quality-checker/issues/new?labels=bug&template=bug-report---.md)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 🙌 Acknowledgments

- [Best-README-Template](https://github.com/othneildrew/Best-README-Template) — README structure inspiration
- [Tailwind CSS](https://tailwindcss.com) — Utility-first CSS framework
- [Google Material Symbols](https://fonts.google.com/icons) — Icon library
- [Shields.io](https://shields.io) — Beautiful badge generation
- [Icons8](https://icons8.com) — Project logo assets
- Literature on chlorophyll spectral reflectance properties for the LPQI algorithm

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/ss-sevesh/leafy-powder-quality-checker.svg?style=for-the-badge
[contributors-url]: https://github.com/ss-sevesh/leafy-powder-quality-checker/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/ss-sevesh/leafy-powder-quality-checker.svg?style=for-the-badge
[forks-url]: https://github.com/ss-sevesh/leafy-powder-quality-checker/network/members
[stars-shield]: https://img.shields.io/github/stars/ss-sevesh/leafy-powder-quality-checker.svg?style=for-the-badge
[stars-url]: https://github.com/ss-sevesh/leafy-powder-quality-checker/stargazers
[issues-shield]: https://img.shields.io/github/issues/ss-sevesh/leafy-powder-quality-checker.svg?style=for-the-badge
[issues-url]: https://github.com/ss-sevesh/leafy-powder-quality-checker/issues
[license-shield]: https://img.shields.io/github/license/ss-sevesh/leafy-powder-quality-checker.svg?style=for-the-badge
[license-url]: https://github.com/ss-sevesh/leafy-powder-quality-checker/blob/master/LICENSE

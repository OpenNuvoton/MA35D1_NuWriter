# NuWriter Tool Release Notes

NuWriter is a specialized burning and deployment tool designed for the Nuvoton **MA35 Series** hardware platforms. This document tracks major updates, hardware support expansions, and deep-dive technical adjustments regarding DDR initialization and system stability.

**Repository:** [https://github.com/OpenNuvoton/MA35D1_NuWriter](https://github.com/OpenNuvoton/MA35D1_NuWriter)

---

## 🔍 Technical Deep Dive: DDR Tuning & System Optimization

### 1. Signal Integrity & Stability Enhancements (2024.12 - 2026.03)
* **Disable Write Leveling Strategy**: 
    - **Impacted Files**: All major MCP package DDR2/DDR3 variants
    - **Change**: Explicitly disabled the **Write Leveling** feature within the DDR controller.
    - **Purpose**: Resolved training synchronization issues encountered with specific Winbond industrial DDR3L batches (e.g., W632GU6NG/W971G16NG) on high-density PCB layouts, ensuring reliable 1066Mbps operation.
* **Clock Source Management**: 
    - **Change**: During DDR initialization, the system now forcefully switches the clock source for **DCUltra** (Display) and **GFX** (Graphics) from `EPLL` to `SYSPLL`.
    - **Purpose**: Prevented critical system reset failures during cold boot by eliminating clock interference during the sensitive DRAM calibration phase.

### 2. Intelligent Device Validation
* **PDID-to-Image Mapping (v1.08)**: 
    - NuWriter now includes a `mapping.txt` database to link the hardware **PDID (Product ID)** to specific binary images.
    - **Safety Logic**: The tool performs a pre-burn check to ensure the selected DDR image is compatible with the connected silicon. 
    - **Exceptions**: The check excludes cases where PDID is reported as `0` to allow for engineering sample testing and manual override in development environments.

---

## 🕒 Release History

### [1.08] - 2026-03
- **Added**: DDR support for **MA35D05KI67C**.
- **Added**: Support for **MX35LF4GE4AD** SPI NAND Flash.
- **Fixed**: UI component adjustments and PDID validation logic refinements.

### [1.07] - 2025-11
- **Feature**: Integrated DDR configuration file checking function.
- **Support**: Added GigaDevice (GD5F2GM7UExxG) and Winbond (W25N02LV) SPI NAND support.
- **Environment**: Upgraded `libusb` to **v1.0.29** for improved Windows 11 connection stability.

### [1.06] - 2024.12
- **DDR**: Major update to disable Write Leveling across all MCP images.
- **MacOS**: Added official support for MacOS 15 (Apple Silicon/M3).
- **Security**: Added OTP content encryption and Read-only lock features.

### [1.00] - 2021 ~ 2023
- Initial release of the core NuWriter architecture.
- Support for eMMC, SPI NAND, and Key Store (KS) programming.

---

### 👥 Contributors
- **HPChen0**: Lead Developer (DDR Tuning, PDID Logic, and UI Maintenance).
- **Jacky Huang**: Hardware Integration and Chip Variant Management.
- **CWWeng**: Storage Driver Development (SPI NAND/eMMC).

> **Note**: These DDR binaries are optimized based on Nuvoton's standard evaluation boards. For custom PCB designs with significantly different trace lengths, please contact Nuvoton for custom DDR tuning parameters.

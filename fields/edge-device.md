# Field Extension: Edge, Embedded & IoT Devices

> **Objective**: Manage hardware compatibility, offline resilience, resource ceilings, thermal throttling constraints, and fail-safe over-the-air (OTA) updates for software running on physical edge devices (NVIDIA Jetson, Raspberry Pi, industrial IPCs, robotics, IoT micro-computers).

---

## 1. Action Items

### A. Hardware & Architectural Compatibility
- [ ] **Multi-Architecture Cross-Compilation**: Build and validate binaries and container images for target processor architectures (`linux/arm64`, `linux/arm/v7`, `linux/amd64`).
- [ ] **Hardware Acceleration & Driver Compatibility**: Validate correct runtime driver versions and permissions for hardware accelerators, GPUs (CUDA, TensorRT), NPUs (Hailo, Rockchip NPU, Coral TPU), and camera/sensor serial buses (V4L2, CAN, I2C).

### B. Offline-First Resilience & Persistence
- [ ] **Uninterrupted Offline Mode**: Ensure the core operational loop continues functioning locally via embedded storage (SQLite, RocksDB, DuckDB) when internet or local network connectivity is severed.
- [ ] **Store-and-Forward Queuing**: When network connectivity is restored, transmit buffered telemetry and state events using exponential backoff without saturating bandwidth.

### C. A/B Dual-Partition OTA & Anti-Brick Protection
- [ ] **Dual-Partition Fail-Safe OTA**: Apply software and OS updates to an inactive partition (Slot B). Upon reboot, bootloader logic must verify software health and automatically fall back to the functional partition (Slot A) if health checks fail (e.g., via RAUC, Mender, or SWUpdate).
- [ ] **Hardware & Software Watchdog Timers**: Enable hardware or kernel-level watchdog timers to trigger automatic hardware resets if the primary application process hangs.

### D. Resource Constraints & Thermal Management
- [ ] **Memory & Flash Endurance**:
  - Enforce strict RAM caps (e.g., maximum 60% of total memory) to prevent kernel OOM killer panics.
  - Mitigate flash memory wear-out by redirecting frequent operational logs to a RAM disk (`tmpfs`) or throttling disk writes.
- [ ] **Thermal Throttling Resilience**: Stress-test the device at elevated ambient temperatures; ensure mission-critical control loops maintain timing deadlines even when CPU frequencies are throttled.
- [ ] **Power-Loss Recovery**: Test unexpected power-cut scenarios; verify that file systems (overlayfs, journaling) and databases recover cleanly without data corruption.

---

## 2. Exit Gate (Field Gate: Edge/Device)

An edge software release cannot be deployed to field devices until **all** of the following criteria are satisfied:
1. All Edge/Device checklist items are completed in `GOLIVE.md`.
2. A continuous 24-hour stress test on target hardware completes with zero application crashes, kernel panics, or memory leaks.
3. A simulated corrupted OTA update demonstrates automatic fallback to the previous operational partition without bricking the device.
4. Simulating five sudden power interruptions during active disk writes produces zero file system or database corruption upon reboot.

---

## 3. Rationale

| Action Item | Why It Is Mandatory |
|:---|:---|
| Dual-Partition A/B OTA | Physical access to deployed edge devices in the field is often impossible. A single bricked update can incur immense maintenance and truck-roll costs. |
| Store-and-Forward Buffering | Network drops can persist for days in industrial or agricultural settings. Without local persistence, critical sensor telemetry is permanently lost. |
| Flash Wear-out Mitigation | Writing continuous debug logs to onboard eMMC or SD cards degrades storage cells within months, causing irreversible hardware failure. |
| Power-Cut Resilience | Power cuts and generator fluctuations are frequent in industrial edge environments. Corrupted filesystems prevent devices from completing reboot sequences. |

---

## 4. Common Pitfalls

- ❌ **Compiling on x86 for ARM**: Compiling binaries on developer workstations and deploying directly to an ARM target, producing `Exec format error`.
- ❌ **Unbuffered Logging to SD Cards**: Allowing high-frequency debug logging directly to flash storage, burning out hardware endurance limits.
- ❌ **Unbounded Network Calls in Control Loops**: Blocking execution loops on remote HTTP requests without timeouts, causing local hardware control to freeze when connectivity drops.
- ❌ **Single-Partition Updates**: Overwriting the active partition in place; a network interruption mid-update leaves the device permanently unbootable.

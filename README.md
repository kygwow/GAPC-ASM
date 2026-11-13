# Geometry-Aware Phase Compensation for Sampling-Efficient Angular Spectrum Method

Official demo for **Geometry-Aware Phase Compensation (GPC)** and **Local Phase Correction (LPC)** techniques designed for sampling-efficient Angular Spectrum Method (ASM) propagation in thick optical systems.
https://doi.org/10.1364/OE.586512
##  Overview

This repository demonstrates a computationally efficient methodology for simulating light propagation through thick refractive elements (e.g., lenslets, micro-optics) at high incident angles. 

Traditional single-step ASM often suffers from numerical instability and phase errors when dealing with geometric thickness. Our approach introduces:
- **Global Phase Correction (GPC)**: Accounting for the bulk phase evolution through the material.
- **Local Phase Correction (LPC)**: An advanced coordinate-skewing technique that preserves the optical path accuracy by accounting for local ray-slanting within the material.

![Integrated Geometry](optical_demo_geometry.png)
![2x5 PSF Matrix Results](optical_demo_results.png)

##  Features

- **Multi-Slice ASM (MS-AS)**: A high-fidelity benchmark that slices the optical element into thin layers to minimize propagation error.
- **Single-Slice ASM (SS-AS)**: An ultra-efficient model utilizing GPC and LPC to achieve benchmark-level fidelity in a single axial step.
- **2x5 PSF Matrix**: Automated visualization comparing 5 simulation variants across both **Front** (curved first) and **Back** (flat first) lens orientations.
- **Quantitative Metrics**: Integrated MS-SSIM and Centroid (µm) calculation for quantitative fidelity verification.


##  Lens Orientation Convention

The heightmap is the material thickness measured from the flat base of the lens.

- `heightmapDirection='front'`: the curved surface faces the incident light (curved first). Multi-slice propagation starts at the apex slice.
- `heightmapDirection='back'`: the flat base faces the incident light (flat first). Multi-slice propagation starts at the base slice.

**Convention change (2026-11-13).** Earlier versions of this code assigned the labels the other way round: `'front'` sliced from the base (flat first) and `'back'` from the apex (curved first), although this README already described `'front'` as curved first. The engines now follow the README. To reproduce results produced with the earlier code, swap `'front'` and `'back'`. The results figure was regenerated with the corrected labels; its rows therefore swap places compared with the earlier figure.

##  Validated Regime and Known Limitations

- **Single-slice accuracy depends on surface curvature.** On the demo lens (ROC 2 mm, thickness 100 µm), SS-AS+LPC tracks the multi-slice reference closely (20° centroid within about 0.4 µm, focus within the depth of focus). On a strongly curved microlens (ROC about 305 µm, sag 22.5 µm), the curved-first single slice differs from multi-slice by 13–32% in near-focus intensity on a small detector. Use the multi-slice engine for strongly curved surfaces.
- `get_grids` builds the spatial grid with `linspace(-L/2, L/2, N)`, a spacing of L/(N-1), while the frequency grid assumes a spacing of `PxSize`.
- The ASM kernel has no band limit.
- GPC uses a single global plane-wave angle for the whole aperture.

##  Testing

```bash
python -m pytest tests/
```

The test checks that the orientation fix is a pure relabel of the earlier code (read from git history) and that `'front'` starts at the apex slice.

##  Requirements

The simulation is built using **PyTorch** for GPU acceleration and automatic differentiation compatibility.


- **Python**: 3.8+
- **CUDA**: Recommended for larger grid sizes (e.g., 1500x1500px).

##  Usage

To run the full PSF fidelity study and generate the result visualizations:

```bash
python optical_demo_main.py
```

### Simulation Parameters
You can adjust the following parameters in `optical_demo_main.py`:
- `PxSize`: Spatial sampling resolution (default: 1.0µm).
- `Grid_Window`: Spatial domain size (default: 1.5mm).
- `WD`: Distance from the lens to the sensor (Working Distance).
- `Lens_Dia`: Lens Diameter (default: 1.0  * mm)
- `ROC`: Radius of curvature of the lens (default: 2.0mm).
- `lens_thick`: Thickness of the lens (default: 100µm).
- `n_mat`: Refractive index of the lens (default: 1.54).
- `n_bkgd`: Refractive index of the background (default: 1.0).
- `Illum_Dia`: Diameter of the illumination aperture (default: 0.7mm).
- `wavelength`: Wavelength of the light (default: 550nm).
- `angle_deg_x`: Incident wave angle in degrees (default: 20).
- `angle_deg_y`: Incident wave angle in degrees (default: 0).
- `dz_gt`: Ground truth propagation distance (default: 1.0µm).
- `dz_coarse`: Coarse propagation distance (default: 50.0µm).
- `Crop_window`: Region of interest for analysis.

##  Project Structure

- `optical_demo_main.py`: Main orchestration script for simulation, metric calculation, and visualization.
- `optical_demo_utils.py`: Core physics engine containing MS-AS, SS-AS, and GPC/LPC implementations.

---
**Imaging Intelligence Lab, SNU** | 2026. 02. 24

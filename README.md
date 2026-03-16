# Football Sniper V20.3.1

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Accuracy](https://img.shields.io/badge/Accuracy-81.4%25-green)
![Yield](https://img.shields.io/badge/Yield-+1.6%25_vs_B365-green)
![CI](https://img.shields.io/badge/95%25_CI-75.3--86.1%25-blue)
![Status](https://img.shields.io/badge/Status-Live-brightgreen)

Football match prediction system menggunakan Dixon-Coles + Elo Walk-Forward.

## Statistik Tervalidasi

| Metrik | Nilai |
|---|---|
| Walk-Forward Accuracy | **81.4%** (194 SNIPER picks) |
| 95% CI Bootstrap | [75.3%, 86.1%] (10,000 iter) |
| p-value vs coin flip | 4.27e-19 |
| Chi-Squared lintas liga | p=0.267 (konsisten) |
| Brier Score | 0.2032 |
| Yield vs B365 | +1.6% |
| Real-world | 88.9% (9 picks, akumulasi) |

## Engine

- **Dixon-Coles V3** (55%) — MLE + tau correction + time-weighted
- **Elo Walk-Forward** (45%) — K=32, HFA +50 points
- **Draw Boost** — per-liga multiplier
- **6-layer Sniper Filter** — threshold, draw warning, giant killer, lambda, Elo gap, EV

## Liga Aktif (V20.3.1)

| Liga | Threshold | Status |
|---|---|---|
| Eredivisie | 0.59 | Active (updated) |
| La Liga | 0.58 | Active |
| Liga Portugal | 0.59 | Active |
| Super Lig | 0.65 | Active |
| Bundesliga | 0.66 | Active |
| Serie A | 0.68 | Active (updated) |
| EPL | 0.68 | Active + EV filter |

## Quick Start
```python
import importlib.util, sys

def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

BASE    = '/content/drive/MyDrive/Football_Project'
src     = BASE + '/github_ready/src'
pred    = load_mod('predictor',     src + '/predictor.py')
sniper  = load_mod('sniper_filter', src + '/sniper_filter.py')
tracker = load_mod('log_tracker',   src + '/log_tracker.py')

pred.load_model(BASE)
tracker.init_tracker(BASE)

pred.predict_v20('PSV Eindhoven', 'Almere City', 'Eredivisie')
```

## Metodologi

Lihat [docs/methodology.md](docs/methodology.md) untuk detail lengkap.

## Integritas Metodologi

V20 awal mencapai 87.5% namun **dicabut sendiri** setelah time leakage
terdeteksi. Angka resmi deployment adalah V20.3 = 81.4% (warm walk-forward,
burn-in 8 pekan, no data leakage).

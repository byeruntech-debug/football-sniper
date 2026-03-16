# Football Sniper V20.3.2

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Accuracy](https://img.shields.io/badge/Accuracy-81.4%25-green)
![Yield](https://img.shields.io/badge/Yield-+1.6%25_vs_B365-green)
![Leagues](https://img.shields.io/badge/Leagues-8_Active-brightgreen)

Football match prediction system using Dixon-Coles V3 + Elo Walk-Forward.

## Statistik Tervalidasi

| Metrik | Nilai |
|---|---|
| Walk-Forward Accuracy | 81.4% (194 picks) |
| 95% CI Bootstrap | [75.3%, 86.1%] |
| p-value vs coin flip | 4.27e-19 |
| Brier Score | 0.2032 |
| Yield vs B365 | +1.6% |

## Liga Aktif (V20.3.2) — 8 Liga

| Liga | Threshold | WF Accuracy |
|---|---|---|
| Eredivisie | 0.59 | 82.1% |
| La Liga | 0.58 | 80.0% |
| Liga Portugal | 0.59 | aktif |
| Super Lig | 0.65 | aktif |
| Bundesliga | 0.66 | 82.9% |
| Serie A | 0.68 | 80.6% |
| EPL | 0.68 | 80.0% |
| Ligue 1 | 0.63 | 82.9% (new) |

## Changelog V20.3.2
- Ligue 1 ditambahkan sebagai liga ke-8
- DC fitting 1,372 laga (4 musim 2021-2025)
- Elo diupdate dari data historis
- WF accuracy Ligue 1: 82.9% (35 picks)
- Draw warning Ligue 1: 0.270

## Quick Start
```python
BASE    = '/content/drive/MyDrive/Football_Project'
pred    = load_mod('predictor',     BASE + '/github_ready/src/predictor.py')
sniper  = load_mod('sniper_filter', BASE + '/github_ready/src/sniper_filter.py')
tracker = load_mod('log_tracker',   BASE + '/github_ready/src/log_tracker.py')

pred.load_model(BASE)
pred.predict_v20('Paris SG', 'Angers', 'Ligue_1')
```

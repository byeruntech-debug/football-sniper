# Football Sniper Prediction System

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Accuracy](https://img.shields.io/badge/WF_Accuracy-81.4%25-green)
![Yield](https://img.shields.io/badge/Yield_vs_B365-%2B1.6%25-brightgreen)
![Leagues](https://img.shields.io/badge/Active_Leagues-7-blue)
![Tests](https://img.shields.io/badge/Stress_Tests-3%2F3_Passed-green)

A production-grade football match prediction system using **Dixon-Coles** statistical modeling combined with **Elo Walk-Forward** validation. Achieves **81.4% accuracy** on 194 out-of-sample sniper picks across 7 European leagues.

## Model Architecture
```
Match Data (CSV)
      │
      ▼
Dixon-Coles V3 (55%)    +    Elo Walk-Forward (45%)
  - Attack parameters          - Burn-in period (season 1)
  - Defense parameters         - Live update per match
  - Home field advantage       - Progressive K=32
  - Rho correlation
      │                               │
      └───────────┬───────────────────┘
                  ▼
          Ensemble Model
                  │
          ┌───────┼───────┐
          ▼       ▼       ▼
     Giant     Draw    Sniper
     Killer   Warning  Filter
     Filter   System  (per-liga
                       threshold)
                  │
                  ▼
          Sniper Pick + Injury Warning
```

## Validated Performance

| Metric | Value | Method |
|--------|-------|--------|
| Walk-Forward Accuracy | **81.4%** | Warm burn-in WF |
| Overall Yield vs B365 | **+1.6%** | 194 picks OOS |
| Serie A Yield | **+6.3%** | Best performing league |
| Underconfident Bias | **+7%** | Calibration curve |
| Stress Tests | **3/3 Passed** | WF + Brier + Bookmaker |

## Active Leagues & Thresholds

| League | Threshold | WF Accuracy | Yield |
|--------|-----------|-------------|-------|
| Bundesliga | 0.66 | 82.9% | +2.8% |
| EPL | 0.68 | 80.0% | -2.8%* |
| Serie A | 0.66 | 80.6% | +6.3% |
| Eredivisie | 0.56 | 82.1% | +3.1% |
| La Liga | 0.58 | 80.0% | -1.2%* |
| Liga Portugal | 0.59 | 80.0% | — |
| Super Lig | 0.65 | 80.3% | — |

*EPL & La Liga avg odds 1.20-1.22 near break-even. Monitor closely.

## Methodology

### Walk-Forward Validation with Burn-In
Unlike standard backtests, this model uses **temporal walk-forward validation**:
1. **Burn-in Phase** (season 2022/23): Elo ratings warm up from base 1500 — no predictions recorded
2. **Live Phase** (seasons 2023/24 + 2024/25): Predictions made with warm Elo, recorded as out-of-sample

This eliminates cold-start bias and time leakage, producing honest performance estimates.

### 3 Stress Tests
1. **Walk-Forward**: Proves no time leakage. Cold WF 72.5% → Warm WF 81.4% (+8.9%)
2. **Brier Score**: Calibration curve shows consistent +7% underconfident bias (margin of safety)
3. **Bookmaker Baseline**: Overall yield +1.6% vs B365 closing odds — beats bookmaker vig

### Key Decisions
| Decision | Choice | Evidence |
|----------|--------|----------|
| Platt Scaler | DISABLED | Draw overfitting → all probs → 0.33 |
| V20.4 EV+Kelly | REJECTED | n=18, variance high, yield -11.9% |
| Injury Lambda | Warning flag only | McNemar p=1.0, Occam's Razor |
| Championship | REJECTED | 49.3% accuracy, high parity |
| Power Transform λ | REJECTED | Destroys Poisson distribution integrity |

## Model Journey

| Version | Accuracy | Finding |
|---------|----------|---------|
| V5 | 44.0% | Monte Carlo baseline |
| V6-V8 | 56-75% | Dixon-Coles + Elo introduced |
| V20 | 87.5%* | Multi-league — time leakage detected |
| V20.2 | 72.5% | Cold walk-forward honest baseline |
| V20.3 | **81.4%** | Warm WF + burn-in — production grade |
| V20.3-E | **81.4%** | +2 leagues (Liga Portugal, Super Lig) |
| V20.5 | **81.4%** | Injury warning flag (Option C) |

*V20 87.5% contained time leakage — 81.4% is the honest number.

## Quick Start (Google Colab)
```python
from google.colab import drive
drive.mount('/content/drive')

BASE = '/content/drive/MyDrive/Football_Project'
exec(open(BASE + '/scripts/football_predictor_full.py').read())

# Predict a match
result = predict_v20('Inter Milan', 'Juventus', 'Serie_A',
                     match_date='2025-03-20')
```

### Output format
```python
{
  'prediction': 'home_win',
  'home_prob': 0.514,
  'draw_prob': 0.218,
  'away_prob': 0.267,
  'confidence': 0.514,
  'tier': 'SKIP',          # SNIPER / HOLD / SKIP
  'threshold': 0.66,
  'warnings': [],           # Giant Killer / Draw Warning
  'injury_warning': {
    'has_warning': True,
    'away': [{'name': 'Bremer', 'position': 'Centre-Back', 'days_out': '266 days'}]
  },
  'lambda_home': 2.908,
  'lambda_away': 2.245,
  'elo_diff': 135,
  'liga': 'Serie_A'
}
```

## Deployment Rules

1. **Flat betting 1 unit** per pick — no Kelly Criterion before 500+ live picks
2. **No minimum odds filter** currently — reduces picks to n=18
3. **Monitor EPL & La Liga** — avg odds 1.20-1.22 near mathematical break-even
4. **Capital allocation**: Serie A (+6.3%) > Eredivisie (+3.1%) > Bundesliga (+2.8%)
5. **Re-evaluate Kelly** after 500+ live picks accumulated

## Repository Structure
```
football-sniper/
├── src/
│   ├── predictor.py          # Main prediction engine (DC + Elo)
│   ├── sniper_filter.py      # Sniper threshold + Giant Killer filter
│   └── log_tracker.py        # Live prediction tracker
├── results/
│   ├── walkforward_v203.csv  # 3,626 walk-forward predictions
│   ├── value_test_v203.csv   # 194 picks with B365 odds + P/L
│   └── fresh_backtest_v202.csv
├── data_sample/              # Sample CSV format (5 rows per league)
├── docs/
│   └── methodology.md        # Detailed methodology documentation
└── notebooks/
    └── analysis_demo.ipynb   # Demo notebook
```

## Roadmap

| Priority | Feature | Estimated Impact | Status |
|----------|---------|-----------------|--------|
| High | Kelly Criterion (after 500 picks) | ROI +3-8% | Pending |
| High | Minimum odds filter (≥1.25) | Yield +2-4% | Pending |
| Medium | Dynamic DC re-fit (every 4-6 weeks) | Acc +1-2% | Pending |
| Medium | Ligue 1 rehabilitation | +1 league | Pending |
| Research | xG integration | Acc +2-4% | Future |
| Research | Asian Handicap extension | Yield +4-8% | Future |

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*Model version: V20.3-EXPANDED-FINAL | Last updated: March 2026*

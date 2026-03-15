# Methodology: Football Sniper V20.3

## Dixon-Coles Model

The core prediction engine uses the Dixon-Coles (1997) Poisson model:

λ_home = exp(α_home + β_away + μ)
λ_away = exp(α_away + β_home)

Where:
- α (attack parameter): offensive strength
- β (defense parameter): defensive weakness (positive = leaks goals)
- μ (home field advantage): typically 0.15-0.30
- ρ (rho): low-score correlation correction

Parameters are estimated via maximum likelihood with temporal weighting:
weight(t) = exp(-ξ × days_before_match)

## Elo Rating System

Progressive K-factor system:
- K = 32 (standard)
- Home advantage = 50 Elo points
- Walk-forward: updated after EACH match (no future leakage)

Burn-in period: First season (2022/23) used exclusively for Elo warm-up.
No predictions recorded during burn-in.

## Ensemble

Final probability = 0.55 × DC_prob + 0.45 × Elo_prob

Draw gap boost: if |P(home) - P(away)| < 0.08, apply draw_boost factor.

## Sniper Filter

Pick is SNIPER if: confidence >= threshold AND no Giant Killer flag

confidence = max(P_home, P_draw, P_away)

## Thresholds (V20.3)

Calibrated from warm walk-forward data (target ≥80% accuracy):

| League | Threshold | Basis |
|--------|-----------|-------|
| Bundesliga | 0.66 | Warm WF scan |
| EPL | 0.68 | Warm WF scan |
| Serie A | 0.66 | Warm WF scan |
| Eredivisie | 0.56 | Warm WF scan |
| La Liga | 0.58 | Warm WF scan |
| Liga Portugal | 0.59 | Isolated WF scan |
| Super Lig | 0.65 | Isolated WF scan |

## Injury Warning System (V20.5)

Based on McNemar test (p=1.0), injury data does NOT significantly alter
sniper pick classification. Implemented as informational warning flag only.

Trigger: key player injured (Goalkeeper, Striker, Centre-Back, Attacking Midfielder)
on match date, based on Transfermarkt injury dataset (15,603 records, 2020-2026).

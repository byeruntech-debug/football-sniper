
import streamlit as st
import pandas as pd
import numpy as np
import os
from collections import Counter

st.set_page_config(page_title="Football Sniper", page_icon="⚽", layout="wide")

BASE = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_results():
    results = {}
    paths = {
        "backtest": "results/fresh_backtest_v202.csv",
        "value":    "results/value_test_v203.csv",
        "walkfwd":  "results/walkforward_v203.csv",
    }
    for key, rel in paths.items():
        full = os.path.join(BASE, rel)
        results[key] = pd.read_csv(full) if os.path.exists(full) else None
    return results

@st.cache_data
def load_samples():
    samples = {}
    for name in ["bundesliga", "epl", "serie_a"]:
        path = os.path.join(BASE, f"data_sample/{name}_sample.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            df.columns = df.columns.str.strip()
            samples[name.replace("_", " ").title()] = df
    return samples

def get_col(df, candidates):
    if df is None: return None
    for c in candidates:
        if c in df.columns: return c
    return None

RES     = load_results()
SAMPLES = load_samples()

st.sidebar.markdown("## ⚽ Football Sniper")
page = st.sidebar.radio("Halaman", ["Overview","Fresh Backtest","Value Bets","Walk-Forward","Data Sample","Simulator"])

# ── OVERVIEW ──────────────────────────────────────────────────────────
if page == "Overview":
    st.title("⚽ Football Sniper — Dashboard")
    bt, vt, wf = RES["backtest"], RES["value"], RES["walkfwd"]
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### Backtest")
        if bt is not None:
            corr = get_col(bt, ["correct","Correct"])
            st.metric("Total Laga", f"{len(bt):,}")
            if corr: st.metric("Akurasi", f"{bt[corr].mean()*100:.1f}%")
        else: st.warning("fresh_backtest_v202.csv tidak ada")
    with c2:
        st.markdown("### Value Bets")
        if vt is not None:
            st.metric("Total", f"{len(vt):,}")
            roi = get_col(vt, ["roi","ROI"])
            if roi: st.metric("ROI", f"{vt[roi].mean():.1f}%")
        else: st.warning("value_test_v203.csv tidak ada")
    with c3:
        st.markdown("### Walk-Forward")
        if wf is not None:
            st.metric("Total Laga", f"{len(wf):,}")
            corr = get_col(wf, ["correct","Correct"])
            if corr: st.metric("Akurasi", f"{wf[corr].mean()*100:.1f}%")
        else: st.warning("walkforward_v203.csv tidak ada")

    st.divider()
    bt = RES["backtest"]
    if bt is not None:
        liga = get_col(bt, ["liga","league","League","Liga"])
        corr = get_col(bt, ["correct","Correct"])
        if liga and corr:
            st.subheader("Akurasi per Liga")
            s = (bt.groupby(liga)[corr].agg(["count","mean"])
                   .rename(columns={"count":"Total","mean":"Akurasi %"})
                   .assign(**{"Akurasi %": lambda x: (x["Akurasi %"]*100).round(1)})
                   .reset_index())
            col_t, col_c = st.columns(2)
            col_t.dataframe(s, use_container_width=True, hide_index=True)
            col_c.bar_chart(s.set_index(liga)["Akurasi %"])

# ── FRESH BACKTEST ────────────────────────────────────────────────────
elif page == "Fresh Backtest":
    st.title("📊 Fresh Backtest")
    bt = RES["backtest"]
    if bt is None:
        st.error("fresh_backtest_v202.csv tidak ditemukan")
        st.stop()
    st.caption(f"{len(bt):,} laga | Kolom: {', '.join(bt.columns)}")
    liga = get_col(bt, ["liga","league","League","Liga"])
    corr = get_col(bt, ["correct","Correct"])
    conf = get_col(bt, ["confidence","Confidence"])
    pred = get_col(bt, ["predicted","prediction"])
    f1,f2,f3 = st.columns(3)
    sel_liga = f1.selectbox("Liga", ["Semua"]+sorted(bt[liga].dropna().unique().tolist())) if liga else "Semua"
    min_conf = f2.slider("Min. Confidence", 0.0, 1.0, 0.0, 0.01) if conf else 0.0
    sel_pred = f3.selectbox("Prediksi", ["Semua"]+sorted(bt[pred].dropna().unique().tolist())) if pred else "Semua"
    filtered = bt.copy()
    if sel_liga != "Semua" and liga: filtered = filtered[filtered[liga]==sel_liga]
    if min_conf > 0 and conf:       filtered = filtered[filtered[conf]>=min_conf]
    if sel_pred != "Semua" and pred: filtered = filtered[filtered[pred]==sel_pred]
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Laga", f"{len(filtered):,}")
    if corr and len(filtered)>0:
        acc = filtered[corr].mean()*100
        m2.metric("Akurasi", f"{acc:.1f}%")
        m3.metric("Benar", int(filtered[corr].sum()))
        m4.metric("Salah", len(filtered)-int(filtered[corr].sum()))
    if liga and corr:
        st.bar_chart(filtered.groupby(liga)[corr].mean().mul(100).rename("Akurasi %"))
    st.dataframe(filtered.reset_index(drop=True), use_container_width=True, height=400)

# ── VALUE BETS ────────────────────────────────────────────────────────
elif page == "Value Bets":
    st.title("💰 Value Bets")
    vt = RES["value"]
    if vt is None:
        st.error("value_test_v203.csv tidak ditemukan")
        st.stop()
    st.caption(f"{len(vt):,} bets | Kolom: {', '.join(vt.columns)}")
    corr = get_col(vt, ["correct","Correct"])
    roi  = get_col(vt, ["roi","ROI"])
    liga = get_col(vt, ["liga","league","League"])
    m1,m2,m3 = st.columns(3)
    m1.metric("Total", f"{len(vt):,}")
    if corr: m2.metric("Hit Rate", f"{vt[corr].mean()*100:.1f}%")
    if roi:  m3.metric("ROI Rata-rata", f"{vt[roi].mean():.1f}%")
    if liga and corr:
        st.bar_chart(vt.groupby(liga)[corr].mean().mul(100).rename("Hit Rate %"))
    st.dataframe(vt.reset_index(drop=True), use_container_width=True, height=400)

# ── WALK-FORWARD ──────────────────────────────────────────────────────
elif page == "Walk-Forward":
    st.title("🚶 Walk-Forward Validation")
    wf = RES["walkfwd"]
    if wf is None:
        st.error("walkforward_v203.csv tidak ditemukan")
        st.stop()
    st.caption(f"{len(wf):,} laga | Kolom: {', '.join(wf.columns)}")
    corr = get_col(wf, ["correct","Correct"])
    conf = get_col(wf, ["confidence","Confidence"])
    liga = get_col(wf, ["liga","league","League"])
    m1,m2,m3 = st.columns(3)
    m1.metric("Total Laga", f"{len(wf):,}")
    if corr: m2.metric("Akurasi", f"{wf[corr].mean()*100:.1f}%")
    if conf and corr:
        sniper = wf[wf[conf]>=0.60]
        m3.metric("Sniper Akurasi", f"{sniper[corr].mean()*100:.1f}%" if len(sniper)>0 else "—")
    if liga and corr:
        st.bar_chart(wf.groupby(liga)[corr].mean().mul(100).rename("Akurasi %"))
    bt = RES["backtest"]
    if bt is not None and corr:
        bt_corr = get_col(bt, ["correct","Correct"])
        if bt_corr:
            wf_acc = wf[corr].mean()*100
            bt_acc = bt[bt_corr].mean()*100
            delta  = wf_acc - bt_acc
            flag   = "POSSIBLE LEAK" if abs(delta)>10 else "KONSISTEN"
            st.info(f"WF: {wf_acc:.1f}% | Backtest: {bt_acc:.1f}% | Delta: {delta:+.1f}% — {flag}")
    st.dataframe(wf.reset_index(drop=True), use_container_width=True, height=400)

# ── DATA SAMPLE ───────────────────────────────────────────────────────
elif page == "Data Sample":
    st.title("📁 Data Sample")
    if not SAMPLES:
        st.error("Tidak ada CSV di data_sample/")
        st.stop()
    liga_sel = st.selectbox("Liga", list(SAMPLES.keys()))
    df = SAMPLES[liga_sel]
    st.caption(f"{len(df):,} laga | Kolom: {', '.join(df.columns)}")
    ftr  = get_col(df, ["FTR","ftr","result"])
    hg   = get_col(df, ["FTHG","hg","home_goals"])
    ag   = get_col(df, ["FTAG","ag","away_goals"])
    m1,m2,m3 = st.columns(3)
    m1.metric("Total Laga", f"{len(df):,}")
    if ftr:
        m2.metric("Home Win Rate", f"{(df[ftr]=='H').mean()*100:.1f}%")
        col1, col2 = st.columns(2)
        col1.bar_chart(df[ftr].value_counts())
        if hg and ag:
            col2.bar_chart(pd.DataFrame({"Home": [df[hg].mean()], "Away": [df[ag].mean()]}).T.rename(columns={0:"Avg Gol"}))
    st.dataframe(df.reset_index(drop=True), use_container_width=True, height=400)

# ── SIMULATOR ─────────────────────────────────────────────────────────
elif page == "Simulator":
    st.title("🎲 Match Simulator")
    all_teams = set()
    for df in SAMPLES.values():
        for c in ["HomeTeam","AwayTeam","home_team","away_team"]:
            if c in df.columns: all_teams.update(df[c].dropna().unique())
    all_teams = sorted(all_teams) if all_teams else ["Team A","Team B"]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🏠 Tim Kandang**")
        home_name = st.selectbox("Tim Kandang", all_teams, key="h")
        xg_h  = st.slider("xG Home", 0.5, 3.0, 1.5, 0.1)
        fat_h = st.slider("Fatigue Home", 0.0, 1.0, 0.2, 0.05)
        sk_h  = st.slider("Shooting Skill Home", 0.85, 1.20, 1.0, 0.01)
    with c2:
        st.markdown("**✈️ Tim Tamu**")
        away_name = st.selectbox("Tim Tamu", all_teams, index=min(1,len(all_teams)-1), key="a")
        xg_a  = st.slider("xG Away", 0.5, 3.0, 1.3, 0.1)
        fat_a = st.slider("Fatigue Away", 0.0, 1.0, 0.2, 0.05)
        sk_a  = st.slider("Shooting Skill Away", 0.85, 1.20, 1.0, 0.01)

    n_sim = st.select_slider("Simulasi", [1000,5000,10000], value=5000)

    if st.button("Jalankan Simulasi", type="primary", use_container_width=True):
        with st.spinner(f"Running {n_sim:,} simulasi..."):
            rng = np.random.default_rng(42)
            sims = []
            for _ in range(n_sim):
                hg = ag = 0
                for seg in range(6):
                    diff = hg - ag
                    lh = max(0.02, xg_h/6*sk_h - fat_h*0.05*(1+seg/6) + 0.02 - 0.015*max(diff,0))
                    la = max(0.02, xg_a/6*sk_a - fat_a*0.05*(1+seg/6)        - 0.015*max(-diff,0))
                    hg += int(rng.poisson(lh))
                    ag += int(rng.poisson(la))
                sims.append((hg, ag))

        hw = sum(h>a for h,a in sims)/n_sim*100
        d  = sum(h==a for h,a in sims)/n_sim*100
        aw = sum(h<a for h,a in sims)/n_sim*100
        btts = sum(h>0 and a>0 for h,a in sims)/n_sim*100
        ov25 = sum(h+a>2.5 for h,a in sims)/n_sim*100

        r1,r2,r3 = st.columns(3)
        r1.metric(f"{home_name} Menang", f"{hw:.1f}%")
        r2.metric("Seri", f"{d:.1f}%")
        r3.metric(f"{away_name} Menang", f"{aw:.1f}%")
        r4,r5 = st.columns(2)
        r4.metric("BTTS", f"{btts:.1f}%")
        r5.metric("Over 2.5", f"{ov25:.1f}%")

        pred  = max({"home_win":hw,"draw":d,"away_win":aw}, key=lambda k:{"home_win":hw,"draw":d,"away_win":aw}[k])
        conf  = max(hw,d,aw)/100
        tier  = "SNIPER" if conf>=0.55 else "HOLD"
        st.success(f"Prediksi: {pred.replace('_',' ').title()} | Confidence: {conf*100:.1f}% | Tier: {tier}")

        top = Counter(sims).most_common(8)
        st.dataframe(pd.DataFrame([{"Skor":f"{s[0][0]}-{s[0][1]}","Prob %":round(s[1]/n_sim*100,2)} for s in top]),
                     use_container_width=True, hide_index=True)

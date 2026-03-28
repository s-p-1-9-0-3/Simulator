import json
import os
import re
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st


# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================
ADMIN_PIN = "1234"  # <-- CAMBIA ESTE PIN

st.set_page_config(
    page_title="Revenue Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body,
[class*="css"],
[data-testid="stAppViewContainer"],
[data-testid="stMarkdownContainer"] {
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 10% -10%, rgba(78,193,181,0.13) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 90% 110%, rgba(99,102,241,0.07) 0%, transparent 55%),
        linear-gradient(165deg, #f0f4f8 0%, #f8fbfb 50%, #f2f6f5 100%);
    min-height: 100vh;
}

[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
}

.block-container {
    max-width: 1200px;
    padding-top: 3.5rem;
    padding-bottom: 3rem;
    position: relative;
    z-index: 1;
}

/* ── ANIMACIONES ─────────────────────────────────────────── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.97); }
    to   { opacity: 1; transform: scale(1); }
}
@keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position: 200% center; }
}
@keyframes pulse-border {
    0%, 100% { box-shadow: 0 0 0 0 rgba(78,193,181,0.0); }
    50%       { box-shadow: 0 0 0 4px rgba(78,193,181,0.18); }
}
@keyframes stepPop {
    from { opacity: 0; transform: translateY(12px) scale(0.98); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}

/* ── HEADER ──────────────────────────────────────────────── */
.header-wrap { animation: fadeUp 0.6s cubic-bezier(0.22,1,0.36,1) both; margin-bottom: 0.2rem; }
.header-logo-wrap { display: flex; align-items: center; justify-content: center; min-height: 88px; }
.header-text-wrap { display: flex; flex-direction: column; justify-content: center; min-height: 88px; }
.top-eyebrow { font-family: 'DM Sans', sans-serif; font-size: 0.72rem; font-weight: 500; letter-spacing: 0.16em; text-transform: uppercase; color: #4ec1b5; margin: 0 0 0.45rem 0; }
.top-title { font-family: 'Syne', sans-serif; font-size: 2.55rem; font-weight: 800; line-height: 1.0; margin: 0; color: #0f1f38; letter-spacing: -0.03em; }
.top-title span { background: linear-gradient(90deg, #4ec1b5 0%, #6366f1 35%, #4ec1b5 65%, #22d3c8 100%); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; animation: shimmer 4s linear infinite; }
.top-subtitle { font-size: 0.95rem; font-weight: 300; color: #7a8fa6; margin: 0.6rem 0 0 0; letter-spacing: 0.01em; }

/* ── DIVISOR ─────────────────────────────────────────────── */
.cards-divider { width: 100%; height: 1px; background: linear-gradient(90deg, transparent, rgba(15,23,42,0.10) 20%, rgba(15,23,42,0.10) 80%, transparent); margin: 28px 0 10px 0; border-radius: 999px; animation: fadeIn 0.8s 0.5s both; }

/* ── NAV GRID 2 TARJETAS ─────────────────────────────────── */
.nav-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    width: 100%;
    margin-bottom: 4px;
}

.nav-card {
    height: 200px;
    border-radius: 28px;
    border: 1px solid rgba(15,23,42,0.10);
    background: linear-gradient(145deg, rgba(255,255,255,0.97) 0%, rgba(248,252,252,0.92) 100%);
    box-shadow: 0 1px 0 rgba(255,255,255,0.9) inset, 0 8px 24px rgba(15,23,42,0.06), 0 2px 6px rgba(15,23,42,0.04);
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 28px 20px;
    position: relative;
    overflow: hidden;
    transition: transform 0.22s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.22s ease, border-color 0.22s ease, background 0.22s ease;
    user-select: none;
    -webkit-user-select: none;
}

.nav-card:nth-child(1) { animation: fadeUp 0.55s 0.10s cubic-bezier(0.22,1,0.36,1) both; }
.nav-card:nth-child(2) { animation: fadeUp 0.55s 0.20s cubic-bezier(0.22,1,0.36,1) both; }

.nav-card::after { content: ''; position: absolute; top: -50%; left: -75%; width: 50%; height: 200%; background: linear-gradient(105deg, transparent, rgba(255,255,255,0.50), transparent); transform: skewX(-20deg); transition: left 0.55s ease; pointer-events: none; }
.nav-card:hover::after { left: 130%; }
.nav-card:hover { transform: translateY(-6px) scale(1.012); border-color: rgba(78,193,181,0.55); box-shadow: 0 1px 0 rgba(255,255,255,0.9) inset, 0 20px 40px rgba(78,193,181,0.16), 0 8px 20px rgba(15,23,42,0.08); background: linear-gradient(145deg, rgba(255,255,255,0.99) 0%, rgba(78,193,181,0.09) 100%); }
.nav-card:active { transform: translateY(-2px) scale(1.005); transition-duration: 0.08s; }

.nav-card-icon { font-size: 2.2rem; line-height: 1; margin-bottom: 4px; }
.nav-card-title { font-family: 'Syne', sans-serif; font-size: 1.2rem; font-weight: 700; color: #172033; text-align: center; letter-spacing: -0.02em; }
.nav-card-desc { font-size: 0.85rem; font-weight: 400; color: #7a8fa6; text-align: center; line-height: 1.4; max-width: 80%; }

.hidden-nav-btns { display: none !important; }

/* ── DASHBOARD CARD ──────────────────────────────────────── */
.dashboard-card {
    border: 1px solid rgba(15,23,42,0.09);
    border-radius: 28px;
    padding: 28px 28px 20px 28px;
    background: linear-gradient(145deg, rgba(255,255,255,0.97) 0%, rgba(248,252,251,0.93) 100%);
    box-shadow: 0 1px 0 rgba(255,255,255,0.9) inset, 0 8px 32px rgba(15,23,42,0.07), 0 2px 8px rgba(15,23,42,0.04);
    margin-bottom: 1.2rem;
    animation: scaleIn 0.45s cubic-bezier(0.22,1,0.36,1) both;
    position: relative;
    overflow: hidden;
}
.dashboard-card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 3px; background: linear-gradient(90deg, #4ec1b5, #6366f1 60%, transparent); border-radius: 28px 28px 0 0; opacity: 0.7; }

.section-title { font-family: 'Syne', sans-serif; font-size: 1.25rem; font-weight: 700; margin-bottom: 0.25rem; color: #0f1f38; letter-spacing: -0.02em; }
.section-subtitle { font-size: 0.9rem; font-weight: 300; color: #7a8fa6; margin-bottom: 1.2rem; }

/* ── WIZARD STEPPER ──────────────────────────────────────── */
.wizard-stepper {
    display: flex;
    align-items: center;
    gap: 0;
    margin-bottom: 2rem;
    margin-top: 0.5rem;
}

.wizard-step {
    display: flex;
    align-items: center;
    flex: 1;
    position: relative;
}

.wizard-step-circle {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    flex-shrink: 0;
    transition: all 0.3s ease;
    z-index: 1;
}

.wizard-step-circle.done {
    background: #4ec1b5;
    color: white;
    box-shadow: 0 4px 12px rgba(78,193,181,0.35);
}

.wizard-step-circle.active {
    background: linear-gradient(135deg, #4ec1b5, #6366f1);
    color: white;
    box-shadow: 0 4px 16px rgba(78,193,181,0.40);
    animation: pulse-border 2s ease-in-out infinite;
}

.wizard-step-circle.pending {
    background: rgba(15,23,42,0.07);
    color: #9aafbf;
    border: 2px solid rgba(15,23,42,0.10);
}

.wizard-step-label {
    font-size: 0.75rem;
    font-weight: 500;
    margin-top: 6px;
    text-align: center;
    white-space: nowrap;
}

.wizard-step-label.done   { color: #4ec1b5; }
.wizard-step-label.active { color: #0f1f38; font-weight: 700; }
.wizard-step-label.pending { color: #b0c4d0; }

.wizard-step-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex-shrink: 0;
}

.wizard-step-line {
    flex: 1;
    height: 2px;
    background: rgba(15,23,42,0.08);
    margin: 0 6px;
    border-radius: 2px;
    margin-bottom: 22px;
    transition: background 0.3s;
}
.wizard-step-line.done { background: #4ec1b5; }

.wizard-step-content {
    animation: stepPop 0.35s cubic-bezier(0.22,1,0.36,1) both;
}

/* ── WIZARD MODOS (Nuevo / Editar) ───────────────────────── */
.wizard-mode-tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 1.8rem;
}

.wizard-mode-tab {
    flex: 1;
    padding: 12px 16px;
    border-radius: 16px;
    border: 1.5px solid rgba(15,23,42,0.10);
    background: rgba(248,250,252,0.8);
    cursor: pointer;
    text-align: center;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    font-weight: 500;
    color: #7a8fa6;
    transition: all 0.18s ease;
    user-select: none;
}

.wizard-mode-tab.active {
    border-color: rgba(78,193,181,0.60);
    background: linear-gradient(145deg, rgba(78,193,181,0.10), rgba(78,193,181,0.04));
    color: #0f1f38;
    font-weight: 600;
    box-shadow: 0 4px 14px rgba(78,193,181,0.14);
}

/* ── SUB-NAV GUESTOOL ────────────────────────────────────── */
.subnav-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
}

.subnav-card {
    height: 140px;
    border-radius: 22px;
    border: 1px solid rgba(15,23,42,0.10);
    background: linear-gradient(145deg, rgba(255,255,255,0.97) 0%, rgba(248,252,252,0.92) 100%);
    box-shadow: 0 4px 16px rgba(15,23,42,0.05);
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 20px;
    position: relative;
    overflow: hidden;
    transition: transform 0.20s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.20s ease, border-color 0.20s ease;
    user-select: none;
    animation: fadeUp 0.45s cubic-bezier(0.22,1,0.36,1) both;
}

.subnav-card:nth-child(1) { animation-delay: 0.05s; }
.subnav-card:nth-child(2) { animation-delay: 0.12s; }

.subnav-card:hover { transform: translateY(-5px) scale(1.012); border-color: rgba(78,193,181,0.50); box-shadow: 0 14px 30px rgba(78,193,181,0.14); }
.subnav-card:active { transform: translateY(-1px); transition-duration: 0.08s; }

.subnav-card-icon  { font-size: 1.8rem; line-height: 1; }
.subnav-card-title { font-family: 'Syne', sans-serif; font-size: 1.0rem; font-weight: 700; color: #172033; }
.subnav-card-desc  { font-size: 0.78rem; color: #7a8fa6; text-align: center; }

/* ── KPI CARDS ───────────────────────────────────────────── */
.kpi-card { border: 1px solid rgba(15,23,42,0.09); border-radius: 20px; padding: 20px 18px 18px; background: rgba(248,250,252,0.80); min-height: 160px; transition: transform 0.2s ease, box-shadow 0.2s ease; animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) both; }
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 12px 28px rgba(15,23,42,0.09); }
.kpi-good { border: 1.5px solid rgba(78,193,181,0.55) !important; background: linear-gradient(145deg, rgba(78,193,181,0.08), rgba(78,193,181,0.04)) !important; animation: pulse-border 2.5s ease-in-out infinite; }
.kpi-good:hover { box-shadow: 0 12px 28px rgba(78,193,181,0.18) !important; }
.kpi-title { font-family: 'Syne', sans-serif; font-size: 0.85rem; font-weight: 600; color: #7a8fa6; margin-bottom: 0.3rem; letter-spacing: 0.04em; text-transform: uppercase; }
.kpi-sub { font-size: 0.82rem; font-weight: 300; color: #9aafbf; margin-top: 0.4rem; }
.kpi-value { font-size: 1.1rem; font-weight: 600; line-height: 1.2; color: #1a2e45; }
.kpi-total { font-family: 'DM Sans', sans-serif; font-size: 1.8rem; font-weight: 600; line-height: 1.1; margin-top: 0.35rem; color: #0f1f38; letter-spacing: -0.01em; }
.kpi-currency { font-size: 1.05rem; font-weight: 400; color: #7a8fa6; margin-left: 4px; vertical-align: middle; letter-spacing: 0; }

.single-rms { max-width: 440px; margin: 0 auto; }
.single-rms .kpi-card { text-align: center; padding: 32px 24px; }
.single-rms .kpi-total { font-size: 3rem; background: linear-gradient(135deg, #0f1f38, #4ec1b5); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }

/* ── INPUTS ──────────────────────────────────────────────── */
div[data-testid="stTextInput"] input { border-radius: 14px !important; border: 1px solid rgba(15,23,42,0.13) !important; background: rgba(255,255,255,0.85) !important; font-family: 'DM Sans', sans-serif !important; transition: border-color 0.2s, box-shadow 0.2s !important; }
div[data-testid="stTextInput"] input:focus { border-color: rgba(78,193,181,0.70) !important; box-shadow: 0 0 0 3px rgba(78,193,181,0.14) !important; }
div[data-testid="stSelectbox"] > div { border-radius: 14px !important; }
div[data-testid="stFileUploader"] section { border-radius: 18px !important; border: 1.5px dashed rgba(78,193,181,0.45) !important; background: rgba(78,193,181,0.03) !important; transition: border-color 0.2s, background 0.2s !important; }
div[data-testid="stFileUploader"] section:hover { border-color: rgba(78,193,181,0.75) !important; background: rgba(78,193,181,0.06) !important; }
div[data-testid="stDataEditor"] { border-radius: 16px !important; }

div[data-testid="stButton"] > button { border-radius: 14px !important; font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important; transition: transform 0.18s ease, box-shadow 0.18s ease !important; }
div[data-testid="stButton"] > button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 18px rgba(78,193,181,0.22) !important; }
div[data-testid="stAlert"] { border-radius: 16px !important; font-family: 'DM Sans', sans-serif !important; animation: fadeUp 0.35s cubic-bezier(0.22,1,0.36,1) both; }
div[data-testid="stCheckbox"] label { font-family: 'DM Sans', sans-serif !important; }
h3 { font-family: 'Syne', sans-serif !important; letter-spacing: -0.02em !important; color: #0f1f38 !important; }
[data-testid="collapsedControl"] { display: none; }

/* ── BACK BUTTON ─────────────────────────────────────────── */
.back-btn-wrap { margin-bottom: 1.2rem; }

/* ── RESPONSIVE ──────────────────────────────────────────── */
@media (max-width: 768px) {
    .block-container { padding-top: 2rem; }
    .top-title { font-size: 1.85rem; }
    .nav-grid { grid-template-columns: 1fr; gap: 12px; }
    .nav-card { height: 160px; border-radius: 22px; }
    .subnav-grid { grid-template-columns: 1fr; }
    .dashboard-card { padding: 20px 16px 16px; border-radius: 22px; }
    .kpi-total { font-size: 1.5rem; }
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# ESTADO UI
# =========================================================
def init_state():
    defaults = {
        "active_section":  None,   # None | "Wizard" | "Guestool"
        "guestool_sub":    None,   # None | "Simuleitor" | "Calculeitor"
        "wizard_mode":     "nuevo",  # "nuevo" | "editar"
        "wizard_step":     1,      # 1..4
        "wizard_empresa_nombre": "",
        "wizard_empresa_id":     "",
        "wizard_archivo":        None,
        "wizard_df_limpio":      None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# =========================================================
# STORAGE
# =========================================================
BASE_DIR   = Path(__file__).resolve().parent
DATA_DIR   = BASE_DIR / "datos"
CONFIG_DIR = BASE_DIR / "config"
CONFIG_PATH = CONFIG_DIR / "empresas_config.json"

DATA_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)


def slugify(texto: str) -> str:
    texto = str(texto).strip().lower()
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_")


def pretty_name_from_slug(slug: str) -> str:
    return str(slug).replace("_", " ").strip().title()


def default_empresa_config(nombre_empresa: str, archivo_csv: str) -> dict:
    return {
        "nombre":      nombre_empresa,
        "archivo_csv": archivo_csv,
        "markups":     {"Airbnb": 0.0, "Booking": 0.0, "Web": 0.0},
        "descuentos":  [],
    }


def load_config_from_disk() -> dict:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}


def save_config_to_disk(config: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def bootstrap_config_with_existing_csvs(config: dict) -> dict:
    changed = False
    for ruta in sorted(DATA_DIR.glob("*.csv")):
        empresa_id = slugify(ruta.stem)
        if empresa_id not in config:
            config[empresa_id] = default_empresa_config(
                nombre_empresa=pretty_name_from_slug(ruta.stem),
                archivo_csv=ruta.name,
            )
            changed = True
        else:
            for campo, valor in [("archivo_csv", ruta.name), ("nombre", pretty_name_from_slug(ruta.stem))]:
                if not config[empresa_id].get(campo):
                    config[empresa_id][campo] = valor
                    changed = True
            if "markups" not in config[empresa_id]:
                config[empresa_id]["markups"] = default_empresa_config("","")["markups"]
                changed = True
            if "descuentos" not in config[empresa_id]:
                config[empresa_id]["descuentos"] = []
                changed = True
    if changed:
        save_config_to_disk(config)
    return config


@st.cache_data(show_spinner=False)
def cargar_config() -> dict:
    config = load_config_from_disk()
    return bootstrap_config_with_existing_csvs(config)


def guardar_config(config: dict):
    save_config_to_disk(config)
    cargar_config.clear()


def invalidar_config():
    cargar_config.clear()


def ruta_csv_empresa(empresa_id: str) -> Path:
    config = cargar_config()
    archivo = config.get(empresa_id, {}).get("archivo_csv", f"{empresa_id}.csv")
    return DATA_DIR / archivo


def obtener_empresas():
    config = cargar_config()
    empresas = []
    for empresa_id, data in config.items():
        ruta = DATA_DIR / data.get("archivo_csv", f"{empresa_id}.csv")
        if ruta.exists() and ruta.stat().st_size > 0:
            empresas.append((empresa_id, data.get("nombre", pretty_name_from_slug(empresa_id))))
    return sorted(empresas, key=lambda x: x[1].lower())


def obtener_markups_empresa(empresa_id: str):
    config = cargar_config()
    m = config.get(empresa_id, {}).get("markups", {})
    return {
        "Airbnb":  float(m.get("Airbnb",  0.0) or 0.0),
        "Booking": float(m.get("Booking", 0.0) or 0.0),
        "Web":     float(m.get("Web",     0.0) or 0.0),
    }


def guardar_markups_empresa(empresa_id: str, airbnb: float, booking: float, web: float):
    config = cargar_config()
    if empresa_id not in config:
        config[empresa_id] = default_empresa_config(pretty_name_from_slug(empresa_id), f"{empresa_id}.csv")
    config[empresa_id]["markups"] = {"Airbnb": airbnb, "Booking": booking, "Web": web}
    guardar_config(config)


def obtener_descuentos_empresa(empresa_id: str) -> pd.DataFrame:
    config = cargar_config()
    descuentos = config.get(empresa_id, {}).get("descuentos", [])
    if descuentos:
        return pd.DataFrame(descuentos)
    return pd.DataFrame(columns=["Desde", "Hasta", "Descuento (%)"])


def guardar_descuentos_empresa(empresa_id: str, df: pd.DataFrame):
    filas = []
    for _, fila in df.iterrows():
        try:
            desde = int(float(str(fila.get("Desde", "")).replace(",", ".")))
            hasta = int(float(str(fila.get("Hasta", "")).replace(",", ".")))
            desc  = float(str(fila.get("Descuento (%)", "")).replace(",", "."))
        except Exception:
            continue
        if desde >= 1 and hasta >= desde:
            filas.append({"Desde": desde, "Hasta": hasta, "Descuento (%)": desc})
    config = cargar_config()
    if empresa_id not in config:
        config[empresa_id] = default_empresa_config(pretty_name_from_slug(empresa_id), f"{empresa_id}.csv")
    config[empresa_id]["descuentos"] = filas
    guardar_config(config)


def obtener_descuento_para_noches(empresa_id: str, noches: int) -> Optional[float]:
    df = obtener_descuentos_empresa(empresa_id)
    for _, fila in df.iterrows():
        try:
            if int(fila["Desde"]) <= noches <= int(fila["Hasta"]):
                return float(fila["Descuento (%)"])
        except Exception:
            continue
    return None


def obtener_apartamentos(empresa_id: str):
    ruta = ruta_csv_empresa(empresa_id)
    if not ruta.exists():
        return []
    try:
        df = pd.read_csv(ruta)
    except Exception:
        return []
    if not {"nombre", "coste_limpieza"}.issubset(set(df.columns)):
        try:
            df = normalizar_df_alojamientos(df)
        except Exception:
            return []
    df["coste_limpieza"] = pd.to_numeric(df["coste_limpieza"], errors="coerce")
    df = df.dropna(subset=["nombre", "coste_limpieza"])
    return list(df[["nombre", "coste_limpieza"]].sort_values("nombre").itertuples(index=False, name=None))


# =========================================================
# HELPERS
# =========================================================
def parse_int_input(valor, nombre, minimo=None, maximo=None) -> int:
    texto = str(valor).strip().replace(",", ".")
    if not texto:
        raise ValueError(f"'{nombre}' no puede estar vacío")
    n = float(texto)
    if not n.is_integer():
        raise ValueError(f"'{nombre}' debe ser un número entero")
    n = int(n)
    if minimo is not None and n < minimo:
        raise ValueError(f"'{nombre}' debe ser ≥ {minimo}")
    if maximo is not None and n > maximo:
        raise ValueError(f"'{nombre}' debe ser ≤ {maximo}")
    return n


def parse_float_input(valor, nombre, minimo=None, maximo=None) -> float:
    texto = str(valor).strip().replace(",", ".")
    if not texto:
        raise ValueError(f"'{nombre}' no puede estar vacío")
    n = float(texto)
    if minimo is not None and n < minimo:
        raise ValueError(f"'{nombre}' debe ser ≥ {minimo}")
    if maximo is not None and n > maximo:
        raise ValueError(f"'{nombre}' debe ser ≤ {maximo}")
    return n


def fmt_markup(v: float) -> str:
    if v == 0.0:
        return "0"
    return f"{v:.4f}".rstrip("0").rstrip(".")


def detectar_columnas(df: pd.DataFrame):
    col_nombre = col_limpieza = None
    for col in df.columns:
        cn = str(col).strip().lower()
        if col_nombre is None and any(k in cn for k in ["nombre","aloj","apart","propiedad"]):
            col_nombre = col
        if col_limpieza is None and any(k in cn for k in ["limp","clean","coste"]):
            col_limpieza = col
    return col_nombre, col_limpieza


def leer_archivo_datos(archivo):
    nombre = archivo.name.lower()
    if nombre.endswith(".xlsx"):
        archivo.seek(0)
        return pd.read_excel(archivo)
    if nombre.endswith(".csv"):
        for enc in ["utf-8", "latin-1", "cp1252"]:
            try:
                archivo.seek(0)
                return pd.read_csv(archivo, encoding=enc, sep=None, engine="python")
            except Exception:
                continue
        raise Exception("No se pudo leer el CSV")
    raise Exception("Formato no soportado. Usa CSV o XLSX")


def normalizar_df_alojamientos(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    col_nombre, col_limpieza = detectar_columnas(df)
    if not col_nombre or not col_limpieza:
        raise ValueError("No se detectan columnas válidas de nombre y limpieza")
    salida = df[[col_nombre, col_limpieza]].copy()
    salida.columns = ["nombre", "coste_limpieza"]
    salida["nombre"] = salida["nombre"].astype(str).str.strip()
    salida["coste_limpieza"] = pd.to_numeric(
        salida["coste_limpieza"].astype(str).str.replace(",", ".", regex=False).str.strip(),
        errors="coerce"
    )
    salida = salida.dropna(subset=["nombre","coste_limpieza"])
    salida = salida[salida["nombre"] != ""]
    return salida.drop_duplicates(subset=["nombre"]).sort_values("nombre").reset_index(drop=True)


# =========================================================
# NAV PRINCIPAL
# =========================================================
def render_nav():
    st.markdown('<div class="header-wrap">', unsafe_allow_html=True)
    col_logo, col_title = st.columns([1.1, 4.9], gap="small")
    with col_logo:
        st.markdown('<div class="header-logo-wrap">', unsafe_allow_html=True)
        if os.path.exists("logo.png"):
            st.image("logo.png", width=140)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_title:
        st.markdown("""
        <div class="header-text-wrap">
            <div class="top-eyebrow">Panel de control</div>
            <div class="top-title">Revenue <span>Dashboard</span></div>
            <div class="top-subtitle">Elige un módulo para trabajar</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div style="height:1.4rem"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="nav-grid">
        <div class="nav-card" id="nc-wizard">
            <div class="nav-card-icon">🧙</div>
            <div class="nav-card-title">Wizard</div>
            <div class="nav-card-desc">Alta y edición de empresas · alojamientos · markups · descuentos</div>
        </div>
        <div class="nav-card" id="nc-guestool">
            <div class="nav-card-icon">⚡</div>
            <div class="nav-card-title">Guestool</div>
            <div class="nav-card-desc">Simuleitor y Calculeitor · herramientas de precio</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="hidden-nav-btns" style="display:none!important;visibility:hidden;height:0;overflow:hidden;position:absolute;">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Wizard", key="nav_wizard"):
            st.session_state.active_section = "Wizard"
            st.session_state.wizard_step = 1
            st.session_state.wizard_mode = "nuevo"
            st.rerun()
    with c2:
        if st.button("Guestool", key="nav_guestool"):
            st.session_state.active_section = "Guestool"
            st.session_state.guestool_sub = None
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <script>
    (function() {
        function wire() {
            const map = { 'nc-wizard': 'Wizard', 'nc-guestool': 'Guestool' };
            Object.entries(map).forEach(([id, label]) => {
                const card = document.getElementById(id);
                if (!card || card._wired) return;
                card._wired = true;
                card.addEventListener('click', () => {
                    const btns = window.parent.document.querySelectorAll('button');
                    for (const btn of btns) {
                        if (btn.innerText.trim() === label) { btn.click(); break; }
                    }
                });
            });
        }
        let n = 0;
        const t = setInterval(() => { wire(); if (++n > 20) clearInterval(t); }, 200);
    })();
    </script>
    """, unsafe_allow_html=True)

    st.markdown('<div class="cards-divider"></div>', unsafe_allow_html=True)


def render_back(label="← Volver al inicio"):
    st.markdown('<div class="back-btn-wrap">', unsafe_allow_html=True)
    if st.button(label, key="btn_back_main"):
        st.session_state.active_section = None
        st.session_state.guestool_sub   = None
        st.session_state.wizard_step    = 1
        st.session_state.wizard_mode    = "nuevo"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# WIZARD — STEPPER UI
# =========================================================
WIZARD_STEPS = ["Empresa", "Archivo", "Markups", "Descuentos"]

def render_stepper(paso_actual: int):
    partes = []
    for i, label in enumerate(WIZARD_STEPS, 1):
        if i < paso_actual:
            estado = "done"
            icono  = "✓"
        elif i == paso_actual:
            estado = "active"
            icono  = str(i)
        else:
            estado = "pending"
            icono  = str(i)

        partes.append(f"""
        <div class="wizard-step-wrap">
            <div class="wizard-step-circle {estado}">{icono}</div>
            <div class="wizard-step-label {estado}">{label}</div>
        </div>
        """)
        if i < len(WIZARD_STEPS):
            line_cls = "done" if i < paso_actual else ""
            partes.append(f'<div class="wizard-step-line {line_cls}"></div>')

    st.markdown(
        f'<div class="wizard-stepper">{"".join(partes)}</div>',
        unsafe_allow_html=True
    )


# ── Paso 1: Nombre de empresa ──────────────────────────────
def wizard_paso1():
    st.markdown('<div class="wizard-step-content">', unsafe_allow_html=True)
    st.markdown("#### Nombre de la empresa")
    st.markdown('<p style="color:#7a8fa6;font-size:0.9rem;margin-top:-0.5rem;">Introduce el nombre tal como quieres que aparezca en la app.</p>', unsafe_allow_html=True)

    nombre = st.text_input(
        "Nombre",
        value=st.session_state.wizard_empresa_nombre,
        placeholder="Ej: Inmalaga",
        key="wiz_nombre"
    )

    st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)

    if st.button("Continuar →", key="wiz_p1_next", use_container_width=False):
        nombre = nombre.strip()
        if not nombre:
            st.error("Introduce un nombre para continuar.")
        else:
            empresa_id = slugify(nombre)
            config = cargar_config()
            if empresa_id in config:
                ruta = DATA_DIR / config[empresa_id].get("archivo_csv", f"{empresa_id}.csv")
                if ruta.exists():
                    st.warning(f"⚠️ Ya existe una empresa llamada **{config[empresa_id]['nombre']}**. Continuando sobreescribirás sus datos.")

            st.session_state.wizard_empresa_nombre = nombre
            st.session_state.wizard_empresa_id     = empresa_id
            st.session_state.wizard_step           = 2
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ── Paso 2: Subir archivo ──────────────────────────────────
def wizard_paso2():
    st.markdown('<div class="wizard-step-content">', unsafe_allow_html=True)
    empresa = st.session_state.wizard_empresa_nombre
    st.markdown(f"#### Archivo de alojamientos · *{empresa}*")
    st.markdown('<p style="color:#7a8fa6;font-size:0.9rem;margin-top:-0.5rem;">Sube un CSV o Excel con una columna de nombre y una de coste de limpieza.</p>', unsafe_allow_html=True)

    archivo = st.file_uploader("Selecciona archivo", type=["csv","xlsx"], key="wiz_archivo")

    if archivo:
        try:
            df = leer_archivo_datos(archivo)
            df_limpio = normalizar_df_alojamientos(df)
            st.success(f"✅ {len(df_limpio)} alojamientos detectados")
            with st.expander("Vista previa", expanded=False):
                st.dataframe(df_limpio, use_container_width=True, hide_index=True)
            st.session_state.wizard_df_limpio = df_limpio
        except Exception as e:
            st.error(f"❌ {e}")
            st.session_state.wizard_df_limpio = None

    cols = st.columns([1, 1, 4])
    with cols[0]:
        if st.button("← Atrás", key="wiz_p2_back"):
            st.session_state.wizard_step = 1
            st.rerun()
    with cols[1]:
        if st.button("Continuar →", key="wiz_p2_next"):
            if st.session_state.wizard_df_limpio is None:
                st.error("Sube un archivo válido para continuar.")
            else:
                st.session_state.wizard_step = 3
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ── Paso 3: Markups ────────────────────────────────────────
def wizard_paso3():
    st.markdown('<div class="wizard-step-content">', unsafe_allow_html=True)
    empresa_id = st.session_state.wizard_empresa_id
    empresa    = st.session_state.wizard_empresa_nombre
    st.markdown(f"#### Markups por canal · *{empresa}*")
    st.markdown('<p style="color:#7a8fa6;font-size:0.9rem;margin-top:-0.5rem;">Introduce el porcentaje de markup para cada canal. Deja en 0 si no aplica.</p>', unsafe_allow_html=True)

    # Cargar valores existentes si los hay
    markups_actuales = obtener_markups_empresa(empresa_id)

    c1, c2, c3 = st.columns(3)
    with c1:
        airbnb_txt = st.text_input("Markup Airbnb (%)",  value=fmt_markup(markups_actuales["Airbnb"]),  placeholder="0", key="wiz_m_airbnb")
    with c2:
        booking_txt = st.text_input("Markup Booking (%)", value=fmt_markup(markups_actuales["Booking"]), placeholder="0", key="wiz_m_booking")
    with c3:
        web_txt = st.text_input("Markup Web (%)",     value=fmt_markup(markups_actuales["Web"]),    placeholder="0", key="wiz_m_web")

    cols = st.columns([1, 1, 4])
    with cols[0]:
        if st.button("← Atrás", key="wiz_p3_back"):
            st.session_state.wizard_step = 2
            st.rerun()
    with cols[1]:
        if st.button("Continuar →", key="wiz_p3_next"):
            try:
                airbnb  = parse_float_input(airbnb_txt  or "0", "Markup Airbnb")
                booking = parse_float_input(booking_txt or "0", "Markup Booking")
                web     = parse_float_input(web_txt     or "0", "Markup Web")
                # Guardar temporalmente en session_state
                st.session_state["wiz_markups"] = {"Airbnb": airbnb, "Booking": booking, "Web": web}
                st.session_state.wizard_step = 4
                st.rerun()
            except ValueError as e:
                st.error(f"❌ {e}")

    st.markdown('</div>', unsafe_allow_html=True)


# ── Paso 4: Descuentos + Guardar ──────────────────────────
def wizard_paso4():
    st.markdown('<div class="wizard-step-content">', unsafe_allow_html=True)
    empresa_id = st.session_state.wizard_empresa_id
    empresa    = st.session_state.wizard_empresa_nombre
    st.markdown(f"#### Descuentos por noches · *{empresa}*")
    st.markdown('<p style="color:#7a8fa6;font-size:0.9rem;margin-top:-0.5rem;">Define rangos de noches y el descuento aplicado. Puedes dejarlo vacío si no usas descuentos.</p>', unsafe_allow_html=True)

    descuentos_df = obtener_descuentos_empresa(empresa_id)
    descuentos_editados = st.data_editor(
        descuentos_df,
        num_rows="dynamic",
        use_container_width=True,
        key=f"wiz_desc_{empresa_id}",
        column_config={
            "Desde":         st.column_config.NumberColumn("Desde (noches)", min_value=1),
            "Hasta":         st.column_config.NumberColumn("Hasta (noches)", min_value=1),
            "Descuento (%)": st.column_config.NumberColumn("Descuento (%)",  min_value=0, max_value=100),
        }
    )

    st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)

    # Resumen antes de guardar
    markups = st.session_state.get("wiz_markups", {})
    df_prev = st.session_state.wizard_df_limpio

    with st.expander("📋 Resumen antes de guardar", expanded=True):
        c1, c2, c3 = st.columns(3)
        c1.metric("Empresa",      empresa)
        c2.metric("Alojamientos", len(df_prev) if df_prev is not None else 0)
        c3.metric("Markups",      f"A:{markups.get('Airbnb',0)}% · B:{markups.get('Booking',0)}% · W:{markups.get('Web',0)}%")

    cols = st.columns([1, 1, 4])
    with cols[0]:
        if st.button("← Atrás", key="wiz_p4_back"):
            st.session_state.wizard_step = 3
            st.rerun()
    with cols[1]:
        if st.button("✅ Guardar todo", key="wiz_p4_save", type="primary"):
            try:
                # 1. Crear / actualizar empresa en config
                config = cargar_config()
                if empresa_id not in config:
                    config[empresa_id] = default_empresa_config(empresa, f"{empresa_id}.csv")
                else:
                    config[empresa_id]["nombre"]      = empresa
                    config[empresa_id]["archivo_csv"] = f"{empresa_id}.csv"
                guardar_config(config)

                # 2. Guardar CSV
                ruta_csv = DATA_DIR / f"{empresa_id}.csv"
                df_prev.to_csv(ruta_csv, index=False, encoding="utf-8")

                # 3. Guardar markups
                m = markups
                guardar_markups_empresa(empresa_id, m["Airbnb"], m["Booking"], m["Web"])

                # 4. Guardar descuentos
                guardar_descuentos_empresa(empresa_id, descuentos_editados)

                invalidar_config()

                st.success(f"🎉 **{empresa}** guardada correctamente con {len(df_prev)} alojamientos.")
                st.balloons()

                # Reset wizard
                st.session_state.wizard_step           = 1
                st.session_state.wizard_empresa_nombre = ""
                st.session_state.wizard_empresa_id     = ""
                st.session_state.wizard_df_limpio      = None
                st.session_state.pop("wiz_markups", None)

            except Exception as e:
                st.error(f"❌ Error al guardar: {e}")

    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# WIZARD — SECCIÓN EDITAR
# =========================================================
def wizard_editar():
    st.markdown("#### Editar empresa existente")
    st.markdown('<p style="color:#7a8fa6;font-size:0.9rem;margin-top:-0.5rem;">Selecciona la empresa y modifica lo que necesites. Cada bloque se guarda por separado.</p>', unsafe_allow_html=True)

    empresas = obtener_empresas()
    if not empresas:
        st.info("No hay empresas registradas todavía. Usa la pestaña 'Nueva empresa' para crear una.")
        return

    opciones = {nombre: eid for eid, nombre in empresas}
    empresa_sel = st.selectbox("Empresa", list(opciones.keys()), key="edit_empresa_sel")
    empresa_id  = opciones[empresa_sel]

    st.markdown("---")

    # ── Bloque 1: Archivo ────────────────────────────────
    with st.expander("📁 Reemplazar archivo de alojamientos", expanded=False):
        archivo = st.file_uploader("Nuevo archivo CSV o Excel", type=["csv","xlsx"], key=f"edit_archivo_{empresa_id}")
        if archivo:
            try:
                df_nuevo = normalizar_df_alojamientos(leer_archivo_datos(archivo))
                st.success(f"✅ {len(df_nuevo)} alojamientos detectados")
                with st.expander("Vista previa", expanded=False):
                    st.dataframe(df_nuevo, use_container_width=True, hide_index=True)
                if st.button("Guardar archivo", key=f"edit_save_archivo_{empresa_id}"):
                    ruta = DATA_DIR / f"{empresa_id}.csv"
                    df_nuevo.to_csv(ruta, index=False, encoding="utf-8")
                    invalidar_config()
                    st.success("✅ Archivo actualizado.")
            except Exception as e:
                st.error(f"❌ {e}")

    # ── Bloque 2: Markups ────────────────────────────────
    with st.expander("⚙️ Markups por canal", expanded=False):
        m = obtener_markups_empresa(empresa_id)
        c1, c2, c3 = st.columns(3)
        with c1:
            a_txt = st.text_input("Airbnb (%)",  value=fmt_markup(m["Airbnb"]),  key=f"edit_airbnb_{empresa_id}")
        with c2:
            b_txt = st.text_input("Booking (%)", value=fmt_markup(m["Booking"]), key=f"edit_booking_{empresa_id}")
        with c3:
            w_txt = st.text_input("Web (%)",     value=fmt_markup(m["Web"]),     key=f"edit_web_{empresa_id}")
        if st.button("Guardar markups", key=f"edit_save_markups_{empresa_id}"):
            try:
                guardar_markups_empresa(
                    empresa_id,
                    parse_float_input(a_txt or "0", "Airbnb"),
                    parse_float_input(b_txt or "0", "Booking"),
                    parse_float_input(w_txt or "0", "Web"),
                )
                st.success("✅ Markups guardados.")
            except ValueError as e:
                st.error(f"❌ {e}")

    # ── Bloque 3: Descuentos ─────────────────────────────
    with st.expander("📊 Descuentos por noches", expanded=False):
        df_desc = obtener_descuentos_empresa(empresa_id)
        df_editado = st.data_editor(
            df_desc,
            num_rows="dynamic",
            use_container_width=True,
            key=f"edit_desc_{empresa_id}",
            column_config={
                "Desde":         st.column_config.NumberColumn("Desde (noches)", min_value=1),
                "Hasta":         st.column_config.NumberColumn("Hasta (noches)", min_value=1),
                "Descuento (%)": st.column_config.NumberColumn("Descuento (%)",  min_value=0, max_value=100),
            }
        )
        if st.button("Guardar descuentos", key=f"edit_save_desc_{empresa_id}"):
            guardar_descuentos_empresa(empresa_id, df_editado)
            st.success("✅ Descuentos guardados.")


# =========================================================
# SECCIÓN: WIZARD COMPLETO
# =========================================================
def section_wizard():
    st.markdown(
        '<div class="dashboard-card">'
        '<div class="section-title">🧙 Wizard</div>'
        '<div class="section-subtitle">Alta y edición de empresas en un flujo guiado</div>',
        unsafe_allow_html=True
    )

    # Tabs Nuevo / Editar con HTML + botones ocultos
    modo = st.session_state.wizard_mode
    tab_nuevo  = "active" if modo == "nuevo"  else ""
    tab_editar = "active" if modo == "editar" else ""

    st.markdown(f"""
    <div class="wizard-mode-tabs">
        <div class="wizard-mode-tab {tab_nuevo}"  id="wiz-tab-nuevo">✨ Nueva empresa</div>
        <div class="wizard-mode-tab {tab_editar}" id="wiz-tab-editar">✏️ Editar empresa</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="display:none!important;visibility:hidden;height:0;overflow:hidden;position:absolute;">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("tab_nuevo", key="wiz_tab_nuevo_btn"):
            st.session_state.wizard_mode = "nuevo"
            st.session_state.wizard_step = 1
            st.rerun()
    with c2:
        if st.button("tab_editar", key="wiz_tab_editar_btn"):
            st.session_state.wizard_mode = "editar"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <script>
    (function() {
        function wireTabs() {
            const map = { 'wiz-tab-nuevo': 'tab_nuevo', 'wiz-tab-editar': 'tab_editar' };
            Object.entries(map).forEach(([id, label]) => {
                const el = document.getElementById(id);
                if (!el || el._wired) return;
                el._wired = true;
                el.addEventListener('click', () => {
                    const btns = window.parent.document.querySelectorAll('button');
                    for (const btn of btns) {
                        if (btn.innerText.trim() === label) { btn.click(); break; }
                    }
                });
            });
        }
        let n = 0;
        const t = setInterval(() => { wireTabs(); if (++n > 20) clearInterval(t); }, 200);
    })();
    </script>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:0.3rem"></div>', unsafe_allow_html=True)

    # Contenido según modo
    if modo == "nuevo":
        render_stepper(st.session_state.wizard_step)
        paso = st.session_state.wizard_step
        if paso == 1:
            wizard_paso1()
        elif paso == 2:
            wizard_paso2()
        elif paso == 3:
            wizard_paso3()
        elif paso == 4:
            wizard_paso4()
    else:
        wizard_editar()

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# SECCIÓN: GUESTOOL
# =========================================================
def section_guestool():
    sub = st.session_state.guestool_sub

    if sub is None:
        # Sub-nav con 2 tarjetas
        st.markdown(
            '<div class="dashboard-card">'
            '<div class="section-title">⚡ Guestool</div>'
            '<div class="section-subtitle">Herramientas de precio · elige una opción</div>',
            unsafe_allow_html=True
        )

        st.markdown("""
        <div class="subnav-grid">
            <div class="subnav-card" id="sub-sim">
                <div class="subnav-card-icon">📊</div>
                <div class="subnav-card-title">Simuleitor</div>
                <div class="subnav-card-desc">Comparativa de precio por canal</div>
            </div>
            <div class="subnav-card" id="sub-calc">
                <div class="subnav-card-icon">🧠</div>
                <div class="subnav-card-title">Calculeitor</div>
                <div class="subnav-card-desc">Precio objetivo a cargar en RMS</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="display:none!important;visibility:hidden;height:0;overflow:hidden;position:absolute;">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("sub_sim", key="sub_sim_btn"):
                st.session_state.guestool_sub = "Simuleitor"
                st.rerun()
        with c2:
            if st.button("sub_calc", key="sub_calc_btn"):
                st.session_state.guestool_sub = "Calculeitor"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <script>
        (function() {
            function wire() {
                const map = { 'sub-sim': 'sub_sim', 'sub-calc': 'sub_calc' };
                Object.entries(map).forEach(([id, label]) => {
                    const el = document.getElementById(id);
                    if (!el || el._wired) return;
                    el._wired = true;
                    el.addEventListener('click', () => {
                        const btns = window.parent.document.querySelectorAll('button');
                        for (const btn of btns) {
                            if (btn.innerText.trim() === label) { btn.click(); break; }
                        }
                    });
                });
            }
            let n = 0;
            const t = setInterval(() => { wire(); if (++n > 20) clearInterval(t); }, 200);
        })();
        </script>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    elif sub == "Simuleitor":
        # Botón volver a Guestool
        if st.button("← Guestool", key="back_to_guestool_sim"):
            st.session_state.guestool_sub = None
            st.rerun()
        section_simuleitor()

    elif sub == "Calculeitor":
        if st.button("← Guestool", key="back_to_guestool_calc"):
            st.session_state.guestool_sub = None
            st.rerun()
        section_calculeitor()


# =========================================================
# SIMULEITOR
# =========================================================
def section_simuleitor():
    st.markdown(
        '<div class="dashboard-card">'
        '<div class="section-title">📊 Simuleitor</div>'
        '<div class="section-subtitle">Compara los tres canales usando el apartamento seleccionado.</div>',
        unsafe_allow_html=True
    )

    empresas = obtener_empresas()
    if not empresas:
        st.info("No hay empresas todavía. Crea una desde el Wizard.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    opciones = {nombre: eid for eid, nombre in empresas}
    empresa_sel = st.selectbox("Empresa", list(opciones.keys()), key="sim_empresa")
    empresa_id  = opciones[empresa_sel]

    datos = obtener_apartamentos(empresa_id)
    if not datos:
        st.info("Esta empresa no tiene alojamientos.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    apartamentos = {nombre: float(limpieza) for nombre, limpieza in datos}
    apt      = st.selectbox("Apartamento", list(apartamentos.keys()), key="sim_apartamento")
    limpieza = apartamentos[apt]

    c1, c2 = st.columns(2)
    with c1:
        precio_txt = st.text_input("Precio medio", "0", key="sim_precio")
    with c2:
        noches_txt = st.text_input("Noches", "2", key="sim_noches")

    c3, c4 = st.columns(2)
    with c3:
        st.text_input("Limpieza (€)", value=f"{limpieza:.2f}", disabled=True, key=f"sim_limp_{apt}")
    with c4:
        promo = st.selectbox("Promo Booking", ["Sin promo", "Genius 2 (23.5%)", "Genius 3 (27.75%)"], key="sim_promo")

    promo_val = 0.0
    if "23.5"  in promo: promo_val = 23.5
    if "27.75" in promo: promo_val = 27.75

    if st.button("Calcular", key="sim_calc_btn"):
        try:
            precio  = parse_float_input(precio_txt, "Precio medio", minimo=0)
            noches  = parse_int_input(noches_txt, "Noches", minimo=1)
            descuento = obtener_descuento_para_noches(empresa_id, noches)

            if descuento is None:
                st.error("No hay descuento configurado para ese número de noches.")
            else:
                markups   = obtener_markups_empresa(empresa_id)
                resultados = {}
                for canal in ["Airbnb", "Booking", "Web"]:
                    pc = precio * (1 + markups[canal] / 100)
                    if canal == "Booking":
                        pc *= (1 - promo_val / 100)
                    pf    = pc * (1 - descuento / 100) + limpieza / noches
                    total = pf * noches
                    resultados[canal] = {"noche": pf, "total": total}

                mejor = min(r["total"] for r in resultados.values())
                st.write("### Resultado")
                cols = st.columns(3)
                for i, (col, canal) in enumerate(zip(cols, ["Airbnb","Booking","Web"])):
                    data = resultados[canal]
                    css  = "kpi-card" + (" kpi-good" if data["total"] == mejor else "")
                    with col:
                        st.markdown(f"""
                        <div class="{css}" style="animation-delay:{i*0.1}s">
                            <div class="kpi-title">{canal}</div>
                            <div class="kpi-sub">precio por noche</div>
                            <div class="kpi-value">{data["noche"]:.2f} <span style="font-size:0.85rem;color:#9aafbf">€</span></div>
                            <div class="kpi-sub" style="margin-top:14px">total estancia</div>
                            <div class="kpi-total">{data["total"]:,.2f}<span class="kpi-currency">€</span></div>
                        </div>""", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# CALCULEITOR
# =========================================================
def section_calculeitor():
    st.markdown(
        '<div class="dashboard-card">'
        '<div class="section-title">🧠 Calculeitor</div>'
        '<div class="section-subtitle">Calcula el precio único a cargar en RMS usando Airbnb.</div>',
        unsafe_allow_html=True
    )

    empresas = obtener_empresas()
    if not empresas:
        st.info("No hay empresas todavía. Crea una desde el Wizard.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    opciones = {nombre: eid for eid, nombre in empresas}
    empresa_sel = st.selectbox("Empresa", list(opciones.keys()), key="calc_empresa")
    empresa_id  = opciones[empresa_sel]

    datos = obtener_apartamentos(empresa_id)
    if not datos:
        st.info("Esta empresa no tiene alojamientos.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    apartamentos = {nombre: float(limpieza) for nombre, limpieza in datos}
    apt      = st.selectbox("Apartamento", list(apartamentos.keys()), key="calc_apt")
    limpieza = apartamentos[apt]

    c1, c2 = st.columns(2)
    with c1:
        adr_txt  = st.text_input("ADR año pasado (€)", "0", key="calc_adr")
        noch_txt = st.text_input("Noches", "2", key="calc_noches")
    with c2:
        inc_txt = st.text_input("% incremento esperado", "0", key="calc_inc")

    st.text_input("Limpieza (€)", value=f"{limpieza:.2f}", disabled=True, key=f"calc_limp_{apt}")

    if st.button("Calcular precio objetivo (RMS)", key="calc_btn"):
        try:
            adr      = parse_float_input(adr_txt,  "ADR año pasado", minimo=0)
            noches   = parse_int_input(noch_txt, "Noches", minimo=1)
            inc      = parse_float_input(inc_txt,  "Incremento")
            descuento = obtener_descuento_para_noches(empresa_id, noches)

            if descuento is None:
                st.error("No hay descuento configurado para ese número de noches.")
            else:
                markups = obtener_markups_empresa(empresa_id)
                adr_obj = adr * (1 + inc / 100)
                fm      = 1 + markups["Airbnb"] / 100
                fd      = 1 - descuento / 100
                limp_n  = limpieza / noches

                if fm * fd == 0:
                    st.error("La configuración produce una división por cero.")
                else:
                    precio_rms = (adr_obj - limp_n) / (fm * fd)
                    st.write("### Precio a cargar en RMS")
                    st.markdown(f"""
                    <div class="single-rms">
                        <div class="kpi-card kpi-good">
                            <div class="kpi-title">Precio único RMS</div>
                            <div class="kpi-total">{precio_rms:,.2f}<span class="kpi-currency">€</span></div>
                        </div>
                    </div>""", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# RENDER PRINCIPAL
# =========================================================
render_nav()

section = st.session_state.active_section

if section is None:
    pass  # Solo se ve el nav
elif section == "Wizard":
    render_back()
    section_wizard()
elif section == "Guestool":
    render_back()
    section_guestool()
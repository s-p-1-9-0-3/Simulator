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

/* ── RESET & BASE ─────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[class*="css"],
[data-testid="stAppViewContainer"],
[data-testid="stMarkdownContainer"] {
    font-family: 'DM Sans', sans-serif !important;
}

/* ── FONDO ────────────────────────────────────────────── */
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 10% -10%, rgba(78,193,181,0.13) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 90% 110%, rgba(99,102,241,0.07) 0%, transparent 55%),
        linear-gradient(165deg, #f0f4f8 0%, #f8fbfb 50%, #f2f6f5 100%);
    min-height: 100vh;
}

/* ruido sutil encima del fondo */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
}

/* ── LAYOUT ───────────────────────────────────────────── */
.block-container {
    max-width: 1200px;
    padding-top: 3.5rem;
    padding-bottom: 3rem;
    position: relative;
    z-index: 1;
}

/* ── ANIMACIONES GLOBALES ─────────────────────────────── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}

@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.95); }
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

/* ── HEADER ───────────────────────────────────────────── */
.header-wrap {
    animation: fadeUp 0.6s cubic-bezier(0.22,1,0.36,1) both;
    margin-bottom: 0.2rem;
}

.header-logo-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 88px;
}

.header-text-wrap {
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 88px;
}

.top-eyebrow {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #4ec1b5;
    margin: 0 0 0.45rem 0;
}

.top-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.55rem;
    font-weight: 800;
    line-height: 1.0;
    margin: 0;
    color: #0f1f38;
    letter-spacing: -0.03em;
}

/* gradiente animado en la última palabra */
.top-title span {
    background: linear-gradient(
        90deg,
        #4ec1b5 0%,
        #6366f1 35%,
        #4ec1b5 65%,
        #22d3c8 100%
    );
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 4s linear infinite;
}

.top-subtitle {
    font-size: 0.95rem;
    font-weight: 300;
    color: #7a8fa6;
    margin: 0.6rem 0 0 0;
    letter-spacing: 0.01em;
}

/* ── DIVISOR ──────────────────────────────────────────── */
.cards-divider {
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(15,23,42,0.10) 20%, rgba(15,23,42,0.10) 80%, transparent);
    margin: 28px 0 10px 0;
    border-radius: 999px;
    animation: fadeIn 0.8s 0.5s both;
}

/* ── NAV GRID (HTML puro, tamaño perfectamente uniforme) ── */
.nav-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    width: 100%;
    margin-bottom: 4px;
}

.nav-card {
    height: 160px;
    border-radius: 24px;
    border: 1px solid rgba(15,23,42,0.10);
    background: linear-gradient(145deg, rgba(255,255,255,0.97) 0%, rgba(248,252,252,0.92) 100%);
    box-shadow:
        0 1px 0 rgba(255,255,255,0.9) inset,
        0 8px 24px rgba(15,23,42,0.06),
        0 2px 6px rgba(15,23,42,0.04);
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 20px 14px;
    position: relative;
    overflow: hidden;
    transition:
        transform 0.22s cubic-bezier(0.34,1.56,0.64,1),
        box-shadow 0.22s ease,
        border-color 0.22s ease,
        background 0.22s ease;
    user-select: none;
    -webkit-user-select: none;
}

.nav-card:nth-child(1) { animation: fadeUp 0.55s 0.10s cubic-bezier(0.22,1,0.36,1) both; }
.nav-card:nth-child(2) { animation: fadeUp 0.55s 0.18s cubic-bezier(0.22,1,0.36,1) both; }
.nav-card:nth-child(3) { animation: fadeUp 0.55s 0.26s cubic-bezier(0.22,1,0.36,1) both; }
.nav-card:nth-child(4) { animation: fadeUp 0.55s 0.34s cubic-bezier(0.22,1,0.36,1) both; }

.nav-card::after {
    content: '';
    position: absolute;
    top: -50%; left: -75%;
    width: 50%; height: 200%;
    background: linear-gradient(105deg, transparent, rgba(255,255,255,0.50), transparent);
    transform: skewX(-20deg);
    transition: left 0.55s ease;
    pointer-events: none;
}

.nav-card:hover::after { left: 130%; }

.nav-card:hover {
    transform: translateY(-6px) scale(1.015);
    border-color: rgba(78,193,181,0.55);
    box-shadow:
        0 1px 0 rgba(255,255,255,0.9) inset,
        0 20px 40px rgba(78,193,181,0.16),
        0 8px 20px rgba(15,23,42,0.08);
    background: linear-gradient(145deg, rgba(255,255,255,0.99) 0%, rgba(78,193,181,0.09) 100%);
}

.nav-card:active {
    transform: translateY(-2px) scale(1.005);
    transition-duration: 0.08s;
}

.nav-card-icon {
    font-size: 1.75rem;
    line-height: 1;
    margin-bottom: 2px;
}

.nav-card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.97rem;
    font-weight: 700;
    color: #172033;
    text-align: center;
    letter-spacing: -0.01em;
}

.nav-card-desc {
    font-size: 0.80rem;
    font-weight: 400;
    color: #7a8fa6;
    text-align: center;
    line-height: 1.35;
    max-width: 90%;
}

/* oculta los botones Streamlit del nav (solo sirven de trigger) */
.hidden-nav-btns {
    display: none !important;
}

/* ── DASHBOARD CARD ───────────────────────────────────── */
.dashboard-card {
    border: 1px solid rgba(15,23,42,0.09);
    border-radius: 28px;
    padding: 28px 28px 20px 28px;
    background:
        linear-gradient(145deg,
            rgba(255,255,255,0.97) 0%,
            rgba(248,252,251,0.93) 100%
        );
    box-shadow:
        0 1px 0 rgba(255,255,255,0.9) inset,
        0 8px 32px rgba(15,23,42,0.07),
        0 2px 8px rgba(15,23,42,0.04);
    margin-bottom: 1.2rem;
    animation: scaleIn 0.45s cubic-bezier(0.22,1,0.36,1) both;
    position: relative;
    overflow: hidden;
}

/* acento de color arriba a la izquierda */
.dashboard-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 3px;
    background: linear-gradient(90deg, #4ec1b5, #6366f1 60%, transparent);
    border-radius: 28px 28px 0 0;
    opacity: 0.7;
}

.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
    color: #0f1f38;
    letter-spacing: -0.02em;
}

.section-subtitle {
    font-size: 0.9rem;
    font-weight: 300;
    color: #7a8fa6;
    margin-bottom: 1.2rem;
}

/* ── KPI CARDS ────────────────────────────────────────── */
.kpi-card {
    border: 1px solid rgba(15,23,42,0.09);
    border-radius: 20px;
    padding: 20px 18px 18px;
    background: rgba(248,250,252,0.80);
    min-height: 160px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    animation: fadeUp 0.5s cubic-bezier(0.22,1,0.36,1) both;
}

.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 28px rgba(15,23,42,0.09);
}

.kpi-good {
    border: 1.5px solid rgba(78,193,181,0.55) !important;
    background: linear-gradient(145deg, rgba(78,193,181,0.08), rgba(78,193,181,0.04)) !important;
    animation: pulse-border 2.5s ease-in-out infinite;
}

.kpi-good:hover {
    box-shadow: 0 12px 28px rgba(78,193,181,0.18) !important;
}

.kpi-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    color: #7a8fa6;
    margin-bottom: 0.3rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.kpi-sub {
    font-size: 0.82rem;
    font-weight: 300;
    color: #9aafbf;
    margin-top: 0.4rem;
}

.kpi-value {
    font-size: 1.1rem;
    font-weight: 600;
    line-height: 1.2;
    color: #1a2e45;
}

.kpi-total {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.8rem;
    font-weight: 600;
    line-height: 1.1;
    margin-top: 0.35rem;
    color: #0f1f38;
    letter-spacing: -0.01em;
}

.kpi-currency {
    font-size: 1.05rem;
    font-weight: 400;
    color: #7a8fa6;
    margin-left: 4px;
    vertical-align: middle;
    letter-spacing: 0;
}

/* ── SINGLE RMS ───────────────────────────────────────── */
.single-rms {
    max-width: 440px;
    margin: 0 auto;
}

.single-rms .kpi-card {
    text-align: center;
    padding: 32px 24px;
}

.single-rms .kpi-total {
    font-size: 3rem;
    background: linear-gradient(135deg, #0f1f38, #4ec1b5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ── INPUTS & WIDGETS ─────────────────────────────────── */
div[data-testid="stTextInput"] input {
    border-radius: 14px !important;
    border: 1px solid rgba(15,23,42,0.13) !important;
    background: rgba(255,255,255,0.85) !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: rgba(78,193,181,0.70) !important;
    box-shadow: 0 0 0 3px rgba(78,193,181,0.14) !important;
}

div[data-testid="stSelectbox"] > div {
    border-radius: 14px !important;
}

div[data-testid="stFileUploader"] section {
    border-radius: 18px !important;
    border: 1.5px dashed rgba(78,193,181,0.45) !important;
    background: rgba(78,193,181,0.03) !important;
    transition: border-color 0.2s, background 0.2s !important;
}

div[data-testid="stFileUploader"] section:hover {
    border-color: rgba(78,193,181,0.75) !important;
    background: rgba(78,193,181,0.06) !important;
}

div[data-testid="stDataEditor"] {
    border-radius: 16px !important;
}

/* ── BOTONES PRINCIPALES ──────────────────────────────── */
div[data-testid="stButton"]:not(.nav-card-wrap div[data-testid="stButton"]) > button {
    border-radius: 14px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease !important;
}

div[data-testid="stButton"]:not(.nav-card-wrap div[data-testid="stButton"]) > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 18px rgba(78,193,181,0.22) !important;
}

div[data-testid="stButton"]:not(.nav-card-wrap div[data-testid="stButton"]) > button:active {
    transform: translateY(0px) !important;
}

/* ── SUCCESS / ERROR / WARNING / INFO ─────────────────── */
div[data-testid="stAlert"] {
    border-radius: 16px !important;
    font-family: 'DM Sans', sans-serif !important;
    animation: fadeUp 0.35s cubic-bezier(0.22,1,0.36,1) both;
}

/* ── CHECKBOX ─────────────────────────────────────────── */
div[data-testid="stCheckbox"] label {
    font-family: 'DM Sans', sans-serif !important;
}

/* ── SUBHEADER ────────────────────────────────────────── */
h3 {
    font-family: 'Syne', sans-serif !important;
    letter-spacing: -0.02em !important;
    color: #0f1f38 !important;
}

/* ── SIDEBAR OCULTA ───────────────────────────────────── */
[data-testid="collapsedControl"] { display: none; }

/* ── RESPONSIVE ───────────────────────────────────────── */
@media (max-width: 1100px) {
    .nav-grid { gap: 10px; }
    .nav-card { height: 150px; border-radius: 20px; }
    .nav-card-title { font-size: 0.90rem; }
    .nav-card-desc { font-size: 0.76rem; }
    .top-title { font-size: 2.2rem; }
}

@media (max-width: 768px) {
    .block-container { padding-top: 2rem; }
    .top-title { font-size: 1.85rem; }
    .top-subtitle { font-size: 0.9rem; }
    .nav-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
    .nav-card { height: 140px; border-radius: 18px; }
    .nav-card-title { font-size: 0.87rem; }
    .nav-card-desc { font-size: 0.74rem; }
    .dashboard-card { padding: 20px 16px 16px; border-radius: 22px; }
    .kpi-total { font-size: 1.5rem; }
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# ESTADO UI
# =========================================================
if "active_section" not in st.session_state:
    st.session_state.active_section = None

if "upload_unlocked" not in st.session_state:
    st.session_state.upload_unlocked = False

if "config_unlocked" not in st.session_state:
    st.session_state.config_unlocked = False


# =========================================================
# STORAGE (CSV + JSON)
# =========================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "datos"
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
        "nombre": nombre_empresa,
        "archivo_csv": archivo_csv,
        "markups": {
            "Airbnb": 0.0,
            "Booking": 0.0,
            "Web": 0.0,
        },
        "descuentos": [],
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
            if not config[empresa_id].get("archivo_csv"):
                config[empresa_id]["archivo_csv"] = ruta.name
                changed = True
            if not config[empresa_id].get("nombre"):
                config[empresa_id]["nombre"] = pretty_name_from_slug(ruta.stem)
                changed = True
            if "markups" not in config[empresa_id]:
                config[empresa_id]["markups"] = default_empresa_config("", "")["markups"]
                changed = True
            if "descuentos" not in config[empresa_id]:
                config[empresa_id]["descuentos"] = default_empresa_config("", "")["descuentos"]
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
    """Llama esto después de cualquier operación que cambie el JSON o los CSVs."""
    cargar_config.clear()


def asegurar_empresa(nombre_empresa: str) -> str:
    empresa_id = slugify(nombre_empresa)
    config = cargar_config()

    if empresa_id not in config:
        config[empresa_id] = default_empresa_config(
            nombre_empresa=nombre_empresa.strip(),
            archivo_csv=f"{empresa_id}.csv",
        )
        guardar_config(config)

    return empresa_id


def ruta_csv_empresa(empresa_id: str) -> Path:
    config = cargar_config()
    archivo = config.get(empresa_id, {}).get("archivo_csv", f"{empresa_id}.csv")
    return DATA_DIR / archivo


# =========================================================
# HELPERS
# =========================================================
def parse_int_input(valor: str, nombre: str, minimo: Optional[int] = None, maximo: Optional[int] = None) -> int:
    texto = str(valor).strip().replace(",", ".")
    if texto == "":
        raise ValueError(f"El campo '{nombre}' no puede estar vacío")

    numero = float(texto)
    if not numero.is_integer():
        raise ValueError(f"El campo '{nombre}' debe ser un número entero")

    numero = int(numero)

    if minimo is not None and numero < minimo:
        raise ValueError(f"El campo '{nombre}' debe ser mayor o igual a {minimo}")
    if maximo is not None and numero > maximo:
        raise ValueError(f"El campo '{nombre}' debe ser menor o igual a {maximo}")

    return numero


def parse_float_input(valor: str, nombre: str, minimo: Optional[float] = None, maximo: Optional[float] = None) -> float:
    texto = str(valor).strip().replace(",", ".")
    if texto == "":
        raise ValueError(f"El campo '{nombre}' no puede estar vacío")

    numero = float(texto)

    if minimo is not None and numero < minimo:
        raise ValueError(f"El campo '{nombre}' debe ser mayor o igual a {minimo}")
    if maximo is not None and numero > maximo:
        raise ValueError(f"El campo '{nombre}' debe ser menor o igual a {maximo}")

    return numero


def contar_alojamientos(empresa_id: str) -> int:
    ruta = ruta_csv_empresa(empresa_id)
    if not ruta.exists():
        return 0

    try:
        df = pd.read_csv(ruta)
        return len(df)
    except Exception:
        return 0


def obtener_empresas():
    config = cargar_config()
    empresas = []
    for empresa_id, data in config.items():
        # Solo incluir si tiene CSV con al menos una fila
        ruta = DATA_DIR / data.get("archivo_csv", f"{empresa_id}.csv")
        if ruta.exists() and ruta.stat().st_size > 0:
            empresas.append((empresa_id, data.get("nombre", pretty_name_from_slug(empresa_id))))
    return sorted(empresas, key=lambda x: x[1].lower())


def obtener_markups_empresa(empresa_id: str):
    config = cargar_config()
    markups = config.get(empresa_id, {}).get("markups", {})
    return {
        "Airbnb": float(markups.get("Airbnb", 0.0) or 0.0),
        "Booking": float(markups.get("Booking", 0.0) or 0.0),
        "Web": float(markups.get("Web", 0.0) or 0.0),
    }


def guardar_markups_empresa(empresa_id: str, markup_airbnb: float, markup_booking: float, markup_web: float):
    config = cargar_config()
    if empresa_id not in config:
        config[empresa_id] = default_empresa_config(pretty_name_from_slug(empresa_id), f"{empresa_id}.csv")

    config[empresa_id]["markups"] = {
        "Airbnb": markup_airbnb,
        "Booking": markup_booking,
        "Web": markup_web,
    }
    guardar_config(config)


def obtener_descuentos_empresa(empresa_id: str) -> pd.DataFrame:
    config = cargar_config()
    descuentos = config.get(empresa_id, {}).get("descuentos", [])

    if descuentos:
        return pd.DataFrame(descuentos)

    return pd.DataFrame({"Desde": [], "Hasta": [], "Descuento (%)": []})


def guardar_descuentos_empresa(empresa_id: str, df_descuentos: pd.DataFrame):
    filas_limpias = []

    for _, fila in df_descuentos.iterrows():
        desde_raw = fila.get("Desde")
        hasta_raw = fila.get("Hasta")
        descuento_raw = fila.get("Descuento (%)")

        if pd.isna(desde_raw) or pd.isna(hasta_raw) or pd.isna(descuento_raw):
            continue

        try:
            desde = int(float(str(desde_raw).replace(",", ".")))
            hasta = int(float(str(hasta_raw).replace(",", ".")))
            descuento = float(str(descuento_raw).replace(",", "."))
        except Exception:
            continue

        if desde < 1 or hasta < desde:
            continue

        filas_limpias.append({
            "Desde": desde,
            "Hasta": hasta,
            "Descuento (%)": descuento,
        })

    config = cargar_config()
    if empresa_id not in config:
        config[empresa_id] = default_empresa_config(pretty_name_from_slug(empresa_id), f"{empresa_id}.csv")

    config[empresa_id]["descuentos"] = filas_limpias
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


def detectar_columnas(df: pd.DataFrame):
    col_nombre = None
    col_limpieza = None

    for col in df.columns:
        col_norm = str(col).strip().lower()

        if col_nombre is None and (
            "nombre" in col_norm or
            "aloj" in col_norm or
            "apart" in col_norm or
            "propiedad" in col_norm
        ):
            col_nombre = col

        if col_limpieza is None and (
            "limp" in col_norm or
            "clean" in col_norm or
            "coste" in col_norm
        ):
            col_limpieza = col

    return col_nombre, col_limpieza


def leer_archivo_datos(archivo):
    nombre = archivo.name.lower()

    if nombre.endswith(".xlsx"):
        archivo.seek(0)
        return pd.read_excel(archivo)

    if nombre.endswith(".csv"):
        for encoding in ["utf-8", "latin-1", "cp1252"]:
            try:
                archivo.seek(0)
                return pd.read_csv(
                    archivo,
                    encoding=encoding,
                    sep=None,
                    engine="python"
                )
            except Exception:
                continue

        raise Exception("No se pudo leer el CSV con ningún encoding compatible")

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
    salida["coste_limpieza"] = (
        salida["coste_limpieza"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .str.strip()
    )

    salida["coste_limpieza"] = pd.to_numeric(salida["coste_limpieza"], errors="coerce")
    salida = salida.dropna(subset=["nombre", "coste_limpieza"])
    salida = salida[salida["nombre"] != ""]
    salida = salida.drop_duplicates(subset=["nombre"]).sort_values("nombre")

    return salida.reset_index(drop=True)


def obtener_apartamentos(empresa_id: str):
    ruta = ruta_csv_empresa(empresa_id)
    if not ruta.exists():
        return []

    try:
        df = pd.read_csv(ruta)
    except Exception:
        return []

    if {"nombre", "coste_limpieza"}.issubset(set(df.columns)):
        normalizado = df.copy()
    else:
        try:
            normalizado = normalizar_df_alojamientos(df)
        except Exception:
            return []

    normalizado["coste_limpieza"] = pd.to_numeric(normalizado["coste_limpieza"], errors="coerce")
    normalizado = normalizado.dropna(subset=["nombre", "coste_limpieza"])

    return list(
        normalizado[["nombre", "coste_limpieza"]]
        .sort_values("nombre")
        .itertuples(index=False, name=None)
    )


# =========================================================
# NAV
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
    st.markdown('<div style="height: 1.4rem;"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="nav-grid">
        <div class="nav-card" id="nc-upload">
            <div class="nav-card-icon">📁</div>
            <div class="nav-card-title">Subir archivo</div>
            <div class="nav-card-desc">CSV o Excel con alojamientos</div>
        </div>
        <div class="nav-card" id="nc-config">
            <div class="nav-card-icon">⚙️</div>
            <div class="nav-card-title">Configuración</div>
            <div class="nav-card-desc">Markups y descuentos por canal</div>
        </div>
        <div class="nav-card" id="nc-sim">
            <div class="nav-card-icon">📊</div>
            <div class="nav-card-title">Simuleitor</div>
            <div class="nav-card-desc">Comparativa por canal</div>
        </div>
        <div class="nav-card" id="nc-calc">
            <div class="nav-card-icon">🧠</div>
            <div class="nav-card-title">Calculeitor</div>
            <div class="nav-card-desc">Precio objetivo RMS</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="hidden-nav-btns" style="display:none!important;visibility:hidden;height:0;overflow:hidden;position:absolute;">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4, gap="small")
    with c1:
        if st.button("Subir archivo", key="nav1", use_container_width=True):
            st.session_state.active_section = "Subir archivo"
            st.rerun()
    with c2:
        if st.button("Configuración", key="nav2", use_container_width=True):
            st.session_state.active_section = "Configuración"
            st.rerun()
    with c3:
        if st.button("Simuleitor", key="nav3", use_container_width=True):
            st.session_state.active_section = "Simuleitor"
            st.rerun()
    with c4:
        if st.button("Calculeitor", key="nav4", use_container_width=True):
            st.session_state.active_section = "Calculeitor"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <script>
    (function() {
        function wireCards() {
            const map = {
                'nc-upload':  'Subir archivo',
                'nc-config':  'Configuración',
                'nc-sim':     'Simuleitor',
                'nc-calc':    'Calculeitor'
            };
            Object.entries(map).forEach(([cardId, label]) => {
                const card = document.getElementById(cardId);
                if (!card || card._wired) return;
                card._wired = true;
                card.addEventListener('click', () => {
                    const doc = window.parent.document;
                    const btns = doc.querySelectorAll('button');
                    for (const btn of btns) {
                        if (btn.innerText.trim() === label) { btn.click(); break; }
                    }
                });
            });
        }
        let attempts = 0;
        const interval = setInterval(() => {
            wireCards();
            attempts++;
            if (attempts > 20) clearInterval(interval);
        }, 200);
    })();
    </script>
    """, unsafe_allow_html=True)

    st.markdown('<div class="cards-divider"></div>', unsafe_allow_html=True)


def pin_gate(section_name: str, state_key: str):
    st.markdown(
        f'<div class="dashboard-card"><div class="section-title">{section_name}</div>'
        f'<div class="section-subtitle">Sección protegida · introduce tu PIN para continuar</div>',
        unsafe_allow_html=True
    )

    if not st.session_state[state_key]:
        pin = st.text_input("PIN de acceso", type="password", key=f"pin_{state_key}")
        if st.button("Desbloquear →", key=f"unlock_{state_key}"):
            if pin == ADMIN_PIN:
                st.session_state[state_key] = True
                st.rerun()
            else:
                st.error("PIN incorrecto")
        st.markdown("</div>", unsafe_allow_html=True)
        return False

    st.success("✓ Sección desbloqueada")
    return True


# =========================================================
# SECCIÓN: SUBIR ARCHIVO
# =========================================================
def section_upload():
    allowed = pin_gate("📁 Subir archivo", "upload_unlocked")
    if not allowed:
        return

    st.subheader("Subida de datos")

    # Selector de empresa existente O nombre nuevo
    config_actual = cargar_config()
    empresas_existentes = sorted(
        [(eid, data.get("nombre", pretty_name_from_slug(eid))) for eid, data in config_actual.items()],
        key=lambda x: x[1].lower()
    )
    nombres_existentes = [nombre for _, nombre in empresas_existentes]

    modo = st.radio(
        "¿Es una empresa nueva o existente?",
        ["Empresa existente", "Nueva empresa"],
        horizontal=True,
        key="upload_modo"
    )

    empresa_nombre = None
    empresa_id_previo = None

    if modo == "Empresa existente":
        if not nombres_existentes:
            st.info("No hay empresas registradas todavía. Elige 'Nueva empresa'.")
        else:
            sel = st.selectbox("Selecciona empresa", nombres_existentes, key="upload_empresa_sel")
            empresa_nombre = sel
            # Recuperar el id real
            empresa_id_previo = next(eid for eid, nom in empresas_existentes if nom == sel)
    else:
        empresa_nombre = st.text_input("Nombre de la nueva empresa", key="upload_empresa_nueva").strip()
        if empresa_nombre:
            slug_nuevo = slugify(empresa_nombre)
            if slug_nuevo in config_actual:
                st.warning(
                    f"⚠️ Ya existe una empresa con un nombre similar "
                    f"({config_actual[slug_nuevo].get('nombre', slug_nuevo)}). "
                    "Se sobreescribirán sus datos si confirmas."
                )
                empresa_id_previo = slug_nuevo

    archivo = st.file_uploader("Sube tu archivo (CSV o Excel)", type=["csv", "xlsx"], key="upload_file")

    if archivo and empresa_nombre:
        try:
            df = leer_archivo_datos(archivo)
            df_limpio = normalizar_df_alojamientos(df)

            st.success(f"✅ Archivo válido · {len(df_limpio)} alojamientos detectados")

            with st.expander("Vista previa de los datos", expanded=False):
                st.dataframe(df_limpio, use_container_width=True, hide_index=True)

            # Calcular empresa_id definitivo
            empresa_id_final = empresa_id_previo if empresa_id_previo else slugify(empresa_nombre)
            total_actual = contar_alojamientos(empresa_id_final)

            if total_actual > 0:
                st.warning(
                    f"⚠️ Esta empresa ya tiene **{total_actual} alojamientos**. "
                    "Al confirmar se reemplazarán por los {len(df_limpio)} del nuevo archivo."
                )

            confirmar = st.checkbox(
                "Confirmo que quiero guardar / reemplazar los datos",
                key="upload_confirm"
            )

            if st.button("Guardar datos", key="upload_update_btn"):
                if not confirmar:
                    st.error("❌ Marca la casilla de confirmación antes de continuar")
                else:
                    # Crear o actualizar la empresa en config (sin duplicar)
                    config = cargar_config()
                    if empresa_id_final not in config:
                        config[empresa_id_final] = default_empresa_config(
                            nombre_empresa=empresa_nombre,
                            archivo_csv=f"{empresa_id_final}.csv",
                        )
                    else:
                        # Actualizar nombre por si ha cambiado ligeramente
                        config[empresa_id_final]["nombre"] = empresa_nombre
                        config[empresa_id_final]["archivo_csv"] = f"{empresa_id_final}.csv"

                    guardar_config(config)

                    # Guardar CSV (sobreescribe si ya existe)
                    ruta_destino = DATA_DIR / f"{empresa_id_final}.csv"
                    df_limpio.to_csv(ruta_destino, index=False, encoding="utf-8")
                    invalidar_config()

                    st.success(
                        f"✅ Datos guardados correctamente. "
                        f"**{len(df_limpio)} alojamientos** cargados para **{empresa_nombre}**."
                    )

        except ValueError as e:
            st.error(f"❌ Problema con el archivo: {e}")
        except Exception as e:
            st.error(f"❌ Error inesperado: {e}")

    elif archivo and not empresa_nombre:
        st.info("Introduce o selecciona el nombre de la empresa para continuar.")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# SECCIÓN: CONFIGURACIÓN
# =========================================================
def section_config():
    allowed = pin_gate("⚙️ Configuración", "config_unlocked")
    if not allowed:
        return

    empresas = obtener_empresas()
    if not empresas:
        st.info("No hay empresas todavía")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    opciones = {nombre: empresa_id for empresa_id, nombre in empresas}
    empresa_sel = st.selectbox("Empresa", list(opciones.keys()), key="config_empresa")
    empresa_id = opciones[empresa_sel]

    markups_actuales = obtener_markups_empresa(empresa_id)

    def fmt_markup(v: float) -> str:
        if v == 0.0:
            return "0"
        s = f"{v:.4f}".rstrip("0").rstrip(".")
        return s

    c1, c2, c3 = st.columns(3)
    with c1:
        markup_airbnb_txt = st.text_input(
            "Markup Airbnb (%)",
            value=fmt_markup(markups_actuales["Airbnb"]),
            key=f"cfg_markup_airbnb_{empresa_id}",
            placeholder="0"
        )
    with c2:
        markup_booking_txt = st.text_input(
            "Markup Booking (%)",
            value=fmt_markup(markups_actuales["Booking"]),
            key=f"cfg_markup_booking_{empresa_id}",
            placeholder="0"
        )
    with c3:
        markup_web_txt = st.text_input(
            "Markup Web (%)",
            value=fmt_markup(markups_actuales["Web"]),
            key=f"cfg_markup_web_{empresa_id}",
            placeholder="0"
        )

    st.write("### 📊 Descuentos por rango de noches")
    descuentos_df_actual = obtener_descuentos_empresa(empresa_id)

    descuentos_editados = st.data_editor(
        descuentos_df_actual,
        num_rows="dynamic",
        use_container_width=True,
        key=f"cfg_descuentos_editor_{empresa_id}"
    )

    if st.button("Guardar configuración", key="cfg_save_btn"):
        try:
            markup_airbnb = parse_float_input(markup_airbnb_txt, "Markup Airbnb (%)")
            markup_booking = parse_float_input(markup_booking_txt, "Markup Booking (%)")
            markup_web = parse_float_input(markup_web_txt, "Markup Web (%)")

            guardar_markups_empresa(empresa_id, markup_airbnb, markup_booking, markup_web)
            guardar_descuentos_empresa(empresa_id, descuentos_editados)
            st.success("✅ Configuración guardada")

        except ValueError as e:
            st.error(f"❌ {e}")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# SECCIÓN: SIMULEITOR
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
        st.info("No hay empresas todavía")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    opciones = {nombre: empresa_id for empresa_id, nombre in empresas}
    empresa_sel = st.selectbox("Empresa", list(opciones.keys()), key="sim_empresa")
    empresa_id = opciones[empresa_sel]

    datos = obtener_apartamentos(empresa_id)
    if not datos:
        st.info("No hay apartamentos")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    apartamentos = {nombre: float(limpieza) for nombre, limpieza in datos}
    apt = st.selectbox("Apartamento", list(apartamentos.keys()), key="sim_apartamento")
    limpieza = apartamentos[apt]

    c1, c2 = st.columns(2)
    with c1:
        precio_txt = st.text_input("Precio medio", "0", key="sim_precio")
    with c2:
        noches_txt = st.text_input("Noches", "2", key="sim_noches")

    c3, c4 = st.columns(2)
    with c3:
        st.text_input(
            "Limpieza (€)",
            value=f"{limpieza:.2f}",
            disabled=True,
            key=f"sim_limpieza_{apt}"
        )
    with c4:
        promo = st.selectbox(
            "Promo Booking",
            ["Sin promo", "Genius 2 (23.5%)", "Genius 3 (27.75%)"],
            key="sim_promo_booking"
        )

    promo_val = 0.0
    if "23.5" in promo:
        promo_val = 23.5
    elif "27.75" in promo:
        promo_val = 27.75

    if st.button("Calcular", key="sim_calc_btn"):
        try:
            precio = parse_float_input(precio_txt, "Precio medio", minimo=0)
            noches = parse_int_input(noches_txt, "Noches", minimo=1)

            descuento = obtener_descuento_para_noches(empresa_id, noches)
            if descuento is None:
                st.error("No hay descuento para esas noches")
            else:
                markups = obtener_markups_empresa(empresa_id)
                resultados = {}

                for canal in ["Airbnb", "Booking", "Web"]:
                    markup = markups[canal]
                    precio_canal = precio * (1 + markup / 100)

                    if canal == "Booking":
                        precio_canal *= (1 - promo_val / 100)

                    precio_desc = precio_canal * (1 - descuento / 100)
                    limpieza_noche = limpieza / noches
                    precio_final = precio_desc + limpieza_noche
                    total = precio_final * noches

                    resultados[canal] = {
                        "noche": precio_final,
                        "total": total
                    }

                mejor_total = min(r["total"] for r in resultados.values())

                st.write("### Resultado")

                cols = st.columns(3)
                for i, (col, canal) in enumerate(zip(cols, ["Airbnb", "Booking", "Web"])):
                    data = resultados[canal]
                    css = "kpi-card"
                    if data["total"] == mejor_total:
                        css += " kpi-good"

                    with col:
                        st.markdown(
                            f"""
                            <div class="{css}" style="animation-delay: {i * 0.1}s;">
                                <div class="kpi-title">{canal}</div>
                                <div class="kpi-sub">precio final por noche</div>
                                <div class="kpi-value">{data["noche"]:.2f} <span style="font-size:0.85rem;color:#9aafbf;font-weight:400;">€</span></div>
                                <div class="kpi-sub" style="margin-top:14px;">total estancia</div>
                                <div class="kpi-total">{data["total"]:,.2f}<span class="kpi-currency">€</span></div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

        except Exception as e:
            st.error(f"Error en Simuleitor: {e}")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# SECCIÓN: CALCULEITOR
# =========================================================
def section_calculeitor():
    st.markdown(
        '<div class="dashboard-card">'
        '<div class="section-title">🧠 Calculeitor</div>'
        '<div class="section-subtitle">Calcula un único precio a cargar en RMS usando Airbnb.</div>',
        unsafe_allow_html=True
    )

    empresas = obtener_empresas()
    if not empresas:
        st.info("No hay empresas todavía")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    opciones = {nombre: empresa_id for empresa_id, nombre in empresas}
    empresa_sel = st.selectbox("Empresa", list(opciones.keys()), key="calc_empresa")
    empresa_id = opciones[empresa_sel]

    datos = obtener_apartamentos(empresa_id)
    if not datos:
        st.info("No hay apartamentos")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    apartamentos = {nombre: float(limpieza) for nombre, limpieza in datos}
    apt = st.selectbox("Apartamento", list(apartamentos.keys()), key="calc_apartamento")
    limpieza = apartamentos[apt]

    c1, c2 = st.columns(2)
    with c1:
        adr_pasado_txt = st.text_input("ADR año pasado (€)", "0", key="calc_adr")
        noches_txt = st.text_input("Noches", "2", key="calc_noches")
    with c2:
        incremento_txt = st.text_input("% esperado este año", "0", key="calc_incremento")

    st.text_input(
        "Limpieza (€)",
        value=f"{limpieza:.2f}",
        disabled=True,
        key=f"calc_limpieza_{apt}"
    )

    if st.button("Calcular precio objetivo (RMS)", key="calc_btn"):
        try:
            adr_pasado = parse_float_input(adr_pasado_txt, "ADR año pasado (€)", minimo=0)
            noches = parse_int_input(noches_txt, "Noches", minimo=1)
            incremento = parse_float_input(incremento_txt, "% esperado este año")

            descuento = obtener_descuento_para_noches(empresa_id, noches)
            if descuento is None:
                st.error("No hay descuento para esas noches")
            else:
                adr_objetivo = adr_pasado * (1 + incremento / 100)
                markups = obtener_markups_empresa(empresa_id)

                markup_airbnb = markups["Airbnb"]
                factor_markup = (1 + markup_airbnb / 100)
                factor_descuento = (1 - descuento / 100)
                limpieza_noche = limpieza / noches

                if factor_markup * factor_descuento == 0:
                    st.error("La configuración actual produce una división por cero.")
                else:
                    precio_rms = (
                        (adr_objetivo - limpieza_noche)
                        / (factor_markup * factor_descuento)
                    )

                    st.write("### Precio a cargar en RMS")
                    st.markdown(
                        f"""
                        <div class="single-rms">
                            <div class="kpi-card kpi-good">
                                <div class="kpi-title">Precio único RMS</div>
                                <div class="kpi-total">{precio_rms:,.2f}<span class="kpi-currency">€</span></div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        except Exception as e:
            st.error(f"Error en Calculeitor: {e}")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# RENDER
# =========================================================
render_nav()

section = st.session_state.active_section

if section == "Subir archivo":
    section_upload()
elif section == "Configuración":
    section_config()
elif section == "Simuleitor":
    section_simuleitor()
elif section == "Calculeitor":
    section_calculeitor()
import os
import sqlite3
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
# DB
# =========================================================
@st.cache_resource
def get_connection():
    conn = sqlite3.connect(
        "alojamientos.db",
        check_same_thread=False,
        timeout=30,
        isolation_level=None
    )
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
    except Exception:
        pass
    return conn


conn = get_connection()

with conn:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS alojamientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        nombre TEXT,
        coste_limpieza REAL,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS configuracion_empresa (
        cliente_id INTEGER PRIMARY KEY,
        markup_airbnb REAL,
        markup_booking REAL,
        markup_web REAL,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS descuentos_empresa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        noches_desde INTEGER,
        noches_hasta INTEGER,
        descuento REAL,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    )
    """)


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


def obtener_o_crear_cliente(nombre_empresa: str) -> int:
    cur = conn.execute("SELECT id FROM clientes WHERE nombre = ?", (nombre_empresa,))
    fila = cur.fetchone()
    if fila:
        return fila[0]

    cur = conn.execute("INSERT INTO clientes (nombre) VALUES (?)", (nombre_empresa,))
    return cur.lastrowid


def contar_alojamientos(cliente_id: int) -> int:
    cur = conn.execute("SELECT COUNT(*) FROM alojamientos WHERE cliente_id = ?", (cliente_id,))
    return cur.fetchone()[0]


def obtener_empresas():
    return conn.execute("SELECT id, nombre FROM clientes ORDER BY nombre").fetchall()


def obtener_apartamentos(cliente_id: int):
    return conn.execute("""
        SELECT nombre, coste_limpieza
        FROM alojamientos
        WHERE cliente_id = ?
        ORDER BY nombre
    """, (cliente_id,)).fetchall()


def obtener_markups_empresa(cliente_id: int):
    cur = conn.execute("""
        SELECT markup_airbnb, markup_booking, markup_web
        FROM configuracion_empresa
        WHERE cliente_id = ?
    """, (cliente_id,))
    fila = cur.fetchone()

    if fila:
        return {
            "Airbnb": float(fila[0]) if fila[0] is not None else 0.0,
            "Booking": float(fila[1]) if fila[1] is not None else 0.0,
            "Web": float(fila[2]) if fila[2] is not None else 0.0,
        }

    return {"Airbnb": 0.0, "Booking": 0.0, "Web": 0.0}


def guardar_markups_empresa(cliente_id: int, markup_airbnb: float, markup_booking: float, markup_web: float):
    conn.execute("""
        INSERT INTO configuracion_empresa (
            cliente_id,
            markup_airbnb,
            markup_booking,
            markup_web
        )
        VALUES (?, ?, ?, ?)
        ON CONFLICT(cliente_id) DO UPDATE SET
            markup_airbnb = excluded.markup_airbnb,
            markup_booking = excluded.markup_booking,
            markup_web = excluded.markup_web
    """, (cliente_id, markup_airbnb, markup_booking, markup_web))


def obtener_descuentos_empresa(cliente_id: int) -> pd.DataFrame:
    cur = conn.execute("""
        SELECT noches_desde, noches_hasta, descuento
        FROM descuentos_empresa
        WHERE cliente_id = ?
        ORDER BY noches_desde
    """, (cliente_id,))
    filas = cur.fetchall()

    if filas:
        return pd.DataFrame(filas, columns=["Desde", "Hasta", "Descuento (%)"])

    return pd.DataFrame({
        "Desde": [2, 4, 7],
        "Hasta": [3, 6, 10],
        "Descuento (%)": [45, 50, 55]
    })


def guardar_descuentos_empresa(cliente_id: int, df_descuentos: pd.DataFrame):
    # FIX: DELETE + INSERTs en una transacción atómica
    with conn:
        conn.execute("DELETE FROM descuentos_empresa WHERE cliente_id = ?", (cliente_id,))

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

            conn.execute("""
                INSERT INTO descuentos_empresa (
                    cliente_id,
                    noches_desde,
                    noches_hasta,
                    descuento
                )
                VALUES (?, ?, ?, ?)
            """, (cliente_id, desde, hasta, descuento))


def obtener_descuento_para_noches(cliente_id: int, noches: int) -> Optional[float]:
    cur = conn.execute("""
        SELECT descuento
        FROM descuentos_empresa
        WHERE cliente_id = ?
          AND ? BETWEEN noches_desde AND noches_hasta
        ORDER BY noches_desde
        LIMIT 1
    """, (cliente_id, noches))
    fila = cur.fetchone()
    return float(fila[0]) if fila else None


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
            "clean" in col_norm
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

    # Cards HTML con tamaño y layout perfectamente fijo
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

    # Botones Streamlit ocultos — las cards HTML los triggean via JS
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
        // Reintenta hasta que el DOM esté listo
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
    empresa = st.text_input("Nombre de la empresa", key="upload_empresa")
    archivo = st.file_uploader("Sube tu archivo", type=["csv", "xlsx"], key="upload_file")

    if archivo and empresa:
        try:
            df = leer_archivo_datos(archivo)
            df.columns = df.columns.str.strip().str.lower()

            st.write("Columnas detectadas:", list(df.columns))
            col_nombre, col_limpieza = detectar_columnas(df)

            if not col_nombre or not col_limpieza:
                st.error("❌ No se detectan columnas válidas en el archivo")
                st.info("Debe haber una columna de nombre/apartamento y otra de limpieza.")
            else:
                st.success(f"✅ Columnas detectadas: {col_nombre} / {col_limpieza}")

                cliente_id = obtener_o_crear_cliente(empresa)
                total_actual = contar_alojamientos(cliente_id)

                if total_actual > 0:
                    st.warning(
                        f"⚠️ Esta empresa ya tiene {total_actual} alojamientos. "
                        "Si continúas, se reemplazarán por los del nuevo archivo."
                    )
                else:
                    st.info("ℹ️ Esta empresa no tiene alojamientos previos.")

                confirmar = st.checkbox(
                    "Confirmo que quiero reemplazar los datos actuales",
                    key="upload_confirm"
                )

                if st.button("Actualizar base de datos", key="upload_update_btn"):
                    if not confirmar:
                        st.error("❌ Debes confirmar antes de continuar")
                    else:
                        conn.execute("DELETE FROM alojamientos WHERE cliente_id = ?", (cliente_id,))

                        insertados = 0
                        for _, fila in df.iterrows():
                            nombre_alojamiento = str(fila[col_nombre]).strip()

                            if nombre_alojamiento == "" or pd.isna(fila[col_limpieza]):
                                continue

                            valor_limpieza = str(fila[col_limpieza]).replace(",", ".").strip()

                            try:
                                limpieza = float(valor_limpieza)
                            except ValueError:
                                continue

                            conn.execute("""
                                INSERT INTO alojamientos (cliente_id, nombre, coste_limpieza)
                                VALUES (?, ?, ?)
                            """, (cliente_id, nombre_alojamiento, limpieza))

                            insertados += 1

                        st.success(f"✅ Datos actualizados correctamente. {insertados} alojamientos cargados.")

        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {e}")

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

    opciones = {nombre: cliente_id for cliente_id, nombre in empresas}
    empresa_sel = st.selectbox("Empresa", list(opciones.keys()), key="config_empresa")
    cliente_id = opciones[empresa_sel]

    markups_actuales = obtener_markups_empresa(cliente_id)

    c1, c2, c3 = st.columns(3)
    with c1:
        # FIX: formato explícito en lugar de .replace(".0", "")
        markup_airbnb_txt = st.text_input(
            "Markup Airbnb (%)",
            value=f"{markups_actuales['Airbnb']:.2f}".rstrip("0").rstrip("."),
            key="cfg_markup_airbnb"
        )
    with c2:
        markup_booking_txt = st.text_input(
            "Markup Booking (%)",
            value=f"{markups_actuales['Booking']:.2f}".rstrip("0").rstrip("."),
            key="cfg_markup_booking"
        )
    with c3:
        markup_web_txt = st.text_input(
            "Markup Web (%)",
            value=f"{markups_actuales['Web']:.2f}".rstrip("0").rstrip("."),
            key="cfg_markup_web"
        )

    st.write("### 📊 Descuentos por rango de noches")
    descuentos_df_actual = obtener_descuentos_empresa(cliente_id)

    descuentos_editados = st.data_editor(
        descuentos_df_actual,
        num_rows="dynamic",
        use_container_width=True,
        key=f"cfg_descuentos_editor_{cliente_id}"
    )

    if st.button("Guardar configuración", key="cfg_save_btn"):
        try:
            markup_airbnb = parse_float_input(markup_airbnb_txt, "Markup Airbnb (%)")
            markup_booking = parse_float_input(markup_booking_txt, "Markup Booking (%)")
            markup_web = parse_float_input(markup_web_txt, "Markup Web (%)")

            guardar_markups_empresa(cliente_id, markup_airbnb, markup_booking, markup_web)
            guardar_descuentos_empresa(cliente_id, descuentos_editados)
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

    opciones = {nombre: cliente_id for cliente_id, nombre in empresas}
    empresa_sel = st.selectbox("Empresa", list(opciones.keys()), key="sim_empresa")
    cliente_id = opciones[empresa_sel]

    datos = obtener_apartamentos(cliente_id)
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

            descuento = obtener_descuento_para_noches(cliente_id, noches)
            if descuento is None:
                st.error("No hay descuento para esas noches")
            else:
                markups = obtener_markups_empresa(cliente_id)
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

    opciones = {nombre: cliente_id for cliente_id, nombre in empresas}
    empresa_sel = st.selectbox("Empresa", list(opciones.keys()), key="calc_empresa")
    cliente_id = opciones[empresa_sel]

    datos = obtener_apartamentos(cliente_id)
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

            descuento = obtener_descuento_para_noches(cliente_id, noches)
            if descuento is None:
                st.error("No hay descuento para esas noches")
            else:
                adr_objetivo = adr_pasado * (1 + incremento / 100)
                markups = obtener_markups_empresa(cliente_id)

                markup_airbnb = markups["Airbnb"]
                factor_markup = (1 + markup_airbnb / 100)
                factor_descuento = (1 - descuento / 100)
                limpieza_noche = limpieza / noches

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
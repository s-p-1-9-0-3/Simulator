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
@import url('https://fonts.googleapis.com/css2?family=ABeeZee&display=swap');

html, body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"] {
    font-family: 'ABeeZee', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at top left, rgba(78,193,181,0.08) 0%, rgba(78,193,181,0.00) 28%),
        linear-gradient(180deg, #f8fbfb 0%, #f5f7f8 100%);
}

.block-container {
    max-width: 1180px;
    padding-top: 3.8rem;
    padding-bottom: 2rem;
}

.top-title {
    font-size: 2.35rem;
    font-weight: 800;
    line-height: 1.05;
    margin: 0;
    color: #172033;
}

.top-subtitle {
    color: #667085;
    margin: 0.55rem 0 0 0;
    font-size: 1rem;
}

.header-logo-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 96px;
}

.header-text-wrap {
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 96px;
}

/* NAV */
.nav-card-wrap {
    width: 100%;
}

.nav-card-wrap .stButton {
    width: 100%;
}

.nav-card-wrap .stButton > button {
    width: 100% !important;
    min-width: 100% !important;
    max-width: 100% !important;

    height: 184px !important;
    min-height: 184px !important;
    max-height: 184px !important;

    border-radius: 22px !important;
    border: 1px solid rgba(15, 23, 42, 0.14) !important;
    background: linear-gradient(180deg, rgba(255,255,255,0.96) 0%, rgba(255,255,255,0.88) 100%) !important;
    box-shadow:
        0 8px 22px rgba(15, 23, 42, 0.05),
        inset 0 1px 0 rgba(255,255,255,0.70) !important;

    color: #172033 !important;
    text-align: center !important;
    white-space: pre-wrap !important;
    line-height: 1.28 !important;
    font-size: 1.00rem !important;
    font-weight: 400 !important;
    padding: 12px 10px !important;
    margin: 0 !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    transition:
        transform 0.18s ease,
        box-shadow 0.18s ease,
        border-color 0.18s ease,
        background 0.18s ease !important;
}

.nav-card-wrap .stButton > button:hover {
    transform: translateY(-4px);
    border-color: rgba(78,193,181,0.70) !important;
    box-shadow:
        0 14px 28px rgba(78,193,181,0.14),
        0 8px 18px rgba(15, 23, 42, 0.06) !important;
    background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(78,193,181,0.07) 100%) !important;
}

.nav-card-wrap .stButton > button:focus {
    outline: none !important;
    border-color: rgba(78,193,181,0.90) !important;
    box-shadow:
        0 0 0 0.18rem rgba(78,193,181,0.16),
        0 14px 26px rgba(78,193,181,0.12) !important;
}

.cards-divider {
    width: 100%;
    height: 1px;
    background: rgba(15,23,42,0.10);
    margin: 22px 0 8px 0;
    border-radius: 999px;
}

/* contenido */
.dashboard-card {
    border: 1px solid rgba(49, 51, 63, 0.10);
    border-radius: 22px;
    padding: 20px 20px 14px 20px;
    background: rgba(255,255,255,0.92);
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
    margin-bottom: 1rem;
}

.section-title {
    font-size: 1.15rem;
    font-weight: 800;
    margin-bottom: 0.35rem;
    color: #172033;
}

.section-subtitle {
    color: #667085;
    margin-bottom: 1rem;
}

.kpi-card {
    border: 1px solid rgba(49, 51, 63, 0.10);
    border-radius: 18px;
    padding: 16px;
    background: #fafafa;
    min-height: 150px;
}

.kpi-good {
    border: 1px solid rgba(78, 193, 181, 0.60);
    background: rgba(78, 193, 181, 0.10);
}

.kpi-title {
    font-size: 0.92rem;
    color: #667085;
    margin-bottom: 0.35rem;
    font-weight: 600;
}

.kpi-value {
    font-size: 1.12rem;
    font-weight: 700;
    line-height: 1.15;
}

.kpi-sub {
    font-size: 0.9rem;
    color: #667085;
    margin-top: 0.45rem;
}

.kpi-total {
    font-size: 2rem;
    font-weight: 800;
    line-height: 1.1;
    margin-top: 0.25rem;
    color: #172033;
}

.single-rms {
    max-width: 420px;
    margin: 0 auto;
}

div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] > div,
div[data-testid="stDataEditor"] {
    border-radius: 12px;
}

div[data-testid="stFileUploader"] section {
    border-radius: 14px;
}

@media (max-width: 1100px) {
    .nav-card-wrap .stButton > button {
        height: 172px !important;
        min-height: 172px !important;
        max-height: 172px !important;
        font-size: 0.96rem !important;
    }
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 2.2rem;
    }

    .top-title {
        font-size: 1.9rem;
    }

    .top-subtitle {
        font-size: 0.95rem;
    }

    .nav-card-wrap .stButton > button {
        height: 156px !important;
        min-height: 156px !important;
        max-height: 156px !important;
        font-size: 0.92rem !important;
        border-radius: 18px !important;
    }
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
    col_logo, col_title = st.columns([1.15, 4.85], gap="small")

    with col_logo:
        st.markdown('<div class="header-logo-wrap">', unsafe_allow_html=True)
        if os.path.exists("logo.png"):
            st.image("logo.png", width=145)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_title:
        st.markdown('<div class="header-text-wrap">', unsafe_allow_html=True)
        st.markdown('<div class="top-title">Revenue Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="top-subtitle">Elige un módulo para trabajar</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height: 1.15rem;"></div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns([1, 1, 1, 1], gap="small")

    with c1:
        st.markdown('<div class="nav-card-wrap">', unsafe_allow_html=True)
        if st.button(
            "📁\n\nSubir archivo\n\nCarga y reemplaza\nalojamientos desde CSV o\nExcel",
            key="nav1",
            use_container_width=True
        ):
            st.session_state.active_section = "Subir archivo"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="nav-card-wrap">', unsafe_allow_html=True)
        if st.button(
            "⚙️\n\nConfiguración\n\nMarkups por canal y\ndescuentos por noches\n",
            key="nav2",
            use_container_width=True
        ):
            st.session_state.active_section = "Configuración"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="nav-card-wrap">', unsafe_allow_html=True)
        if st.button(
            "📊\n\nSimuleitor\n\nComparativa por canal\n\n",
            key="nav3",
            use_container_width=True
        ):
            st.session_state.active_section = "Simuleitor"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="nav-card-wrap">', unsafe_allow_html=True)
        if st.button(
            "🧠\n\nCalculeitor\n\nPrecio objetivo RMS\n\n",
            key="nav4",
            use_container_width=True
        ):
            st.session_state.active_section = "Calculeitor"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="cards-divider"></div>', unsafe_allow_html=True)


def pin_gate(section_name: str, state_key: str):
    st.markdown(
        f'<div class="dashboard-card"><div class="section-title">{section_name}</div><div class="section-subtitle">Sección protegida por PIN</div>',
        unsafe_allow_html=True
    )

    if not st.session_state[state_key]:
        pin = st.text_input("Introduce PIN", type="password", key=f"pin_{state_key}")
        if st.button("Desbloquear", key=f"unlock_{state_key}"):
            if pin == ADMIN_PIN:
                st.session_state[state_key] = True
                st.rerun()
            else:
                st.error("PIN incorrecto")
        st.markdown("</div>", unsafe_allow_html=True)
        return False

    st.success("Sección desbloqueada")
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
        markup_airbnb_txt = st.text_input(
            "Markup Airbnb (%)",
            value=str(markups_actuales["Airbnb"]).replace(".0", ""),
            key="cfg_markup_airbnb"
        )
    with c2:
        markup_booking_txt = st.text_input(
            "Markup Booking (%)",
            value=str(markups_actuales["Booking"]).replace(".0", ""),
            key="cfg_markup_booking"
        )
    with c3:
        markup_web_txt = st.text_input(
            "Markup Web (%)",
            value=str(markups_actuales["Web"]).replace(".0", ""),
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
        '<div class="dashboard-card"><div class="section-title">📊 Simuleitor</div><div class="section-subtitle">Compara los tres canales usando el apartamento seleccionado.</div>',
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
                for col, canal in zip(cols, ["Airbnb", "Booking", "Web"]):
                    data = resultados[canal]
                    css = "kpi-card"
                    if data["total"] == mejor_total:
                        css += " kpi-good"

                    with col:
                        st.markdown(
                            f"""
                            <div class="{css}">
                                <div class="kpi-title">{canal}</div>
                                <div class="kpi-sub">precio final por noche</div>
                                <div class="kpi-value">{data["noche"]:.2f} €</div>
                                <div class="kpi-sub" style="margin-top:16px;">total estancia</div>
                                <div class="kpi-total">{data["total"]:.2f} €</div>
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
        '<div class="dashboard-card"><div class="section-title">🧠 Calculeitor</div><div class="section-subtitle">Calcula un único precio a cargar en RMS usando Airbnb.</div>',
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
                        <div class="kpi-card kpi-good" style="text-align:center;">
                            <div class="kpi-title">Precio único RMS</div>
                            <div class="kpi-total">{precio_rms:.2f} €</div>
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
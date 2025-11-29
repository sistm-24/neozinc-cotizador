import datetime
import urllib.parse
import os
from typing import List, Dict
import pandas as pd
import streamlit as st
from fpdf import FPDF
import altair as alt

# ------------------------------------------------------
# 1. CONFIGURACIÓN VISUAL (DISEÑO PREMIUM)
# ------------------------------------------------------
st.set_page_config(
    page_title="Neozinc Systems | Manager v15",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS AVANZADO PARA EFECTO CRISTAL Y FONDO PROFESIONAL ---
st.markdown("""
    <style>
    /* 1. FONDO DEGRADADO TECH */
    .stApp {
        background: radial-gradient(circle at 10% 20%, #0f172a 0%, #000000 90%);
        color: #e2e8f0;
    }

    /* 2. TARJETAS CON EFECTO CRISTAL (GLASSMORPHISM) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(30, 41, 59, 0.4);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* 3. PESTAÑAS (TABS) ESTILIZADAS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(0,0,0,0);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 8px 8px 0 0;
        color: #94a3b8;
        border: 1px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00E5FF !important;
        color: #000000 !important;
        font-weight: bold;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.4);
    }

    /* 4. BOTONES NEÓN */
    .stButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%);
        color: white;
        border: none;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%);
        box-shadow: 0 0 12px rgba(14, 165, 233, 0.6);
        transform: translateY(-2px);
    }

    /* 5. MÉTRICAS IMPACTANTES */
    div[data-testid="stMetricValue"] {
        background: -webkit-linear-gradient(0deg, #00E5FF, #2979FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem !important;
        font-weight: 800;
    }
    
    /* 6. EXPANDERS */
    .streamlit-expanderHeader {
        background-color: #0f172a;
        color: #38bdf8; 
        border-radius: 6px;
    }
    </style>
    """, unsafe_allow_html=True)

# ------------------------------------------------------
# 2. CLASE PDF (REPORTE COMPLETO)
# ------------------------------------------------------
class PDF(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            self.image('logo.png', 10, 8, 25)
            self.set_font('Arial', 'B', 15)
            self.cell(35) 
            self.cell(0, 8, 'NEOZINC SYSTEMS', 0, 1, 'L')
            self.set_font('Arial', 'I', 9)
            self.cell(35)
            self.cell(0, 5, 'Ingeniería - Detección y Extinción de Incendios', 0, 1, 'L')
            self.set_font('Arial', 'B', 9)
            self.cell(35)
            self.cell(0, 5, 'Contacto: 925 940 657', 0, 1, 'L') 
        else:
            self.set_font('Arial', 'B', 16)
            self.cell(0, 10, 'NEOZINC SYSTEMS', 0, 1, 'C')
        
        self.ln(8)
        self.set_draw_color(0, 229, 255) # Cyan Neón
        self.line(10, 35, 200, 35)
        self.set_draw_color(0, 0, 0)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()} - Generado por Neozinc Systems', 0, 0, 'C')

def generar_pdf_bytes(cliente, fecha, area, servicio, materiales, mano_obra, gg, margen, total):
    pdf = PDF()
    pdf.add_page()
    
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 6, f"Cliente: {cliente}", ln=True)
    pdf.cell(0, 6, f"Fecha: {fecha}", ln=True)
    pdf.cell(0, 6, f"Referencia: {servicio} - {area}", ln=True)
    pdf.ln(5)
    
    # Filtros
    lista_equipos = [m for m in materiales if m['Tipo'] == 'Equipo']
    lista_materiales = [m for m in materiales if m['Tipo'] == 'Material']
    lista_herramientas = [m for m in materiales if m['Tipo'] == 'Herramienta']

    # Helper tabla
    def dibujar_tabla(titulo, lista, color_rgb):
        if lista:
            pdf.set_fill_color(*color_rgb) 
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(0, 10, titulo, ln=True)
            pdf.cell(100, 8, "Descripción", 1, 0, 'C', fill=True)
            pdf.cell(30, 8, "Cant.", 1, 0, 'C', fill=True)
            pdf.cell(30, 8, "P.Unit", 1, 0, 'C', fill=True)
            pdf.cell(30, 8, "Total", 1, 1, 'C', fill=True)
            pdf.set_font("Arial", size=9)
            for m in lista:
                pdf.cell(100, 8, f"{m['Nombre'][:60]}", 1) 
                pdf.cell(30, 8, f"{m['Cantidad']} {m['Unidad']}", 1, 0, 'C')
                pdf.cell(30, 8, f"{m['Precio Unit.']:.2f}", 1, 0, 'R')
                pdf.cell(30, 8, f"{m['Subtotal']:.2f}", 1, 1, 'R')
            pdf.ln(5)

    dibujar_tabla("1. SUMINISTRO DE EQUIPOS (ACTIVOS)", lista_equipos, (220, 240, 255))
    dibujar_tabla("2. SUMINISTRO DE MATERIALES", lista_materiales, (235, 255, 235))
    dibujar_tabla("3. HERRAMIENTAS Y EQUIPOS MENORES", lista_herramientas, (255, 250, 230))

    if mano_obra:
        pdf.set_fill_color(255, 240, 240)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 10, "4. MANO DE OBRA ESPECIALIZADA", ln=True)
        pdf.cell(100, 8, "Rol / Cargo", 1, 0, 'C', fill=True)
        pdf.cell(30, 8, "Pers.", 1, 0, 'C', fill=True)
        pdf.cell(30, 8, "Hrs.", 1, 0, 'C', fill=True)
        pdf.cell(30, 8, "Total", 1, 1, 'C', fill=True)
        pdf.set_font("Arial", size=9)
        for mo in mano_obra:
            pdf.cell(100, 8, f"{mo['Cargo']}", 1)
            pdf.cell(30, 8, str(mo['Personas']), 1, 0, 'C')
            pdf.cell(30, 8, str(mo['Horas']), 1, 0, 'C')
            pdf.cell(30, 8, f"{mo['Subtotal']:.2f}", 1, 1, 'R')
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(130)
    pdf.cell(30, 12, "TOTAL VENTA:", 0, 0, 'R')
    pdf.cell(30, 12, f"S/. {total:,.2f}", 0, 1, 'R')
    return pdf.output(dest='S').encode('latin-1')

# ------------------------------------------------------
# 3. DATOS Y LÓGICA
# ------------------------------------------------------
def init_session():
    if "recursos" not in st.session_state:
        datos_iniciales = [
            # DACI
            {"Nombre": 'Panel de Alarma 4Z', "Tipo": "Equipo", "Categoría": "DACI", "Unidad": "und", "Costo Unitario": 1200.0},
            {"Nombre": 'Detector de Humo', "Tipo": "Equipo", "Categoría": "DACI", "Unidad": "und", "Costo Unitario": 45.0},
            {"Nombre": 'Estación Manual', "Tipo": "Equipo", "Categoría": "DACI", "Unidad": "und", "Costo Unitario": 65.0},
            {"Nombre": 'TUBERIA EMT 3/4"', "Tipo": "Material", "Categoría": "DACI", "Unidad": "und", "Costo Unitario": 6.20},
            {"Nombre": 'Cable FPL 2x18AWG', "Tipo": "Material", "Categoría": "DACI", "Unidad": "rollo", "Costo Unitario": 280.0},
            # HERRAMIENTAS DACI
            {"Nombre": 'Multímetro Fluke (Alquiler)', "Tipo": "Herramienta", "Categoría": "DACI", "Unidad": "día", "Costo Unitario": 35.0},
            {"Nombre": 'Escalera de Tijera 8 pasos', "Tipo": "Herramienta", "Categoría": "DACI", "Unidad": "día", "Costo Unitario": 15.0},
            {"Nombre": 'Andamio Normado (1 Cuerpo)', "Tipo": "Herramienta", "Categoría": "DACI", "Unidad": "día", "Costo Unitario": 25.0},
            
            # ACI
            {"Nombre": 'Gabinete CI c/manguera', "Tipo": "Equipo", "Categoría": "ACI", "Unidad": "und", "Costo Unitario": 850.0},
            {"Nombre": 'Rociador K5.6', "Tipo": "Material", "Categoría": "ACI", "Unidad": "und", "Costo Unitario": 18.0},
            {"Nombre": 'Manómetro 300PSI', "Tipo": "Material", "Categoría": "ACI", "Unidad": "und", "Costo Unitario": 45.0},
            # HERRAMIENTAS ACI
            {"Nombre": 'Roscadora de Tubos 1/2-2" (Alquiler)', "Tipo": "Herramienta", "Categoría": "ACI", "Unidad": "día", "Costo Unitario": 65.0},
            {"Nombre": 'Ranuradora (Roll Groover)', "Tipo": "Herramienta", "Categoría": "ACI", "Unidad": "día", "Costo Unitario": 80.0},
            {"Nombre": 'Llave Stilson 24"', "Tipo": "Herramienta", "Categoría": "ACI", "Unidad": "día", "Costo Unitario": 10.0},

            # BCI
            {"Nombre": 'Bomba Jockey 5HP', "Tipo": "Equipo", "Categoría": "BCI", "Unidad": "und", "Costo Unitario": 950.0},
            {"Nombre": 'Empaquetadura', "Tipo": "Material", "Categoría": "BCI", "Unidad": "mt", "Costo Unitario": 45.0},
            # HERRAMIENTAS BCI
            {"Nombre": 'Alineador Laser de Ejes', "Tipo": "Herramienta", "Categoría": "BCI", "Unidad": "día", "Costo Unitario": 150.0},
            {"Nombre": 'Torquímetro', "Tipo": "Herramienta", "Categoría": "BCI", "Unidad": "día", "Costo Unitario": 40.0},
            {"Nombre": 'Tecle de Cadena 1Ton', "Tipo": "Herramienta", "Categoría": "BCI", "Unidad": "día", "Costo Unitario": 35.0},
        ]
        st.session_state.recursos = pd.DataFrame(datos_iniciales)
    
    if "roles" not in st.session_state:
        st.session_state.roles = pd.DataFrame([
            {"Cargo": "Técnico Líder", "Costo Hora": 35.0},
            {"Cargo": "Ayudante", "Costo Hora": 15.0},
            {"Cargo": "Soldador", "Costo Hora": 45.0},
        ])
    if "items_mat" not in st.session_state: st.session_state.items_mat = []
    if "items_mo" not in st.session_state: st.session_state.items_mo = []
    if "gg" not in st.session_state: st.session_state.gg = 50.0
    if "margen" not in st.session_state: st.session_state.margen = 30

init_session()

def agregar_item(item_dict, cantidad):
    st.session_state.items_mat.append({
        "Nombre": item_dict['Nombre'], 
        "Tipo": item_dict['Tipo'], 
        "Unidad": item_dict['Unidad'], 
        "Precio Unit.": item_dict['Costo Unitario'], 
        "Cantidad": cantidad, 
        "Subtotal": item_dict['Costo Unitario'] * cantidad
    })
    st.toast("✅ Agregado correctamente")

def eliminar_item(idx, tipo):
    if tipo == 'mat': st.session_state.items_mat.pop(idx)
    elif tipo == 'mo': st.session_state.items_mo.pop(idx)
    st.rerun()

def formatear_moneda(val): return f"S/. {val:,.2f}"

# ------------------------------------------------------
# 4. INTERFAZ GRÁFICA (UI)
# ------------------------------------------------------
# Sidebar
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)
else:
    st.sidebar.title("NEOZINC")

st.sidebar.markdown("### ⚙️ Panel de Control")
with st.sidebar.expander("📦 Base de Datos", expanded=False):
    edited_df = st.data_editor(st.session_state.recursos, num_rows="dynamic", key="data_recursos") 
    st.session_state.recursos = edited_df

with st.sidebar.expander("👷 Tarifas Personal", expanded=False):
    edited_roles = st.data_editor(st.session_state.roles, num_rows="dynamic", key="data_roles")
    st.session_state.roles = edited_roles

if st.sidebar.button("🧹 LIMPIAR TODO", use_container_width=True):
    st.session_state.items_mat = []
    st.session_state.items_mo = []
    st.rerun()

# Main Header
st.markdown("<h1 style='text-align: center; color: white;'>NEOZINC <span style='color:#00E5FF'>MANAGER</span></h1>", unsafe_allow_html=True)

# PESTAÑAS (NOMBRE ACTUALIZADO)
tab1, tab2, tab3 = st.tabs(["📝 COTIZADOR", "📊 GRÁFICOS Y ESTADÍSTICAS", "📤 EXPORTAR"])

with tab1:
    with st.container(border=True):
        st.markdown("#### 📁 Información del Proyecto")
        c1, c2, c3, c4 = st.columns(4)
        cliente = c1.text_input("Cliente", "Cliente Nuevo")
        contacto = c2.text_input("Celular", "51")
        area = c3.selectbox("Sistema", ["Integral", "Detección", "Agua", "Bombas"])
        servicio = c4.selectbox("Servicio", ["Correctivo", "Preventivo", "Instalación"])

    st.write(" ")

    # GENERADOR DE SECCIONES
    def seccion_categoria(cat_code, titulo, icono):
        with st.expander(f"{icono} {titulo}", expanded=False):
            df_cat = st.session_state.recursos[st.session_state.recursos['Categoría'] == cat_code]
            
            def selector_tipo(tipo_label, tipo_code, color_emoji):
                st.markdown(f"**{color_emoji} {tipo_label}**")
                df = df_cat[df_cat['Tipo'] == tipo_code]
                if not df.empty:
                    map_items = {f"{r['Nombre']} (S/.{r['Costo Unitario']})": r for r in df.to_dict("records")}
                    c1, c2, c3 = st.columns([3, 1, 1], vertical_alignment="bottom")
                    sel = c1.selectbox(f"Item", list(map_items.keys()), key=f"s_{cat_code}_{tipo_code}", label_visibility="collapsed")
                    cant = c2.number_input("Cant.", 1.0, key=f"c_{cat_code}_{tipo_code}", label_visibility="collapsed")
                    if c3.button("AGREGAR", key=f"b_{cat_code}_{tipo_code}", use_container_width=True):
                        agregar_item(map_items[sel], cant)
                else:
                    st.info(f"No hay {tipo_label} registrados.")
                st.write("")

            selector_tipo("EQUIPOS (Activos)", "Equipo", "📡")
            st.divider()
            selector_tipo("MATERIALES (Insumos)", "Material", "🔩")
            st.divider()
            selector_tipo("HERRAMIENTAS (Uso)", "Herramienta", "🛠️")

    seccion_categoria("DACI", "SISTEMA DE DETECCIÓN (DACI)", "🔴")
    seccion_categoria("ACI", "SISTEMA DE AGUA (ACI)", "🔵")
    seccion_categoria("BCI", "SISTEMA DE BOMBAS (BCI)", "🟢")

    st.write(" ")
    # CANASTA
    if st.session_state.items_mat:
        with st.container(border=True):
            st.markdown("#### 🛒 Canasta de Productos")
            st.markdown("""<div style="display: flex; font-weight: bold; margin-bottom: 5px; color:#00E5FF;">
                <div style="flex: 1;">Tipo</div>
                <div style="flex: 3;">Descripción</div>
                <div style="flex: 1;">Cant</div>
                <div style="flex: 1;">Total</div>
                <div style="flex: 0.5;"></div>
            </div>""", unsafe_allow_html=True)
            
            for i, item in enumerate(st.session_state.items_mat):
                c1, c2, c3, c4, c5 = st.columns([1, 3, 1, 1, 0.5])
                c1.caption(item['Tipo'])
                c2.write(item['Nombre'])
                c3.write(f"{item['Cantidad']} {item['Unidad']}")
                c4.write(f"{item['Subtotal']:.2f}")
                if c5.button("❌", key=f"del_mat_{i}"): eliminar_item(i, 'mat')

    st.write(" ")
    with st.container(border=True):
        st.markdown("#### 👷 Mano de Obra")
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1], vertical_alignment="bottom")
        df_rol = st.session_state.roles.to_dict("records")
        map_rol = {f"{r['Cargo']} (S/.{r['Costo Hora']})": r for r in df_rol}
        
        with c1: sel_rol = st.selectbox("Cargo", list(map_rol.keys()) if map_rol else [])
        with c2: n_per = st.number_input("Pers.", 1, key="np")
        with c3: n_hrs = st.number_input("Hrs.", 4.0, key="nh")
        with c4:
            if st.button("AGREGAR", key="b_mo", use_container_width=True) and map_rol:
                r = map_rol[sel_rol]
                st.session_state.items_mo.append({
                    "Cargo": r['Cargo'], "Personas": n_per, "Horas": n_hrs,
                    "Subtotal": r['Costo Hora']*n_per*n_hrs
                })
        
        if st.session_state.items_mo:
            st.dataframe(pd.DataFrame(st.session_state.items_mo)[["Cargo", "Personas", "Horas", "Subtotal"]], use_container_width=True)

# CÁLCULOS
t_mat = sum(x['Subtotal'] for x in st.session_state.items_mat)
t_mo = sum(x['Subtotal'] for x in st.session_state.items_mo)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💰 Finanzas")
st.session_state.gg = st.sidebar.number_input("Gastos Grales (S/.)", value=st.session_state.gg)
st.session_state.margen = st.sidebar.slider("Margen %", 0, 100, st.session_state.margen)

costo_dir = t_mat + t_mo + st.session_state.gg
precio_final = costo_dir * (1 + st.session_state.margen/100)
utilidad = precio_final - costo_dir

# --- DASHBOARD (GRÁFICOS) ---
with tab2:
    st.markdown("### 📊 Tablero de Control Financiero")
    
    with st.container(border=True):
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        col_kpi1.metric("COSTO DIRECTO", formatear_moneda(costo_dir), delta="Inversión")
        col_kpi2.metric("PRECIO VENTA", formatear_moneda(precio_final), delta=f"{st.session_state.margen}% Margen")
        col_kpi3.metric("UTILIDAD NETA", formatear_moneda(utilidad), delta_color="normal")
    
    st.write(" ")

    if costo_dir > 0:
        c1, c2 = st.columns(2)
        
        # Datos para Gráficos
        t_eq = sum(x['Subtotal'] for x in st.session_state.items_mat if x['Tipo'] == 'Equipo')
        t_mt = sum(x['Subtotal'] for x in st.session_state.items_mat if x['Tipo'] == 'Material')
        t_he = sum(x['Subtotal'] for x in st.session_state.items_mat if x['Tipo'] == 'Herramienta')
        
        data_pie = pd.DataFrame([
            {"Categoría": "Equipos", "Monto": t_eq},
            {"Categoría": "Materiales", "Monto": t_mt},
            {"Categoría": "Herramientas", "Monto": t_he},
            {"Categoría": "Mano Obra", "Monto": t_mo},
            {"Categoría": "Gastos Grales", "Monto": st.session_state.gg},
            {"Categoría": "Utilidad", "Monto": utilidad}
        ])
        
        with c1:
            with st.container(border=True):
                st.markdown("**Distribución del Precio Total**")
                base = alt.Chart(data_pie).encode(theta=alt.Theta("Monto", stack=True))
                pie = base.mark_arc(outerRadius=120, innerRadius=60).encode(
                    color=alt.Color("Categoría", scale=alt.Scale(scheme='spectral')),
                    order=alt.Order("Monto", sort="descending"),
                    tooltip=["Categoría", "Monto"]
                )
                text = base.mark_text(radius=140).encode(
                    text=alt.Text("Monto", format=",.0f"),
                    order=alt.Order("Monto", sort="descending"),
                    color=alt.value("white")
                )
                st.altair_chart(pie + text, use_container_width=True)
        
        with c2:
            with st.container(border=True):
                st.markdown("**Top Costos (Pareto)**")
                if st.session_state.items_mat:
                    df_bar = pd.DataFrame(st.session_state.items_mat)
                    bar = alt.Chart(df_bar).mark_bar().encode(
                        x=alt.X("Subtotal", title="Costo (S/.)"),
                        y=alt.Y("Nombre", sort="-x"),
                        color="Tipo",
                        tooltip=["Nombre", "Subtotal"]
                    )
                    st.altair_chart(bar, use_container_width=True)

# --- EXPORTAR ---
with tab3:
    st.markdown("### 📤 Finalizar Proyecto")
    
    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        with st.container(border=True):
            st.metric("TOTAL A COBRAR", formatear_moneda(precio_final))
            st.write(" ")
            
            if st.session_state.items_mat or st.session_state.items_mo:
                pdf_data = generar_pdf_bytes(cliente, str(datetime.date.today()), area, servicio, 
                                            st.session_state.items_mat, st.session_state.items_mo, 
                                            st.session_state.gg, st.session_state.margen, precio_final)
                
                st.download_button("📄 1. DESCARGAR PDF", pdf_data, f"Cotizacion_{cliente}.pdf", "application/pdf", type="primary", use_container_width=True)
                
                st.write(" ")
                msg = urllib.parse.quote(f"*NEOZINC*\nCliente: {cliente}\nTotal: {formatear_moneda(precio_final)}")
                st.link_button("🟢 2. ENVIAR WHATSAPP", f"https://wa.me/{contacto}?text={msg}", use_container_width=True)
            else:
                st.warning("Cotización vacía.")
 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/app.py b/app.py
new file mode 100644
index 0000000000000000000000000000000000000000..9bff0ade3b6b25c44e6896bae189a40a9d5bd059
--- /dev/null
+++ b/app.py
@@ -0,0 +1,297 @@
+import datetime
+from typing import List, Dict
+
+import pandas as pd
+import streamlit as st
+
+
+st.set_page_config(
+    page_title="Cotización de Sistemas Contra Incendio",
+    layout="wide",
+    initial_sidebar_state="expanded",
+)
+
+
+# -----------------------
+# Datos iniciales y estado
+# -----------------------
+
+def seed_data():
+    if "categorias" not in st.session_state:
+        st.session_state.categorias = [
+            "Detección de Incendio",
+            "Agua Contra Incendio",
+            "Bombas Contra Incendio",
+        ]
+    if "servicios" not in st.session_state:
+        st.session_state.servicios = [
+            "Mantenimiento Preventivo",
+            "Mantenimiento Correctivo",
+            "Instalación",
+        ]
+    if "recursos" not in st.session_state:
+        st.session_state.recursos = pd.DataFrame(
+            [
+                {
+                    "ID": "MAT-001",
+                    "Nombre": "Detector de humo óptico",
+                    "Tipo": "Material",
+                    "Categoría": "Detección de Incendio",
+                    "Unidad": "pieza",
+                    "Costo Unitario": 45.0,
+                },
+                {
+                    "ID": "MAT-002",
+                    "Nombre": "Gabinete contra incendio",
+                    "Tipo": "Equipo",
+                    "Categoría": "Agua Contra Incendio",
+                    "Unidad": "pieza",
+                    "Costo Unitario": 180.0,
+                },
+                {
+                    "ID": "MAT-003",
+                    "Nombre": "Bomba jockey 5HP",
+                    "Tipo": "Equipo",
+                    "Categoría": "Bombas Contra Incendio",
+                    "Unidad": "unidad",
+                    "Costo Unitario": 950.0,
+                },
+                {
+                    "ID": "MAT-004",
+                    "Nombre": "Cable libre de halógeno 2x18",
+                    "Tipo": "Material",
+                    "Categoría": "Detección de Incendio",
+                    "Unidad": "metro",
+                    "Costo Unitario": 1.9,
+                },
+                {
+                    "ID": "MAT-005",
+                    "Nombre": "Mano de obra especializada",
+                    "Tipo": "Servicio",
+                    "Categoría": "Agua Contra Incendio",
+                    "Unidad": "jornada",
+                    "Costo Unitario": 300.0,
+                },
+            ]
+        )
+    if "roles" not in st.session_state:
+        st.session_state.roles = pd.DataFrame(
+            [
+                {"Cargo": "Técnico", "Costo Hora": 22.0},
+                {"Cargo": "Ayudante", "Costo Hora": 15.0},
+                {"Cargo": "Ingeniero", "Costo Hora": 35.0},
+                {"Cargo": "Supervisor", "Costo Hora": 28.0},
+            ]
+        )
+    if "items_materiales" not in st.session_state:
+        st.session_state.items_materiales: List[Dict] = []
+    if "items_mano_obra" not in st.session_state:
+        st.session_state.items_mano_obra: List[Dict] = []
+    if "gastos_generales" not in st.session_state:
+        st.session_state.gastos_generales = 0.0
+    if "margen" not in st.session_state:
+        st.session_state.margen = 20.0
+
+
+def actualizar_recursos(df: pd.DataFrame):
+    st.session_state.recursos = df
+
+
+def actualizar_roles(df: pd.DataFrame):
+    st.session_state.roles = df
+
+
+def agregar_material(recurso: Dict, cantidad: float):
+    if not recurso or cantidad <= 0:
+        return
+    nuevo = recurso.copy()
+    nuevo["Cantidad"] = cantidad
+    nuevo["Subtotal"] = round(recurso["Costo Unitario"] * cantidad, 2)
+    st.session_state.items_materiales.append(nuevo)
+
+
+def agregar_mano_obra(role: Dict, personas: int, horas: float):
+    if not role or personas <= 0 or horas <= 0:
+        return
+    subtotal = round(role["Costo Hora"] * personas * horas, 2)
+    st.session_state.items_mano_obra.append(
+        {
+            "Cargo": role["Cargo"],
+            "Personas": personas,
+            "Horas": horas,
+            "Costo Hora": role["Costo Hora"],
+            "Subtotal": subtotal,
+        }
+    )
+
+
+def calcular_totales():
+    costo_materiales = sum(item["Subtotal"] for item in st.session_state.items_materiales)
+    costo_mano_obra = sum(item["Subtotal"] for item in st.session_state.items_mano_obra)
+    gastos = st.session_state.gastos_generales
+    costo_directo = costo_materiales + costo_mano_obra + gastos
+    precio_venta = round(costo_directo * (1 + st.session_state.margen / 100), 2)
+    return costo_materiales, costo_mano_obra, costo_directo, precio_venta
+
+
+def formatear_moneda(valor: float) -> str:
+    return f"$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
+
+
+seed_data()
+
+# -----------------------
+# Panel de administración
+# -----------------------
+st.sidebar.title("Panel de administración")
+st.sidebar.write("Actualiza costos de materiales y mano de obra. Los cambios se guardan en la sesión.")
+
+with st.sidebar.expander("Recursos (Inventario)", expanded=True):
+    recursos_editados = st.data_editor(
+        st.session_state.recursos,
+        num_rows="dynamic",
+        use_container_width=True,
+        key="editor_recursos",
+    )
+    actualizar_recursos(recursos_editados)
+
+with st.sidebar.expander("Roles (Mano de obra)", expanded=True):
+    roles_editados = st.data_editor(
+        st.session_state.roles,
+        num_rows="dynamic",
+        use_container_width=True,
+        key="editor_roles",
+    )
+    actualizar_roles(roles_editados)
+
+# -----------------------
+# Generador de cotizaciones
+# -----------------------
+st.title("Cotización de Sistemas Contra Incendio")
+st.caption("Genera presupuestos rápidos diferenciando costos y precios de venta.")
+
+col_cliente, col_fecha = st.columns([2, 1])
+with col_cliente:
+    cliente = st.text_input("Cliente", placeholder="Nombre de la empresa o persona")
+with col_fecha:
+    fecha = st.date_input("Fecha", value=datetime.date.today())
+
+col_area, col_servicio = st.columns(2)
+with col_area:
+    area = st.selectbox("Área", st.session_state.categorias)
+with col_servicio:
+    tipo_servicio = st.selectbox("Tipo de servicio", st.session_state.servicios)
+
+st.markdown("---")
+st.subheader("1. Selección de recursos")
+
+col_sel, col_qty, col_btn = st.columns([3, 1, 1])
+recursos_disponibles = st.session_state.recursos
+recursos_options = recursos_disponibles.to_dict("records")
+
+with col_sel:
+    recurso_sel = st.selectbox(
+        "Recurso",
+        recursos_options,
+        format_func=lambda r: f"{r['ID']} - {r['Nombre']} ({r['Unidad']}) | $ {r['Costo Unitario']}/u",
+        key="sel_recurso",
+    )
+with col_qty:
+    cantidad_sel = st.number_input("Cantidad", min_value=0.0, step=1.0, value=0.0)
+with col_btn:
+    if st.button("Agregar", type="primary"):
+        agregar_material(recurso_sel, cantidad_sel)
+
+if st.session_state.items_materiales:
+    st.dataframe(pd.DataFrame(st.session_state.items_materiales), use_container_width=True)
+else:
+    st.info("Agrega recursos para comenzar a calcular el costo directo de materiales.")
+
+st.markdown("---")
+st.subheader("2. Mano de obra")
+
+col_role, col_personas, col_horas, col_btn_role = st.columns([3, 1, 1, 1])
+roles_options = st.session_state.roles.to_dict("records")
+with col_role:
+    role_sel = st.selectbox("Rol", roles_options, format_func=lambda r: r["Cargo"], key="sel_rol")
+with col_personas:
+    personas = st.number_input("Cantidad de personas", min_value=0, step=1, value=0)
+with col_horas:
+    horas = st.number_input("Horas de trabajo", min_value=0.0, step=1.0, value=0.0)
+with col_btn_role:
+    if st.button("Agregar personal", type="secondary"):
+        agregar_mano_obra(role_sel, personas, horas)
+
+if st.session_state.items_mano_obra:
+    st.dataframe(pd.DataFrame(st.session_state.items_mano_obra), use_container_width=True)
+else:
+    st.info("Agrega roles y horas para calcular el costo directo de mano de obra.")
+
+st.markdown("---")
+st.subheader("3. Totales")
+
+costo_mat, costo_mo, costo_directo, precio_venta = calcular_totales()
+
+col_costos, col_margen = st.columns([2, 1])
+with col_costos:
+    st.metric("Costo materiales", formatear_moneda(costo_mat))
+    st.metric("Costo mano de obra", formatear_moneda(costo_mo))
+with col_margen:
+    st.session_state.gastos_generales = st.number_input(
+        "Gastos generales (transporte, viáticos, etc.)",
+        min_value=0.0,
+        step=10.0,
+        value=float(st.session_state.gastos_generales),
+    )
+    st.session_state.margen = st.slider(
+        "Margen de ganancia (%)", min_value=0, max_value=100, value=int(st.session_state.margen), step=1
+    )
+
+st.metric("Costo directo (materiales + mano de obra + gastos)", formatear_moneda(costo_directo))
+st.metric("Precio de venta total", formatear_moneda(precio_venta))
+
+st.markdown("---")
+
+if st.button("Generar resumen", type="primary"):
+    resumen_lines = [
+        "Resumen de cotización",
+        f"Cliente: {cliente or 'N/D'}",
+        f"Fecha: {fecha.strftime('%d/%m/%Y')}",
+        f"Área: {area}",
+        f"Tipo de servicio: {tipo_servicio}",
+        "",
+        "Materiales y equipos:",
+    ]
+
+    if st.session_state.items_materiales:
+        for item in st.session_state.items_materiales:
+            resumen_lines.append(
+                f"- {item['Nombre']} | Cant: {item['Cantidad']} {item['Unidad']} | Subtotal: {formatear_moneda(item['Subtotal'])}"
+            )
+    else:
+        resumen_lines.append("- Sin materiales registrados")
+
+    resumen_lines.append("")
+    resumen_lines.append("Mano de obra:")
+    if st.session_state.items_mano_obra:
+        for item in st.session_state.items_mano_obra:
+            resumen_lines.append(
+                f"- {item['Cargo']} | Personas: {item['Personas']} | Horas: {item['Horas']} | Subtotal: {formatear_moneda(item['Subtotal'])}"
+            )
+    else:
+        resumen_lines.append("- Sin mano de obra registrada")
+
+    resumen_lines.extend(
+        [
+            "",
+            f"Gastos generales: {formatear_moneda(st.session_state.gastos_generales)}",
+            f"Margen de ganancia: {st.session_state.margen}%",
+            f"Costo directo: {formatear_moneda(costo_directo)}",
+            f"Precio de venta total: {formatear_moneda(precio_venta)}",
+        ]
+    )
+
+    st.success("Resumen generado. Copia y pega en tu correo.")
+    st.text_area("Resumen", value="\n".join(resumen_lines), height=250)
+
+st.caption("Los datos se mantienen mientras dure la sesión activa en el navegador.")
 
EOF
)
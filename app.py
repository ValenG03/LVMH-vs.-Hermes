import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="LVMH vs Hermès · El mercado del lujo",
    page_icon="👜",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Paleta: cuero LV, naranja Hermès, azul francés, oro, crema
LV = "#6B4226"        # marrón cuero / monograma
LV_SOFT = "#A9825E"
HE = "#E8702A"        # naranja Hermès
HE_SOFT = "#F2A56E"
NAVY = "#1F2A44"      # azul francés
GOLD = "#B8975A"
CREAM = "#F6F0E4"
IVORY = "#FBF8F1"
INK = "#2B2118"
MUTED = "#7A6A58"

# ─────────────────────────────────────────────
# ESTILO
# ─────────────────────────────────────────────
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'Inter', sans-serif;
    color: {INK};
}}
.stApp {{
    background: radial-gradient(circle at 15% 0%, #FFFDF8 0%, {CREAM} 45%, #EFE5D3 100%);
}}
.block-container {{ padding-top: 1.6rem; padding-bottom: 2rem; max-width: 1400px; }}
header[data-testid="stHeader"] {{ background: transparent; }}

h1, h2, h3, .serif {{ font-family: 'Cormorant Garamond', serif !important; color: {NAVY}; }}

.hero {{
    background: linear-gradient(120deg, {NAVY} 0%, #2C3A5C 55%, {LV} 100%);
    border-radius: 18px;
    padding: 30px 38px;
    color: {IVORY};
    border: 1px solid {GOLD};
    box-shadow: 0 10px 30px rgba(31,42,68,.18);
    margin-bottom: 18px;
}}
.hero h1 {{ color: {IVORY} !important; font-size: 2.7rem; margin: 0; letter-spacing: .5px; }}
.hero .vs {{ color: {GOLD}; font-style: italic; }}
.hero p {{ color: #E9DFCB; margin: 6px 0 0 0; font-size: 1rem; }}
.hero .tag {{
    display:inline-block; margin-top:14px; padding:4px 12px; border:1px solid {GOLD};
    border-radius:999px; color:{GOLD}; font-size:.78rem; letter-spacing:1.5px; text-transform:uppercase;
}}

.card {{
    background: {IVORY};
    border: 1px solid #E4D6BD;
    border-top: 3px solid {GOLD};
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: 0 4px 14px rgba(107,66,38,.08);
    height: 100%;
}}
.card .label {{
    font-size: .74rem; letter-spacing: 1.4px; text-transform: uppercase; color: {MUTED}; margin-bottom: 10px;
}}
.card .row {{ display:flex; justify-content:space-between; align-items:baseline; margin: 4px 0; }}
.card .brand {{ font-size:.82rem; font-weight:600; }}
.card .val {{ font-family:'Cormorant Garamond', serif; font-size:1.65rem; font-weight:700; }}
.card .delta {{ font-size:.75rem; color:{MUTED}; }}
.lv {{ color: {LV}; }}
.he {{ color: {HE}; }}

.section {{
    font-family:'Cormorant Garamond', serif; font-size:1.7rem; color:{NAVY};
    border-bottom: 1px solid {GOLD}; padding-bottom: 4px; margin: 26px 0 10px 0;
}}
.insight {{
    background: #F1E8D8; border-left: 4px solid {GOLD}; border-radius: 8px;
    padding: 12px 16px; font-size: .92rem; color: {INK}; margin-top: 6px;
}}
.footer {{ font-size:.78rem; color:{MUTED}; margin-top: 28px; line-height:1.6; }}

div[data-testid="stTabs"] button p {{ font-family:'Inter', sans-serif; font-weight:600; color:{NAVY}; }}
div[data-testid="stTabs"] button[aria-selected="true"] {{ border-bottom-color: {GOLD} !important; }}
div[role="radiogroup"] label p {{ font-weight:600; color:{NAVY}; }}
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# DATOS OFICIALES (millones de euros)
# Fuentes: comunicados de resultados anuales y semestrales de LVMH y Hermès
# ─────────────────────────────────────────────
YEARS = [2021, 2022, 2023, 2024, 2025]

annual = pd.DataFrame({
    "Año": YEARS * 2,
    "Empresa": ["LVMH"] * 5 + ["Hermès"] * 5,
    "Ingresos": [64215, 79184, 86153, 84683, 80807,
                 8982, 11602, 13427, 15170, 16002],
    "Resultado operativo": [17151, 21055, 22802, 19571, 17755,
                            3530, 4697, 5650, 6150, 6569],
    "Beneficio neto": [12036, 14084, 15174, 12550, 10878,
                       2445, 3367, 4311, 4603, 4524],
})
annual["Margen operativo %"] = annual["Resultado operativo"] / annual["Ingresos"] * 100
annual["Margen neto %"] = annual["Beneficio neto"] / annual["Ingresos"] * 100
annual["Crecimiento %"] = annual.groupby("Empresa")["Ingresos"].pct_change() * 100

# KPIs por período
KPI = {
    "Año 2025": {
        "LVMH": dict(ing=80807, rop=17755, neto=10878, org=-1.0, rep=-4.6, fcf=11333,
                     caja=-6857, empleados="211.000+", div=13.0),
        "Hermès": dict(ing=16002, rop=6569, neto=4524, org=8.9, rep=5.5, fcf=3880,
                       caja=12773, empleados="26.494", div=18.0),
    },
    "1er semestre 2026": {
        "LVMH": dict(ing=38644, rop=8691, neto=5697, org=2.0, rep=-2.9, fcf=4100,
                     caja=-8245, empleados="211.000+", div=None),
        "Hermès": dict(ing=8163, rop=3351, neto=2238, org=6.1, rep=1.6, fcf=2182,
                       caja=12926, empleados="27.107", div=None),
    },
}

# Ingresos trimestrales (M€)
quarters = ["T1 25", "T2 25", "T3 25", "T4 25", "T1 26", "T2 26"]
q_lvmh = [20311, 19499, 18280, 22717, 19121, 19524]
q_herm = [4129, 3905, 3881, 4087, 4070, 4094]

# Mix de negocio 2025 (M€)
mix_lvmh = pd.DataFrame({
    "Segmento": ["Moda y Marroquinería", "Distribución selectiva", "Relojes y Joyería",
                 "Perfumes y Cosméticos", "Vinos y Espirituosos", "Otros"],
    "Ingresos": [37770, 18348, 10486, 8174, 5358, 671],
})
mix_herm = pd.DataFrame({
    "Segmento": ["Marroquinería y Talabartería", "Prêt-à-porter y Accesorios",
                 "Otros sectores (Joyería, Hogar)", "Seda y Textiles", "Relojes",
                 "Perfume y Belleza", "Otros productos"],
    "Ingresos": [7070, 4525, 2055, 964, 549, 489, 349],
})

# Mix de negocio H1 2026 (M€)
mix_lvmh_h1 = pd.DataFrame({
    "Segmento": mix_lvmh["Segmento"],
    "Ingresos": [18146, 8406, 5225, 3914, 2598, 356],
})
mix_herm_h1 = pd.DataFrame({
    "Segmento": mix_herm["Segmento"],
    "Ingresos": [3761, 2198, 1065, 469, 269, 233, 168],
})

# Geografía 2025 (M€)
geo = pd.DataFrame({
    "Región": ["Francia", "Europa (sin Francia)", "Estados Unidos / Américas*",
               "Japón", "Asia (sin Japón)", "Otros mercados"],
    "LVMH": [6732, 14530, 20686, 6378, 21389, 11091],
    "Hermès": [1575, 2362, 3075, 1591, 6702, 697],
})
geo["LVMH %"] = geo["LVMH"] / geo["LVMH"].sum() * 100
geo["Hermès %"] = geo["Hermès"] / geo["Hermès"].sum() * 100

# Rentabilidad por segmento LVMH 2025 (margen operativo %)
seg_margin = pd.DataFrame({
    "Segmento": ["Moda y Marroquinería", "Vinos y Espirituosos", "Relojes y Joyería",
                 "Distribución selectiva", "Perfumes y Cosméticos"],
    "Margen": [13209 / 37770 * 100, 1016 / 5358 * 100, 1514 / 10486 * 100,
               1780 / 18348 * 100, 727 / 8174 * 100],
})

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def fmt_b(x):
    return f"€{x/1000:,.1f} B".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_pct(x, sign=False):
    s = f"{x:+.1f}%" if sign else f"{x:.1f}%"
    return s.replace(".", ",")

def card(label, lv_val, he_val, lv_sub="", he_sub=""):
    return f"""
    <div class="card">
        <div class="label">{label}</div>
        <div class="row"><span class="brand lv">LVMH</span><span class="val lv">{lv_val}</span></div>
        <div class="delta" style="text-align:right">{lv_sub}</div>
        <div class="row"><span class="brand he">HERMÈS</span><span class="val he">{he_val}</span></div>
        <div class="delta" style="text-align:right">{he_sub}</div>
    </div>"""

def base_layout(fig, height=380, title=None):
    fig.update_layout(
        height=height,
        title=dict(text=title, font=dict(family="Cormorant Garamond", size=20, color=NAVY)) if title else None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=INK, size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=60 if title else 30, b=10),
        hoverlabel=dict(bgcolor=IVORY, font_family="Inter"),
    )
    fig.update_xaxes(showgrid=False, linecolor="#D8C8AC")
    fig.update_yaxes(gridcolor="#E7DCC8", zeroline=False)
    return fig

COLORS = {"LVMH": LV, "Hermès": HE}

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown(
    """
<div class="hero">
    <h1>LVMH <span class="vs">vs.</span> Hermès</h1>
    <p>El conglomerado más grande del lujo frente a la maison artesanal más rentable del mundo.
    Análisis comparativo 2021–2026 del mercado global del lujo.</p>
    <span class="tag">Datos oficiales · Resultados anuales y semestrales · Cifras en euros</span>
</div>
""",
    unsafe_allow_html=True,
)

periodo = st.radio("Período", list(KPI.keys()), horizontal=True, label_visibility="collapsed")
L, H = KPI[periodo]["LVMH"], KPI[periodo]["Hermès"]
comp = "vs. 2024" if periodo == "Año 2025" else "vs. 1S 2025"

# ─────────────────────────────────────────────
# TARJETAS KPI
# ─────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(card("Ingresos", fmt_b(L["ing"]), fmt_b(H["ing"]),
                     f"{fmt_pct(L['rep'], True)} publicado {comp}",
                     f"{fmt_pct(H['rep'], True)} publicado {comp}"), unsafe_allow_html=True)
with c2:
    st.markdown(card("Crecimiento orgánico", fmt_pct(L["org"], True), fmt_pct(H["org"], True),
                     "tipo de cambio constante", "tipo de cambio constante"), unsafe_allow_html=True)
with c3:
    st.markdown(card("Resultado operativo recurrente", fmt_b(L["rop"]), fmt_b(H["rop"]),
                     f"margen {fmt_pct(L['rop']/L['ing']*100)}",
                     f"margen {fmt_pct(H['rop']/H['ing']*100)}"), unsafe_allow_html=True)
with c4:
    st.markdown(card("Beneficio neto (grupo)", fmt_b(L["neto"]), fmt_b(H["neto"]),
                     f"margen neto {fmt_pct(L['neto']/L['ing']*100)}",
                     f"margen neto {fmt_pct(H['neto']/H['ing']*100)}"), unsafe_allow_html=True)
with c5:
    lv_caja = f"Deuda neta {fmt_b(abs(L['caja']))}"
    he_caja = f"Caja neta {fmt_b(H['caja'])}"
    st.markdown(card("Free cash flow", fmt_b(L["fcf"]), fmt_b(H["fcf"]), lv_caja, he_caja),
                unsafe_allow_html=True)

ratio_ing = L["ing"] / H["ing"]
ratio_neto = H["neto"] / L["neto"] * 100
st.markdown(
    f"""<div class="insight">LVMH factura <b>{f"{ratio_ing:.1f}".replace(".", ",")} veces</b> más que Hermès,
    pero Hermès genera un beneficio neto equivalente al <b>{ratio_neto:.0f}%</b> del de LVMH:
    por cada €100 vendidos, Hermès retiene <b>€{H['neto']/H['ing']*100:.0f}</b> y LVMH <b>€{L['neto']/L['ing']*100:.0f}</b>.</div>""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# PESTAÑAS — 5 PARÁMETROS
# ─────────────────────────────────────────────
st.markdown('<div class="section">Análisis comparativo</div>', unsafe_allow_html=True)
t1, t2, t3, t4, t5 = st.tabs([
    "① Ingresos", "② Rentabilidad", "③ Evolución trimestral", "④ Mix de negocio", "⑤ Geografía y modelo",
])

# ① INGRESOS
with t1:
    a, b = st.columns([3, 2])
    with a:
        fig = go.Figure()
        for emp in ["LVMH", "Hermès"]:
            d = annual[annual["Empresa"] == emp]
            fig.add_bar(x=d["Año"], y=d["Ingresos"] / 1000, name=emp, marker_color=COLORS[emp],
                        text=[f"{v/1000:.1f}" for v in d["Ingresos"]], textposition="outside",
                        hovertemplate="%{x}: €%{y:.1f} B<extra>" + emp + "</extra>")
        fig.update_layout(barmode="group", yaxis_title="Miles de millones €")
        st.plotly_chart(base_layout(fig, 400, "Ingresos anuales 2021–2025"), width="stretch")
    with b:
        fig = go.Figure()
        for emp in ["LVMH", "Hermès"]:
            d = annual[(annual["Empresa"] == emp) & (annual["Año"] > 2021)]
            fig.add_scatter(x=d["Año"], y=d["Crecimiento %"], name=emp, mode="lines+markers+text",
                            line=dict(color=COLORS[emp], width=3), marker=dict(size=9),
                            text=[f"{v:+.1f}%" for v in d["Crecimiento %"]], textposition="top center",
                            hovertemplate="%{x}: %{y:.1f}%<extra>" + emp + "</extra>")
        fig.add_hline(y=0, line_color=GOLD, line_dash="dot")
        fig.update_layout(yaxis_title="% interanual (publicado)")
        fig.update_xaxes(dtick=1)
        st.plotly_chart(base_layout(fig, 400, "Crecimiento de ingresos"), width="stretch")
    st.markdown(
        """<div class="insight">Desde 2021, Hermès casi <b>duplicó</b> sus ventas (+78%), mientras que LVMH
        alcanzó su pico en 2023 (€86,2 B) y retrocedió dos años seguidos. En 2025 Hermès creció +8,9% orgánico
        y LVMH cayó −1%.</div>""",
        unsafe_allow_html=True,
    )

# ② RENTABILIDAD
with t2:
    a, b = st.columns(2)
    with a:
        fig = go.Figure()
        for emp in ["LVMH", "Hermès"]:
            d = annual[annual["Empresa"] == emp]
            fig.add_scatter(x=d["Año"], y=d["Margen operativo %"], name=f"{emp} · operativo",
                            mode="lines+markers", line=dict(color=COLORS[emp], width=3), marker=dict(size=9),
                            hovertemplate="%{x}: %{y:.1f}%<extra></extra>")
            fig.add_scatter(x=d["Año"], y=d["Margen neto %"], name=f"{emp} · neto",
                            mode="lines+markers", line=dict(color=COLORS[emp], width=2, dash="dot"),
                            marker=dict(size=6), hovertemplate="%{x}: %{y:.1f}%<extra></extra>")
        fig.update_layout(yaxis_title="% sobre ingresos")
        fig.update_xaxes(dtick=1)
        st.plotly_chart(base_layout(fig, 400, "Margen operativo y neto"), width="stretch")
    with b:
        fig = go.Figure()
        for emp in ["LVMH", "Hermès"]:
            d = annual[annual["Empresa"] == emp]
            fig.add_bar(x=d["Año"], y=d["Beneficio neto"] / 1000, name=emp, marker_color=COLORS[emp],
                        text=[f"{v/1000:.1f}" for v in d["Beneficio neto"]], textposition="outside",
                        hovertemplate="%{x}: €%{y:.2f} B<extra>" + emp + "</extra>")
        fig.update_layout(barmode="group", yaxis_title="Miles de millones €")
        st.plotly_chart(base_layout(fig, 400, "Beneficio neto (parte del grupo)"), width="stretch")

    a, b = st.columns([2, 3])
    with a:
        gm = pd.DataFrame({"Empresa": ["LVMH", "Hermès"], "Margen bruto": [53528 / 80807 * 100, 11379 / 16002 * 100]})
        fig = go.Figure(go.Bar(x=gm["Margen bruto"], y=gm["Empresa"], orientation="h",
                               marker_color=[LV, HE], text=[fmt_pct(v) for v in gm["Margen bruto"]],
                               textposition="inside", insidetextfont=dict(color=IVORY, size=14)))
        fig.update_xaxes(range=[0, 100], title="% sobre ingresos")
        st.plotly_chart(base_layout(fig, 260, "Margen bruto 2025"), width="stretch")
    with b:
        sm = seg_margin.sort_values("Margen")
        fig = go.Figure(go.Bar(x=sm["Margen"], y=sm["Segmento"], orientation="h",
                               marker_color=[LV_SOFT] * 4 + [LV], text=[fmt_pct(v) for v in sm["Margen"]],
                               textposition="outside"))
        fig.add_vline(x=6569 / 16002 * 100, line_color=HE, line_dash="dash",
                      annotation_text="Hermès total 41,0%", annotation_font_color=HE)
        fig.update_xaxes(range=[0, 48], title="Margen operativo recurrente 2025 (%)")
        st.plotly_chart(base_layout(fig, 260, "LVMH por división vs. Hermès"), width="stretch")
    st.markdown(
        """<div class="insight">El margen operativo de Hermès (41%) supera incluso al de Moda y Marroquinería,
        la división estrella de LVMH (35%). LVMH pasó de 26,7% en 2021 a 22,0% en 2025; Hermès se mantiene
        estable entre 39% y 42%.</div>""",
        unsafe_allow_html=True,
    )

# ③ EVOLUCIÓN TRIMESTRAL
with t3:
    a, b = st.columns(2)
    with a:
        fig = go.Figure(go.Bar(x=quarters, y=[v / 1000 for v in q_lvmh], marker_color=[LV_SOFT] * 4 + [LV] * 2,
                               text=[f"{v/1000:.1f}" for v in q_lvmh], textposition="outside",
                               hovertemplate="%{x}: €%{y:.2f} B<extra>LVMH</extra>"))
        fig.update_layout(yaxis_title="Miles de millones €")
        fig.update_yaxes(range=[0, 26])
        st.plotly_chart(base_layout(fig, 360, "LVMH · ingresos por trimestre"), width="stretch")
    with b:
        fig = go.Figure(go.Bar(x=quarters, y=[v / 1000 for v in q_herm], marker_color=[HE_SOFT] * 4 + [HE] * 2,
                               text=[f"{v/1000:.2f}" for v in q_herm], textposition="outside",
                               hovertemplate="%{x}: €%{y:.2f} B<extra>Hermès</extra>"))
        fig.update_layout(yaxis_title="Miles de millones €")
        fig.update_yaxes(range=[0, 4.8])
        st.plotly_chart(base_layout(fig, 360, "Hermès · ingresos por trimestre"), width="stretch")

    h1 = pd.DataFrame({
        "Métrica": ["Ingresos", "Resultado operativo", "Beneficio neto"],
        "LVMH 1S25": [39810, 9012, 5698], "LVMH 1S26": [38644, 8691, 5697],
        "Hermès 1S25": [8034, 3327, 2246], "Hermès 1S26": [8163, 3351, 2238],
    })
    fig = go.Figure()
    for emp, col in [("LVMH", LV), ("Hermès", HE)]:
        var = (h1[f"{emp} 1S26"] / h1[f"{emp} 1S25"] - 1) * 100
        fig.add_bar(x=h1["Métrica"], y=var, name=emp, marker_color=col,
                    text=[fmt_pct(v, True) for v in var], textposition="outside")
    fig.add_hline(y=0, line_color=GOLD)
    fig.update_layout(barmode="group", yaxis_title="Variación publicada (%)")
    fig.update_yaxes(range=[-6, 4])
    st.plotly_chart(base_layout(fig, 340, "1er semestre 2026 vs. 1er semestre 2025"), width="stretch")
    st.markdown(
        """<div class="insight">En euros publicados, el tipo de cambio pesa en ambos (−5% en LVMH, −€360 M en Hermès).
        A moneda constante, LVMH volvió a crecer (+2% en el semestre, +3% en el T2) y Hermès sostiene +6%.</div>""",
        unsafe_allow_html=True,
    )

# ④ MIX DE NEGOCIO
with t4:
    mix_per = st.radio("Mix", ["Año 2025", "1er semestre 2026"], horizontal=True,
                       label_visibility="collapsed", key="mix")
    ml, mh = (mix_lvmh, mix_herm) if mix_per == "Año 2025" else (mix_lvmh_h1, mix_herm_h1)
    lv_pal = [LV, "#8A5A3B", LV_SOFT, GOLD, "#D6BE94", "#E9DCC4"]
    he_pal = [HE, NAVY, "#F08C4A", "#4A5A7E", HE_SOFT, GOLD, "#E9DCC4"]
    a, b = st.columns(2)
    for col, df, pal, name in [(a, ml, lv_pal, "LVMH"), (b, mh, he_pal, "Hermès")]:
        with col:
            fig = go.Figure(go.Pie(labels=df["Segmento"], values=df["Ingresos"], hole=.58,
                                   marker=dict(colors=pal, line=dict(color=IVORY, width=2)),
                                   textinfo="percent", sort=False,
                                   hovertemplate="%{label}<br>€%{value:,.0f} M · %{percent}<extra></extra>"))
            fig.add_annotation(text=f"<b>{name}</b><br>{fmt_b(df['Ingresos'].sum())}", showarrow=False,
                               font=dict(family="Cormorant Garamond", size=20, color=COLORS[name]))
            fig.update_layout(legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"))
            st.plotly_chart(base_layout(fig, 430, f"{name} · ingresos por división"), width="stretch")
    st.markdown(
        """<div class="insight"><b>Dos modelos opuestos:</b> LVMH es un portafolio de +75 maisons en cinco industrias
        (de Louis Vuitton a Sephora y Moët). Hermès es una sola marca con 16 métiers, donde la marroquinería
        (Birkin, Kelly) explica ~44% de las ventas.</div>""",
        unsafe_allow_html=True,
    )

# ⑤ GEOGRAFÍA Y MODELO
with t5:
    a, b = st.columns([3, 2])
    with a:
        fig = go.Figure()
        fig.add_bar(y=geo["Región"], x=geo["LVMH %"], name="LVMH", orientation="h", marker_color=LV,
                    text=[fmt_pct(v) for v in geo["LVMH %"]], textposition="outside")
        fig.add_bar(y=geo["Región"], x=geo["Hermès %"], name="Hermès", orientation="h", marker_color=HE,
                    text=[fmt_pct(v) for v in geo["Hermès %"]], textposition="outside")
        fig.update_layout(barmode="group", xaxis_title="% de ingresos 2025")
        fig.update_yaxes(autorange="reversed")
        fig.update_xaxes(range=[0, 50])
        st.plotly_chart(base_layout(fig, 430, "Peso de cada región en las ventas 2025"), width="stretch")
        st.caption("*LVMH reporta Estados Unidos; Hermès reporta Américas. Hermès: ventas por destino.")
    with b:
        modelo = pd.DataFrame({
            "Dimensión": ["Estructura", "Marcas", "Empleados", "Producción",
                          "Distribución", "Dividendo 2025", "Posición financiera"],
            "LVMH": ["Conglomerado multi-industria", "+75 maisons", "+211.000",
                     "Mixta, global", "Propia + Sephora/DFS", "€13,00 / acción", "Deuda neta €6,9 B"],
            "Hermès": ["Maison única, familiar", "1 marca · 16 métiers", "26.494",
                       "55% en talleres propios · 75% hecho en Francia", "Red exclusiva propia",
                       "€18,00 / acción", "Caja neta €12,8 B"],
        })
        st.markdown('<p class="serif" style="font-size:1.3rem;margin:8px 0 4px 0;">Modelo de negocio</p>',
                    unsafe_allow_html=True)
        st.dataframe(modelo, hide_index=True, width="stretch", height=290)
    st.markdown(
        """<div class="insight">Asia (sin Japón) es el primer mercado de ambos, pero pesa mucho más en Hermès (42%)
        que en LVMH (26%). LVMH tiene mayor exposición a EE.UU. y a Europa, y depende más del consumo aspiracional;
        Hermès vende a una clientela de ultra alto poder adquisitivo con escasez deliberada de oferta.</div>""",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# FUENTES
# ─────────────────────────────────────────────
st.markdown(
    """
<div class="footer">
<b>Fuentes oficiales:</b> LVMH — comunicados de resultados anuales 2021–2025 (27/01/2026) y semestrales 2026 (27/07/2026),
Informe Anual Interactivo 2025 · Hermès International — resultados anuales 2021–2025 (12/02/2026) y semestrales 2026 (29/07/2026).<br>
Resultado operativo = <i>profit from recurring operations</i> (LVMH) / <i>recurring operating income</i> (Hermès).
Free cash flow = <i>operating free cash flow</i> (LVMH) / <i>adjusted free cash flow</i> (Hermès).
Beneficio neto 2025 de Hermès incluye la contribución excepcional sobre grandes empresas en Francia (sin ella: €4,86 B).
Cifras en millones de euros, publicadas salvo indicación de crecimiento orgánico.
</div>
""",
    unsafe_allow_html=True,
)

import base64
import io
from pathlib import Path

import numpy as np
from PIL import Image

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

SERIF = "'Source Serif 4', Georgia, serif"   # clásica, formal, cifras legibles
SANS = "Inter, sans-serif"

# ─────────────────────────────────────────────
# ESTILO
# ─────────────────────────────────────────────
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'Inter', sans-serif;
    color: {INK};
}}
.stApp {{
    background: radial-gradient(circle at 15% 0%, #FFFDF8 0%, {CREAM} 45%, #EFE5D3 100%);
}}
.block-container {{ padding-top: 1.6rem; padding-bottom: 2rem; max-width: 1400px; }}
header[data-testid="stHeader"] {{ background: transparent; }}

h1, h2, h3, .serif {{
    font-family: 'Source Serif 4', Georgia, serif !important; color: {NAVY};
    font-variant-numeric: lining-nums;
}}

.hero {{
    position: relative;
    background: linear-gradient(180deg, #FFFDF8 0%, #F7F0E3 100%);
    border: 1px solid {GOLD};
    border-radius: 18px;
    box-shadow: inset 0 0 0 7px #FFFDF8, inset 0 0 0 8px rgba(184,151,90,.45), 0 10px 28px rgba(107,66,38,.10);
    padding: 34px 44px 28px 44px;
    margin-bottom: 20px;
    overflow: hidden;
}}
.hero::before {{
    content: ""; position: absolute; left: 0; right: 0; top: 0; height: 5px;
    background: linear-gradient(90deg, {LV} 0%, {LV} 45%, {GOLD} 50%, {HE} 55%, {HE} 100%);
}}
.hero-brands {{
    display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 28px;
}}
.brand-slot {{ display: flex; flex-direction: column; align-items: center; gap: 18px; min-width: 0; }}
.brand-slot .logo {{ height: 104px; display: flex; align-items: center; justify-content: center; }}
.brand-slot img {{ max-height: 100%; max-width: 100%; object-fit: contain; }}
.brand-slot.lvmh img {{ height: 70px; }}
.brand-slot.hermes img {{ height: 104px; }}
.brand-slot .cap {{
    font-size: .72rem; letter-spacing: 2px; text-transform: uppercase; color: {MUTED};
    padding-top: 8px; border-top: 2px solid; min-width: 210px; text-align: center;
}}
.brand-slot.lvmh .cap {{ border-color: {LV}; }}
.brand-slot.hermes .cap {{ border-color: {HE}; }}
.vs-medal {{
    width: 64px; height: 64px; border-radius: 50%; border: 1px solid {GOLD};
    box-shadow: inset 0 0 0 4px #FFFDF8, inset 0 0 0 5px rgba(184,151,90,.5);
    display: flex; align-items: center; justify-content: center;
    font-family: 'Source Serif 4', Georgia, serif; font-style: italic; font-size: 1.35rem; color: {GOLD};
    background: #FFFDF8;
}}
.hero-rule {{
    height: 1px; margin: 26px auto 18px auto; max-width: 760px;
    background: linear-gradient(90deg, transparent, {GOLD}, transparent);
}}
.hero h1 {{
    text-align: center; color: {INK} !important; font-size: 2.05rem; font-weight: 600;
    margin: 0; padding: 0; letter-spacing: .3px;
}}
.hero p {{ text-align: center; color: {MUTED}; margin: 8px auto 0 auto; font-size: 1rem; max-width: 780px; }}
.hero .tags {{ text-align: center; margin-top: 16px; }}
.hero .tag {{
    display:inline-block; padding:4px 14px; border:1px solid {GOLD}; border-radius:999px;
    color:{LV}; font-size:.72rem; letter-spacing:1.6px; text-transform:uppercase; background:#FFFDF8;
}}
@media (max-width: 760px) {{
    .hero {{ padding: 26px 18px 22px 18px; }}
    .hero-brands {{ grid-template-columns: 1fr; gap: 16px; }}
    .brand-slot.lvmh img {{ height: 52px; }}
    .brand-slot.hermes img {{ height: 84px; }}
    .vs-medal {{ margin: 0 auto; width: 48px; height: 48px; font-size: 1.1rem; }}
    .hero h1 {{ font-size: 1.6rem; }}
}}

.card {{
    background: {IVORY};
    border: 1px solid #E4D6BD;
    border-top: 3px solid {GOLD};
    border-radius: 14px;
    padding: 16px 18px 14px 18px;
    box-shadow: 0 4px 14px rgba(107,66,38,.08);
    min-height: 178px;
}}
.card .label {{
    font-size: .76rem; letter-spacing: 1.4px; text-transform: uppercase; color: {NAVY};
    font-weight: 600; margin-bottom: 12px;
}}
.card .row {{ display:flex; justify-content:space-between; align-items:center; margin: 2px 0; }}
.card .brand {{ font-size:.8rem; font-weight:600; letter-spacing:.5px; }}
.card .val {{
    font-family: 'Source Serif 4', Georgia, serif; font-size: 1.5rem; font-weight: 600;
    font-variant-numeric: lining-nums tabular-nums; letter-spacing: 0;
}}
.card .delta {{ font-size:.74rem; color:{MUTED}; text-align:right; margin-bottom: 8px; }}
.lv {{ color: {LV}; }}
.he {{ color: {HE}; }}

.section {{
    font-family: 'Source Serif 4', Georgia, serif; font-size:1.6rem; font-weight:600; color:{NAVY};
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
label[data-testid="stRadioOption"] > div > div:first-child {{ border-color: {GOLD} !important; }}
label[data-testid="stRadioOption"][data-selected="true"] > div > div:first-child {{
    background-color: {LV} !important; border-color: {LV} !important;
}}
div[data-baseweb="tab-highlight"] {{ background-color: {GOLD} !important; }}
[data-baseweb="tab"][aria-selected="true"] * {{ color: {LV} !important; }}
[data-testid="stTab"] p {{ font-weight:600; color:{NAVY}; }}
[data-testid="stTab"][aria-selected="true"] p {{ color: {LV} !important; }}
[data-testid="stTab"] .react-aria-SelectionIndicator {{ background-color: {GOLD} !important; }}

.mtable {{ width:100%; border-collapse:collapse; background:{IVORY}; border:1px solid #E4D6BD;
          border-radius:12px; overflow:hidden; font-size:.86rem; }}
.mtable th {{ background:{NAVY}; color:{IVORY}; text-align:left; padding:9px 12px; font-weight:600; }}
.mtable th.lv {{ background:{LV}; }} .mtable th.he {{ background:{HE}; }}
.mtable td {{ padding:9px 12px; border-top:1px solid #EADFCB; vertical-align:top; line-height:1.35; }}
.mtable td:first-child {{ color:{MUTED}; font-weight:600; white-space:nowrap; }}
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

# Períodos base
FY25 = {
    "LVMH": dict(ing=80807, rop=17755, neto=10878, fcf=11333, caja=-6857, org=-1.0, prev=84683),
    "Hermès": dict(ing=16002, rop=6569, neto=4524, fcf=3880, caja=12773, org=8.9, prev=15170),
}
H126 = {
    "LVMH": dict(ing=38644, rop=8691, neto=5697, fcf=4100, caja=-8245, org=2.0, prev=39810),
    "Hermès": dict(ing=8163, rop=3351, neto=2238, fcf=2182, caja=12926, org=6.1, prev=8034),
}
# Acumulado 18 meses: año 2025 + 1er semestre 2026 (posición de caja/deuda al 30/06/2026)
ACUM = {
    emp: dict(
        ing=FY25[emp]["ing"] + H126[emp]["ing"],
        rop=FY25[emp]["rop"] + H126[emp]["rop"],
        neto=FY25[emp]["neto"] + H126[emp]["neto"],
        fcf=FY25[emp]["fcf"] + H126[emp]["fcf"],
        caja=H126[emp]["caja"],
        org=None,
        prev=FY25[emp]["prev"] + H126[emp]["prev"],   # 2024 + 1S 2025
    )
    for emp in ["LVMH", "Hermès"]
}
KPI = {"Año 2025": FY25, "1er semestre 2026": H126, "Acumulado 2025 + 1S 2026": ACUM}
COMP = {"Año 2025": "vs. 2024", "1er semestre 2026": "vs. 1S 2025",
        "Acumulado 2025 + 1S 2026": "vs. 2024 + 1S 2025"}

# Ingresos trimestrales (M€)
quarters = ["T1 25", "T2 25", "T3 25", "T4 25", "T1 26", "T2 26"]
q_lvmh = [20311, 19499, 18280, 22717, 19121, 19524]
q_herm = [4129, 3905, 3881, 4087, 4070, 4094]

# Mix de negocio (M€)
SEG_LV = ["Moda y Marroquinería", "Distribución selectiva", "Relojes y Joyería",
          "Perfumes y Cosméticos", "Vinos y Espirituosos", "Otros"]
SEG_HE = ["Marroquinería y Talabartería", "Prêt-à-porter y Accesorios",
          "Joyería y Hogar", "Seda y Textiles", "Relojes",
          "Perfume y Belleza", "Otros productos"]
MIX = {
    "Año 2025": ([37770, 18348, 10486, 8174, 5358, 671],
                 [7070, 4525, 2055, 964, 549, 489, 349]),
    "1er semestre 2026": ([18146, 8406, 5225, 3914, 2598, 356],
                          [3761, 2198, 1065, 469, 269, 233, 168]),
}
MIX["Acumulado 2025 + 1S 2026"] = (
    [a + b for a, b in zip(MIX["Año 2025"][0], MIX["1er semestre 2026"][0])],
    [a + b for a, b in zip(MIX["Año 2025"][1], MIX["1er semestre 2026"][1])],
)

# Geografía 2025 (M€)
geo = pd.DataFrame({
    "Región": ["Francia", "Europa (sin Francia)", "EE.UU. / Américas*",
               "Japón", "Asia (sin Japón)", "Otros mercados"],
    "LVMH": [6732, 14530, 20686, 6378, 21389, 11091],
    "Hermès": [1575, 2362, 3075, 1591, 6702, 697],
})
geo["LVMH %"] = geo["LVMH"] / geo["LVMH"].sum() * 100
geo["Hermès %"] = geo["Hermès"] / geo["Hermès"].sum() * 100

# Rentabilidad por división LVMH 2025 (margen operativo %)
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
    x = round(x, 1) + 0.0
    if x == 0:
        x = 0.0
    s = f"{x:+.1f}%" if sign else f"{x:.1f}%"
    return s.replace(".", ",")

def card(label, lv_val, he_val, lv_sub="", he_sub=""):
    return f"""
    <div class="card">
        <div class="label">{label}</div>
        <div class="row"><span class="brand lv">LVMH</span><span class="val lv">{lv_val}</span></div>
        <div class="delta">{lv_sub}</div>
        <div class="row"><span class="brand he">HERMÈS</span><span class="val he">{he_val}</span></div>
        <div class="delta">{he_sub}</div>
    </div>"""

def base_layout(fig, height=400, title=None, legend="bottom", xtitle=False, top=None):
    """Título arriba a la izquierda; leyenda debajo del gráfico (o a la derecha) sin pisar datos."""
    top = top or (64 if title else 24)
    if legend == "bottom":
        leg = dict(orientation="h", xanchor="center", x=0.5, yanchor="top",
                   y=-0.26 if xtitle else -0.12, font=dict(size=12))
        bottom = 110 if xtitle else 70
    elif legend == "right":
        leg = dict(orientation="v", xanchor="left", x=1.02, yanchor="middle", y=0.5,
                   font=dict(size=12), itemsizing="constant")
        bottom = 20
    else:
        leg = None
        bottom = 60 if xtitle else 30
    fig.update_layout(
        height=height,
        title=dict(text=title, x=0, xanchor="left", y=0.98, yanchor="top",
                   font=dict(family=SERIF, size=19, color=NAVY)) if title else None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=SANS, color=INK, size=12),
        showlegend=legend is not None,
        legend=leg,
        margin=dict(l=10, r=10, t=top, b=bottom),
        hoverlabel=dict(bgcolor=IVORY, font_family=SANS),
        uniformtext=dict(minsize=10, mode="hide"),
    )
    fig.update_xaxes(showgrid=False, linecolor="#D8C8AC")
    fig.update_yaxes(gridcolor="#E7DCC8", zeroline=False)
    fig.update_traces(cliponaxis=False, selector=dict(type="bar"))
    fig.update_traces(cliponaxis=False, selector=dict(type="scatter"))
    return fig

COLORS = {"LVMH": LV, "Hermès": HE}

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
BASE = Path(__file__).parent

@st.cache_data
def logo_b64(names):
    """Busca el logo en el repo, le quita el fondo (blanco o cuadriculado) y lo tiñe en tono tinta."""
    p = next((BASE / n for n in names if (BASE / n).exists()), None)
    if p is None:
        return None
    im = Image.open(p).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    lum = np.asarray(bg.convert("L"), dtype=float)
    alpha = (np.clip((170 - lum) / 110, 0, 1) * 255).astype(np.uint8)
    out = np.zeros((*lum.shape, 4), dtype=np.uint8)
    out[..., 0], out[..., 1], out[..., 2] = 43, 33, 24      # INK
    out[..., 3] = alpha
    img = Image.fromarray(out)
    if img.getbbox():
        img = img.crop(img.getbbox())
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def logo(names, alt):
    b64 = logo_b64(tuple(names))
    if b64:
        return f'<img src="data:image/png;base64,{b64}" alt="{alt}">'
    return f'<span class="serif" style="font-size:2.4rem;font-weight:600;color:{INK}">{alt}</span>'

st.markdown(
    f'''<div class="hero">
<div class="hero-brands">
<div class="brand-slot lvmh"><div class="logo">{logo(["LVMH.png", "lvmh.png", "logo_lvmh.png"], "LVMH")}</div>
<div class="cap">Grupo · 75+ maisons · Fundado en 1987</div></div>
<div class="vs-medal">vs.</div>
<div class="brand-slot hermes"><div class="logo">{logo(["hermes.png", "Hermes.png", "logo_hermes.png"], "Hermès")}</div>
<div class="cap">Maison · 16 métiers · Fundada en 1837</div></div>
</div>
<div class="hero-rule"></div>
<h1>El mercado global del lujo</h1>
<p>El conglomerado más grande del sector frente a la maison artesanal más rentable del mundo.
Análisis comparativo 2021 – 2026.</p>
<div class="tags"><span class="tag">Datos oficiales · Resultados anuales y semestrales · Cifras en euros</span></div>
</div>''',
    unsafe_allow_html=True,
)

periodo = st.radio("Período", list(KPI.keys()), horizontal=True, label_visibility="collapsed")
L, H = KPI[periodo]["LVMH"], KPI[periodo]["Hermès"]
comp = COMP[periodo]
acum = periodo.startswith("Acumulado")

# ─────────────────────────────────────────────
# TARJETAS KPI
# ─────────────────────────────────────────────
def growth(d):
    return (d["ing"] / d["prev"] - 1) * 100

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    sub_lv = "18 meses · ene-25 a jun-26" if acum else f"{fmt_pct(growth(L), True)} publicado {comp}"
    sub_he = "18 meses · ene-25 a jun-26" if acum else f"{fmt_pct(growth(H), True)} publicado {comp}"
    st.markdown(card("Ingresos", fmt_b(L["ing"]), fmt_b(H["ing"]), sub_lv, sub_he), unsafe_allow_html=True)
with c2:
    st.markdown(card("Margen operativo",
                     fmt_pct(L["rop"] / L["ing"] * 100), fmt_pct(H["rop"] / H["ing"] * 100),
                     f"resultado operativo {fmt_b(L['rop'])}",
                     f"resultado operativo {fmt_b(H['rop'])}"), unsafe_allow_html=True)
with c3:
    st.markdown(card("Beneficio neto", fmt_b(L["neto"]), fmt_b(H["neto"]),
                     f"margen neto {fmt_pct(L['neto']/L['ing']*100)}",
                     f"margen neto {fmt_pct(H['neto']/H['ing']*100)}"), unsafe_allow_html=True)
with c4:
    st.markdown(card("Free Cash Flow", fmt_b(L["fcf"]), fmt_b(H["fcf"]),
                     f"deuda neta {fmt_b(abs(L['caja']))}",
                     f"caja neta {fmt_b(H['caja'])}"), unsafe_allow_html=True)
with c5:
    if acum:
        st.markdown(card("Crecimiento publicado",
                         fmt_pct(growth(L), True), fmt_pct(growth(H), True),
                         f"publicado {comp}", f"publicado {comp}"), unsafe_allow_html=True)
    else:
        st.markdown(card("Crecimiento orgánico", fmt_pct(L["org"], True), fmt_pct(H["org"], True),
                         f"tipo de cambio constante {comp}", f"tipo de cambio constante {comp}"),
                    unsafe_allow_html=True)

ratio_ing = f"{L['ing'] / H['ing']:.1f}".replace(".", ",")
ratio_neto = H["neto"] / L["neto"] * 100
st.markdown(
    f"""<div class="insight">LVMH factura <b>{ratio_ing} veces</b> más que Hermès,
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
                        text=[f"{v/1000:.1f}".replace(".", ",") for v in d["Ingresos"]],
                        textposition="outside", textfont=dict(family=SERIF, size=12),
                        hovertemplate="%{x}: €%{y:.1f} B<extra>" + emp + "</extra>")
        fig.update_layout(barmode="group", yaxis_title="Miles de millones €")
        fig.update_yaxes(range=[0, 100])
        st.plotly_chart(base_layout(fig, 420, "Ingresos anuales 2021–2025"), width="stretch")
    with b:
        fig = go.Figure()
        for emp, pos in [("LVMH", "bottom center"), ("Hermès", "top center")]:
            d = annual[(annual["Empresa"] == emp) & (annual["Año"] > 2021)]
            fig.add_scatter(x=d["Año"], y=d["Crecimiento %"], name=emp, mode="lines+markers+text",
                            line=dict(color=COLORS[emp], width=3), marker=dict(size=9),
                            text=[fmt_pct(v, True) for v in d["Crecimiento %"]], textposition=pos,
                            textfont=dict(color=COLORS[emp], size=11),
                            hovertemplate="%{x}: %{y:.1f}%<extra>" + emp + "</extra>")
        fig.add_hline(y=0, line_color=GOLD, line_dash="dot")
        fig.update_layout(yaxis_title="% interanual (publicado)")
        fig.update_xaxes(dtick=1, range=[2021.6, 2025.4])
        fig.update_yaxes(range=[-12, 38])
        st.plotly_chart(base_layout(fig, 420, "Crecimiento de ingresos"), width="stretch")
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
            fig.add_scatter(x=d["Año"], y=d["Margen operativo %"], name=f"{emp} · margen operativo",
                            mode="lines+markers", line=dict(color=COLORS[emp], width=3), marker=dict(size=9),
                            hovertemplate="%{x}: %{y:.1f}%<extra>" + emp + " · operativo</extra>")
            fig.add_scatter(x=d["Año"], y=d["Margen neto %"], name=f"{emp} · margen neto",
                            mode="lines+markers", line=dict(color=COLORS[emp], width=2, dash="dot"),
                            marker=dict(size=6),
                            hovertemplate="%{x}: %{y:.1f}%<extra>" + emp + " · neto</extra>")
        fig.update_layout(yaxis_title="% sobre ingresos", legend_traceorder="normal")
        fig.update_xaxes(dtick=1)
        fig.update_yaxes(range=[0, 50])
        st.plotly_chart(base_layout(fig, 440, "Margen operativo y margen neto"), width="stretch")
    with b:
        fig = go.Figure()
        for emp in ["LVMH", "Hermès"]:
            d = annual[annual["Empresa"] == emp]
            fig.add_bar(x=d["Año"], y=d["Beneficio neto"] / 1000, name=emp, marker_color=COLORS[emp],
                        text=[f"{v/1000:.1f}".replace(".", ",") for v in d["Beneficio neto"]],
                        textposition="outside", textfont=dict(family=SERIF, size=12),
                        hovertemplate="%{x}: €%{y:.2f} B<extra>" + emp + "</extra>")
        fig.update_layout(barmode="group", yaxis_title="Miles de millones €")
        fig.update_yaxes(range=[0, 18])
        st.plotly_chart(base_layout(fig, 440, "Beneficio neto (parte del grupo)"), width="stretch")

    a, b = st.columns([2, 3])
    with a:
        gm = pd.DataFrame({"Empresa": ["LVMH", "Hermès"],
                           "Margen bruto": [53528 / 80807 * 100, 11379 / 16002 * 100]})
        fig = go.Figure(go.Bar(x=gm["Margen bruto"], y=gm["Empresa"], orientation="h",
                               marker_color=[LV, HE], text=[fmt_pct(v) for v in gm["Margen bruto"]],
                               textposition="inside", insidetextanchor="end",
                               textfont=dict(color=IVORY, size=14, family=SERIF),
                               hovertemplate="%{y}: %{x:.1f}%<extra></extra>"))
        fig.update_xaxes(range=[0, 100], title="% sobre ingresos")
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(base_layout(fig, 320, "Margen bruto 2025", legend=None, xtitle=True), width="stretch")
    with b:
        sm = seg_margin.sort_values("Margen")
        fig = go.Figure(go.Bar(x=sm["Margen"], y=sm["Segmento"], orientation="h",
                               marker_color=[LV_SOFT] * 4 + [LV], text=[fmt_pct(v) for v in sm["Margen"]],
                               textposition="outside", textfont=dict(family=SERIF, size=12),
                               hovertemplate="%{y}: %{x:.1f}%<extra></extra>"))
        he_m = 6569 / 16002 * 100
        fig.add_vline(x=he_m, line_color=HE, line_dash="dash", line_width=2)
        fig.add_annotation(x=he_m, y=1, yref="paper", yanchor="bottom", xanchor="center",
                           text=f"<b>Hermès total {fmt_pct(he_m)}</b>", showarrow=False,
                           font=dict(color=HE, size=12), bgcolor=IVORY)
        fig.update_xaxes(range=[0, 50], title="Margen operativo recurrente 2025 (%)")
        st.plotly_chart(base_layout(fig, 320, "Divisiones de LVMH vs. Hermès", legend=None, xtitle=True, top=84),
                        width="stretch")
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
                               text=[f"{v/1000:.1f}".replace(".", ",") for v in q_lvmh], textposition="outside",
                               textfont=dict(family=SERIF, size=12),
                               hovertemplate="%{x}: €%{y:.2f} B<extra>LVMH</extra>"))
        fig.update_layout(yaxis_title="Miles de millones €")
        fig.update_yaxes(range=[0, 26])
        st.plotly_chart(base_layout(fig, 380, "LVMH · ingresos por trimestre", legend=None), width="stretch")
    with b:
        fig = go.Figure(go.Bar(x=quarters, y=[v / 1000 for v in q_herm], marker_color=[HE_SOFT] * 4 + [HE] * 2,
                               text=[f"{v/1000:.2f}".replace(".", ",") for v in q_herm], textposition="outside",
                               textfont=dict(family=SERIF, size=12),
                               hovertemplate="%{x}: €%{y:.2f} B<extra>Hermès</extra>"))
        fig.update_layout(yaxis_title="Miles de millones €")
        fig.update_yaxes(range=[0, 4.8])
        st.plotly_chart(base_layout(fig, 380, "Hermès · ingresos por trimestre", legend=None), width="stretch")
    st.caption("Tono claro: 2025 · Tono pleno: 2026")

    h1 = pd.DataFrame({
        "Métrica": ["Ingresos", "Resultado operativo", "Beneficio neto"],
        "LVMH 1S25": [39810, 9012, 5698], "LVMH 1S26": [38644, 8691, 5697],
        "Hermès 1S25": [8034, 3327, 2246], "Hermès 1S26": [8163, 3351, 2238],
    })
    fig = go.Figure()
    for emp, col in [("LVMH", LV), ("Hermès", HE)]:
        var = (h1[f"{emp} 1S26"] / h1[f"{emp} 1S25"] - 1) * 100
        fig.add_bar(x=h1["Métrica"], y=var, name=emp, marker_color=col,
                    text=[fmt_pct(v, True) for v in var], textposition="outside",
                    textfont=dict(family=SERIF, size=12),
                    hovertemplate="%{x}: %{y:.1f}%<extra>" + emp + "</extra>")
    fig.add_hline(y=0, line_color=GOLD)
    fig.update_layout(barmode="group", yaxis_title="Variación publicada (%)")
    fig.update_yaxes(range=[-6, 4])
    st.plotly_chart(base_layout(fig, 380, "1er semestre 2026 vs. 1er semestre 2025"), width="stretch")
    st.markdown(
        """<div class="insight">En euros publicados, el tipo de cambio pesa en ambos (−5% en LVMH, −€360 M en Hermès).
        A moneda constante, LVMH volvió a crecer (+2% en el semestre, +3% en el T2) y Hermès sostiene +6%.</div>""",
        unsafe_allow_html=True,
    )

# ④ MIX DE NEGOCIO
with t4:
    mix_per = st.radio("Mix", list(MIX.keys()), horizontal=True, label_visibility="collapsed", key="mix",
                       index=list(MIX.keys()).index(periodo))
    vals_lv, vals_he = MIX[mix_per]
    lv_pal = [LV, "#8A5A3B", LV_SOFT, GOLD, "#D6BE94", "#E9DCC4"]
    he_pal = [HE, NAVY, "#F08C4A", "#4A5A7E", HE_SOFT, GOLD, "#D9CBB0"]
    a, b = st.columns(2)
    for col, labels, vals, pal, name in [(a, SEG_LV, vals_lv, lv_pal, "LVMH"),
                                         (b, SEG_HE, vals_he, he_pal, "Hermès")]:
        with col:
            tot = sum(vals)
            txt = [fmt_pct(v / tot * 100) if v / tot >= 0.04 else "" for v in vals]
            fig = go.Figure(go.Pie(
                labels=labels, values=vals, hole=.6, sort=False, direction="clockwise",
                marker=dict(colors=pal, line=dict(color=IVORY, width=2)),
                text=txt, textinfo="text", textposition="inside", insidetextorientation="horizontal",
                textfont=dict(family=SERIF, size=13),
                title=dict(text=f"<b>{name}</b><br>{fmt_b(tot)}",
                           font=dict(family=SERIF, size=17, color=COLORS[name])),
                hovertemplate="%{label}<br>€%{value:,.0f} M · %{percent}<extra></extra>",
            ))
            st.plotly_chart(base_layout(fig, 400, f"{name} · ingresos por división", legend="right"),
                            width="stretch")
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
                    text=[fmt_pct(v) for v in geo["LVMH %"]], textposition="outside",
                    textfont=dict(family=SERIF, size=12),
                    hovertemplate="%{y}: %{x:.1f}%<extra>LVMH</extra>")
        fig.add_bar(y=geo["Región"], x=geo["Hermès %"], name="Hermès", orientation="h", marker_color=HE,
                    text=[fmt_pct(v) for v in geo["Hermès %"]], textposition="outside",
                    textfont=dict(family=SERIF, size=12),
                    hovertemplate="%{y}: %{x:.1f}%<extra>Hermès</extra>")
        fig.update_layout(barmode="group", xaxis_title="% de ingresos 2025", bargap=0.25)
        fig.update_yaxes(autorange="reversed")
        fig.update_xaxes(range=[0, 50])
        st.plotly_chart(base_layout(fig, 480, "Peso de cada región en las ventas 2025", xtitle=True),
                        width="stretch")
        st.caption("*LVMH reporta Estados Unidos; Hermès reporta Américas. Hermès: ventas por destino. "
                   "Datos regionales completos disponibles solo para el año 2025.")
    with b:
        filas = [
            ("Estructura", "Conglomerado multi-industria", "Maison única, familiar"),
            ("Marcas", "+75 maisons", "1 marca · 16 métiers"),
            ("Empleados", "+211.000", "26.494"),
            ("Producción", "Mixta, global", "55% en talleres propios · 75% hecho en Francia"),
            ("Distribución", "Red propia + Sephora / DFS", "Red exclusiva propia"),
            ("Dividendo 2025", "€13,00 por acción", "€18,00 por acción"),
            ("Posición financiera", "Deuda neta €6,9 B", "Caja neta €12,8 B"),
        ]
        rows = "".join(f"<tr><td>{d}</td><td>{l}</td><td>{h}</td></tr>" for d, l, h in filas)
        st.markdown('<p class="serif" style="font-size:1.2rem;font-weight:600;margin:8px 0 8px 0;">'
                    'Modelo de negocio</p>'
                    f'<table class="mtable"><tr><th></th><th class="lv">LVMH</th><th class="he">Hermès</th></tr>'
                    f'{rows}</table>', unsafe_allow_html=True)
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
<b>B</b> = miles de millones de euros. Resultado operativo = <i>profit from recurring operations</i> (LVMH) /
<i>recurring operating income</i> (Hermès). Free Cash Flow = <i>operating free cash flow</i> (LVMH) /
<i>adjusted free cash flow</i> (Hermès). <b>Acumulado</b> = suma del año 2025 y el 1er semestre 2026 (18 meses);
deuda/caja neta al 30/06/2026; su crecimiento es publicado (las empresas no informan crecimiento orgánico para ese período).
Beneficio neto 2025 de Hermès incluye la contribución excepcional sobre grandes empresas en Francia (sin ella: €4,86 B).
</div>
""",
    unsafe_allow_html=True,
)

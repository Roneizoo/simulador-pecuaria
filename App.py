import streamlit as st
from sim_recria import render_recria
from sim_confinamento import render_confinamento

st.set_page_config(page_title="Simuladores Econômicos", layout="wide")

st.markdown("<h1 style='text-align:center;'>📊 Simuladores Econômicos</h1>", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2 = st.tabs(["🌱 Recria a Pasto", "🏭 Confinamento"])

with tab1:
    render_recria(prefix="recria")

with tab2:
    render_confinamento(prefix="conf")

import streamlit as st

def render_confinamento(prefix: str = "conf"):

    st.markdown("<h2 style='text-align:center;'>🏭 Análise Econômica do Confinamento</h2>", unsafe_allow_html=True)
    st.markdown("---")

    # ==============================
    # 1) PEGAR AUTOMATICAMENTE OS DADOS DA RECRIA
    # ==============================
    dados_recria = st.session_state.get("recria_output", None)

    if dados_recria is not None:
        peso_inicial_padrao = float(dados_recria.get("peso_final", 350.0))
        preco_compra_padrao = float(dados_recria.get("preco_venda_kg", 11.30))
        st.info(f"Link automático: entrada do confinamento = saída da recria "
                f"(Peso: {peso_inicial_padrao:.2f} kg | Preço: {preco_compra_padrao:.2f} $/kg PV)")
    else:
        peso_inicial_padrao = 350.0
        preco_compra_padrao = 11.30
        st.warning("Ainda não existe saída da Recria. Use a aba Recria primeiro.")

    # ==============================
    # 2) ENTRADAS (COM VALORES PADRÃO VINDO DA RECRIA)
    # ==============================
    st.sidebar.header("Parâmetros de Entrada")

    with st.sidebar.expander("🏭 Confinamento", expanded=True):

        peso_inicial = st.number_input(
            "Peso inicial (kg)", value=peso_inicial_padrao, min_value=0.0, step=1.0,
            format="%.2f", key=f"{prefix}_peso_inicial"
        )

        ganho_dia = st.number_input(
            "Ganho de peso/dia (kg)", value=1.40, min_value=0.0, step=0.05,
            format="%.2f", key=f"{prefix}_ganho_dia"
        )

        dias = st.number_input(
            "Período de trato (dias)", value=110, min_value=1, step=1,
            key=f"{prefix}_dias"
        )

        rendimento_ini = st.number_input(
            "Rendimento inicial (%)", value=50.0, min_value=0.0, max_value=100.0,
            step=0.1, format="%.2f", key=f"{prefix}_rend_ini"
        ) / 100

        rendimento_fim = st.number_input(
            "Rendimento final (%)", value=56.0, min_value=0.0, max_value=100.0,
            step=0.1, format="%.2f", key=f"{prefix}_rend_fim"
        ) / 100

        preco_compra_kg = st.number_input(
            "Valor de compra ($/kg PV)",
            value=preco_compra_padrao,
            min_value=0.0, step=0.01, format="%.2f",
            key=f"{prefix}_preco_compra"
        )

        preco_venda_kg = st.number_input(
            "Valor de venda ($/kg carcaça)", value=4.90, min_value=0.0, step=0.01,
            format="%.2f", key=f"{prefix}_preco_venda"
        )

        diaria = st.number_input(
            "Custo nutricional ($/dia)", value=2.75, min_value=0.0, step=0.1,
            format="%.2f", key=f"{prefix}_diaria"
        )

        servicos_operacionais = st.number_input(
            "Serviços operacionais ($/animal/dia)", value=0.40, min_value=0.0,
            step=0.10, format="%.2f", key=f"{prefix}_servicos"
        )

        custos_extras = st.number_input(
            "Custos extras ($/animal)", value=0.0, min_value=0.0,
            step=0.10, format="%.2f", key=f"{prefix}_extras"
        )

        juros_mes = st.number_input(
            "Juros sobre custo do animal (% ao mês)", value=0.50, min_value=0.0,
            step=0.05, format="%.2f", key=f"{prefix}_juros"
        ) / 100

    # ==============================
    # CÁLCULOS
    # ==============================
    peso_final = peso_inicial + ganho_dia * dias
    carcaca_final = peso_final * rendimento_fim

    ganho_peso = peso_final - peso_inicial
    ganho_carcaca = carcaca_final - (peso_inicial * rendimento_ini)
    carcaca_dia = ganho_carcaca / dias if dias > 0 else 0

    valor_compra = peso_inicial * preco_compra_kg
    custo_nutricional = diaria * dias
    custo_servicos = servicos_operacionais * dias
    despesas_totais = custo_nutricional + custo_servicos + custos_extras

    juros = valor_compra * juros_mes * (dias / 30)
    custo_total = valor_compra + despesas_totais + juros

    receita = carcaca_final * preco_venda_kg
    lucro = receita - custo_total

    margem_lucro = (lucro / receita * 100) if receita > 0 else 0
    roi = (lucro / valor_compra * 100) if valor_compra > 0 else 0
    roi_mensal = (roi / dias) * 30 if dias > 0 else 0
    roi_custo = (lucro / custo_total * 100) if custo_total > 0 else 0
    roi_custo_mensal = (roi_custo / dias) * 30 if dias > 0 else 0

    # ==============================
    # SAÍDAS
    # ==============================
    col1, col2, col3 = st.columns([1.2, 1.2, 1.2])

    with col1:
        st.subheader("⚖️ Indicadores Zootécnicos")
        st.write(f"Peso inicial: **{peso_inicial:.2f} kg**")
        st.write(f"Peso final: **{peso_final:.2f} kg**")
        st.write(f"Dias de trato: **{dias}**")
        st.write(f"Ganho de peso: **{ganho_peso:.2f} kg**")
        st.write(f"Ganho diário: **{ganho_dia:.2f} kg/dia**")
        st.write(f"Carcaça final: **{carcaca_final:.2f} kg**")
        st.write(f"Carcaça/dia: **{carcaca_dia:.2f} kg/dia**")

    with col2:
        st.subheader("💰 Custos")
        st.write(f"Custo animal: **${valor_compra:,.2f}**")
        st.write(f"Custo nutricional: **${custo_nutricional:,.2f}**")
        st.write(f"Serviços: **${custo_servicos:,.2f}**")
        st.write(f"Custos extras: **${custos_extras:,.2f}**")
        st.write(f"Juros: **${juros:,.2f}**")
        st.write(f"🔴 Custo total: **${custo_total:,.2f}**")

    with col3:
        st.subheader("📊 Resultado Econômico")
        st.write(f"Receita: **${receita:,.2f}**")
        st.write(f"Lucro: **${lucro:,.2f}**")
        st.write(f"Margem: **{margem_lucro:.2f}%**")
        st.write(f"ROI: **{roi:.2f}%**")
        st.write(f"ROI mensal: **{roi_mensal:.2f}%/mês**")
        st.write(f"ROI custo total: **{roi_custo:.2f}%**")
        st.write(f"ROI mensal custo total: **{roi_custo_mensal:.2f}%/mês**")

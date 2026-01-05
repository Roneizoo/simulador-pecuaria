# -*- coding: utf-8 -*-
import streamlit as st
import datetime
import io

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm


def render_recria(prefix: str = "recria"):
    st.markdown("<h2 style='text-align: center;'>🐂 Análise Econômica da Recria a Pasto</h2>", unsafe_allow_html=True)
    st.markdown("---")

    # ==============================
    # ENTRADAS (no sidebar, isoladas por prefix/key)
    # ==============================
    st.sidebar.header("Parâmetros de Entrada")

    with st.sidebar.expander("🌱 Recria a Pasto", expanded=True):
        peso_inicial = st.number_input(
            "Peso inicial (kg)", value=175.0, min_value=0.0, step=1.0, format="%.2f",
            key=f"{prefix}_peso_inicial"
        )
        preco_compra_pyg = st.number_input(
            "Preço compra (₲/kg PV)", value=20000.0, min_value=0.0, step=100.0, format="%.2f",
            key=f"{prefix}_preco_compra_pyg"
        )
        cambio = st.number_input(
            "Câmbio (₲/US$)", value=7320.0, min_value=0.0, step=10.0, format="%.2f",
            key=f"{prefix}_cambio"
        )

        dias = st.number_input(
            "Período (dias em pastejo)", value=365, min_value=1, step=1,
            key=f"{prefix}_dias"
        )
        gmd = st.number_input(
            "Ganho médio diário (kg/dia)", value=0.490, min_value=0.0, step=0.01, format="%.2f",
            key=f"{prefix}_gmd"
        )

        custo_aluguel = st.number_input(
            "Custo aluguel (US$/mês)", value=5.40, min_value=0.0, step=0.1, format="%.2f",
            key=f"{prefix}_custo_aluguel"
        )
        custo_nutricional = st.number_input(
            "Custo nutrição (US$/mês)", value=4.0, min_value=0.0, step=0.1, format="%.2f",
            key=f"{prefix}_custo_nutricional"
        )
        custo_operacional = st.number_input(
            "Custo operações (US$/mês)", value=3.44, min_value=0.0, step=0.1, format="%.2f",
            key=f"{prefix}_custo_operacional"
        )

        frete = st.number_input(
            "Frete (US$/cab)", value=8.0, min_value=0.0, step=0.5, format="%.2f",
            key=f"{prefix}_frete"
        )
        comissao = st.number_input(
            "Comissão (US$/cab)", value=4.0, min_value=0.0, step=0.5, format="%.2f",
            key=f"{prefix}_comissao"
        )

        juros_anual = st.number_input(
            "Juros anual (%)", value=8.5, min_value=0.0, step=0.1, format="%.2f",
            key=f"{prefix}_juros_anual"
        ) / 100.0

        preco_venda_kg = st.number_input(
            "Preço venda (US$/kg PV)", value=2.40, min_value=0.0, step=0.01, format="%.2f",
            key=f"{prefix}_preco_venda_kg"
        )

    # ==============================
    # CÁLCULOS
    # ==============================
    valor_compra_usd = (peso_inicial * preco_compra_pyg) / cambio if cambio > 0 else 0
    preco_compra_usd_kg = (preco_compra_pyg / cambio) if cambio > 0 else 0

    agio = ((preco_compra_usd_kg - preco_venda_kg) / preco_venda_kg * 100) if preco_venda_kg > 0 else 0

    peso_final = peso_inicial + gmd * dias
    gpv = peso_final - peso_inicial

    meses = dias / 30.5
    custo_mensal = custo_aluguel + custo_nutricional + custo_operacional
    custo_total_periodo = custo_mensal * meses

    custo_total = valor_compra_usd + custo_total_periodo + frete + comissao

    receita = peso_final * preco_venda_kg
    juros_valor = valor_compra_usd * juros_anual * (dias / 365)

    lucro = receita - custo_total - juros_valor

    margem_periodo = (lucro / receita * 100) if receita > 0 else 0
    margem_mensal = (margem_periodo / meses) if meses > 0 else 0

    roi = (lucro / valor_compra_usd * 100) if valor_compra_usd > 0 else 0
    roi_mensal = (roi / meses) if meses > 0 else 0

    roi_custo = (lucro / custo_total * 100) if custo_total > 0 else 0
    roi_custo_mensal = (roi_custo / meses) if meses > 0 else 0

    data_inicial = datetime.date.today()
    data_final = data_inicial + datetime.timedelta(days=int(dias))

    # ==============================
    # QUADRO DE COMPRA
    # ==============================
    st.subheader("📋 Parâmetros de Compra")
    st.write(f"💱 Câmbio: **₲ {cambio:,.0f}/US$**")
    st.write(f"🐄 Preço bezerro: **₲ {preco_compra_pyg:,.0f}/kg PV**")
    st.write(f"💵 Preço bezerro: **${preco_compra_usd_kg:.2f}/kg PV**")
    st.write(f"🏷️ Preço de venda: **${preco_venda_kg:.2f}/kg PV**")
    st.write(f"📊 Ágio: **{agio:.2f}%**")
    st.markdown("---")

    # ==============================
    # SAÍDAS EM 3 COLUNAS
    # ==============================
    col1, col2, col3 = st.columns([1.2, 1.2, 1.2])

    with col1:
        st.subheader("⚖️ Indicadores Zootécnicos")
        st.write(f"📆 Data inicial: **{data_inicial.strftime('%d/%m/%Y')}**")
        st.write(f"📆 Data final: **{data_final.strftime('%d/%m/%Y')}**")
        st.write(f"📆 Dias em pastejo: **{dias}**")
        st.write(f"🐄 Peso inicial: **{peso_inicial:.2f} kg**")
        st.write(f"⚖️ Peso final: **{peso_final:.2f} kg**")
        st.write(f"➕ GPV: **{gpv:.2f} kg**")
        st.write(f"📈 GMD: **{gmd:.2f} kg/dia**")

    with col2:
        st.subheader("💰 Custos Detalhados")

        st.markdown("<h5>🐂 Custos de Compra</h5>", unsafe_allow_html=True)
        st.write(f"• Custo do animal: **${valor_compra_usd:,.2f}**")
        st.write(f"• 🚚 Frete: **${frete:.2f}**")
        st.write(f"• 🤝 Comissão: **${comissao:.2f}**")

        st.markdown("<h5>🌱 Custos Variáveis de Produção</h5>", unsafe_allow_html=True)
        st.write(f"• Custo aluguel/mês: **${custo_aluguel:.2f}**")
        st.write(f"• Custo nutrição/mês: **${custo_nutricional:.2f}**")
        st.write(f"• Custo operações/mês: **${custo_operacional:.2f}**")

        st.markdown("<h5>📊 Totais</h5>", unsafe_allow_html=True)
        st.write(f"• 🗓️ Custo total período: **${custo_total_periodo:,.2f}**")
        st.write(f"• 🏦 Juros sobre compra do animal: **${juros_valor:.2f}**")
        st.write(f"• 🔴 **Custo total: ${custo_total:,.2f}**")

    with col3:
        st.subheader("📊 Resultado Econômico")
        st.write(f"💵 Receita de venda: **${receita:,.2f}**")
        st.markdown(f"🟢 <span style='color:green'>**Lucro líquido: ${lucro:,.2f}**</span>", unsafe_allow_html=True)
        st.write(f"📈 Margem de lucro: **{margem_periodo:.2f}%**")
        st.write(f"📆 Margem mensal: **{margem_mensal:.2f}%**")
        st.write(f"📊 Retorno sobre investimento: **{roi:.2f}%**")
        st.write(f"📆 ROI mensal: **{roi_mensal:.2f}%/mês**")
        st.write(f"📊 Retorno sobre custo total: **{roi_custo:.2f}%**")
        st.write(f"📆 ROI mensal sobre custo total: **{roi_custo_mensal:.2f}%/mês**")



            # ====== SAÍDA PARA O CONFINAMENTO (LINK AUTOMÁTICO) ======
    st.session_state["recria_output"] = {
        "peso_final": peso_final,
        "preco_venda_kg": preco_venda_kg
    }





      

    # ==============================
    # PDF EXPORT
    # ==============================
    def gerar_pdf():
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=2 * cm, rightMargin=2 * cm,
            topMargin=2 * cm, bottomMargin=2 * cm
        )

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name="TituloSecao",
            fontSize=12, leading=14,
            textColor=colors.HexColor("#003366"),
            spaceBefore=8, spaceAfter=8
        ))

        elementos = []
        elementos.append(Paragraph("Relatório de Viabilidade Econômica – Recria a Pasto", styles["Heading1"]))

        elementos.append(Paragraph("Parâmetros de Compra", styles["TituloSecao"]))
        tabela_params = Table([
            ["Câmbio (₲/US$)", f"{cambio:,.0f}"],
            ["Preço bezerro (₲/kg PV)", f"{preco_compra_pyg:,.0f}"],
            ["Preço bezerro (US$/kg PV)", f"{preco_compra_usd_kg:.2f}"],
            ["Preço de venda (US$/kg PV)", f"{preco_venda_kg:.2f}"],
            ["Ágio (%)", f"{agio:.2f}%"],
        ], colWidths=[doc.width * 0.55, doc.width * 0.35])
        tabela_params.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black)]))
        elementos.append(tabela_params)
        elementos.append(Spacer(1, 12))

        elementos.append(Paragraph("Indicadores Zootécnicos", styles["TituloSecao"]))
        tabela_ind = Table([
            ["Data inicial", data_inicial.strftime('%d/%m/%Y')],
            ["Data final", data_final.strftime('%d/%m/%Y')],
            ["Dias em pastejo", f"{dias}"],
            ["Peso inicial (kg)", f"{peso_inicial:.2f}"],
            ["Peso final (kg)", f"{peso_final:.2f}"],
            ["GPV (kg)", f"{gpv:.2f}"],
            ["GMD (kg/dia)", f"{gmd:.2f}"],
        ], colWidths=[doc.width * 0.55, doc.width * 0.35])
        tabela_ind.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black)]))
        elementos.append(tabela_ind)
        elementos.append(Spacer(1, 12))

        elementos.append(Paragraph("Custos Detalhados", styles["TituloSecao"]))
        tbl_custos = Table([
            ["Custo do animal (US$)", f"{valor_compra_usd:,.2f}"],
            ["Frete (US$)", f"{frete:.2f}"],
            ["Comissão (US$)", f"{comissao:.2f}"],
            ["Custo aluguel/mês (US$)", f"{custo_aluguel:.2f}"],
            ["Custo nutrição/mês (US$)", f"{custo_nutricional:.2f}"],
            ["Custo operações/mês (US$)", f"{custo_operacional:.2f}"],
            ["Custo total período (US$)", f"{custo_total_periodo:,.2f}"],
            ["Juros sobre compra do animal (US$)", f"{juros_valor:.2f}"],
            ["Custo total (US$)", f"{custo_total:,.2f}"],
        ], colWidths=[doc.width * 0.55, doc.width * 0.35])
        tbl_custos.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black)]))
        elementos.append(tbl_custos)
        elementos.append(Spacer(1, 12))

        elementos.append(Paragraph("Resultado Econômico", styles["TituloSecao"]))
        tbl_res = Table([
            ["Receita (US$)", f"{receita:,.2f}"],
            ["Lucro líquido (US$)", f"{lucro:,.2f}"],
            ["Margem período (%)", f"{margem_periodo:.2f}%"],
            ["Margem mensal (%)", f"{margem_mensal:.2f}%"],
            ["ROI (%)", f"{roi:.2f}%"],
            ["ROI mensal (%)", f"{roi_mensal:.2f}%"],
            ["ROI sobre custo total (%)", f"{roi_custo:.2f}%"],
            ["ROI mensal sobre custo total (%)", f"{roi_custo_mensal:.2f}%"],
        ], colWidths=[doc.width * 0.55, doc.width * 0.35])
        tbl_res.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black)]))
        elementos.append(tbl_res)

        doc.build(elementos)
        buffer.seek(0)
        return buffer

    st.markdown("---")
    if st.button("📥 Exportar Relatório PDF", key=f"{prefix}_btn_pdf"):
        pdf_final = gerar_pdf()
        st.download_button(
            "⬇️ Baixar PDF",
            data=pdf_final,
            file_name="recria_pasto.pdf",
            mime="application/pdf",
            key=f"{prefix}_download_pdf"
        )

    # ==============================
    # Sensibilidade
    # ==============================
    st.subheader("📉 Análise de Sensibilidade Interativa")

    colA, colB, colC = st.columns(3)

    with colA:
        sens_preco_compra = st.slider(
            "Preço compra (₲/kg PV)",
            min_value=15000, max_value=25000,
            value=int(preco_compra_pyg), step=100,
            key=f"{prefix}_sens_preco_compra"
        )

    with colB:
        sens_preco_venda = st.slider(
            "Preço venda (US$/kg PV)",
            min_value=1.5, max_value=3.5,
            value=float(preco_venda_kg), step=0.01,
            key=f"{prefix}_sens_preco_venda"
        )

    with colC:
        sens_gmd = st.slider(
            "GMD (kg/dia)",
            min_value=0.3, max_value=1.5,
            value=float(gmd), step=0.01,
            key=f"{prefix}_sens_gmd"
        )

    valor_compra_usd_sens = (peso_inicial * sens_preco_compra) / cambio if cambio > 0 else 0
    peso_final_sens = peso_inicial + sens_gmd * dias
    receita_sens = peso_final_sens * sens_preco_venda
    custo_total_sens = valor_compra_usd_sens + custo_total_periodo + frete + comissao
    juros_sens = valor_compra_usd_sens * juros_anual * (dias / 365)
    lucro_sens = receita_sens - custo_total_sens - juros_sens

    st.markdown("### 🔮 Resultado do Cenário")
    st.write(f"🐂 Preço compra: **₲ {sens_preco_compra:,.0f} | ${(sens_preco_compra/cambio) if cambio>0 else 0:.2f}/kg PV**")
    st.write(f"💵 Preço venda: **${sens_preco_venda:.2f}/kg PV**")
    st.write(f"📈 GMD: **{sens_gmd:.2f} kg/dia**")
    st.write(f"🟢 Lucro líquido: **${lucro_sens:,.2f}**")

    st.subheader("📈 Análise de Impacto")

    incremento_gmd = 0.01  # 10 g/dia
    ganho_extra = incremento_gmd * dias
    lucro_extra = ganho_extra * preco_venda_kg

    st.markdown(f"- ⚖️ A cada **+10 g/dia** no ganho de peso, o lucro **aumenta** em ~ **${lucro_extra:,.2f}** no período de **{dias} dias**.")
    st.markdown(f"- ⚖️ A cada **-10 g/dia** no ganho de peso, o lucro **reduz** em ~ **${lucro_extra:,.2f}** no período de **{dias} dias**.")
    st.markdown("---")

    colX, colY = st.columns(2)
    with colX:
        variacao_compra = st.slider(
            "Variação (%) no valor de compra",
            min_value=0.0, max_value=10.0,
            value=2.0, step=0.1,
            key=f"{prefix}_var_compra"
        )
    with colY:
        variacao_venda = st.slider(
            "Variação (%) no preço de venda",
            min_value=0.0, max_value=10.0,
            value=2.0, step=0.1,
            key=f"{prefix}_var_venda"
        )

    novo_valor_compra = valor_compra_usd * (1 + variacao_compra / 100)
    novo_juros = novo_valor_compra * juros_anual * (dias / 365)
    novo_custo_total = novo_valor_compra + custo_total_periodo + frete + comissao + novo_juros
    novo_lucro = receita - novo_custo_total

    impacto_compra_abs = lucro - novo_lucro
    impacto_compra_pct = (impacto_compra_abs / lucro * 100) if lucro != 0 else 0
    st.markdown(
        f"- 🐂 A cada **+{variacao_compra:.1f}%** no valor de compra do animal, "
        f"o lucro **reduz** em ~ **${impacto_compra_abs:,.2f} ({impacto_compra_pct:.2f}%)**."
    )

    novo_preco_venda = preco_venda_kg * (1 + variacao_venda / 100)
    nova_receita = peso_final * novo_preco_venda
    novo_lucro_venda = nova_receita - novo_custo_total

    impacto_venda_abs = novo_lucro_venda - novo_lucro
    impacto_venda_pct = (impacto_venda_abs / novo_lucro * 100) if novo_lucro != 0 else 0
    st.markdown(
        f"- 💵 A cada **+{variacao_venda:.1f}%** no preço de venda, "
        f"o lucro **aumenta** em ~ **${impacto_venda_abs:,.2f} ({impacto_venda_pct:.2f}%)**."
    )

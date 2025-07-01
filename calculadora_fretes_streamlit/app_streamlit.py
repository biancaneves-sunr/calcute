#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Calculadora de Fretes - Interface Streamlit (Versão 5.0)
-------------------------------------------------------
Interface web para a calculadora de fretes recalibrada.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys
from calculadora_frete import CalculadoraFrete

# Configuração da página
st.set_page_config(
    page_title="Calculadora de Fretes v5.0",
    page_icon="🚚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para melhorar a aparência
st.markdown("""
<style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
        color: #1E88E5;
    }
    .medium-font {
        font-size:24px !important;
        font-weight: bold;
        color: #1E88E5;
    }
    .result-box {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    .result-value {
        font-size: 36px !important;
        font-weight: bold;
        color: #1E88E5;
    }
    .result-label {
        font-size: 16px;
        color: #555;
    }
    .detail-box {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 5px;
        margin-top: 10px;
    }
    .detail-value {
        font-weight: bold;
        color: #333;
    }
    .info-icon {
        color: #1E88E5;
        font-size: 18px;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
        padding: 10px 0;
    }
    .stButton>button:hover {
        background-color: #1565C0;
    }
    .stNumberInput>div>div>input {
        text-align: center;
        font-size: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Título
st.markdown('<p class="big-font">Calculadora de Fretes</p>', unsafe_allow_html=True)

# Formulário de entrada
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("Origem")
        origem = st.text_input("", value="", key="origem", help="Cidade/Estado ou endereço completo")
    
    with col2:
        st.markdown("Destino")
        destino = st.text_input("", value="", key="destino", help="Cidade/Estado ou endereço completo")

    # Modo de cálculo
    st.markdown("Modo de cálculo")
    modo_calculo = st.radio("", ["Por módulos", "Por peso (kg)"], horizontal=True, help="Escolha o modo de cálculo")
    
    # Campo dinâmico baseado no modo de cálculo
    if modo_calculo == "Por módulos":
        st.markdown("Quantidade de Módulos")
        quantidade = st.number_input("", min_value=1, value=200, step=1, key="modulos", help="Número de módulos")
        num_modulos = quantidade
        peso_kg = None
    else:
        st.markdown("Peso em kg")
        quantidade = st.number_input("", min_value=1, value=6000, step=100, key="peso", help="Peso em kg")
        peso_kg = quantidade
        num_modulos = None
    
    # Data prevista
    st.markdown("Data Prevista")
    data_prevista = st.date_input("", value=datetime.now(), key="data", help="Data prevista para o frete")
    
    # Botão de cálculo
    calcular = st.button("Calcular Frete")

# Processamento e exibição do resultado
if calcular:
    # Verificar se os campos obrigatórios foram preenchidos
    if not origem or not destino:
        st.error("Por favor, preencha os campos de origem e destino.")
    else:
        # Inicializar a calculadora
        try:
            # Verificar se o arquivo Excel existe
            arquivo_excel = "/home/ubuntu/upload/BancodeDados-Logistica.xlsx"
            if not os.path.exists(arquivo_excel):
                st.warning("Arquivo de dados não encontrado. Usando valores de referência.")
                calculadora = CalculadoraFrete()
            else:
                calculadora = CalculadoraFrete(arquivo_excel)
            
            # Converter modo de cálculo para o formato esperado pela calculadora
            modo = "modulos" if modo_calculo == "Por módulos" else "peso"
            
            # Calcular frete
            resultado = calculadora.calcular_frete(
                origem,
                destino,
                num_modulos,
                peso_kg,
                data_prevista,
                modo
            )
            
            if resultado['status'] == 'sucesso':
                # Exibir resultado
                st.markdown('<p class="medium-font">Resultado da Cotação</p>', unsafe_allow_html=True)
                
                # Valor estimado do frete
                st.markdown(f"""
                <div class="result-box">
                    <div class="result-value">R$ {resultado['valor_estimado']:.2f}</div>
                    <div class="result-label">Valor estimado do frete</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Valor por quilômetro
                st.markdown(f"""
                <div class="result-box">
                    <div class="result-value" style="color: #4CAF50;">R$ {resultado['valor_por_km']:.2f}/km</div>
                    <div class="result-label">Valor por quilômetro</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Detalhes da cotação e do cálculo
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<p class="medium-font">Detalhes da Cotação</p>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="detail-box">
                        <p><strong>Origem:</strong> {origem}</p>
                        <p><strong>Destino:</strong> {destino}</p>
                        <p><strong>{'Módulos' if modo == 'modulos' else 'Peso'}:</strong> {quantidade} {'módulos' if modo == 'modulos' else 'kg'}</p>
                        <p><strong>Distância:</strong> {resultado['distancia_km']} km</p>
                        <p><strong>Data da Consulta:</strong> {data_prevista.strftime('%d/%m/%Y')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<p class="medium-font">Detalhes do Cálculo</p>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="detail-box">
                        <p><strong>Valor médio base:</strong> R$ {resultado['valor_medio_original']:.2f}</p>
                        <p><strong>Ajuste por {'módulos' if modo == 'modulos' else 'peso'}:</strong> R$ {resultado['ajuste_quantidade']:.2f}</p>
                        <p><strong>Ajuste de inflação:</strong> R$ {resultado['ajuste_inflacao']:.2f}</p>
                        <p><strong>Margem aplicada (10%):</strong> R$ {resultado['margem_aplicada']:.2f}</p>
                        <p><strong>Fretes base:</strong> {resultado.get('fretes_base', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Informações sobre o cálculo
                with st.expander("Informações sobre o cálculo"):
                    st.markdown("""
                    O cálculo do frete é baseado em dados históricos e considera:
                    
                    1. **Valor médio base**: Média de fretes similares em distância e quantidade
                    2. **Ajuste por módulos/peso**: Correção baseada na diferença entre a quantidade solicitada e a média histórica
                    3. **Ajuste de inflação**: Correção monetária baseada na diferença temporal
                    4. **Margem aplicada**: Adicional de 10% sobre o valor final
                    
                    Para fretes curtos (menos de 10km), é utilizada uma lógica específica com valores de referência.
                    """)
            else:
                st.error(f"Erro ao calcular frete: {resultado['mensagem']}")
        except Exception as e:
            st.error(f"Erro ao processar o cálculo: {str(e)}")

# Rodapé
st.markdown("<div style='text-align: center; color: #888; padding-top: 30px;'>Calculadora de Fretes © 2025</div>", unsafe_allow_html=True)

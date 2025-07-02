#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Calculadora de Fretes - Interface Streamlit (Versão 6.0)
--------------------------------------------------------
Interface web para a calculadora de fretes com valores calibrados
baseados em dados históricos reais.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys
import re
import requests
import io

# Importar a calculadora de fretes
sys.path.append(os.path.dirname(__file__))
try:
    from calculadora_frete import CalculadoraFrete
except ImportError:
    # Fallback para o caso de o arquivo estar no mesmo diretório
    from calculadora_frete import CalculadoraFrete

# Configuração da página
st.set_page_config(
    page_title="Calculadora de Fretes",
    page_icon="🚚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilo personalizado
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
        color: #26A69A;
    }
    .result-box {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
    }
    .detail-box {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .info-text {
        color: #555;
        font-size: 14px;
    }
    .header-box {
        background-color: #1E88E5;
        padding: 10px;
        border-radius: 5px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    .subheader-box {
        background-color: #26A69A;
        padding: 8px;
        border-radius: 5px;
        color: white;
        text-align: center;
        margin: 8px 0;
    }
    .value-display {
        font-size: 22px;
        font-weight: bold;
        color: #1E88E5;
    }
    .km-display {
        font-size: 18px;
        font-weight: bold;
        color: #26A69A;
    }
    .footer {
        margin-top: 50px;
        text-align: center;
        color: #888;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Título da aplicação
st.markdown('<div class="header-box"><h1>Calculadora de Fretes</h1></div>', unsafe_allow_html=True)

# Formulário de entrada
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="subheader-box">Origem</div>', unsafe_allow_html=True)
    origem = st.text_input("", placeholder="Digite a cidade de origem", help="Exemplo: São Paulo/SP", key="origem")
    
with col2:
    st.markdown('<div class="subheader-box">Destino</div>', unsafe_allow_html=True)
    destino = st.text_input("", placeholder="Digite a cidade de destino", help="Exemplo: Rio de Janeiro/RJ", key="destino")

# Modo de cálculo
st.markdown('<div class="subheader-box">Modo de cálculo</div>', unsafe_allow_html=True)
modo_calculo = st.radio("", ["Por módulos", "Por peso (kg)"], horizontal=True, key="modo_calculo")

# Quantidade de módulos ou peso
if modo_calculo == "Por módulos":
    st.markdown('<div class="subheader-box">Quantidade de Módulos</div>', unsafe_allow_html=True)
    quantidade = st.number_input("", min_value=1, value=200, step=1, format="%d", key="quantidade")
    peso_kg = None
else:
    st.markdown('<div class="subheader-box">Peso em kg</div>', unsafe_allow_html=True)
    peso_kg = st.number_input("", min_value=1.0, value=6000.0, step=100.0, format="%.1f", key="peso_kg")
    quantidade = None

# Data prevista
st.markdown('<div class="subheader-box">Data Prevista</div>', unsafe_allow_html=True)
data_prevista = st.date_input("", datetime.now(), key="data_prevista")

# Botão de cálculo
if st.button("Calcular Frete", type="primary", use_container_width=True):
    # Verificar se os campos obrigatórios foram preenchidos
    if not origem or not destino:
        st.error("Por favor, preencha os campos de origem e destino.")
    else:
        # Inicializar a calculadora
        calculadora = CalculadoraFrete(usar_url=True)
        
        # Calcular o frete
        resultado = calculadora.calcular_frete(
            origem=origem,
            destino=destino,
            num_modulos=quantidade if modo_calculo == "Por módulos" else None,
            peso_kg=peso_kg if modo_calculo == "Por peso (kg)" else None,
            data_prevista=data_prevista,
            modo_calculo="modulos" if modo_calculo == "Por módulos" else "peso"
        )
        
        # Exibir o resultado
        if resultado['status'] == 'sucesso':
            # Resultado principal
            st.markdown('<div class="subheader-box"><h2>Resultado da Cotação</h2></div>', unsafe_allow_html=True)
            
            # Valor estimado
            st.markdown(f"""
            <div class="result-box">
                <div class="big-font">R$ {resultado['valor_estimado']:.2f}</div>
                <div class="info-text">Valor estimado do frete</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Valor por quilômetro
            st.markdown(f"""
            <div class="result-box">
                <div class="medium-font">R$ {resultado['valor_por_km']:.2f}/km</div>
                <div class="info-text">Valor por quilômetro</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Detalhes da cotação
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="subheader-box"><h3>Detalhes da Cotação</h3></div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="detail-box">
                    <p><strong>Origem:</strong> {resultado['origem']}</p>
                    <p><strong>Destino:</strong> {resultado['destino']}</p>
                    <p><strong>{'Módulos' if modo_calculo == 'Por módulos' else 'Peso'}:</strong> {quantidade if modo_calculo == 'Por módulos' else f"{peso_kg} kg"}</p>
                    <p><strong>Distância:</strong> {resultado['distancia_km']} km</p>
                    <p><strong>Data da Consulta:</strong> {data_prevista.strftime('%d/%m/%Y')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="subheader-box"><h3>Detalhes do Cálculo</h3></div>', unsafe_allow_html=True)
                
                if resultado.get('valor_absoluto', False):
                    st.markdown(f"""
                    <div class="detail-box">
                        <p><strong>Valor baseado em caso histórico conhecido</strong></p>
                        <p>Este valor foi calculado com base em um frete similar existente no histórico da empresa.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="detail-box">
                        <p><strong>Valor médio base:</strong> R$ {resultado['valor_medio_original']:.2f}</p>
                        <p><strong>Ajuste por {'módulos' if modo_calculo == 'Por módulos' else 'peso'}:</strong> R$ {resultado['ajuste_quantidade']:.2f}</p>
                        <p><strong>Ajuste de inflação:</strong> R$ {resultado['ajuste_inflacao']:.2f}</p>
                        <p><strong>Margem aplicada (10%):</strong> R$ {resultado['margem_aplicada']:.2f}</p>
                        {'<p><strong>Fretes base:</strong> ' + str(resultado.get('fretes_base', 'N/A')) + '</p>' if 'fretes_base' in resultado else ''}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Informações adicionais
            with st.expander("Informações sobre o cálculo"):
                st.markdown("""
                O cálculo do frete é baseado em dados históricos e considera os seguintes fatores:
                
                - **Distância entre origem e destino**: Calculada automaticamente com base nos endereços fornecidos
                - **Quantidade de módulos ou peso**: Influencia diretamente no valor do frete
                - **Data prevista**: Utilizada para ajustes de inflação
                - **Histórico de fretes similares**: Quando disponíveis, são utilizados como referência
                
                O valor final inclui uma margem de 10% sobre o valor calculado.
                """)
        else:
            st.error(f"Erro ao calcular o frete: {resultado['mensagem']}")

# Rodapé
st.markdown('<div class="footer">Calculadora de Fretes © 2025</div>', unsafe_allow_html=True)

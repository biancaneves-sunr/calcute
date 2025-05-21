#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface Streamlit para Calculadora de Fretes - Versão 3.0
----------------------------------------------------------
Este script implementa uma interface Streamlit para a calculadora de fretes,
com valores recalibrados e interface aprimorada conforme feedback do usuário.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys
from calculadora_frete import CalculadoraFrete

# Configurações da página
st.set_page_config(
    page_title="Calculadora de Fretes",
    page_icon="🚚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilo personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #0d6efd;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #6c757d;
        margin-bottom: 2rem;
        text-align: center;
    }
    .result-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-top: 2rem;
    }
    .big-number {
        font-size: 3.5rem;
        font-weight: bold;
        color: #0d6efd;
        text-align: center;
    }
    .medium-number {
        font-size: 2.2rem;
        font-weight: bold;
        color: #198754;
        text-align: center;
    }
    .info-text {
        color: #6c757d;
        font-size: 1.1rem;
        text-align: center;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        color: #6c757d;
        font-size: 0.9rem;
    }
    .stButton>button {
        font-size: 1.2rem;
        font-weight: bold;
        height: 3rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def carregar_calculadora():
    """Carrega a calculadora de fretes (com cache para evitar recarregamento)."""
    try:
        # Ajuste o caminho conforme necessário quando publicar
        arquivo_excel = 'https://raw.githubusercontent.com/biancaneves-sunr/calcute/0026cd7d0bf1ae3cf6a5be69516155e39b0f0e3d/Banco%20de%20Dados%20-%20Logistica.xlsx'
        return CalculadoraFrete(arquivo_excel)
    except Exception as e:
        st.error(f"Erro ao carregar a calculadora: {e}")
        return None

def main():
    """Função principal da interface Streamlit."""
    # Cabeçalho
    st.markdown('<h1 class="main-header">Calculadora de Fretes</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Estimativa de fretes com base em dados históricos</p>', unsafe_allow_html=True)
    
    # Carregar calculadora
    calculadora = carregar_calculadora()
    
    if calculadora is None:
        st.error("Não foi possível inicializar a calculadora. Verifique o arquivo de dados.")
        return
    
    # Formulário de entrada
    with st.form("formulario_frete"):
        col1, col2 = st.columns(2)
        
        with col1:
            origem = st.text_input(
                "Origem",
                placeholder="Cidade/Estado ou endereço com CEP",
                help="Ex: São Paulo, SP ou Rua Exemplo, 123 - São Paulo, SP, 01234-567"
            )
        
        with col2:
            destino = st.text_input(
                "Destino",
                placeholder="Cidade/Estado ou endereço com CEP",
                help="Ex: Rio de Janeiro, RJ ou Av. Exemplo, 456 - Rio de Janeiro, RJ, 20000-000"
            )
        
        # Seleção do modo de cálculo
        modo_calculo = st.radio(
            "Modo de cálculo",
            options=["Por módulos", "Por peso (kg)"],
            horizontal=True,
            help="Escolha se o cálculo será baseado na quantidade de módulos ou no peso em kg"
        )
        
        # Campos específicos conforme o modo de cálculo
        if modo_calculo == "Por módulos":
            num_modulos = st.number_input(
                "Quantidade de Módulos",
                min_value=1,
                value=100,
                step=10,
                help="Número de módulos a serem transportados"
            )
            peso_kg = None
        else:  # Por peso
            peso_kg = st.number_input(
                "Peso em kg",  # Corrigido conforme solicitado
                min_value=1.0,
                value=3000.0,
                step=100.0,
                format="%.1f",
                help="Peso total em kg a ser transportado"
            )
            num_modulos = None
        
        # Data prevista
        data = st.date_input(
            "Data Prevista",
            value=datetime.now(),
            help="Data prevista para o frete"
        )
        
        # Botão de envio
        submitted = st.form_submit_button("Calcular Frete", use_container_width=True)
    
    # Processamento do formulário
    if submitted:
        if not origem or not destino:
            st.error("Origem e destino são campos obrigatórios.")
            return
        
        with st.spinner("Calculando frete..."):
            # Converter data para datetime
            data_dt = datetime.combine(data, datetime.min.time())
            
            # Definir modo de cálculo para a API
            modo_api = "modulos" if modo_calculo == "Por módulos" else "peso"
            
            # Calcular frete
            resultado = calculadora.calcular_frete(
                origem=origem,
                destino=destino,
                num_modulos=num_modulos,
                peso_kg=peso_kg,
                data=data_dt,
                modo_calculo=modo_api
            )
            
            # Exibir resultado
            if resultado["status"] == "sucesso":
                # Seção de resultado
                st.markdown("## Resultado da Cotação")
                
                # Valor estimado em destaque
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.markdown('<p class="big-number">R$ {:.2f}</p>'.format(resultado["valor_estimado"]), unsafe_allow_html=True)
                st.markdown('<p class="info-text">Valor estimado do frete</p>', unsafe_allow_html=True)
                
                # Valor por km
                if resultado["distancia_km"]:
                    st.markdown('<p class="medium-number">R$ {:.2f}/km</p>'.format(resultado["valor_por_km"]), unsafe_allow_html=True)
                    st.markdown('<p class="info-text">Valor por quilômetro</p>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Detalhes em colunas
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Detalhes da Cotação")
                    st.write(f"**Origem:** {origem}")
                    st.write(f"**Destino:** {destino}")
                    
                    if modo_calculo == "Por módulos":
                        st.write(f"**Módulos:** {num_modulos}")
                    else:
                        st.write(f"**Peso:** {peso_kg} kg")
                    
                    if resultado["distancia_km"]:
                        st.write(f"**Distância:** {resultado['distancia_km']:.2f} km")
                    else:
                        st.write("**Distância:** Não calculada")
                    
                    st.write(f"**Data da Consulta:** {data_dt.strftime('%d/%m/%Y')}")
                
                with col2:
                    st.subheader("Detalhes do Cálculo")
                    st.write(f"**Valor médio base:** R$ {resultado['valor_medio_original']:.2f}")
                    
                    if modo_calculo == "Por módulos":
                        st.write(f"**Ajuste por módulos:** R$ {resultado['ajuste_quantidade']:.2f}")
                    else:
                        st.write(f"**Ajuste por peso:** R$ {resultado['ajuste_quantidade']:.2f}")
                    
                    st.write(f"**Ajuste de inflação:** R$ {resultado['ajuste_inflacao']:.2f}")
                    st.write(f"**Margem aplicada (10%):** R$ {resultado['margem_aplicada']:.2f}")
                    st.write(f"**Fretes base:** {resultado['fretes_base']}")
                
                # Informações adicionais
                with st.expander("Informações sobre o cálculo"):
                    st.write("""
                    O cálculo do frete é baseado em dados históricos, ajustados pelos seguintes fatores:
                    
                    1. **Busca de fretes similares**: Busca por origem, destino e quantidade similar
                    2. **Ajuste por quantidade**: Aplica economia de escala (módulos ou peso)
                    3. **Ajuste de inflação**: Considera a diferença temporal entre fretes históricos e a data atual
                    4. **Valor por km**: Calculado com base nos fretes históricos similares
                    5. **Margem adicional**: Aplica margem de 10% sobre o valor final
                    
                    Para fretes curtos (menos de 10km), o sistema utiliza uma lógica especial baseada no histórico de fretes similares.
                    """)
            else:
                st.error(f"Erro no cálculo: {resultado['mensagem']}")
    
    # Rodapé
    st.markdown('<div class="footer">Calculadora de Fretes © 2025</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

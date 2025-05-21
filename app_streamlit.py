#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface Streamlit para Calculadora de Fretes
----------------------------------------------
Este script implementa uma interface Streamlit para a calculadora de fretes,
permitindo fácil publicação e uso por múltiplos usuários.
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
        font-size: 2.5rem;
        color: #0d6efd;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
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
        font-size: 2.5rem;
        font-weight: bold;
        color: #0d6efd;
        text-align: center;
    }
    .info-text {
        color: #6c757d;
        font-size: 0.9rem;
        text-align: center;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        color: #6c757d;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def carregar_calculadora():
    """Carrega a calculadora de fretes (com cache para evitar recarregamento)."""
    try:
        # Ajuste o caminho conforme necessário quando publicar
        arquivo_excel = '/home/ubuntu/upload/Banco de Dados - Logistica.xlsx'
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
        
        col3, col4 = st.columns(2)
        
        with col3:
            modulos = st.number_input(
                "Quantidade de Módulos",
                min_value=1,
                value=100,
                step=10,
                help="Número de módulos a serem transportados"
            )
        
        with col4:
            data = st.date_input(
                "Data Prevista",
                value=datetime.now(),
                help="Data prevista para o frete (opcional)"
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
            
            # Calcular frete
            resultado = calculadora.calcular_frete(origem, destino, modulos, data_dt)
            
            # Exibir resultado
            if resultado["status"] == "sucesso":
                # Seção de resultado
                st.markdown("## Resultado da Cotação")
                
                # Valor estimado em destaque
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.markdown('<p class="big-number">R$ {:.2f}</p>'.format(resultado["valor_estimado"]), unsafe_allow_html=True)
                st.markdown('<p class="info-text">Valor estimado do frete</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Detalhes em colunas
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Detalhes da Cotação")
                    st.write(f"**Origem:** {origem}")
                    st.write(f"**Destino:** {destino}")
                    st.write(f"**Módulos:** {modulos}")
                    if resultado["distancia_km"]:
                        st.write(f"**Distância:** {resultado['distancia_km']:.2f} km")
                    else:
                        st.write("**Distância:** Não calculada")
                    st.write(f"**Data da Consulta:** {data_dt.strftime('%d/%m/%Y')}")
                
                with col2:
                    st.subheader("Detalhes do Cálculo")
                    st.write(f"**Valor médio base:** R$ {resultado['valor_medio_original']:.2f}")
                    st.write(f"**Ajuste por módulos:** R$ {resultado['ajuste_modulos']:.2f}")
                    st.write(f"**Ajuste de inflação:** R$ {resultado['ajuste_inflacao']:.2f}")
                    st.write(f"**Margem aplicada (10%):** R$ {resultado['margem_aplicada']:.2f}")
                    st.write(f"**Fretes base:** {resultado['fretes_base']}")
                
                # Informações adicionais
                with st.expander("Informações sobre o cálculo"):
                    st.write("""
                    O cálculo do frete é baseado em dados históricos, ajustados pelos seguintes fatores:
                    
                    1. **Busca de fretes similares**: Busca por origem, destino e quantidade similar de módulos
                    2. **Ajuste por quantidade de módulos**: Aplica economia de escala
                    3. **Ajuste de inflação**: Considera a diferença temporal entre fretes históricos e a data atual
                    4. **Margem adicional**: Aplica margem de 10% sobre o valor final
                    """)
            else:
                st.error(f"Erro no cálculo: {resultado['mensagem']}")
    
    # Rodapé
    st.markdown('<div class="footer">Calculadora de Fretes © 2025</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

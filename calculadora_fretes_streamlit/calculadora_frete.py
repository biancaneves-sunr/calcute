#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Calculadora de Fretes - Protótipo Básico
----------------------------------------
Este script implementa uma calculadora de fretes baseada em dados históricos,
com ajustes de inflação e margem adicional.
"""

import pandas as pd
import argparse
import datetime
import os
import sys
import re
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import numpy as np
from datetime import datetime

# Configurações
ARQUIVO_EXCEL = '/home/ubuntu/upload/Banco de Dados - Logistica.xlsx'
TAXA_INFLACAO_ANUAL = 0.045  # 4.5% ao ano (média IPCA)
MARGEM_ADICIONAL = 0.10  # 10% de margem adicional

class CalculadoraFrete:
    def __init__(self, arquivo_excel=ARQUIVO_EXCEL):
        """Inicializa a calculadora de fretes."""
        self.dados = self._carregar_dados(arquivo_excel)
        self.geolocator = Nominatim(user_agent="calculadora_frete")
        
    def _carregar_dados(self, arquivo_excel):
        """Carrega os dados do arquivo Excel."""
        try:
            df = pd.read_excel(arquivo_excel)
            # Filtrar apenas registros com valor de frete
            df = df[df['(R$) Frete'].notna()]
            # Converter datas para datetime
            for col in ['Data Envio Proposta', 'Data de Orçamento']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            return df
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            sys.exit(1)
    
    def _obter_coordenadas(self, endereco):
        """Obtém as coordenadas geográficas a partir de um endereço."""
        try:
            location = self.geolocator.geocode(endereco)
            if location:
                return (location.latitude, location.longitude)
            return None
        except Exception as e:
            print(f"Erro ao obter coordenadas para {endereco}: {e}")
            return None
    
    def _calcular_distancia(self, origem, destino):
        """Calcula a distância entre dois pontos geográficos."""
        coord_origem = self._obter_coordenadas(origem)
        coord_destino = self._obter_coordenadas(destino)
        
        if coord_origem and coord_destino:
            distancia = geodesic(coord_origem, coord_destino).kilometers
            return round(distancia, 2)
        return None
    
    def _extrair_cidade_estado(self, endereco):
        """Extrai cidade e estado de um endereço completo."""
        # Padrão simples para extrair cidade/estado
        padrao = r'([A-Za-zÀ-ÖØ-öø-ÿ\s]+)[,-/]?\s*([A-Z]{2})'
        match = re.search(padrao, endereco)
        if match:
            cidade = match.group(1).strip()
            estado = match.group(2).strip()
            return f"{cidade}/{estado}"
        return endereco  # Retorna o endereço original se não conseguir extrair
    
    def _buscar_fretes_similares(self, cidade_origem, cidade_destino, num_modulos, distancia=None):
        """Busca fretes similares na base de dados."""
        # Extrair cidade e estado
        cidade_origem_formatada = self._extrair_cidade_estado(cidade_origem)
        cidade_destino_formatada = self._extrair_cidade_estado(cidade_destino)
        
        # Busca exata
        fretes_exatos = self.dados[
            (self.dados['Cidade/Estado'].str.contains(cidade_origem_formatada, case=False, na=False)) &
            (self.dados['Destino'].str.contains(cidade_destino_formatada, case=False, na=False)) &
            (self.dados['Núm. Módulos'].between(num_modulos * 0.7, num_modulos * 1.3))
        ]
        
        if not fretes_exatos.empty:
            return fretes_exatos
        
        # Busca por proximidade (apenas origem)
        fretes_origem = self.dados[
            (self.dados['Cidade/Estado'].str.contains(cidade_origem_formatada.split('/')[0], case=False, na=False)) &
            (self.dados['Núm. Módulos'].between(num_modulos * 0.5, num_modulos * 1.5))
        ]
        
        if not fretes_origem.empty:
            return fretes_origem
        
        # Busca por distância similar
        if distancia:
            fretes_distancia = self.dados[
                (self.dados['Distancia Valinhos (km)'].between(distancia * 0.8, distancia * 1.2)) &
                (self.dados['Núm. Módulos'].between(num_modulos * 0.5, num_modulos * 1.5))
            ]
            
            if not fretes_distancia.empty:
                return fretes_distancia
        
        # Retorna dados vazios se não encontrar nada
        return pd.DataFrame()
    
    def _calcular_ajuste_inflacao(self, valor, data_referencia):
        """Calcula o ajuste de inflação com base na data de referência."""
        hoje = datetime.now()
        
        if pd.isna(data_referencia):
            # Se não tiver data, assume 1 ano de inflação
            anos = 1
        else:
            # Calcula a diferença em anos
            delta = hoje - data_referencia
            anos = delta.days / 365
        
        # Aplica a inflação composta
        fator_inflacao = (1 + TAXA_INFLACAO_ANUAL) ** anos
        return valor * fator_inflacao
    
    def _ajustar_por_modulos(self, valor_base, modulos_base, modulos_alvo):
        """Ajusta o valor com base na diferença de módulos."""
        if modulos_base == 0 or pd.isna(modulos_base):
            return valor_base
        
        # Fator de economia de escala: quanto maior a quantidade, menor o valor por módulo
        fator = (modulos_alvo / modulos_base) ** (-0.1)  # Expoente negativo para economia de escala
        return valor_base * (modulos_alvo / modulos_base) * fator
    
    def calcular_frete(self, origem, destino, num_modulos, data=None):
        """Calcula o valor estimado do frete."""
        if data is None:
            data = datetime.now()
        
        # Calcular distância
        distancia = self._calcular_distancia(origem, destino)
        
        # Buscar fretes similares
        fretes_similares = self._buscar_fretes_similares(origem, destino, num_modulos, distancia)
        
        if fretes_similares.empty:
            return {
                "status": "erro",
                "mensagem": "Não foram encontrados fretes similares na base de dados."
            }
        
        # Calcular valor base (média ponderada dos fretes similares)
        fretes_similares['Peso'] = 1.0  # Peso padrão
        
        # Dar mais peso para fretes mais recentes
        for idx, row in fretes_similares.iterrows():
            if not pd.isna(row['Data Envio Proposta']):
                # Quanto mais recente, maior o peso
                dias_passados = (datetime.now() - row['Data Envio Proposta']).days
                if dias_passados > 0:
                    fretes_similares.at[idx, 'Peso'] = 1 + (365 / dias_passados) * 0.5
        
        # Calcular média ponderada
        valor_medio = np.average(
            fretes_similares['(R$) Frete'], 
            weights=fretes_similares['Peso']
        )
        
        modulos_medio = fretes_similares['Núm. Módulos'].mean()
        
        # Ajustar por quantidade de módulos
        valor_ajustado_modulos = self._ajustar_por_modulos(valor_medio, modulos_medio, num_modulos)
        
        # Obter data média dos fretes similares
        data_media = fretes_similares['Data Envio Proposta'].mean()
        
        # Ajustar por inflação
        valor_ajustado_inflacao = self._calcular_ajuste_inflacao(valor_ajustado_modulos, data_media)
        
        # Aplicar margem adicional
        valor_final = valor_ajustado_inflacao * (1 + MARGEM_ADICIONAL)
        
        # Preparar resultado
        resultado = {
            "status": "sucesso",
            "valor_estimado": round(valor_final, 2),
            "distancia_km": distancia,
            "fretes_base": len(fretes_similares),
            "valor_medio_original": round(valor_medio, 2),
            "ajuste_modulos": round(valor_ajustado_modulos - valor_medio, 2),
            "ajuste_inflacao": round(valor_ajustado_inflacao - valor_ajustado_modulos, 2),
            "margem_aplicada": round(valor_final - valor_ajustado_inflacao, 2),
            "detalhes": {
                "origem": origem,
                "destino": destino,
                "modulos": num_modulos,
                "data_consulta": data.strftime("%Y-%m-%d")
            }
        }
        
        return resultado

def formatar_resultado(resultado):
    """Formata o resultado para exibição."""
    if resultado["status"] == "erro":
        return f"ERRO: {resultado['mensagem']}"
    
    saida = "\n" + "=" * 50 + "\n"
    saida += "ESTIMATIVA DE FRETE\n"
    saida += "=" * 50 + "\n\n"
    
    saida += f"Origem: {resultado['detalhes']['origem']}\n"
    saida += f"Destino: {resultado['detalhes']['destino']}\n"
    saida += f"Módulos: {resultado['detalhes']['modulos']}\n"
    saida += f"Distância: {resultado['distancia_km']} km\n\n"
    
    saida += f"VALOR ESTIMADO: R$ {resultado['valor_estimado']:.2f}\n\n"
    
    saida += "Detalhes do cálculo:\n"
    saida += f"- Valor médio base: R$ {resultado['valor_medio_original']:.2f}\n"
    saida += f"- Ajuste por módulos: R$ {resultado['ajuste_modulos']:.2f}\n"
    saida += f"- Ajuste de inflação: R$ {resultado['ajuste_inflacao']:.2f}\n"
    saida += f"- Margem aplicada (10%): R$ {resultado['margem_aplicada']:.2f}\n\n"
    
    saida += f"Baseado em {resultado['fretes_base']} fretes similares.\n"
    saida += f"Data da consulta: {resultado['detalhes']['data_consulta']}\n"
    
    return saida

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description='Calculadora de Fretes')
    parser.add_argument('--origem', required=True, help='Endereço de origem')
    parser.add_argument('--destino', required=True, help='Endereço de destino')
    parser.add_argument('--modulos', type=int, required=True, help='Número de módulos')
    parser.add_argument('--data', help='Data prevista (formato YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # Converter data se fornecida
    data = None
    if args.data:
        try:
            data = datetime.strptime(args.data, '%Y-%m-%d')
        except ValueError:
            print("Erro: Formato de data inválido. Use YYYY-MM-DD.")
            sys.exit(1)
    
    # Inicializar calculadora
    calculadora = CalculadoraFrete()
    
    # Calcular frete
    resultado = calculadora.calcular_frete(args.origem, args.destino, args.modulos, data)
    
    # Exibir resultado
    print(formatar_resultado(resultado))

if __name__ == "__main__":
    main()

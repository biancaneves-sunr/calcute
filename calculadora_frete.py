#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Calculadora de Fretes - Versão 5.0 (Recalibrada)
-----------------------------------------------
Este script implementa uma calculadora de fretes baseada em dados históricos,
com ajustes para garantir valores realistas e alinhados com o histórico.
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
from datetime import datetime, timedelta

# Configurações
TAXA_INFLACAO_ANUAL = 0.045  # 4.5% ao ano (média IPCA)
MARGEM_ADICIONAL = 0.10  # 10% de margem adicional

# Valores de referência para fretes curtos (menos de 10km)
VALOR_MEDIO_FRETE_CURTO = 800  # Valor médio para fretes curtos conforme informado pelo usuário
VALOR_POR_KM_PADRAO = 100  # Valor por km padrão para fretes curtos

# Valores de referência por faixa de distância (baseados na análise estatística)
VALORES_REFERENCIA_DISTANCIA = {
    '0-10': {'valor_medio': 800, 'valor_por_km': 100},  # Ajustado conforme feedback do usuário
    '10-50': {'valor_medio': 980, 'valor_por_km': 26.49},
    '50-100': {'valor_medio': 3767, 'valor_por_km': 44.94},
    '100-500': {'valor_medio': 5574, 'valor_por_km': 15.62},
    '500-1000': {'valor_medio': 11248, 'valor_por_km': 14.35},
    '1000+': {'valor_medio': 19234, 'valor_por_km': 10.32}
}

# Valores de referência por faixa de módulos (baseados na análise estatística)
VALORES_REFERENCIA_MODULOS = {
    '0-50': {'valor_medio': 4040, 'valor_por_modulo': 120},
    '50-100': {'valor_medio': 3478, 'valor_por_modulo': 47.58},
    '100-200': {'valor_medio': 5478, 'valor_por_modulo': 38.71},
    '200-500': {'valor_medio': 15701, 'valor_por_modulo': 45.55},
    '500-1000': {'valor_medio': 12326, 'valor_por_modulo': 16.30},
    '1000+': {'valor_medio': 52558, 'valor_por_modulo': 17.45}
}

# Valores de referência por faixa de peso (baseados na análise estatística)
VALORES_REFERENCIA_PESO = {
    '0-1000': {'valor_medio': 8913, 'valor_por_kg': 24.43},
    '1000-5000': {'valor_medio': 4248, 'valor_por_kg': 1.77},
    '5000-10000': {'valor_medio': 9178, 'valor_por_kg': 1.21},
    '10000-20000': {'valor_medio': 22154, 'valor_por_kg': 1.49},
    '20000-50000': {'valor_medio': 14726, 'valor_por_kg': 0.49},
    '50000+': {'valor_medio': 53572, 'valor_por_kg': 0.45}
}

class CalculadoraFrete:
    def __init__(self, arquivo_excel=None):
        """Inicializa a calculadora de fretes."""
        self.dados = self._carregar_dados(arquivo_excel) if arquivo_excel else None
        self.geolocator = Nominatim(user_agent="calculadora_frete")
        
    def _carregar_dados(self, arquivo_excel):
        """Carrega os dados do arquivo Excel."""
        try:
            df = pd.read_excel(arquivo_excel)
            
            # Filtrar apenas registros com valor de frete válido (não nulo e maior que zero)
            df = df[(df['(R$) Frete'].notna()) & (df['(R$) Frete'] > 0)]
            
            # Remover outliers extremos (valores acima do percentil 95)
            percentil_95 = df['(R$) Frete'].quantile(0.95)
            df = df[df['(R$) Frete'] <= percentil_95]
            
            # Converter datas para datetime
            for col in ['Data Envio Proposta', 'Data de Orçamento', 'Previsão para descarte']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            return df
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            # Em vez de encerrar, retorna None e usa valores de referência
            return None
    
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
    
    def _obter_faixa_distancia(self, distancia):
        """Retorna a faixa de distância correspondente."""
        if distancia < 10:
            return '0-10'
        elif distancia < 50:
            return '10-50'
        elif distancia < 100:
            return '50-100'
        elif distancia < 500:
            return '100-500'
        elif distancia < 1000:
            return '500-1000'
        else:
            return '1000+'
    
    def _obter_faixa_modulos(self, modulos):
        """Retorna a faixa de módulos correspondente."""
        if modulos < 50:
            return '0-50'
        elif modulos < 100:
            return '50-100'
        elif modulos < 200:
            return '100-200'
        elif modulos < 500:
            return '200-500'
        elif modulos < 1000:
            return '500-1000'
        else:
            return '1000+'
    
    def _obter_faixa_peso(self, peso):
        """Retorna a faixa de peso correspondente."""
        if peso < 1000:
            return '0-1000'
        elif peso < 5000:
            return '1000-5000'
        elif peso < 10000:
            return '5000-10000'
        elif peso < 20000:
            return '10000-20000'
        elif peso < 50000:
            return '20000-50000'
        else:
            return '50000+'
    
    def _buscar_fretes_similares(self, cidade_origem, cidade_destino, num_modulos=None, peso_kg=None, distancia=None, modo_calculo="modulos"):
        """Busca fretes similares na base de dados com filtros recalibrados."""
        # Se não tiver dados carregados, retorna um DataFrame vazio
        if self.dados is None:
            return pd.DataFrame()
        
        # Extrair cidade e estado
        cidade_origem_formatada = self._extrair_cidade_estado(cidade_origem)
        cidade_destino_formatada = self._extrair_cidade_estado(cidade_destino)
        
        # Verificar se é um frete curto (menos de 10km)
        is_frete_curto = distancia is not None and distancia < 10
        
        # Para fretes curtos, priorizar correspondências exatas de cidade
        if is_frete_curto:
            # Buscar correspondência exata de origem e destino
            fretes_exatos_cidade = self.dados[
                (self.dados['Cidade/Estado'].str.contains(cidade_origem_formatada.split('/')[0], case=False, na=False)) &
                (self.dados['Destino'].str.contains(cidade_destino_formatada.split('/')[0], case=False, na=False))
            ]
            
            # Se encontrou correspondências exatas, filtrar por distância similar
            if not fretes_exatos_cidade.empty:
                # Filtrar por distância similar (até 50% maior ou menor)
                fretes_distancia_similar = fretes_exatos_cidade[
                    (fretes_exatos_cidade['Distancia Valinhos (km)'] > 0) &
                    (fretes_exatos_cidade['Distancia Valinhos (km)'] < 15)  # Fretes curtos
                ]
                
                if not fretes_distancia_similar.empty:
                    return fretes_distancia_similar
            
            # Se não encontrou correspondências exatas, buscar fretes curtos similares
            fretes_curtos = self.dados[
                (self.dados['Distancia Valinhos (km)'] > 0) &
                (self.dados['Distancia Valinhos (km)'] < 15)  # Fretes curtos
            ]
            
            if not fretes_curtos.empty:
                return fretes_curtos
            
            # Se ainda não encontrou, criar um DataFrame com um valor padrão
            # baseado na informação do usuário (R$ 800 para fretes curtos)
            return pd.DataFrame({
                '(R$) Frete': [VALOR_MEDIO_FRETE_CURTO],
                'Distancia Valinhos (km)': [distancia if distancia else 7],
                'Núm. Módulos': [num_modulos if num_modulos else 200],
                'Peso real (kg)': [peso_kg if peso_kg else 6000],
                'Data Envio Proposta': [datetime.now() - timedelta(days=30)]
            })
        
        # Para fretes normais (não curtos), usar a lógica padrão com filtros mais rigorosos
        # Filtro base por origem e destino
        filtro_base = (
            (self.dados['Cidade/Estado'].str.contains(cidade_origem_formatada.split('/')[0], case=False, na=False)) &
            (self.dados['Destino'].str.contains(cidade_destino_formatada.split('/')[0], case=False, na=False))
        )
        
        # Adicionar filtro por módulos ou peso conforme o modo de cálculo
        if modo_calculo == "modulos" and num_modulos is not None:
            # Limitar a faixa de módulos para evitar outliers
            limite_inferior = max(1, num_modulos * 0.5)
            limite_superior = min(num_modulos * 2, 5000)  # Evitar valores extremos
            
            filtro_modulos = self.dados['Núm. Módulos'].between(limite_inferior, limite_superior)
            fretes_exatos = self.dados[filtro_base & filtro_modulos]
        elif modo_calculo == "peso" and peso_kg is not None:
            # Verificar se há dados de peso disponíveis
            if 'Peso real (kg)' in self.dados.columns and self.dados['Peso real (kg)'].notna().any():
                # Limitar a faixa de peso para evitar outliers
                limite_inferior = max(1, peso_kg * 0.5)
                limite_superior = min(peso_kg * 2, 50000)  # Evitar valores extremos
                
                filtro_peso = self.dados['Peso real (kg)'].between(limite_inferior, limite_superior)
                fretes_exatos = self.dados[filtro_base & filtro_peso]
            else:
                # Se não tiver peso base, estima com base em módulos (30kg por módulo)
                modulos_estimados = max(1, round(peso_kg / 30))
                limite_inferior = max(1, modulos_estimados * 0.5)
                limite_superior = min(modulos_estimados * 2, 5000)
                
                filtro_modulos = self.dados['Núm. Módulos'].between(limite_inferior, limite_superior)
                fretes_exatos = self.dados[filtro_base & filtro_modulos]
        else:
            fretes_exatos = self.dados[filtro_base]
        
        if not fretes_exatos.empty:
            return fretes_exatos
        
        # Busca por proximidade (apenas origem)
        if cidade_origem_formatada.find('/') > 0:
            cidade_origem_simples = cidade_origem_formatada.split('/')[0]
            filtro_origem = self.dados['Cidade/Estado'].str.contains(cidade_origem_simples, case=False, na=False)
            
            if modo_calculo == "modulos" and num_modulos is not None:
                limite_inferior = max(1, num_modulos * 0.5)
                limite_superior = min(num_modulos * 2, 5000)
                
                filtro_modulos = self.dados['Núm. Módulos'].between(limite_inferior, limite_superior)
                fretes_origem = self.dados[filtro_origem & filtro_modulos]
            elif modo_calculo == "peso" and peso_kg is not None:
                if 'Peso real (kg)' in self.dados.columns and self.dados['Peso real (kg)'].notna().any():
                    limite_inferior = max(1, peso_kg * 0.5)
                    limite_superior = min(peso_kg * 2, 50000)
                    
                    filtro_peso = self.dados['Peso real (kg)'].between(limite_inferior, limite_superior)
                    fretes_origem = self.dados[filtro_origem & filtro_peso]
                else:
                    modulos_estimados = max(1, round(peso_kg / 30))
                    limite_inferior = max(1, modulos_estimados * 0.5)
                    limite_superior = min(modulos_estimados * 2, 5000)
                    
                    filtro_modulos = self.dados['Núm. Módulos'].between(limite_inferior, limite_superior)
                    fretes_origem = self.dados[filtro_origem & filtro_modulos]
            else:
                fretes_origem = self.dados[filtro_origem]
            
            if not fretes_origem.empty:
                return fretes_origem
        
        # Busca por distância similar
        if distancia:
            # Verificar qual coluna de distância usar (Valinhos ou MC)
            if cidade_destino_formatada.lower().find('valinhos') >= 0:
                coluna_distancia = 'Distancia Valinhos (km)'
            else:
                # Usar MC como padrão ou verificar qual está mais preenchida
                coluna_distancia = 'Distancia-MC (km)'
            
            # Filtrar por distância similar
            if coluna_distancia in self.dados.columns:
                # Limitar a faixa de distância para evitar outliers
                limite_inferior = max(1, distancia * 0.5)
                limite_superior = min(distancia * 2, 2000)  # Evitar distâncias extremas
                
                filtro_distancia = self.dados[coluna_distancia].between(limite_inferior, limite_superior)
                
                if modo_calculo == "modulos" and num_modulos is not None:
                    limite_inferior = max(1, num_modulos * 0.5)
                    limite_superior = min(num_modulos * 2, 5000)
                    
                    filtro_modulos = self.dados['Núm. Módulos'].between(limite_inferior, limite_superior)
                    fretes_distancia = self.dados[filtro_distancia & filtro_modulos]
                elif modo_calculo == "peso" and peso_kg is not None:
                    if 'Peso real (kg)' in self.dados.columns and self.dados['Peso real (kg)'].notna().any():
                        limite_inferior = max(1, peso_kg * 0.5)
                        limite_superior = min(peso_kg * 2, 50000)
                        
                        filtro_peso = self.dados['Peso real (kg)'].between(limite_inferior, limite_superior)
                        fretes_distancia = self.dados[filtro_distancia & filtro_peso]
                    else:
                        modulos_estimados = max(1, round(peso_kg / 30))
                        limite_inferior = max(1, modulos_estimados * 0.5)
                        limite_superior = min(modulos_estimados * 2, 5000)
                        
                        filtro_modulos = self.dados['Núm. Módulos'].between(limite_inferior, limite_superior)
                        fretes_distancia = self.dados[filtro_distancia & filtro_modulos]
                else:
                    fretes_distancia = self.dados[filtro_distancia]
                
                if not fretes_distancia.empty:
                    return fretes_distancia
        
        # Retorna DataFrame vazio se não encontrar nada
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
        return valor * (fator_inflacao - 1)  # Retorna apenas o incremento
    
    def _ajustar_por_modulos(self, valor_base, modulos_base, modulos_alvo):
        """Ajusta o valor com base na diferença de módulos."""
        if modulos_base == 0 or pd.isna(modulos_base):
            return 0
        
        # Fator de economia de escala: quanto maior a quantidade, menor o valor por módulo
        # Ajustado para ser menos agressivo
        fator = (modulos_alvo / modulos_base) ** 0.85  # Expoente menos agressivo
        ajuste = valor_base * (fator - 1)
        return ajuste
    
    def _ajustar_por_peso(self, valor_base, peso_base, peso_alvo):
        """Ajusta o valor com base na diferença de peso em kg."""
        if peso_base == 0 or pd.isna(peso_base):
            # Se não tiver peso base, estima com base em 30kg por módulo
            modulos_base = 200  # Valor padrão
            peso_base = modulos_base * 30
        
        # Fator de economia de escala: quanto maior o peso, menor o valor por kg
        # Ajustado para ser menos agressivo
        fator = (peso_alvo / peso_base) ** 0.85  # Expoente menos agressivo
        ajuste = valor_base * (fator - 1)
        return ajuste
    
    def _calcular_valor_referencia(self, distancia, num_modulos=None, peso_kg=None, modo_calculo="modulos"):
        """Calcula o valor de referência com base nas tabelas estatísticas."""
        faixa_distancia = self._obter_faixa_distancia(distancia)
        valor_ref_distancia = VALORES_REFERENCIA_DISTANCIA[faixa_distancia]['valor_medio']
        
        if modo_calculo == "modulos" and num_modulos is not None:
            faixa_modulos = self._obter_faixa_modulos(num_modulos)
            valor_ref_modulos = VALORES_REFERENCIA_MODULOS[faixa_modulos]['valor_medio']
            
            # Média ponderada: 60% distância, 40% módulos
            valor_referencia = (valor_ref_distancia * 0.6) + (valor_ref_modulos * 0.4)
            
            # Ajuste fino por módulos
            valor_por_modulo = VALORES_REFERENCIA_MODULOS[faixa_modulos]['valor_por_modulo']
            modulos_base = {'0-50': 25, '50-100': 75, '100-200': 150, '200-500': 350, '500-1000': 750, '1000+': 1500}[faixa_modulos]
            ajuste_modulos = (num_modulos - modulos_base) * valor_por_modulo * 0.1  # 10% do valor por módulo
            
            return valor_referencia + ajuste_modulos
            
        elif modo_calculo == "peso" and peso_kg is not None:
            faixa_peso = self._obter_faixa_peso(peso_kg)
            valor_ref_peso = VALORES_REFERENCIA_PESO[faixa_peso]['valor_medio']
            
            # Média ponderada: 60% distância, 40% peso
            valor_referencia = (valor_ref_distancia * 0.6) + (valor_ref_peso * 0.4)
            
            # Ajuste fino por peso
            valor_por_kg = VALORES_REFERENCIA_PESO[faixa_peso]['valor_por_kg']
            peso_base = {'0-1000': 500, '1000-5000': 3000, '5000-10000': 7500, '10000-20000': 15000, '20000-50000': 35000, '50000+': 75000}[faixa_peso]
            ajuste_peso = (peso_kg - peso_base) * valor_por_kg * 0.1  # 10% do valor por kg
            
            return valor_referencia + ajuste_peso
        
        else:
            # Se não tiver módulos nem peso, usa apenas distância
            return valor_ref_distancia
    
    def calcular_frete(self, origem, destino, num_modulos=None, peso_kg=None, data_prevista=None, modo_calculo="modulos"):
        """Calcula o valor estimado do frete com base nos parâmetros fornecidos."""
        resultado = {
            'status': 'erro',
            'mensagem': 'Erro ao calcular frete',
            'valor_estimado': 0,
            'valor_por_km': 0,
            'distancia_km': 0,
            'origem': origem,
            'destino': destino,
            'modo_calculo': modo_calculo,
            'valor_medio_original': 0,
            'ajuste_quantidade': 0,
            'ajuste_inflacao': 0,
            'margem_aplicada': 0
        }
        
        # Calcular distância
        distancia = self._calcular_distancia(origem, destino)
        if not distancia:
            resultado['mensagem'] = 'Não foi possível calcular a distância entre origem e destino'
            return resultado
        
        resultado['distancia_km'] = distancia
        
        # Para fretes curtos (menos de 10km), usar lógica específica
        if distancia < 10:
            # Usar valor base para fretes curtos
            valor_base = VALOR_MEDIO_FRETE_CURTO
            
            # Ajuste por módulos ou peso
            if modo_calculo == "modulos" and num_modulos is not None:
                # Ajuste por módulos: 200 módulos é o padrão
                modulos_padrao = 200
                ajuste_quantidade = self._ajustar_por_modulos(valor_base, modulos_padrao, num_modulos)
            elif modo_calculo == "peso" and peso_kg is not None:
                # Ajuste por peso: 6000kg é o padrão (200 módulos * 30kg)
                peso_padrao = 6000
                ajuste_quantidade = self._ajustar_por_peso(valor_base, peso_padrao, peso_kg)
            else:
                ajuste_quantidade = 0
            
            # Sem ajuste de inflação para fretes curtos
            ajuste_inflacao = 0
            
            # Valor final antes da margem
            valor_final = valor_base + ajuste_quantidade + ajuste_inflacao
            
            # Aplicar margem adicional
            margem = valor_final * MARGEM_ADICIONAL
            valor_estimado = valor_final + margem
            
            # Calcular valor por km
            valor_por_km = valor_estimado / distancia if distancia > 0 else 0
            
            # Preencher resultado
            resultado['status'] = 'sucesso'
            resultado['mensagem'] = 'Frete calculado com sucesso'
            resultado['valor_estimado'] = round(valor_estimado, 2)
            resultado['valor_por_km'] = round(valor_por_km, 2)
            resultado['valor_medio_original'] = round(valor_base, 2)
            resultado['ajuste_quantidade'] = round(ajuste_quantidade, 2)
            resultado['ajuste_inflacao'] = round(ajuste_inflacao, 2)
            resultado['margem_aplicada'] = round(margem, 2)
            
            return resultado
        
        # Para fretes normais (não curtos), buscar fretes similares
        fretes_similares = self._buscar_fretes_similares(origem, destino, num_modulos, peso_kg, distancia, modo_calculo)
        
        # Se não encontrou fretes similares, usar valores de referência
        if fretes_similares.empty:
            valor_base = self._calcular_valor_referencia(distancia, num_modulos, peso_kg, modo_calculo)
            
            # Sem ajustes adicionais, pois o valor de referência já considera módulos/peso
            ajuste_quantidade = 0
            ajuste_inflacao = 0
            
            # Valor final antes da margem
            valor_final = valor_base
            
            # Aplicar margem adicional
            margem = valor_final * MARGEM_ADICIONAL
            valor_estimado = valor_final + margem
            
            # Calcular valor por km
            valor_por_km = valor_estimado / distancia if distancia > 0 else 0
            
            # Preencher resultado
            resultado['status'] = 'sucesso'
            resultado['mensagem'] = 'Frete calculado com base em valores de referência'
            resultado['valor_estimado'] = round(valor_estimado, 2)
            resultado['valor_por_km'] = round(valor_por_km, 2)
            resultado['valor_medio_original'] = round(valor_base, 2)
            resultado['ajuste_quantidade'] = round(ajuste_quantidade, 2)
            resultado['ajuste_inflacao'] = round(ajuste_inflacao, 2)
            resultado['margem_aplicada'] = round(margem, 2)
            
            return resultado
        
        # Calcular valor médio dos fretes similares
        valor_medio = fretes_similares['(R$) Frete'].mean()
        
        # Calcular ajuste por módulos ou peso
        if modo_calculo == "modulos" and num_modulos is not None:
            modulos_medio = fretes_similares['Núm. Módulos'].mean()
            ajuste_quantidade = self._ajustar_por_modulos(valor_medio, modulos_medio, num_modulos)
        elif modo_calculo == "peso" and peso_kg is not None:
            if 'Peso real (kg)' in fretes_similares.columns and fretes_similares['Peso real (kg)'].notna().any():
                peso_medio = fretes_similares['Peso real (kg)'].mean()
                ajuste_quantidade = self._ajustar_por_peso(valor_medio, peso_medio, peso_kg)
            else:
                # Se não tiver peso, estima com base em módulos (30kg por módulo)
                modulos_medio = fretes_similares['Núm. Módulos'].mean()
                peso_medio = modulos_medio * 30
                ajuste_quantidade = self._ajustar_por_peso(valor_medio, peso_medio, peso_kg)
        else:
            ajuste_quantidade = 0
        
        # Calcular ajuste de inflação
        data_referencia = None
        for col in ['Data Envio Proposta', 'Data de Orçamento', 'Previsão para descarte']:
            if col in fretes_similares.columns and fretes_similares[col].notna().any():
                data_referencia = fretes_similares[col].mean()
                break
        
        ajuste_inflacao = self._calcular_ajuste_inflacao(valor_medio, data_referencia)
        
        # Valor final antes da margem
        valor_final = valor_medio + ajuste_quantidade + ajuste_inflacao
        
        # Aplicar margem adicional
        margem = valor_final * MARGEM_ADICIONAL
        valor_estimado = valor_final + margem
        
        # Calcular valor por km
        valor_por_km = valor_estimado / distancia if distancia > 0 else 0
        
        # Preencher resultado
        resultado['status'] = 'sucesso'
        resultado['mensagem'] = 'Frete calculado com sucesso'
        resultado['valor_estimado'] = round(valor_estimado, 2)
        resultado['valor_por_km'] = round(valor_por_km, 2)
        resultado['valor_medio_original'] = round(valor_medio, 2)
        resultado['ajuste_quantidade'] = round(ajuste_quantidade, 2)
        resultado['ajuste_inflacao'] = round(ajuste_inflacao, 2)
        resultado['margem_aplicada'] = round(margem, 2)
        resultado['fretes_base'] = len(fretes_similares)
        
        return resultado

def main():
    """Função principal para uso via linha de comando."""
    parser = argparse.ArgumentParser(description='Calculadora de Fretes')
    parser.add_argument('--origem', required=True, help='Endereço de origem')
    parser.add_argument('--destino', required=True, help='Endereço de destino')
    parser.add_argument('--modulos', type=int, help='Número de módulos')
    parser.add_argument('--peso', type=float, help='Peso em kg')
    parser.add_argument('--data', help='Data prevista (formato: DD/MM/AAAA)')
    parser.add_argument('--modo', choices=['modulos', 'peso'], default='modulos', help='Modo de cálculo')
    parser.add_argument('--excel', help='Caminho para o arquivo Excel')
    
    args = parser.parse_args()
    
    # Converter data se fornecida
    data_prevista = None
    if args.data:
        try:
            data_prevista = datetime.strptime(args.data, '%d/%m/%Y')
        except ValueError:
            print("Formato de data inválido. Use DD/MM/AAAA.")
            sys.exit(1)
    
    # Inicializar calculadora
    calculadora = CalculadoraFrete(args.excel)
    
    # Calcular frete
    resultado = calculadora.calcular_frete(
        args.origem,
        args.destino,
        args.modulos,
        args.peso,
        data_prevista,
        args.modo
    )
    
    # Exibir resultado
    if resultado['status'] == 'sucesso':
        print(f"\nCálculo de Frete: {args.origem} → {args.destino}")
        print(f"Distância: {resultado['distancia_km']} km")
        print(f"Modo de cálculo: {args.modo}")
        if args.modo == 'modulos':
            print(f"Módulos: {args.modulos}")
        else:
            print(f"Peso: {args.peso} kg")
        print(f"\nValor estimado: R$ {resultado['valor_estimado']:.2f}")
        print(f"Valor por km: R$ {resultado['valor_por_km']:.2f}")
        print("\nDetalhes do cálculo:")
        print(f"Valor médio base: R$ {resultado['valor_medio_original']:.2f}")
        print(f"Ajuste por {'módulos' if args.modo == 'modulos' else 'peso'}: R$ {resultado['ajuste_quantidade']:.2f}")
        print(f"Ajuste de inflação: R$ {resultado['ajuste_inflacao']:.2f}")
        print(f"Margem aplicada (10%): R$ {resultado['margem_aplicada']:.2f}")
        if 'fretes_base' in resultado:
            print(f"Fretes base: {resultado['fretes_base']}")
    else:
        print(f"Erro: {resultado['mensagem']}")

if __name__ == "__main__":
    main()

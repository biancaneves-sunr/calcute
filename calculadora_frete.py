#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Calculadora de Fretes - Versão 3.0 (Recalibrada)
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
ARQUIVO_EXCEL = 'https://raw.githubusercontent.com/biancaneves-sunr/calcute/0026cd7d0bf1ae3cf6a5be69516155e39b0f0e3d/Banco%20de%20Dados%20-%20Logistica.xlsx'
TAXA_INFLACAO_ANUAL = 0.045  # 4.5% ao ano (média IPCA)
MARGEM_ADICIONAL = 0.10  # 10% de margem adicional

# Valores de referência para fretes curtos (menos de 10km)
VALOR_MEDIO_FRETE_CURTO = 800  # Valor médio para fretes curtos conforme informado pelo usuário
VALOR_POR_KM_PADRAO = 100  # Valor por km padrão para fretes curtos

class CalculadoraFrete:
    def __init__(self, arquivo_excel=ARQUIVO_EXCEL):
        """Inicializa a calculadora de fretes."""
        self.dados = self._carregar_dados(arquivo_excel)
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
    
    def _buscar_fretes_similares(self, cidade_origem, cidade_destino, num_modulos=None, peso_kg=None, distancia=None, modo_calculo="modulos"):
        """Busca fretes similares na base de dados com filtros mais rigorosos."""
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
        
        # Se não encontrou nada específico, usar valores médios da faixa de distância
        if distancia:
            # Criar um DataFrame com valores médios baseados na distância
            if distancia < 10:  # Fretes curtos
                return pd.DataFrame({
                    '(R$) Frete': [VALOR_MEDIO_FRETE_CURTO],
                    'Distancia Valinhos (km)': [distancia if distancia else 7],
                    'Núm. Módulos': [num_modulos if num_modulos else 200],
                    'Peso real (kg)': [peso_kg if peso_kg else 6000],
                    'Data Envio Proposta': [datetime.now() - timedelta(days=30)]
                })
            elif distancia < 100:  # Fretes médios
                return pd.DataFrame({
                    '(R$) Frete': [distancia * 120],  # Valor médio por km para fretes médios
                    'Distancia Valinhos (km)': [distancia],
                    'Núm. Módulos': [num_modulos if num_modulos else 200],
                    'Peso real (kg)': [peso_kg if peso_kg else 6000],
                    'Data Envio Proposta': [datetime.now() - timedelta(days=30)]
                })
            else:  # Fretes longos
                return pd.DataFrame({
                    '(R$) Frete': [distancia * 100],  # Valor médio por km para fretes longos
                    'Distancia Valinhos (km)': [distancia],
                    'Núm. Módulos': [num_modulos if num_modulos else 200],
                    'Peso real (kg)': [peso_kg if peso_kg else 6000],
                    'Data Envio Proposta': [datetime.now() - timedelta(days=30)]
                })
        
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
        # Ajustado para ser menos agressivo
        fator = (modulos_alvo / modulos_base) ** (-0.05)  # Expoente menos agressivo
        return valor_base * (modulos_alvo / modulos_base) * fator
    
    def _ajustar_por_peso(self, valor_base, peso_base, peso_alvo):
        """Ajusta o valor com base na diferença de peso em kg."""
        if peso_base == 0 or pd.isna(peso_base):
            # Se não tiver peso base, estima com base em 30kg por módulo
            modulos_base = 200  # Valor padrão
            peso_base = modulos_base * 30
        
        # Fator de economia de escala: quanto maior o peso, menor o valor por kg
        # Ajustado para ser menos agressivo
        fator = (peso_alvo / peso_base) ** (-0.05)  # Expoente menos agressivo
        return valor_base * (peso_alvo / peso_base) * fator
    
    def _calcular_valor_por_km(self, fretes_similares, distancia):
        """Calcula o valor médio por km com base nos fretes similares."""
        if distancia is None or distancia == 0:
            # Se não tiver distância calculada, usar a média das distâncias disponíveis
            distancia_valinhos = fretes_similares['Distancia Valinhos (km)'].mean()
            distancia_mc = fretes_similares['Distancia-MC (km)'].mean()
            
            if not pd.isna(distancia_valinhos) and distancia_valinhos > 0:
                distancia = distancia_valinhos
            elif not pd.isna(distancia_mc) and distancia_mc > 0:
                distancia = distancia_mc
            else:
                return VALOR_POR_KM_PADRAO  # Valor padrão por km
        
        # Para fretes curtos, usar um valor por km mais alto
        if distancia < 10:
            return VALOR_POR_KM_PADRAO
        
        # Calcular valor por km para cada frete similar
        valores_por_km = []
        for _, row in fretes_similares.iterrows():
            frete = row['(R$) Frete']
            
            # Verificar qual coluna de distância usar
            if not pd.isna(row.get('Distancia Valinhos (km)', np.nan)) and row['Distancia Valinhos (km)'] > 0:
                dist = row['Distancia Valinhos (km)']
            elif not pd.isna(row.get('Distancia-MC (km)', np.nan)) and row['Distancia-MC (km)'] > 0:
                dist = row['Distancia-MC (km)']
            else:
                continue
            
            if dist > 0:
                valores_por_km.append(frete / dist)
        
        # Calcular média dos valores por km
        if valores_por_km:
            # Remover outliers (valores acima do percentil 90)
            if len(valores_por_km) > 5:
                valores_por_km.sort()
                valores_por_km = valores_por_km[:int(len(valores_por_km) * 0.9)]
            
            valor_medio_por_km = np.mean(valores_por_km)
            return valor_medio_por_km
        
        # Se não conseguir calcular, usar valor padrão baseado na distância
        if distancia < 10:
            return VALOR_POR_KM_PADRAO
        elif distancia < 100:
            return 120  # Valor médio por km para fretes médios
        else:
            return 100  # Valor médio por km para fretes longos
    
    def calcular_frete(self, origem, destino, num_modulos=None, peso_kg=None, data=None, modo_calculo="modulos"):
        """Calcula o valor estimado do frete."""
        if data is None:
            data = datetime.now()
        
        # Validar parâmetros
        if modo_calculo == "modulos" and (num_modulos is None or num_modulos <= 0):
            return {
                "status": "erro",
                "mensagem": "Número de módulos deve ser fornecido e maior que zero para cálculo por módulos."
            }
        
        if modo_calculo == "peso" and (peso_kg is None or peso_kg <= 0):
            return {
                "status": "erro",
                "mensagem": "Peso em kg deve ser fornecido e maior que zero para cálculo por peso."
            }
        
        # Calcular distância
        distancia = self._calcular_distancia(origem, destino)
        
        # Verificar se é um frete curto (menos de 10km)
        is_frete_curto = distancia is not None and distancia < 10
        
        # Buscar fretes similares
        fretes_similares = self._buscar_fretes_similares(
            origem, destino, num_modulos, peso_kg, distancia, modo_calculo
        )
        
        if fretes_similares.empty:
            return {
                "status": "erro",
                "mensagem": "Não foram encontrados fretes similares na base de dados."
            }
        
        # Para fretes curtos, usar lógica simplificada
        if is_frete_curto:
            # Usar valor médio informado pelo usuário (R$ 800) como base
            valor_base = VALOR_MEDIO_FRETE_CURTO
            
            # Ajustar por distância
            if distancia:
                valor_por_km = VALOR_POR_KM_PADRAO
                valor_base = max(valor_base, distancia * valor_por_km)
            
            # Ajustar por quantidade
            if modo_calculo == "modulos" and num_modulos:
                # Ajuste simples: 10% a mais ou a menos para cada 50 módulos de diferença
                modulos_padrao = 200
                fator_ajuste = 1 + ((num_modulos - modulos_padrao) / modulos_padrao) * 0.1
                valor_base *= max(0.5, min(fator_ajuste, 2.0))  # Limitar o ajuste
            
            # Aplicar margem adicional
            valor_final = valor_base * (1 + MARGEM_ADICIONAL)
            
            # Preparar resultado
            resultado = {
                "status": "sucesso",
                "valor_estimado": round(valor_final, 2),
                "distancia_km": distancia,
                "fretes_base": 1,
                "valor_medio_original": round(valor_base, 2),
                "valor_por_km": round(VALOR_POR_KM_PADRAO, 2),
                "valor_total_por_km": round(distancia * VALOR_POR_KM_PADRAO if distancia else 0, 2),
                "ajuste_quantidade": 0,
                "ajuste_inflacao": 0,
                "margem_aplicada": round(valor_base * MARGEM_ADICIONAL, 2),
                "detalhes": {
                    "origem": origem,
                    "destino": destino,
                    "modo_calculo": modo_calculo,
                    "parametro_base": 200 if modo_calculo == "modulos" else 6000,
                    "parametro_alvo": num_modulos if modo_calculo == "modulos" else peso_kg,
                    "unidade": "módulos" if modo_calculo == "modulos" else "kg",
                    "data_consulta": data.strftime("%Y-%m-%d")
                }
            }
            
            return resultado
        
        # Para fretes normais, usar lógica padrão com ajustes
        # Calcular valor base (média ponderada dos fretes similares)
        fretes_similares['Peso'] = 1.0  # Peso padrão
        
        # Dar mais peso para fretes mais recentes
        for idx, row in fretes_similares.iterrows():
            # Priorizar 'Previsão para descarte' como data de referência
            data_ref = None
            if not pd.isna(row.get('Previsão para descarte', pd.NaT)):
                data_ref = row['Previsão para descarte']
            elif not pd.isna(row.get('Data Envio Proposta', pd.NaT)):
                data_ref = row['Data Envio Proposta']
            
            if data_ref is not None:
                # Quanto mais recente, maior o peso
                dias_passados = (datetime.now() - data_ref).days
                if dias_passados > 0:
                    fretes_similares.at[idx, 'Peso'] = 1 + (365 / dias_passados) * 0.5
        
        # Calcular média ponderada do valor do frete
        valor_medio = np.average(
            fretes_similares['(R$) Frete'], 
            weights=fretes_similares['Peso']
        )
        
        # Calcular valor por km
        valor_por_km_unitario = self._calcular_valor_por_km(fretes_similares, distancia)
        
        # Usar distância calculada ou média das distâncias disponíveis
        if distancia is None:
            distancia_valinhos = fretes_similares['Distancia Valinhos (km)'].mean()
            distancia_mc = fretes_similares['Distancia-MC (km)'].mean()
            
            if not pd.isna(distancia_valinhos) and distancia_valinhos > 0:
                distancia = distancia_valinhos
            elif not pd.isna(distancia_mc) and distancia_mc > 0:
                distancia = distancia_mc
        
        # Calcular valor total por km
        valor_por_km = valor_por_km_unitario * (distancia if distancia else 0)
        
        # Ajustar valor conforme o modo de cálculo
        if modo_calculo == "modulos":
            modulos_medio = fretes_similares['Núm. Módulos'].mean()
            valor_ajustado = self._ajustar_por_modulos(valor_medio, modulos_medio, num_modulos)
            parametro_base = modulos_medio
            parametro_alvo = num_modulos
            unidade = "módulos"
        else:  # modo_calculo == "peso"
            # Verificar se há dados de peso disponíveis
            if 'Peso real (kg)' in fretes_similares.columns and fretes_similares['Peso real (kg)'].notna().any():
                peso_medio = fretes_similares['Peso real (kg)'].mean()
            else:
                # Estimar peso médio com base em módulos (30kg por módulo)
                modulos_medio = fretes_similares['Núm. Módulos'].mean()
                peso_medio = modulos_medio * 30
            
            valor_ajustado = self._ajustar_por_peso(valor_medio, peso_medio, peso_kg)
            parametro_base = peso_medio
            parametro_alvo = peso_kg
            unidade = "kg"
        
        # Obter data média dos fretes similares para ajuste de inflação
        data_media = None
        if 'Previsão para descarte' in fretes_similares.columns:
            data_media = fretes_similares['Previsão para descarte'].mean()
        if pd.isna(data_media) and 'Data Envio Proposta' in fretes_similares.columns:
            data_media = fretes_similares['Data Envio Proposta'].mean()
        
        # Ajustar por inflação
        valor_ajustado_inflacao = self._calcular_ajuste_inflacao(valor_ajustado, data_media)
        
        # Aplicar margem adicional
        valor_final = valor_ajustado_inflacao * (1 + MARGEM_ADICIONAL)
        
        # Garantir que o valor final não seja menor que o valor por km
        if valor_por_km > 0:
            valor_final = max(valor_final, valor_por_km * (1 + MARGEM_ADICIONAL))
        
        # Preparar resultado
        resultado = {
            "status": "sucesso",
            "valor_estimado": round(valor_final, 2),
            "distancia_km": distancia,
            "fretes_base": len(fretes_similares),
            "valor_medio_original": round(valor_medio, 2),
            "valor_por_km": round(valor_por_km_unitario, 2),
            "valor_total_por_km": round(valor_por_km, 2),
            "ajuste_quantidade": round(valor_ajustado - valor_medio, 2),
            "ajuste_inflacao": round(valor_ajustado_inflacao - valor_ajustado, 2),
            "margem_aplicada": round(valor_final - valor_ajustado_inflacao, 2),
            "detalhes": {
                "origem": origem,
                "destino": destino,
                "modo_calculo": modo_calculo,
                "parametro_base": round(parametro_base, 2) if parametro_base else 0,
                "parametro_alvo": parametro_alvo,
                "unidade": unidade,
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
    
    if resultado['detalhes']['modo_calculo'] == "modulos":
        saida += f"Módulos: {resultado['detalhes']['parametro_alvo']}\n"
    else:
        saida += f"Peso: {resultado['detalhes']['parametro_alvo']} kg\n"
    
    saida += f"Distância: {resultado['distancia_km']} km\n\n"
    
    saida += f"VALOR ESTIMADO: R$ {resultado['valor_estimado']:.2f}\n"
    saida += f"Valor por km: R$ {resultado['valor_por_km']:.2f}\n\n"
    
    saida += "Detalhes do cálculo:\n"
    saida += f"- Valor médio base: R$ {resultado['valor_medio_original']:.2f}\n"
    
    if resultado['detalhes']['modo_calculo'] == "modulos":
        saida += f"- Ajuste por módulos: R$ {resultado['ajuste_quantidade']:.2f}\n"
    else:
        saida += f"- Ajuste por peso: R$ {resultado['ajuste_quantidade']:.2f}\n"
    
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
    parser.add_argument('--modulos', type=int, help='Número de módulos')
    parser.add_argument('--peso', type=float, help='Peso em kg')
    parser.add_argument('--modo', choices=['modulos', 'peso'], default='modulos', help='Modo de cálculo')
    parser.add_argument('--data', help='Data prevista (formato YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # Validar argumentos
    if args.modo == 'modulos' and args.modulos is None:
        print("Erro: Para o modo de cálculo por módulos, o número de módulos é obrigatório.")
        sys.exit(1)
    
    if args.modo == 'peso' and args.peso is None:
        print("Erro: Para o modo de cálculo por peso, o peso em kg é obrigatório.")
        sys.exit(1)
    
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
    if args.modo == 'modulos':
        resultado = calculadora.calcular_frete(args.origem, args.destino, args.modulos, None, data, "modulos")
    else:
        resultado = calculadora.calcular_frete(args.origem, args.destino, None, args.peso, data, "peso")
    
    # Exibir resultado
    print(formatar_resultado(resultado))

if __name__ == "__main__":
    main()

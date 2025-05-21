#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de Teste para Calculadora de Fretes
------------------------------------------
Este script executa testes automatizados na calculadora de fretes
para validar seu funcionamento em diferentes cenários.
"""

import os
import sys
import pandas as pd
from datetime import datetime
from calculadora_frete import CalculadoraFrete

def executar_teste(calculadora, origem, destino, modulos, descricao):
    """Executa um teste específico e formata o resultado."""
    print(f"\n{'=' * 60}")
    print(f"TESTE: {descricao}")
    print(f"{'=' * 60}")
    print(f"Origem: {origem}")
    print(f"Destino: {destino}")
    print(f"Módulos: {modulos}")
    
    try:
        resultado = calculadora.calcular_frete(origem, destino, modulos)
        
        if resultado["status"] == "sucesso":
            print(f"\nResultado: SUCESSO")
            print(f"Valor estimado: R$ {resultado['valor_estimado']:.2f}")
            print(f"Distância: {resultado['distancia_km']} km")
            print(f"Fretes base: {resultado['fretes_base']}")
            print("\nDetalhes do cálculo:")
            print(f"- Valor médio base: R$ {resultado['valor_medio_original']:.2f}")
            print(f"- Ajuste por módulos: R$ {resultado['ajuste_modulos']:.2f}")
            print(f"- Ajuste de inflação: R$ {resultado['ajuste_inflacao']:.2f}")
            print(f"- Margem aplicada (10%): R$ {resultado['margem_aplicada']:.2f}")
        else:
            print(f"\nResultado: ERRO")
            print(f"Mensagem: {resultado['mensagem']}")
        
        return resultado
    except Exception as e:
        print(f"\nErro durante o teste: {e}")
        return {"status": "erro", "mensagem": str(e)}

def main():
    """Função principal para execução dos testes."""
    print("Iniciando testes da Calculadora de Fretes...")
    
    # Inicializar calculadora
    calculadora = CalculadoraFrete()
    
    # Definir cenários de teste
    cenarios = [
        {
            "descricao": "Caso 1: Cidades grandes com muitos módulos",
            "origem": "São Paulo, SP",
            "destino": "Rio de Janeiro, RJ",
            "modulos": 300
        },
        {
            "descricao": "Caso 2: Cidades médias com poucos módulos",
            "origem": "Campinas, SP",
            "destino": "Valinhos, SP",
            "modulos": 50
        },
        {
            "descricao": "Caso 3: Cidades distantes com módulos médios",
            "origem": "Porto Alegre, RS",
            "destino": "Manaus, AM",
            "modulos": 150
        },
        {
            "descricao": "Caso 4: Usando CEPs",
            "origem": "04538-133, São Paulo, SP",
            "destino": "22031-001, Rio de Janeiro, RJ",
            "modulos": 200
        },
        {
            "descricao": "Caso 5: Cidades sem histórico direto",
            "origem": "Chapecó, SC",
            "destino": "Palmas, TO",
            "modulos": 100
        }
    ]
    
    # Executar testes
    resultados = []
    for cenario in cenarios:
        resultado = executar_teste(
            calculadora,
            cenario["origem"],
            cenario["destino"],
            cenario["modulos"],
            cenario["descricao"]
        )
        resultados.append({
            "cenario": cenario,
            "resultado": resultado
        })
    
    # Resumo dos testes
    print("\n\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    sucessos = sum(1 for r in resultados if r["resultado"].get("status") == "sucesso")
    print(f"Total de testes: {len(resultados)}")
    print(f"Sucessos: {sucessos}")
    print(f"Falhas: {len(resultados) - sucessos}")
    
    # Salvar resultados em CSV para análise
    dados = []
    for r in resultados:
        if r["resultado"].get("status") == "sucesso":
            dados.append({
                "Descrição": r["cenario"]["descricao"],
                "Origem": r["cenario"]["origem"],
                "Destino": r["cenario"]["destino"],
                "Módulos": r["cenario"]["modulos"],
                "Valor Estimado": r["resultado"].get("valor_estimado", 0),
                "Distância (km)": r["resultado"].get("distancia_km", 0),
                "Fretes Base": r["resultado"].get("fretes_base", 0),
                "Status": "Sucesso"
            })
        else:
            dados.append({
                "Descrição": r["cenario"]["descricao"],
                "Origem": r["cenario"]["origem"],
                "Destino": r["cenario"]["destino"],
                "Módulos": r["cenario"]["modulos"],
                "Valor Estimado": 0,
                "Distância (km)": 0,
                "Fretes Base": 0,
                "Status": "Falha"
            })
    
    df = pd.DataFrame(dados)
    arquivo_saida = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados_teste.csv")
    df.to_csv(arquivo_saida, index=False)
    print(f"\nResultados salvos em: {arquivo_saida}")

if __name__ == "__main__":
    main()

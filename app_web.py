#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface Web para Calculadora de Fretes
----------------------------------------
Este script implementa uma interface web simples para a calculadora de fretes,
permitindo o uso por múltiplos usuários sem necessidade de linha de comando.
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, request, render_template, jsonify
from calculadora_frete import CalculadoraFrete

app = Flask(__name__)
calculadora = None

@app.route('/')
def index():
    """Renderiza a página inicial com o formulário de cotação."""
    return render_template('index.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    """Processa a requisição de cálculo de frete e retorna o resultado."""
    try:
        # Obter dados do formulário
        origem = request.form.get('origem', '')
        destino = request.form.get('destino', '')
        modulos = request.form.get('modulos', '0')
        data_str = request.form.get('data', '')
        
        # Validar dados
        if not origem or not destino:
            return jsonify({
                "status": "erro",
                "mensagem": "Origem e destino são obrigatórios."
            })
        
        try:
            modulos = int(modulos)
            if modulos <= 0:
                return jsonify({
                    "status": "erro",
                    "mensagem": "A quantidade de módulos deve ser um número positivo."
                })
        except ValueError:
            return jsonify({
                "status": "erro",
                "mensagem": "A quantidade de módulos deve ser um número válido."
            })
        
        # Processar data
        data = None
        if data_str:
            try:
                data = datetime.strptime(data_str, '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    "status": "erro",
                    "mensagem": "Formato de data inválido. Use YYYY-MM-DD."
                })
        
        # Calcular frete
        global calculadora
        if calculadora is None:
            calculadora = CalculadoraFrete()
        
        resultado = calculadora.calcular_frete(origem, destino, modulos, data)
        return jsonify(resultado)
    
    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro ao processar requisição: {str(e)}"
        })

@app.route('/historico')
def historico():
    """Renderiza a página de histórico de cotações."""
    # Em uma implementação completa, isso buscaria do banco de dados
    # Por enquanto, apenas renderiza a página vazia
    return render_template('historico.html', cotacoes=[])

def criar_estrutura_pastas():
    """Cria a estrutura de pastas necessária para a aplicação."""
    # Criar pasta de templates
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Criar pasta de arquivos estáticos
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    os.makedirs(static_dir, exist_ok=True)
    os.makedirs(os.path.join(static_dir, 'css'), exist_ok=True)
    os.makedirs(os.path.join(static_dir, 'js'), exist_ok=True)
    
    # Criar templates HTML
    index_html = os.path.join(templates_dir, 'index.html')
    historico_html = os.path.join(templates_dir, 'historico.html')
    base_html = os.path.join(templates_dir, 'base.html')
    
    # Criar arquivos estáticos
    style_css = os.path.join(static_dir, 'css', 'style.css')
    script_js = os.path.join(static_dir, 'js', 'script.js')
    
    # Conteúdo do template base
    with open(base_html, 'w') as f:
        f.write("""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Calculadora de Fretes{% endblock %}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">Calculadora de Fretes</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Nova Cotação</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/historico">Histórico</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>

    <footer class="footer mt-5 py-3 bg-light">
        <div class="container text-center">
            <span class="text-muted">Calculadora de Fretes &copy; 2025</span>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
""")
    
    # Conteúdo da página inicial
    with open(index_html, 'w') as f:
        f.write("""{% extends "base.html" %}

{% block title %}Calculadora de Fretes - Nova Cotação{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8 offset-md-2">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h2 class="card-title mb-0">Nova Cotação de Frete</h2>
            </div>
            <div class="card-body">
                <form id="freteForm">
                    <div class="mb-3">
                        <label for="origem" class="form-label">Origem:</label>
                        <input type="text" class="form-control" id="origem" name="origem" 
                               placeholder="Cidade/Estado ou endereço completo com CEP" required>
                        <div class="form-text">Ex: São Paulo, SP ou Rua Exemplo, 123 - São Paulo, SP, 01234-567</div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="destino" class="form-label">Destino:</label>
                        <input type="text" class="form-control" id="destino" name="destino" 
                               placeholder="Cidade/Estado ou endereço completo com CEP" required>
                    </div>
                    
                    <div class="mb-3">
                        <label for="modulos" class="form-label">Quantidade de Módulos:</label>
                        <input type="number" class="form-control" id="modulos" name="modulos" 
                               min="1" step="1" required>
                    </div>
                    
                    <div class="mb-3">
                        <label for="data" class="form-label">Data Prevista (opcional):</label>
                        <input type="date" class="form-control" id="data" name="data">
                    </div>
                    
                    <div class="d-grid gap-2">
                        <button type="submit" class="btn btn-primary btn-lg">Calcular Frete</button>
                    </div>
                </form>
            </div>
        </div>
        
        <div id="resultado" class="mt-4" style="display: none;">
            <div class="card">
                <div class="card-header bg-success text-white">
                    <h3 class="card-title mb-0">Resultado da Cotação</h3>
                </div>
                <div class="card-body">
                    <div id="resultadoConteudo">
                        <!-- Conteúdo preenchido via JavaScript -->
                    </div>
                </div>
            </div>
        </div>
        
        <div id="erro" class="mt-4 alert alert-danger" style="display: none;">
            <h4>Erro na Cotação</h4>
            <p id="mensagemErro"></p>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
document.getElementById('freteForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Mostrar indicador de carregamento
    document.getElementById('resultado').style.display = 'none';
    document.getElementById('erro').style.display = 'none';
    
    // Obter dados do formulário
    const formData = new FormData(this);
    
    // Enviar requisição
    fetch('/calcular', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'sucesso') {
            // Formatar e exibir resultado
            const html = `
                <div class="row">
                    <div class="col-md-6">
                        <h4>Detalhes da Cotação</h4>
                        <table class="table">
                            <tr>
                                <th>Origem:</th>
                                <td>${data.detalhes.origem}</td>
                            </tr>
                            <tr>
                                <th>Destino:</th>
                                <td>${data.detalhes.destino}</td>
                            </tr>
                            <tr>
                                <th>Módulos:</th>
                                <td>${data.detalhes.modulos}</td>
                            </tr>
                            <tr>
                                <th>Distância:</th>
                                <td>${data.distancia_km ? data.distancia_km + ' km' : 'Não calculada'}</td>
                            </tr>
                            <tr>
                                <th>Data da Consulta:</th>
                                <td>${data.detalhes.data_consulta}</td>
                            </tr>
                        </table>
                    </div>
                    <div class="col-md-6">
                        <div class="text-center mb-4">
                            <h4>Valor Estimado</h4>
                            <div class="display-4 text-primary">R$ ${data.valor_estimado.toFixed(2)}</div>
                            <p class="text-muted">Baseado em ${data.fretes_base} fretes similares</p>
                        </div>
                        
                        <h5>Detalhes do Cálculo</h5>
                        <table class="table table-sm">
                            <tr>
                                <th>Valor médio base:</th>
                                <td>R$ ${data.valor_medio_original.toFixed(2)}</td>
                            </tr>
                            <tr>
                                <th>Ajuste por módulos:</th>
                                <td>R$ ${data.ajuste_modulos.toFixed(2)}</td>
                            </tr>
                            <tr>
                                <th>Ajuste de inflação:</th>
                                <td>R$ ${data.ajuste_inflacao.toFixed(2)}</td>
                            </tr>
                            <tr>
                                <th>Margem aplicada (10%):</th>
                                <td>R$ ${data.margem_aplicada.toFixed(2)}</td>
                            </tr>
                        </table>
                    </div>
                </div>
            `;
            
            document.getElementById('resultadoConteudo').innerHTML = html;
            document.getElementById('resultado').style.display = 'block';
        } else {
            // Exibir mensagem de erro
            document.getElementById('mensagemErro').textContent = data.mensagem;
            document.getElementById('erro').style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        document.getElementById('mensagemErro').textContent = 'Erro ao processar a requisição. Tente novamente.';
        document.getElementById('erro').style.display = 'block';
    });
});
</script>
{% endblock %}
""")
    
    # Conteúdo da página de histórico
    with open(historico_html, 'w') as f:
        f.write("""{% extends "base.html" %}

{% block title %}Calculadora de Fretes - Histórico{% endblock %}

{% block content %}
<div class="card">
    <div class="card-header bg-primary text-white">
        <h2 class="card-title mb-0">Histórico de Cotações</h2>
    </div>
    <div class="card-body">
        {% if cotacoes %}
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Data</th>
                            <th>Origem</th>
                            <th>Destino</th>
                            <th>Módulos</th>
                            <th>Valor</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for cotacao in cotacoes %}
                        <tr>
                            <td>{{ cotacao.data }}</td>
                            <td>{{ cotacao.origem }}</td>
                            <td>{{ cotacao.destino }}</td>
                            <td>{{ cotacao.modulos }}</td>
                            <td>R$ {{ cotacao.valor }}</td>
                            <td>
                                <button class="btn btn-sm btn-primary">Detalhes</button>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        {% else %}
            <div class="alert alert-info">
                <p>Nenhuma cotação realizada ainda. <a href="/">Faça sua primeira cotação</a>.</p>
            </div>
        {% endif %}
    </div>
</div>
{% endblock %}
""")
    
    # Conteúdo do CSS
    with open(style_css, 'w') as f:
        f.write("""/* Estilos personalizados para a Calculadora de Fretes */

body {
    background-color: #f8f9fa;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.navbar {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    border: none;
}

.card-header {
    border-radius: 8px 8px 0 0 !important;
}

.btn-primary {
    background-color: #0d6efd;
    border-color: #0d6efd;
}

.btn-primary:hover {
    background-color: #0b5ed7;
    border-color: #0a58ca;
}

.footer {
    box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.05);
}

/* Estilos para o resultado */
#resultado .card-header {
    background-color: #198754;
}

.display-4 {
    font-weight: bold;
}

/* Responsividade para dispositivos móveis */
@media (max-width: 768px) {
    .card-body {
        padding: 1rem;
    }
    
    .display-4 {
        font-size: 2rem;
    }
}
""")
    
    # Conteúdo do JavaScript
    with open(script_js, 'w') as f:
        f.write("""// Funções JavaScript para a Calculadora de Fretes

// Função para formatar valores monetários
function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

// Função para formatar datas
function formatarData(dataString) {
    const data = new Date(dataString);
    return data.toLocaleDateString('pt-BR');
}

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    console.log('Calculadora de Fretes inicializada');
    
    // Definir data mínima como hoje para o campo de data
  
(Content truncated due to size limit. Use line ranges to read in chunks)
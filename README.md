# Documentação da Calculadora de Fretes

## Visão Geral

A Calculadora de Fretes é um sistema que permite estimar o valor de fretes com base em dados históricos, ajustando os valores de acordo com a inflação, quantidade de módulos e aplicando uma margem adicional de 10%. O sistema foi desenvolvido para facilitar a cotação de fretes, utilizando como referência uma base de dados de fretes anteriores.

## Funcionalidades Principais

1. **Cálculo de Frete Baseado em Histórico**:
   - Busca fretes similares na base de dados
   - Ajusta valores considerando a quantidade de módulos
   - Aplica correção de inflação com base na data
   - Adiciona margem de 10% sobre o valor final

2. **Cálculo de Distância**:
   - Utiliza geolocalização para calcular distâncias entre origem e destino
   - Suporta endereços completos com CEP ou apenas cidade/estado

3. **Interfaces Disponíveis**:
   - Interface de linha de comando (CLI) para uso rápido
   - Interface web para uso por múltiplos usuários sem instalação

## Requisitos do Sistema

- Python 3.6 ou superior
- Bibliotecas: pandas, geopy, flask (para interface web)
- Arquivo Excel com histórico de fretes

## Instalação

1. Clone ou baixe o repositório para sua máquina local
2. Instale as dependências necessárias:

```bash
pip install pandas geopy flask
```

3. Configure o caminho para o arquivo Excel na variável `ARQUIVO_EXCEL` no arquivo `calculadora_frete.py`

## Uso da Interface de Linha de Comando

Para calcular um frete via linha de comando:

```bash
python calculadora_frete.py --origem "São Paulo, SP" --destino "Rio de Janeiro, RJ" --modulos 200
```

Parâmetros disponíveis:
- `--origem`: Endereço de origem (obrigatório)
- `--destino`: Endereço de destino (obrigatório)
- `--modulos`: Número de módulos (obrigatório)
- `--data`: Data prevista no formato YYYY-MM-DD (opcional)

## Uso da Interface Web

Para iniciar a interface web:

```bash
python app_web.py
```

Após iniciar, acesse a interface em seu navegador através do endereço:
```
http://localhost:5000
```

Na interface web, você pode:
1. Preencher o formulário com origem, destino e quantidade de módulos
2. Visualizar o resultado detalhado da cotação
3. Acessar o histórico de cotações (funcionalidade a ser implementada em versões futuras)

## Estrutura de Arquivos

- `calculadora_frete.py`: Implementação principal da calculadora
- `teste_calculadora.py`: Script para testes automatizados
- `app_web.py`: Interface web usando Flask
- `templates/`: Arquivos HTML para a interface web
- `static/`: Arquivos CSS e JavaScript para a interface web
- `regras_calculo.md`: Documentação das regras de cálculo
- `fluxo_interativo.md`: Documentação do fluxo de interação

## Regras de Cálculo

O sistema utiliza as seguintes regras para calcular o valor do frete:

1. **Busca de Fretes Similares**:
   - Busca exata por origem, destino e quantidade similar de módulos
   - Se não encontrar, busca por proximidade geográfica
   - Se ainda não encontrar, utiliza fretes com distância similar

2. **Ajuste por Quantidade de Módulos**:
   - Aplica economia de escala: quanto maior a quantidade, menor o valor por módulo
   - Fórmula: `Valor Ajustado = Valor Base × (Módulos Alvo / Módulos Base) × Fator de Escala`

3. **Ajuste de Inflação**:
   - Calcula a diferença temporal entre a data do frete histórico e a data atual
   - Aplica taxa de inflação acumulada (atualmente 4.5% ao ano)
   - Fórmula: `Valor Ajustado = Valor Original × (1 + Taxa de Inflação) ^ Anos`

4. **Margem Adicional**:
   - Aplica margem de 10% sobre o valor final
   - Fórmula: `Valor Final = Valor Ajustado × 1.10`

## Integração com Notion

Para integrar com o Notion (implementação futura):

1. Utilize a API oficial do Notion para acessar os dados
2. Configure as credenciais de acesso no arquivo de configuração
3. Implemente a sincronização periódica dos dados

## Personalização

Você pode personalizar os seguintes parâmetros no arquivo `calculadora_frete.py`:

- `TAXA_INFLACAO_ANUAL`: Taxa de inflação anual para ajuste (padrão: 4.5%)
- `MARGEM_ADICIONAL`: Margem adicional sobre o valor final (padrão: 10%)
- `ARQUIVO_EXCEL`: Caminho para o arquivo Excel com histórico de fretes

## Solução de Problemas

### Erro ao obter coordenadas geográficas

Se o sistema não conseguir obter as coordenadas geográficas, verifique:
- Conexão com a internet
- Formato do endereço fornecido
- Limite de requisições da API de geolocalização

### Fretes similares não encontrados

Se o sistema não encontrar fretes similares:
- Verifique se há dados suficientes na base histórica
- Tente usar apenas cidade/estado em vez de endereço completo
- Considere adicionar mais registros à base de dados

## Próximos Passos e Melhorias Futuras

1. **Banco de Dados**:
   - Migrar de Excel para um banco de dados relacional ou NoSQL
   - Implementar cache de consultas frequentes

2. **Funcionalidades Adicionais**:
   - Histórico de cotações por usuário
   - Exportação de resultados em PDF ou CSV
   - Dashboard com análises e tendências

3. **Integração**:
   - API REST completa para integração com outros sistemas
   - Webhooks para notificações automáticas

## Suporte

Para dúvidas ou suporte, entre em contato com a equipe de desenvolvimento.

---

Desenvolvido com base nos requisitos fornecidos para cálculo de fretes com base em histórico, ajuste de inflação e margem adicional.

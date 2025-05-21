# Fluxo Interativo da Calculadora de Fretes

## Visão Geral do Sistema
A calculadora de fretes será um sistema que permite aos usuários obter estimativas de custo de frete com base em dados históricos, ajustados por inflação e com margem adicional. O sistema deve ser intuitivo, fácil de usar e capaz de lidar com diferentes cenários de disponibilidade de dados.

## Fluxo de Interação

### 1. Entrada de Dados
O usuário fornecerá as seguintes informações:

**Obrigatórias:**
- **Origem:** Cidade/Estado ou CEP completo
- **Destino:** Cidade/Estado ou CEP completo
- **Quantidade de Módulos:** Número inteiro

**Opcionais:**
- **Data Prevista:** Data para a qual o frete está sendo cotado (padrão: data atual)
- **Observações:** Informações adicionais relevantes

### 2. Processamento
O sistema seguirá estas etapas de processamento:

1. **Validação de Dados:**
   - Verificar se todos os campos obrigatórios foram preenchidos
   - Validar formato de CEP (se fornecido)
   - Validar quantidade de módulos (deve ser um número positivo)

2. **Enriquecimento de Dados:**
   - Se apenas cidade/estado for fornecido, tentar determinar CEP central
   - Calcular distância entre origem e destino usando API de geolocalização

3. **Busca de Fretes Similares:**
   - Aplicar regras de busca conforme definido no documento de regras
   - Priorizar correspondências exatas, depois proximidade geográfica

4. **Cálculo do Valor:**
   - Aplicar ajustes por quantidade de módulos
   - Aplicar correção de inflação
   - Adicionar margem de 10%

### 3. Apresentação de Resultados
O sistema apresentará:

- **Valor Estimado do Frete:** Valor final com todos os ajustes aplicados
- **Detalhes do Cálculo:** Informações sobre os fretes históricos utilizados como base
- **Distância Calculada:** Distância entre origem e destino
- **Fatores de Ajuste:** Inflação aplicada, ajuste por quantidade, etc.

## Interfaces do Sistema

### 1. Interface de Linha de Comando (CLI)
Para uso rápido e integração com outros sistemas:

```
python calcular_frete.py --origem "São Paulo, SP" --destino "Rio de Janeiro, RJ" --modulos 200
```

### 2. Interface Web Simples
Para uso por múltiplos usuários sem necessidade de instalação:

- **Página de Entrada:** Formulário com campos para origem, destino, quantidade de módulos e data
- **Página de Resultados:** Exibição do valor estimado e detalhes do cálculo
- **Histórico de Consultas:** Registro das consultas anteriores (opcional)

### 3. API REST
Para integração com outros sistemas:

- **Endpoint de Cotação:** `/api/v1/cotacao`
- **Método:** POST
- **Parâmetros:** origem, destino, modulos, data
- **Resposta:** JSON com valor estimado e detalhes

## Tratamento de Casos Especiais

### 1. Sem Dados Históricos
Quando não houver dados históricos similares:

1. Informar ao usuário que a estimativa é baseada em médias gerais
2. Utilizar valor médio por km e por módulo da base completa
3. Aplicar fator de ajuste regional se disponível

### 2. Dados Incompletos
Quando o usuário não fornecer todos os dados opcionais:

1. Assumir valores padrão (data atual, etc.)
2. Informar claramente quais pressupostos foram feitos

### 3. Múltiplas Correspondências
Quando houver múltiplos fretes históricos similares:

1. Utilizar média ponderada, dando mais peso aos mais recentes
2. Informar a quantidade de registros utilizados no cálculo

## Fluxograma do Sistema

```
[Entrada de Dados] → [Validação] → [Enriquecimento] → [Busca de Similares] → [Cálculo] → [Apresentação]
     ↑                   |               |                    |                 |             |
     |                   ↓               |                    |                 |             |
     +------------------[Correção]       |                    |                 |             |
                                         ↓                    |                 |             |
                         [API Geolocalização] ---------------→|                 |             |
                                                              ↓                 |             |
                                          [Base de Dados Históricos] ----------→|             |
                                                                                ↓             |
                                                             [Ajustes (Inflação, Margem)] ---→|
                                                                                              ↓
                                                                                      [Resultado Final]
```

## Considerações para Múltiplos Usuários

1. **Autenticação:** Sistema simples de login para rastrear quem fez cada consulta (opcional)
2. **Histórico por Usuário:** Cada usuário pode ver seu histórico de consultas
3. **Níveis de Acesso:** Possibilidade de definir quem pode ver detalhes completos do cálculo
4. **Exportação de Dados:** Permitir exportar resultados em CSV ou PDF

## Integração com Notion

Para integração com a base de dados do Notion:

1. Utilizar API oficial do Notion para acesso aos dados
2. Sincronizar periodicamente os dados para um cache local
3. Implementar mecanismo de atualização para manter dados atualizados

## Próximos Passos para Implementação

1. Desenvolver protótipo básico com interface de linha de comando
2. Implementar conexão com a base de dados Excel
3. Adicionar cálculo de distância via API de geolocalização
4. Desenvolver interface web simples
5. Implementar integração com Notion (opcional)

# Regras de Cálculo para a Calculadora de Fretes

## Campos Relevantes Identificados
Com base na análise da planilha, os seguintes campos são essenciais para o cálculo do frete:

1. **Origem/Destino**:
   - `Cidade/Estado` (100% preenchido)
   - `CEP origem` (63.4% preenchido)
   - `Destino` (71.9% preenchido)

2. **Distância**:
   - `Distancia Valinhos (km)` (63.6% preenchido)
   - `Distancia-MC (km)` (63.1% preenchido)

3. **Quantidade**:
   - `Núm. Módulos` (83.9% preenchido)

4. **Valores**:
   - `(R$) Frete` (60.3% preenchido)

5. **Datas**:
   - `Data Envio Proposta` (13.2% preenchido)
   - `Data de Orçamento` (4.6% preenchido)

## Regras de Cálculo do Frete

### 1. Busca de Fretes Similares
Quando um novo pedido de cotação for recebido, o sistema deverá:

1. **Busca Exata**: Verificar se existe um frete com a mesma origem e destino (cidade) e quantidade de módulos similar.
   
2. **Busca por Proximidade**: Se não houver correspondência exata:
   - Buscar fretes com origem na mesma cidade ou região
   - Considerar destinos similares (mesma cidade ou região)
   - Ajustar com base na diferença de distância

3. **Prioridade de Campos**:
   - Cidade/Estado (origem e destino)
   - Número de Módulos
   - Distância em km

### 2. Cálculo de Distância
Quando o CEP for fornecido:
1. Utilizar API de geolocalização para obter as coordenadas dos CEPs
2. Calcular a distância entre os pontos
3. Se não houver CEP, utilizar a distância média para a cidade/região

### 3. Ajuste por Quantidade de Módulos
1. Identificar fretes com quantidade de módulos similar
2. Aplicar ajuste proporcional quando a quantidade for diferente:
   - Se a quantidade for maior: redução proporcional no valor por módulo
   - Se a quantidade for menor: aumento proporcional no valor por módulo

### 4. Ajuste de Inflação
1. Calcular a diferença temporal entre a data do frete histórico e a data atual
2. Aplicar taxa de inflação acumulada no período (IPCA)
3. Fórmula: `Valor Ajustado = Valor Original × (1 + Taxa de Inflação Acumulada)`

### 5. Aplicação de Margem
1. Após todos os ajustes, aplicar margem adicional de 10% sobre o valor final
2. Fórmula: `Valor Final = Valor Ajustado × 1.10`

### 6. Tratamento de Casos Especiais
1. **Sem Histórico Similar**: 
   - Utilizar média de valores por km e por módulo
   - Aplicar fator de ajuste regional

2. **Dados Incompletos**:
   - Se faltar CEP: solicitar cidade/estado
   - Se faltar quantidade de módulos: solicitar estimativa

## Formato do Prompt Padrão
Para padronizar as consultas, o prompt deverá conter:

```
Origem: [Endereço completo com CEP]
Destino: [Endereço completo com CEP]
Quantidade de Módulos: [Número]
Data Prevista: [Data]
```

## Formato da Resposta
A resposta deverá incluir:

1. Valor estimado do frete (com margem de 10%)
2. Distância calculada entre origem e destino
3. Base de cálculo (fretes similares encontrados)
4. Observações relevantes (ajustes aplicados)

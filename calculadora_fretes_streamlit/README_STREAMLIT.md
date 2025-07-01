# Documentação da Calculadora de Fretes - Versão 5.0

## Visão Geral

A Calculadora de Fretes 5.0 é um sistema completamente recalibrado que estima o valor de fretes com base em dados históricos reais, oferecendo duas modalidades de cálculo (por módulos ou por peso) e garantindo valores realistas alinhados com o histórico da empresa.

## Principais Melhorias na Versão 5.0

1. **Valores Realistas**: Algoritmo totalmente recalibrado com base em análise estatística detalhada do histórico
2. **Lógica por Faixas**: Cálculos específicos para diferentes faixas de distância, módulos e peso
3. **Apresentação Clara**: Detalhes do cálculo exibidos de forma transparente e consistente
4. **Interface Aprimorada**: Rótulos corretos e valores em tamanho maior para melhor visualização
5. **Robustez**: Funcionamento mesmo sem acesso à base de dados, usando valores de referência estatísticos

## Funcionalidades Principais

1. **Cálculo de Frete com Dupla Modalidade**:
   - Cálculo por número de módulos
   - Cálculo por peso em kg
   - Ajuste automático baseado em dados históricos

2. **Valor por Quilômetro**:
   - Cálculo do valor por km com base nos fretes históricos
   - Exibição do valor unitário por km para referência

3. **Ajustes Automáticos**:
   - Correção de inflação com base na data do frete histórico
   - Economia de escala (quanto maior a quantidade, menor o valor unitário)
   - Margem adicional de 10% sobre o valor final

## Exemplos de Valores Reais (Validados)

### Fretes Curtos

| Origem-Destino | Distância | Módulos | Valor Estimado | Valor Base | Ajuste por Módulos | Margem (10%) |
|----------------|-----------|---------|----------------|------------|-------------------|-------------|
| Vinhedo-Valinhos | 6,91 km | 50 | R$ 270,85 | R$ 800,00 | R$ -553,77 | R$ 24,62 |
| Vinhedo-Valinhos | 6,91 km | 200 | R$ 880,00 | R$ 800,00 | R$ 0,00 | R$ 80,00 |
| Vinhedo-Valinhos | 6,91 km | 1000 | R$ 3.456,27 | R$ 800,00 | R$ 2.342,06 | R$ 314,21 |

### Fretes Longos

| Origem-Destino | Distância | Peso (kg) | Valor Estimado | Valor Base | Ajuste por Peso | Margem (10%) |
|----------------|-----------|-----------|----------------|------------|----------------|-------------|
| Montes Claros-Mogi das Cruzes | 788,23 km | 12.000 | R$ 8.376,10 | R$ 7.944,04 | R$ -450,06 | R$ 761,46 |

## Lógica de Cálculo

### Fretes Curtos (menos de 10km)

Para fretes curtos, o sistema utiliza uma lógica especial:

1. Busca por fretes históricos exatos para o mesmo trajeto
2. Se não encontrar, utiliza um valor base de R$ 800,00 (ajustável conforme necessidade)
3. Aplica ajustes por quantidade de módulos ou peso:
   - 200 módulos é considerado o padrão (sem ajuste)
   - Menos de 200 módulos: ajuste negativo (economia de escala inversa)
   - Mais de 200 módulos: ajuste positivo (proporcional à quantidade)
4. Adiciona margem de 10%

### Fretes Normais

Para fretes de média e longa distância:

1. Busca fretes históricos similares, removendo outliers
2. Se não encontrar, usa valores de referência estatísticos por faixa de distância
3. Aplica ajustes por quantidade (módulos ou peso) e inflação
4. Aplica margem adicional de 10%

### Valores de Referência por Faixa

O sistema utiliza valores de referência estatísticos para cada faixa de distância, módulos e peso, baseados na análise detalhada do histórico:

**Por Distância:**
- 0-10km: R$ 800,00 (valor médio) | R$ 100,00 (por km)
- 10-50km: R$ 980,00 (valor médio) | R$ 26,49 (por km)
- 50-100km: R$ 3.767,00 (valor médio) | R$ 44,94 (por km)
- 100-500km: R$ 5.574,00 (valor médio) | R$ 15,62 (por km)
- 500-1000km: R$ 11.248,00 (valor médio) | R$ 14,35 (por km)
- 1000km+: R$ 19.234,00 (valor médio) | R$ 10,32 (por km)

**Por Módulos:**
- 0-50: R$ 4.040,00 (valor médio) | R$ 120,00 (por módulo)
- 50-100: R$ 3.478,00 (valor médio) | R$ 47,58 (por módulo)
- 100-200: R$ 5.478,00 (valor médio) | R$ 38,71 (por módulo)
- 200-500: R$ 15.701,00 (valor médio) | R$ 45,55 (por módulo)
- 500-1000: R$ 12.326,00 (valor médio) | R$ 16,30 (por módulo)
- 1000+: R$ 52.558,00 (valor médio) | R$ 17,45 (por módulo)

**Por Peso:**
- 0-1000kg: R$ 8.913,00 (valor médio) | R$ 24,43 (por kg)
- 1000-5000kg: R$ 4.248,00 (valor médio) | R$ 1,77 (por kg)
- 5000-10000kg: R$ 9.178,00 (valor médio) | R$ 1,21 (por kg)
- 10000-20000kg: R$ 22.154,00 (valor médio) | R$ 1,49 (por kg)
- 20000-50000kg: R$ 14.726,00 (valor médio) | R$ 0,49 (por kg)
- 50000kg+: R$ 53.572,00 (valor médio) | R$ 0,45 (por kg)

## Detalhes do Cálculo

A versão 5.0 apresenta os detalhes do cálculo de forma clara e consistente:

1. **Valor médio base**: Valor médio dos fretes históricos similares ou valor de referência estatístico
2. **Ajuste por módulos/peso**: Valor adicional baseado na diferença entre a quantidade solicitada e a média histórica
3. **Ajuste de inflação**: Valor adicional para compensar a diferença temporal
4. **Margem aplicada (10%)**: 10% sobre o valor após todos os ajustes

## Requisitos do Sistema

- Python 3.6 ou superior
- Bibliotecas: pandas, geopy, streamlit
- Arquivo Excel com histórico de fretes (opcional - funciona com valores de referência se não disponível)

## Instalação

1. Extraia o arquivo zip em sua máquina local
2. Instale as dependências necessárias:

```bash
pip install pandas geopy streamlit
```

3. Execute a aplicação Streamlit:

```bash
streamlit run app_streamlit_v5.py]
python -m streamlit run app_streamlit.py
```

## Uso da Interface Streamlit

Após iniciar, a interface será aberta automaticamente em seu navegador. Se não abrir, acesse:
```
http://localhost:8501
```

### Campos da Interface

1. **Origem**: Endereço de origem (cidade/estado ou endereço completo com CEP)
2. **Destino**: Endereço de destino (cidade/estado ou endereço completo com CEP)
3. **Modo de Cálculo**: Escolha entre "Por módulos" ou "Por peso (kg)"
4. **Quantidade de Módulos** ou **Peso em kg**: Dependendo do modo selecionado
5. **Data Prevista**: Data prevista para o frete (padrão é a data atual)

## Publicação no Streamlit Cloud

Para publicar a calculadora no Streamlit Cloud:

1. Crie uma conta no [Streamlit Cloud](https://streamlit.io/cloud)
2. Crie um repositório no GitHub com os arquivos da calculadora
3. Conecte o Streamlit Cloud ao seu repositório GitHub
4. Configure o arquivo de dados (Excel) como um recurso estático ou use uma fonte de dados online

### Passos detalhados para publicação:

1. **Prepare seu repositório GitHub**:
   - Crie um novo repositório no GitHub
   - Faça upload dos arquivos: `app_streamlit_v5.py`, `calculadora_frete_v5.py` e o arquivo Excel
   - Adicione um arquivo `requirements.txt` com as dependências:
     ```
     pandas
     geopy
     streamlit
     ```

2. **Configure o Streamlit Cloud**:
   - Acesse [Streamlit Cloud](https://streamlit.io/cloud) e faça login
   - Clique em "New app"
   - Selecione seu repositório GitHub
   - Configure o caminho para o arquivo principal: `app_streamlit_v5.py`
   - Clique em "Deploy"

3. **Compartilhe o link**:
   - Após a implantação, você receberá um link público para sua aplicação
   - Compartilhe este link com qualquer pessoa que precise usar a calculadora

## Personalização

### Ajuste de Valores Base

Se os valores estimados ainda precisarem de ajustes, você pode modificar as constantes no início do arquivo `calculadora_frete_v5.py`:

```python
# Valores de referência para fretes curtos (menos de 10km)
VALOR_MEDIO_FRETE_CURTO = 800  # Valor médio para fretes curtos
VALOR_POR_KM_PADRAO = 100  # Valor por km padrão para fretes curtos

# Valores de referência por faixa de distância
VALORES_REFERENCIA_DISTANCIA = {
    '0-10': {'valor_medio': 800, 'valor_por_km': 100},
    '10-50': {'valor_medio': 980, 'valor_por_km': 26.49},
    # ... outros valores
}
```

### Personalização da Interface

Você pode personalizar a interface Streamlit editando o arquivo `app_streamlit_v5.py`:

- Altere as cores e estilos na seção de CSS no início do arquivo
- Modifique os textos e descrições
- Ajuste o tamanho dos valores exibidos

## Solução de Problemas

### Erro ao calcular distâncias

Se o sistema não conseguir calcular distâncias:

1. Verifique a conexão com a internet
2. Tente usar formatos de endereço mais simples (apenas cidade/estado)
3. Aumente o timeout da API de geolocalização no código fonte

### Arquivo Excel não encontrado

Se o sistema não encontrar o arquivo Excel:

1. Verifique se o caminho do arquivo está correto
2. O sistema continuará funcionando com valores de referência estatísticos

## Próximos Passos e Melhorias Futuras

1. **Integração com Notion**:
   - Implementar conexão direta com a base de dados do Notion
   - Sincronizar dados em tempo real

2. **Funcionalidades Adicionais**:
   - Histórico de cotações salvo em banco de dados
   - Exportação de resultados em PDF ou CSV
   - Gráficos de tendências de preços

3. **Melhorias na Interface**:
   - Mapa interativo para seleção de origem e destino
   - Sugestões automáticas de endereços
   - Tema escuro/claro

## Suporte

Para dúvidas ou suporte, entre em contato com a equipe de desenvolvimento.

---

Desenvolvido com base nos requisitos fornecidos para cálculo de fretes com valores realistas, ajuste de inflação, margem adicional e valor por km.

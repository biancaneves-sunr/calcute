# Documentação da Calculadora de Fretes - Versão 3.0

## Visão Geral

A Calculadora de Fretes 3.0 é um sistema recalibrado que estima o valor de fretes com base em dados históricos, oferecendo duas modalidades de cálculo (por módulos ou por peso) e garantindo valores realistas alinhados com o histórico da empresa.

## Principais Melhorias na Versão 3.0

1. **Valores Realistas**: Algoritmo recalibrado para garantir estimativas alinhadas com o histórico real
2. **Tratamento Especial para Fretes Curtos**: Lógica específica para trajetos menores que 10km
3. **Interface Aprimorada**: Rótulos corretos e valores em tamanho maior para melhor visualização
4. **Remoção de Outliers**: Filtros rigorosos para evitar distorções por valores extremos
5. **Valor por km Ajustado**: Cálculo mais preciso do valor por quilômetro

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

## Exemplos de Valores Reais

| Origem-Destino | Distância | Módulos | Valor Estimado |
|----------------|-----------|---------|----------------|
| Vinhedo-Valinhos | 6,91 km | 50 | R$ 814,00 |
| Vinhedo-Valinhos | 6,91 km | 100 | R$ 836,00 |
| Vinhedo-Valinhos | 6,91 km | 200 | R$ 880,00 |
| Vinhedo-Valinhos | 6,91 km | 500 | R$ 1.012,00 |
| Vinhedo-Valinhos | 6,91 km | 1000 | R$ 1.232,00 |
| Campinas-Valinhos | 9,72 km | 200 | R$ 1.069,20 |
| Jundiaí-Várzea Paulista | 6,27 km | 200 | R$ 880,00 |
| Osasco-São Paulo | 16,29 km | 200 | R$ 2.158,07 |
| São Paulo-Rio de Janeiro | 412 km | 200 | R$ 3.062,12 |

## Requisitos do Sistema

- Python 3.6 ou superior
- Bibliotecas: pandas, geopy, streamlit
- Arquivo Excel com histórico de fretes

## Instalação

1. Extraia o arquivo zip em sua máquina local
2. Instale as dependências necessárias:

```bash
pip install pandas geopy streamlit
```

3. Execute a aplicação Streamlit:

```bash
streamlit run app_streamlit_v3.py
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

## Lógica de Cálculo

### Fretes Curtos (menos de 10km)

Para fretes curtos, o sistema utiliza uma lógica especial:

1. Busca por fretes históricos exatos para o mesmo trajeto
2. Se não encontrar, utiliza um valor base de R$ 800,00 (ajustável conforme necessidade)
3. Aplica ajustes por distância e quantidade de módulos/peso
4. Adiciona margem de 10%

### Fretes Normais

Para fretes de média e longa distância:

1. Busca fretes históricos similares, removendo outliers
2. Calcula média ponderada, dando mais peso aos fretes recentes
3. Ajusta por quantidade (módulos ou peso) e inflação
4. Aplica margem adicional de 10%

## Publicação no Streamlit Cloud

Para publicar a calculadora no Streamlit Cloud:

1. Crie uma conta no [Streamlit Cloud](https://streamlit.io/cloud)
2. Crie um repositório no GitHub com os arquivos da calculadora
3. Conecte o Streamlit Cloud ao seu repositório GitHub
4. Configure o arquivo de dados (Excel) como um recurso estático ou use uma fonte de dados online

### Passos detalhados para publicação:

1. **Prepare seu repositório GitHub**:
   - Crie um novo repositório no GitHub
   - Faça upload dos arquivos: `app_streamlit_v3.py`, `calculadora_frete_v3.py` e o arquivo Excel
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
   - Configure o caminho para o arquivo principal: `app_streamlit_v3.py`
   - Clique em "Deploy"

3. **Compartilhe o link**:
   - Após a implantação, você receberá um link público para sua aplicação
   - Compartilhe este link com qualquer pessoa que precise usar a calculadora

## Personalização

### Ajuste de Valores Base

Se os valores estimados ainda precisarem de ajustes, você pode modificar as constantes no início do arquivo `calculadora_frete_v3.py`:

```python
# Valores de referência para fretes curtos (menos de 10km)
VALOR_MEDIO_FRETE_CURTO = 800  # Valor médio para fretes curtos
VALOR_POR_KM_PADRAO = 100  # Valor por km padrão para fretes curtos
```

### Personalização da Interface

Você pode personalizar a interface Streamlit editando o arquivo `app_streamlit_v3.py`:

- Altere as cores e estilos na seção de CSS no início do arquivo
- Modifique os textos e descrições
- Ajuste o tamanho dos valores exibidos

## Solução de Problemas

### Valores ainda não realistas

Se os valores calculados ainda não parecerem realistas:

1. Verifique os valores base no arquivo `calculadora_frete_v3.py`
2. Ajuste as constantes `VALOR_MEDIO_FRETE_CURTO` e `VALOR_POR_KM_PADRAO`
3. Considere adicionar mais registros históricos para trajetos específicos

### Erro ao calcular distâncias

Se o sistema não conseguir calcular distâncias:

1. Verifique a conexão com a internet
2. Tente usar formatos de endereço mais simples (apenas cidade/estado)
3. O sistema utilizará as distâncias registradas no Excel como fallback

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

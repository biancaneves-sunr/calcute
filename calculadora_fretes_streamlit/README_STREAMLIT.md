# Documentação da Calculadora de Fretes - Versão Streamlit

## Visão Geral

A Calculadora de Fretes é um sistema que permite estimar o valor de fretes com base em dados históricos, ajustando os valores de acordo com a inflação, quantidade de módulos e aplicando uma margem adicional de 10%. Esta versão utiliza o Streamlit para criar uma interface web interativa e fácil de publicar.

## Funcionalidades Principais

1. **Cálculo de Frete Baseado em Histórico**:
   - Busca fretes similares na base de dados
   - Ajusta valores considerando a quantidade de módulos
   - Aplica correção de inflação com base na data
   - Adiciona margem de 10% sobre o valor final

2. **Interface Streamlit**:
   - Interface web moderna e responsiva
   - Fácil de publicar e compartilhar
   - Suporte a múltiplos usuários simultâneos
   - Visualização clara dos resultados

## Requisitos do Sistema

- Python 3.6 ou superior
- Bibliotecas: pandas, geopy, streamlit
- Arquivo Excel com histórico de fretes

## Instalação

1. Clone ou baixe o repositório para sua máquina local
2. Instale as dependências necessárias:

```bash
pip install pandas geopy streamlit
```

3. Configure o caminho para o arquivo Excel na variável `arquivo_excel` no arquivo `app_streamlit.py`

## Uso da Interface Streamlit

Para iniciar a interface Streamlit localmente:

```bash
streamlit run app_streamlit.py
```

Após iniciar, a interface será aberta automaticamente em seu navegador. Se não abrir, acesse:
```
http://localhost:8501
```

## Publicação no Streamlit Cloud

Para publicar a calculadora no Streamlit Cloud e torná-la acessível a qualquer pessoa:

1. Crie uma conta no [Streamlit Cloud](https://streamlit.io/cloud)
2. Crie um repositório no GitHub com os arquivos da calculadora
3. Conecte o Streamlit Cloud ao seu repositório GitHub
4. Configure o arquivo de dados (Excel) como um recurso estático ou use uma fonte de dados online

### Passos detalhados para publicação:

1. **Prepare seu repositório GitHub**:
   - Crie um novo repositório no GitHub
   - Faça upload dos arquivos: `app_streamlit.py`, `calculadora_frete.py` e o arquivo Excel
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
   - Configure o caminho para o arquivo principal: `app_streamlit.py`
   - Clique em "Deploy"

3. **Compartilhe o link**:
   - Após a implantação, você receberá um link público para sua aplicação
   - Compartilhe este link com qualquer pessoa que precise usar a calculadora

## Uso da Interface

A interface Streamlit é intuitiva e contém os seguintes campos:

1. **Origem**: Endereço de origem (cidade/estado ou endereço completo com CEP)
2. **Destino**: Endereço de destino (cidade/estado ou endereço completo com CEP)
3. **Quantidade de Módulos**: Número de módulos a serem transportados
4. **Data Prevista**: Data prevista para o frete (opcional, padrão é a data atual)

Após preencher os campos, clique no botão "Calcular Frete" para obter a estimativa.

## Personalização da Interface

Você pode personalizar a interface Streamlit editando o arquivo `app_streamlit.py`:

- Altere as cores e estilos na seção de CSS no início do arquivo
- Modifique os textos e descrições
- Adicione novos campos ou funcionalidades conforme necessário

## Solução de Problemas

### Erro ao publicar no Streamlit Cloud

Se encontrar problemas ao publicar no Streamlit Cloud:

1. Verifique se todas as dependências estão listadas no arquivo `requirements.txt`
2. Certifique-se de que o caminho para o arquivo Excel está configurado corretamente
3. Considere usar um serviço de armazenamento em nuvem (como Google Drive ou Dropbox) para o arquivo Excel

### Erro ao calcular distâncias

Se o sistema não conseguir calcular distâncias:

1. Verifique a conexão com a internet
2. Tente usar formatos de endereço mais simples (apenas cidade/estado)
3. Considere implementar uma API de geolocalização alternativa

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

Desenvolvido com base nos requisitos fornecidos para cálculo de fretes com base em histórico, ajuste de inflação e margem adicional.

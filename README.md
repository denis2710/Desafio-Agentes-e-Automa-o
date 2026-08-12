# 🏦 ClearBank - ETL de Transações Diárias

Pipeline de dados construído para processar, auditar e sumarizar transações financeiras com foco em resiliência (tolerância a falhas em registros individuais).

## 🚀 Como Executar

**Pré-requisitos:** Python 3.8+ instalado.

1. Insira o arquivo `transacoes.csv` no mesmo diretório dos scripts.
2. **Abordagem Nativa (Sem dependências extras):** 
   Abra o Jupyter Notebook e execute as células sequencialmente. O relatório será exibido na tela e o arquivo `relatorio.json` será gerado.
3. **Abordagem Analítica Opcional (Com Pandas/Matplotlib):**
   ```bash
   pip install pandas matplotlib
   python analise_pandas.py

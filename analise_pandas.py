import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

ARQUIVO = 'transacoes.csv'
LIMITE_SUSPEITO = 10000.00

def executar_pipeline_pandas():
    try:
        # Leitura inicial lendo tudo como string para validação segura
        df = pd.read_csv(ARQUIVO, dtype=str)
    except FileNotFoundError:
        print("Erro: Arquivo CSV não encontrado.")
        return

    total_lidas = len(df)

    # 1. VALIDAÇÃO VETORIZADA
    # Remove nulos e strings vazias em colunas essenciais
    df = df.dropna(subset=['id', 'cliente_id', 'data', 'tipo', 'valor'])
    df = df[df['id'].str.isnumeric()]
    df = df[df['tipo'].isin(['credito', 'debito'])]

    # Conversão de Valor com coerção de erro (transforma erros em NaN, depois descarta)
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    df = df[(df['valor'].notna()) & (df['valor'] > 0)]

    # Conversão de Data
    df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d', errors='coerce')
    df = df[df['data'].notna()]

    linhas_validas = len(df)
    linhas_invalidas = total_lidas - linhas_validas
    
    print(f"Lidas: {total_lidas} | Válidas: {linhas_validas} | Inválidas: {linhas_invalidas}")

    if linhas_validas == 0: return

    # 2. MÉTRICAS E GRUPOS
    df['mes_ano'] = df['data'].dt.to_period('M').astype(str)
    df['valor_saldo'] = df.apply(lambda x: x['valor'] if x['tipo'] == 'credito' else -x['valor'], axis=1)

    # Agrupamento para Gráfico
    saldo_mensal = df.groupby('mes_ano')['valor_saldo'].sum()

    # 3. EXPORTAÇÃO DO GRÁFICO (Matplotlib)
    plt.figure(figsize=(10, 6))
    bars = saldo_mensal.plot(kind='bar', color=['#2ca02c' if v > 0 else '#d62728' for v in saldo_mensal])
    
    plt.title('Saldo Mensal - ClearBank', fontsize=14, fontweight='bold')
    plt.xlabel('Mês/Ano')
    plt.ylabel('Saldo (R$)')
    plt.axhline(0, color='black', linewidth=1)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig('grafico.png')
    print("✅ Gráfico salvo como 'grafico.png'")

if __name__ == "__main__":
    executar_pipeline_pandas()

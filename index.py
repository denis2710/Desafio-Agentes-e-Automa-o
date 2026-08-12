# ==========================================
# CÉLULA 1: Importações e Configurações
# ==========================================
import csv
import json
from datetime import datetime

# Constantes de auditoria
LIMITE_SUSPEITO = 10000.00
ARQUIVO_ENTRADA = 'transacoes.csv'
ARQUIVO_SAIDA = 'relatorio.json'


# ==========================================
# CÉLULA 2: Funções Auxiliares (Formatação)
# ==========================================
def formatar_brl(valor: float) -> str:
    """Formata float para moeda brasileira (R$ X.XXX,XX) usando manipulação de string."""
    # Gera a string com separador de milhar americano e ponto decimal
    valor_str = f"{valor:,.2f}"
    # Substitui a vírgula temporariamente, troca ponto por vírgula, e restaura o separador
    valor_formatado = valor_str.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {valor_formatado}"


# ==========================================
# CÉLULA 3: Validação de Dados
# ==========================================
def validar_transacao(linha: dict) -> dict:
    """Valida cada campo. Descarta silenciosamente retornando None em caso de falha."""
    # Validar ID e Cliente_ID
    if not linha.get('id') or not linha['id'].isdigit(): return None
    if not linha.get('cliente_id') or not linha['cliente_id'].strip(): return None
    
    # Validar Tipo
    if linha.get('tipo') not in ['credito', 'debito']: return None

    # Validar e Converter Valor (Tratamento de Exceção Obrigatório)
    try:
        valor = float(linha['valor'])
        if valor <= 0: return None
        linha['valor'] = valor 
    except (ValueError, TypeError):
        return None

    # Validar e Converter Data (Tratamento de Exceção Obrigatório)
    try:
        data_obj = datetime.strptime(linha['data'], '%Y-%m-%d')
        linha['data_obj'] = data_obj 
    except (ValueError, TypeError):
        return None

    return linha


# ==========================================
# CÉLULA 4: Leitura e ETL
# ==========================================
def ler_transacoes(caminho_arquivo: str):
    """Lê o arquivo CSV, processa as linhas e separa as válidas/suspeitas."""
    transacoes_validas = []
    transacoes_suspeitas = []
    total_lidas = 0
    total_invalidas = 0

    # Abertura de arquivo (Tratamento de Exceção Obrigatório)
    try:
        with open(caminho_arquivo, mode='r', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo)
            for linha in leitor:
                total_lidas += 1
                linha_valida = validar_transacao(linha)
                
                if linha_valida:
                    transacoes_validas.append(linha_valida)
                    if linha_valida['valor'] > LIMITE_SUSPEITO:
                        transacoes_suspeitas.append(linha_valida)
                else:
                    total_invalidas += 1
                    
    except FileNotFoundError:
        print(f"❌ Erro Crítico: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return None, None, 0, 0

    return transacoes_validas, transacoes_suspeitas, total_lidas, total_invalidas


# ==========================================
# CÉLULA 5: Processamento de Métricas
# ==========================================
def gerar_relatorio(transacoes_validas: list) -> tuple:
    """Calcula as métricas financeiras mensais e o delta em dias."""
    resumo_mensal = {}
    
    if not transacoes_validas:
        return resumo_mensal, 0

    # Cálculo do Delta em dias
    datas = [t['data_obj'] for t in transacoes_validas]
    delta_dias = (max(datas) - min(datas)).days

    # Agrupamento e processamento
    for t in transacoes_validas:
        mes_ano = t['data_obj'].strftime('%Y-%m')
        valor = t['valor']
        tipo = t['tipo']

        if mes_ano not in resumo_mensal:
            resumo_mensal[mes_ano] = {
                "quantidade": 0, "total_credito": 0.0, "total_debito": 0.0,
                "saldo": 0.0, "media": 0.0, "maior_valor": valor, "menor_valor": valor,
                "_soma_total": 0.0 # Campo temporário
            }

        rm = resumo_mensal[mes_ano]
        rm['quantidade'] += 1
        rm['_soma_total'] += valor

        if tipo == 'credito':
            rm['total_credito'] += valor
            rm['saldo'] += valor
        else:
            rm['total_debito'] += valor
            rm['saldo'] -= valor

        if valor > rm['maior_valor']: rm['maior_valor'] = valor
        if valor < rm['menor_valor']: rm['menor_valor'] = valor

    # Finalizar cálculos (Média e arredondamentos)
    for rm in resumo_mensal.values():
        rm['media'] = round(rm['_soma_total'] / rm['quantidade'], 2)
        rm['total_credito'] = round(rm['total_credito'], 2)
        rm['total_debito'] = round(rm['total_debito'], 2)
        rm['saldo'] = round(rm['saldo'], 2)
        del rm['_soma_total'] # Limpa campo temporário

    return resumo_mensal, delta_dias


# ==========================================
# CÉLULA 6: Exportação JSON
# ==========================================
def salvar_json(resumo_mensal: dict, lidas: int, invalidas: int, caminho: str):
    """Exporta o resumo final seguindo o esquema esperado."""
    validas = lidas - invalidas
    estrutura = {
        "gerado_em": datetime.now().strftime('%Y-%m-%d'),
        "total_transacoes_validas": validas,
        "total_transacoes_invalidas": invalidas,
        "resumo_mensal": resumo_mensal
    }
    
    with open(caminho, 'w', encoding='utf-8') as arquivo:
        json.dump(estrutura, arquivo, indent=2, ensure_ascii=False)


# ==========================================
# CÉLULA 7: Exibição no Terminal
# ==========================================
def exibir_relatorio(lidas, validas, invalidas, delta, resumo_mensal, suspeitas):
    """Exibe o relatório formatado no terminal com separadores."""
    print("==================================================")
    print("📊 RELATÓRIO DE PROCESSAMENTO CLEARBANK")
    print("==================================================")
    print(f"Total de linhas lidas    : {lidas}")
    print(f"Linhas válidas           : {len(validas)}")
    print(f"Linhas inválidas         : {invalidas}")
    print(f"Intervalo de processamento: {delta} dias")
    print("==================================================")
    
    print("\n💰 RESUMO MENSAL")
    for mes, metricas in resumo_mensal.items():
        print(f"  • Mês: {mes}")
        print(f"    - Saldo: {formatar_brl(metricas['saldo'])}")
        print(f"    - Total Crédito: {formatar_brl(metricas['total_credito'])}")
        print(f"    - Total Débito: {formatar_brl(metricas['total_debito'])}")
    print("==================================================")
    
    print("\n⚠️ AUDITORIA - TRANSAÇÕES SUSPEITAS (Acima de R$ 10k)")
    if not suspeitas:
        print("  ✅ Nenhuma transação suspeita encontrada.")
    else:
        for s in suspeitas:
            print(f"  🚨 ID: {s['id']} | Cliente: {s['cliente_id']} | "
                  f"Data: {s['data']} | Valor: {formatar_brl(s['valor'])}")
    print("==================================================")


# ==========================================
# CÉLULA 8: Execução Principal
# ==========================================
validas, suspeitas, lidas, invalidas = ler_transacoes(ARQUIVO_ENTRADA)

if validas is not None:
    resumo, delta_dias = gerar_relatorio(validas)
    salvar_json(resumo, lidas, invalidas, ARQUIVO_SAIDA)
    exibir_relatorio(lidas, validas, invalidas, delta_dias, resumo, suspeitas)

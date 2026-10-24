import pandas as pd
import os

# Carrega e prepara os dados
def carregar_dados():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "data", "Exercicio-pedidos_2025.csv")

    df = pd.read_csv(csv_path)

    # Conversão da coluna de data
    df["data_pedido"] = pd.to_datetime(df["data_pedido"])

    # Remoção de linhas exatamente duplicadas
    df = df.drop_duplicates()

    return df

# Calcula os indicadores do relatório
def calcular_indicadores(df):
    indicadores = {}

    # Pedidos cancelados e população usada nos gastos
    df_gastos = df[df["status"] != "cancelado"]

    # 1. Contagem total de pedidos
    indicadores["total_pedidos"] = df["id_pedido"].count()

    # 2. Contagem de pedidos cancelados
    indicadores["pedidos_cancelados"] = (df["status"] == "cancelado").sum()

    # 3. Gastos com e sem pedidos cancelados
    indicadores["gastos_com_cancelados"] = df["valor_brl"].sum()
    indicadores["gastos_sem_cancelados"] = df_gastos["valor_brl"].sum()

    # 4. Percentual dos gastos com Manutenção
    gasto_por_categoria = df_gastos.groupby("categoria")["valor_brl"].sum()
    porcentagem_por_categoria = (gasto_por_categoria / df_gastos["valor_brl"].sum()) * 100

    indicadores["percentual_manutencao"] = porcentagem_por_categoria["Manutenção"]

    # 5. Percentual dos gastos dos três maiores fornecedores
    gasto_por_fornecedor = df_gastos.groupby("fornecedor")["valor_brl"].sum()
    porcentagem_por_fornecedor = (gasto_por_fornecedor / df_gastos["valor_brl"].sum()) * 100

    indicadores["percentual_top3_fornecedores"] = (porcentagem_por_fornecedor.sort_values(ascending=False).head(3).sum())

    # 6. Mediana e média do valor por pedido
    valor_por_pedido = df_gastos.groupby("id_pedido")["valor_brl"].sum()

    indicadores["ticket_mediano"] = valor_por_pedido.median()
    indicadores["ticket_medio"] = valor_por_pedido.mean()

    # 7. Gastos por trimestre
    for i in range(1, 5):
        gasto = df_gastos[df_gastos["data_pedido"].dt.quarter == i]
        indicadores[f"gastos_trimestre_{i}"] = gasto["valor_brl"].sum()

    # 8. Prazo médio de entrega
    indicadores["prazo_medio_entrega"] = df_gastos["prazo_entrega_dias"].mean()

    # 9. Percentual de pedidos em aberto
    porcentagem_em_aberto = ((df["status"] == "em aberto").sum() / df["id_pedido"].count()) * 100

    indicadores["percentual_em_aberto"] = porcentagem_em_aberto

    # 10. Gastos com TI e maior valor individual na categoria
    df_ti = df_gastos[df_gastos["categoria"] == "TI"]

    indicadores["gastos_ti"] = df_ti["valor_brl"].sum()
    indicadores["maior_valor_ti"] = df_ti["valor_brl"].max()

    return indicadores

# Carrega os dados do relatório
def carregar_relatorio():
    # Deve ser adaptado de acordo com uma saída padrão do relatório do agente de IA
    relatorio = {
        "total_pedidos": 243,
        "pedidos_cancelados": 16,
        "gastos_sem_cancelados": 8380000.00,
        "percentual_manutencao": 37.00,
        "percentual_top3_fornecedores": 56.00,
        "ticket_mediano": 34800.00,
        "gastos_trimestre_3": 4150000.00,
        "prazo_medio_entrega": 19.00,
        "percentual_em_aberto": 12.00,
        "gastos_ti": 2320000.00,
        "maior_valor_ti": 612000.00,
    }

    return relatorio

# Compara os indicadores calculados com os valores do relatório
def validar_relatorio(calculados, relatorio, tolerancias):
    resultados = {}

    for indicador, valor_relatorio in relatorio.items():

        if indicador not in calculados:
            resultados[indicador] = {
                "status": "ERRO",
                "calculado": None,
                "relatorio": valor_relatorio,
                "mensagem": "Indicador não encontrado nos cálculos."
            }
            continue

        valor_calculado = calculados[indicador]
        tolerancia = tolerancias.get(indicador, 0)

        diferenca = abs(valor_calculado - valor_relatorio)

        if diferenca <= tolerancia:
            status = "CORRETO"
            mensagem = "Valor compatível com o arredondamento."
        else:
            status = "INCORRETO"
            mensagem = "Valor diferente do cálculo."

        resultados[indicador] = {
            "status": status,
            "calculado": valor_calculado,
            "relatorio": valor_relatorio,
            "mensagem": mensagem
        }

    return resultados

# Executa o programa
def main():
    df = carregar_dados()

    indicadores = calcular_indicadores(df)
    relatorio = carregar_relatorio()
    tolerancias = {
        "gastos_ti": 50000,
        "gastos_sem_cancelados": 50000,
        "maior_valor_ti": 500,
        "percentual_manutencao": 0.5,
        "percentual_top3_fornecedores": 0.5,
        "percentual_em_aberto": 0.5,
        "prazo_medio_entrega": 0.1
    }
    
    resultados = validar_relatorio(indicadores, relatorio, tolerancias)

    for nome, resultado in resultados.items():
        print(f"\nIndicador: {nome}")
        print(f"Status: {resultado['status']}")
        print(f"Valor calculado: {resultado['calculado']}")
        print(f"Valor do relatório: {resultado['relatorio']}")
        print(f"Motivo: {resultado['mensagem']}")

if __name__ == "__main__":
    main()

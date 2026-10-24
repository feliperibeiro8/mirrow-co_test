import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "data", "Exercicio-pedidos_2025.csv")

df = pd.read_csv(csv_path)
print(df.info())

# Conversão da coluna de data
df["data_pedido"] = pd.to_datetime(df["data_pedido"])
df = df.drop_duplicates() 
print(df.info())
print()

# 1. Contagem total de pedidos
print("Número de pedidos:", df['id_pedido'].count())
print()

# 2. Contagem de pedidos cancelados
print("Cancelados:", (df["status"] == 'cancelado').sum())
print()

# Remoção dos pedidos cancelados
df_gastos = df[df["status"] != 'cancelado']

# 3. Comparação dos gastos com e sem pedidos cancelados
print(f"Com cancelados: R$ {df['valor_brl'].sum():.2f}")
print(f"Sem cancelados: R$ {df_gastos['valor_brl'].sum():.2f}")
print()

# 4. Cálculo do percentual de gastos com Manutenção
gasto_por_categoria = df_gastos.groupby('categoria')['valor_brl'].sum()
porcentagem_por_categoria = (gasto_por_categoria / df_gastos['valor_brl'].sum()) * 100
print(f"Gasto Manutenção: {porcentagem_por_categoria['Manutenção']:.2f}%")
print()

# 5. Cálculo do percentual de gastos dos três maiores fornecedores
gasto_por_fornecedor = df_gastos.groupby('fornecedor')['valor_brl'].sum()
porcentagem_por_forncedor = (gasto_por_fornecedor / df_gastos['valor_brl'].sum()) * 100
print(f"Gasto 3 maiores fornecedores: {porcentagem_por_forncedor.sort_values(ascending=False).head(3).sum():.2f}%")
print()

# 6. Mediana do valor por pedido
ticket_mediano = df_gastos.groupby("id_pedido")["valor_brl"].sum().median()
ticket_medio = df_gastos.groupby("id_pedido")["valor_brl"].sum().mean()
print(f'Ticket mediano: R$ {ticket_mediano:.2f}')
print(f'Ticket médio: R$ {ticket_medio:.2f}')

print()

# 7. Gastos nos trimestres

for i in range(1,5):
    gasto = df_gastos[df_gastos["data_pedido"].dt.quarter == i]
    print(f'Gasto no {i}º trimestre: R$ {gasto["valor_brl"].sum():.2f}')

print()

# 8. Prazo médio de entrega
print(f'Prazo médio de entrega: {int(df_gastos["prazo_entrega_dias"].mean())}')
print()

# 9. Percentual de pedidos em aberto sobre o total
porcentagem_em_aberto = df['status'].value_counts(normalize=True)['em aberto'] * 100
print(f'Pedidos em aberto: {porcentagem_em_aberto:.2f}%')
print()

# 10. Análise TI (Gastos e maior pedido)
df_ti = df_gastos[df_gastos['categoria'] == 'TI']
gasto_TI = df_ti['valor_brl'].sum()
print(f'Gastos TI: R$ {gasto_TI:.2f}')

maior_pedido_ti = df_ti['valor_brl'].max()
print(f'Maior pedido de TI: R$ {maior_pedido_ti:.2f}')

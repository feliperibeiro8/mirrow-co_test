import pandas as pd
import pytest, os, sys

# Obtém o diretório raiz do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Adiciona a raiz ao caminho de busca do Python
sys.path.insert(0, BASE_DIR)

# Testes da função validar_relatorio()
from src.verificador import calcular_indicadores, validar_relatorio

def test_valor_exatamente_igual():
    calculados = {"gastos_ti": 300_000}
    relatorio = {"gastos_ti": 300_000}
    tolerancias = {"gastos_ti": 0}

    resultados = validar_relatorio(
        calculados, relatorio, tolerancias
    )

    assert resultados["gastos_ti"]["status"] == "CORRETO"


def test_valor_dentro_da_tolerancia():
    calculados = {"gastos_ti": 2_190_000}
    relatorio = {"gastos_ti": 2_200_000}
    tolerancias = {"gastos_ti": 10_000}

    resultados = validar_relatorio(
        calculados, relatorio, tolerancias
    )

    assert resultados["gastos_ti"]["status"] == "CORRETO"


def test_valor_fora_da_tolerancia():
    calculados = {"gastos_ti": 2_190_000}
    relatorio = {"gastos_ti": 2_300_000}
    tolerancias = {"gastos_ti": 10_000}

    resultados = validar_relatorio(
        calculados, relatorio, tolerancias
    )

    assert resultados["gastos_ti"]["status"] == "INCORRETO"


def test_indicador_ausente_nos_calculos():
    calculados = {"gastos_ti": 300_000}
    relatorio = {"ticket_mediano": 100_000}
    tolerancias = {}

    resultados = validar_relatorio(
        calculados, relatorio, tolerancias
    )

    assert resultados["ticket_mediano"]["status"] == "ERRO"
    assert resultados["ticket_mediano"]["calculado"] is None


def test_valor_incorreto_retorna_os_dois_valores():
    calculados = {"total_pedidos": 240}
    relatorio = {"total_pedidos": 243}
    tolerancias = {"total_pedidos": 0}

    resultados = validar_relatorio(
        calculados, relatorio, tolerancias
    )

    assert resultados["total_pedidos"]["calculado"] == 240
    assert resultados["total_pedidos"]["relatorio"] == 243


# Testes da função calcular_indicadores()

@pytest.fixture
def dados_teste():
    return pd.DataFrame({
        "id_pedido": [1, 2, 3, 4],
        "data_pedido": pd.to_datetime([
            "2025-01-10",
            "2025-07-15",
            "2025-07-20",
            "2025-10-05",
        ]),
        "fornecedor": ["A", "B", "A", "C"],
        "categoria": [
            "Manutenção", "TI", "TI", "Manutenção"
        ],
        "valor_brl": [100, 300, 200, 100],
        "prazo_entrega_dias": [10, 20, 30, 30],
        "status": [
            "entregue", "em aberto", "cancelado", "entregue"
        ],
    })


def test_contagem_de_pedidos(dados_teste):
    indicadores = calcular_indicadores(dados_teste)

    assert indicadores["total_pedidos"] == 4
    assert indicadores["pedidos_cancelados"] == 1


def test_gastos_excluem_pedidos_cancelados(dados_teste):
    indicadores = calcular_indicadores(dados_teste)

    assert indicadores["gastos_com_cancelados"] == 700
    assert indicadores["gastos_sem_cancelados"] == 500


def test_percentual_de_manutencao(dados_teste):
    indicadores = calcular_indicadores(dados_teste)

    assert indicadores["percentual_manutencao"] == pytest.approx(40.0)


def test_ticket_mediano(dados_teste):
    indicadores = calcular_indicadores(dados_teste)

    assert indicadores["ticket_mediano"] == pytest.approx(100.0)


def test_gastos_por_trimestre(dados_teste):
    indicadores = calcular_indicadores(dados_teste)

    assert indicadores["gastos_trimestre_1"] == 100
    assert indicadores["gastos_trimestre_2"] == 0
    assert indicadores["gastos_trimestre_3"] == 300
    assert indicadores["gastos_trimestre_4"] == 100


def test_percentual_de_pedidos_em_aberto(dados_teste):
    indicadores = calcular_indicadores(dados_teste)

    assert indicadores["percentual_em_aberto"] == pytest.approx(25.0)


def test_gastos_e_maior_pedido_de_ti(dados_teste):
    indicadores = calcular_indicadores(dados_teste)

    assert indicadores["gastos_ti"] == 300
    assert indicadores["maior_valor_ti"] == 300
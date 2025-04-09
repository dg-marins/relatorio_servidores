import json
from typing import Dict, Any
import matplotlib.pyplot as plt
from pathlib import Path

def read_json_file(config_file) -> Dict[str, Any]:
    """Lê os dados do arquivo de configuração JSON.

    Returns:
        Dict[str, Any]: Dados da configuração.
    """
    with config_file.open('r') as json_file:
        data = json.load(json_file)
        return data

def create_graph(host_name, data_frame):
    # Criando gráficos
    plt.figure(figsize=(12, 8), constrained_layout=True)
    for column in data_frame.columns[1:]:  # pula a coluna "Data"
        plt.plot(data_frame["Data"], data_frame[column], label=column)

    plt.xlabel("Data")
    plt.ylabel("Valor")
    plt.title(f"Histórico dos Itens - {host_name}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Caminho para salvar o gráfico
    graphs_dir = Path() / "relatorios"
    graphs_dir.mkdir(parents=True, exist_ok=True)
    graph_path = graphs_dir / f"grafico_{host_name}.png"

    plt.savefig(graph_path)
    plt.close()
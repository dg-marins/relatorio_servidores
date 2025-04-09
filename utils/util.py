import json
from typing import Dict, Any
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from fpdf import FPDF
import pandas as pd
import itertools

CATEGORIAS_METRICAS = {
    "cpu": ["cpu", "system.cpu", "processor"],
    "memoria": ["memory", "vm.memory", "mem"],
    "load": ["load", "system.load"],
    "disco": ["vfs.fs", "disk", "space"],
    "rede": ["net", "interface", "network", "if"],
    "sistema": ["uptime", "os", "hostname", "system.localtime"]
}


def classificar_item(item_name_or_key: str) -> str:
    for categoria, termos in CATEGORIAS_METRICAS.items():
        for termo in termos:
            if termo.lower() in item_name_or_key.lower():
                return categoria
    return "outros"

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

def gerar_graficos_por_categoria(hostname: str, dados_categorizados: dict):
    base_path = Path("relatorios")
    base_path.mkdir(parents=True, exist_ok=True)

    for categoria, itens in dados_categorizados.items():
        if not itens:
            continue

        df = pd.DataFrame()
        for nome_item, info in itens.items():
            temp_df = pd.DataFrame({"Data": info["timestamps"], nome_item: info["values"]})
            df = temp_df if df.empty else df.merge(temp_df, on="Data", how="outer")

        df.sort_values("Data", inplace=True)
        df.ffill(inplace=True)

        fig, ax = plt.subplots(figsize=(12, 6))
        for col in df.columns[1:]:
            ax.plot(df["Data"], df[col], label=col)

        ax.set_title(f"{categoria.upper()} - {hostname}")
        ax.set_xlabel("Data")
        ax.set_ylabel("Valor")
        ax.grid(True)
        ax.legend()
        fig.tight_layout()

        path = base_path / f"{hostname}_{categoria}.png"
        fig.savefig(path)
        plt.close(fig)

def create_pdf_summary(host_name: str, graph_path: Path):
    """Gera um relatório PDF com o gráfico e título."""

    output_pdf = Path("relatorios") / f"{host_name}_relatorio.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Relatório do Host: {host_name}", ln=True)

    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True)

    # Adiciona gráfico
    if graph_path.exists():
        pdf.image(str(graph_path), x=10, y=40, w=180)

    pdf.output(str(output_pdf))

def save_excel_report(df: pd.DataFrame, host_name: str) -> Path:
    output_file = Path("relatorios") / f"{host_name}_relatorio.xlsx"
    df.to_excel(output_file, index=False)
    return output_file
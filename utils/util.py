import json
from typing import Dict, Any
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from fpdf import FPDF
import pandas as pd

def classificar_item(item_name_or_key: str) -> str:
    """Classefica um item de métrica de acordo com a categoria."""

    CATEGORIAS_METRICAS = {
    "cpu": ["cpu", "system.cpu", "processor"],
    "memoria": ["memory", "vm.memory", "mem"],
    "load": ["load", "system.load"],
    "disco": ["vfs.fs", "disk", "space"],
    "rede": ["net", "interface", "network", "if"],
    "sistema": ["uptime", "os", "hostname", "system.localtime"]
    }
    
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

def create_graph(hostname, data_frame):
    
    # Criando gráficos
    plt.figure(figsize=(12, 8), constrained_layout=True)
    for column in data_frame.columns[1:]:  # pula a coluna "Data"
        plt.plot(data_frame["Data"], data_frame[column], label=column)

    plt.xlabel("Data")
    plt.ylabel("Valor")
    plt.title(f"Histórico dos Itens - {hostname}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Caminho para salvar o gráfico
    graphs_dir = Path() / "relatorios" / hostname / datetime.now().strftime('%Y-%m-%d')
    graphs_dir.mkdir(parents=True, exist_ok=True)
    graph_path = graphs_dir / f"grafico_{hostname}.png"

    plt.savefig(graph_path)
    plt.close()

def gerar_graficos_por_categoria(hostname: str, dados_categorizados: dict):
    base_path = Path("relatorios") / hostname / datetime.now().strftime('%Y-%m-%d')
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

def create_pdf_summary(hostname: str, dados_categorizados: Dict):
    """Gera um relatório PDF com os gráficos e título."""

    output_pdf = Path("relatorios") / hostname / datetime.now().strftime('%Y-%m-%d') / f"{hostname}_relatorio.pdf"

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Relatório do Host: {hostname}", ln=True)

    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True)

    current_y = pdf.get_y() + 10  # Começa um pouco abaixo do título

    for categoria, itens in dados_categorizados.items():
        if not itens:
            continue

        graph_path = Path("relatorios") / hostname / datetime.now().strftime('%Y-%m-%d') / f"{hostname}_{categoria}.png"

        if graph_path.exists():
            # Verifica se há espaço suficiente na página, senão adiciona nova
            if current_y + 100 > pdf.h - 15:  # considerando altura da imagem 100
                pdf.add_page()
                current_y = 10  # reinicia no topo da nova página

            # Adiciona título da categoria
            pdf.set_y(current_y)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, f"Categoria: {categoria}", ln=True)
            current_y = pdf.get_y()

            # Adiciona a imagem
            pdf.image(str(graph_path), x=10, y=current_y, w=180)
            current_y += 100  # Atualiza posição Y para a próxima imagem

    pdf.output(str(output_pdf))


def save_excel_report(df: pd.DataFrame, hostname: str) -> Path:
    output_file = Path("relatorios") / hostname / datetime.now().strftime('%Y-%m-%d') / f"{hostname}_relatorio.xlsx"
    df.to_excel(output_file, index=False)
    return output_file
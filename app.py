from utils import util
from consumers import zabbix
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging

# Configuração
config_path = Path() / 'config' / 'config.json'
configFile = util.read_json_file(config_path)
zbx = zabbix.Zabbix(configFile.get("zabbix_url"), configFile.get("username"), configFile.get("password"))
auth_token = zbx.login()

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

for hostname in configFile.get("hostnames"):
    try:
        items = zbx.get_items(auth_token, hostname)
    except Exception as e:
        logging.error(f'Erro ao obter itens para {hostname}: {e}')
        continue

    data = {}
    for item in items:
        try:
            history = zbx.get_history(auth_token, item["itemid"], configFile.get("last_days"))
        except Exception as e:
            logging.warning(f'Erro ao obter histórico de {item["name"]}: {e}')
            continue

        timestamps = [datetime.fromtimestamp(int(h["clock"])) for h in history]
        values = [float(h["value"]) for h in history]

        data[item["name"]] = {"timestamps": timestamps, "values": values}

    # DataFrame
    df = pd.DataFrame()
    for name, info in data.items():
        temp_df = pd.DataFrame({"Data": info["timestamps"], name: info["values"]})
        df = temp_df if df.empty else df.merge(temp_df, on="Data", how="outer")

    df.sort_values("Data", inplace=True)
    df.ffill(inplace=True)

    # Criar gráfico
    try:
        util.create_graph(hostname, df)
        logging.info(f"Gráfico criado para {hostname}")
    except Exception as e:
        logging.error(f"Erro ao criar gráfico para {hostname}: {e}")

    # # Salvar Excel
    # try:
    #     path_excel = util.save_excel_report(df, hostname)
    #     logging.info(f"Excel salvo em {path_excel}")
    # except Exception as e:
    #     logging.error(f"Erro ao salvar Excel: {e}")

    # Salvar PDF com gráfico
    try:
        graph_path = Path("relatorios") / f"grafico_{hostname}.png"
        util.create_pdf_summary(hostname, graph_path)
        logging.info(f"PDF gerado para {hostname}")
    except Exception as e:
        logging.error(f"Erro ao gerar PDF: {e}")

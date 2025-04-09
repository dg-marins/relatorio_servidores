import pandas as pd
from datetime import datetime
from consumers import zabbix, unifi
from pathlib import Path
from utils import util
import openpyxl
import logging

## Caminho do arquivo de configuração
config_path = Path() / 'config' / 'config.json'

## Lendo parâmetros de configuração.
configFile = util.read_json_file(config_path)

## Instância e login do módulo zabbix
zabbix = zabbix.Zabbix(configFile.get("zabbix_url"), configFile.get("username"),
                        configFile.get("password"))
auth_token = zabbix.login()

# Configuração de logs
logging.basicConfig(filename='logs/app.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

for hostname in configFile.get("hostnames"):
    try:
        items = zabbix.get_items(auth_token, hostname)
        logging.info(f'Obtendo itens para o hostname {hostname}')
    except Exception as e:
        logging.error(f'Erro ao obter itens para o hostname {hostname}: {str(e)}')
        continue

    # Criando um dicionário para armazenar os dados
    data = {}

    for item in items:
        try:
            history = zabbix.get_history(auth_token, item["itemid"], configFile.get("last_days"))
            logging.info(f'Obtendo historico para o item {item["name"]}')
        except Exception as e:
            logging.error(f'Erro ao obter historico para o item {item["name"]}: {str(e)}')
            continue

        timestamps = [datetime.fromtimestamp(int(h["clock"])) for h in history]
        values = [float(h["value"]) for h in history]

        data[item["name"]] = {"timestamps": timestamps, "values": values}

    # Criando um DataFrame do Pandas
    df = pd.DataFrame()
    for name, info in data.items():
        temp_df = pd.DataFrame({"Data": info["timestamps"], name: info["values"]})
        df = temp_df if df.empty else df.merge(temp_df, on="Data", how="outer")

    df.sort_values("Data", inplace=True)
    df.ffill(inplace=True)

    # Criando gráficos
    try:
        util.create_graph(hostname, df)
        logging.info(f'Gráfico criado para o hostname {hostname}')
    except Exception as e:
        logging.error(f'Erro ao criar gráfico para o hostname {hostname}: {str(e)}')

    #Criando Planiclha Excel
    
    # Caminho para salvar a planilha
    output_dir = Path() / "relatorios"
    output_dir.mkdir(parents=True, exist_ok=True)  # Garante que o diretório exista
    output_file = output_dir / f"{hostname}_relatorio.xlsx"

    # Salvando o DataFrame em uma planilha Excel
    try:
        df.to_excel(output_file, index=False)
        logging.info(f'Planilha salva em: {output_file}')
        print(f"✅ Planilha salva em: {output_file}")
    except Exception as e:
        logging.error(f'Erro ao salvar planilha em: {output_file}: {str(e)}')

    

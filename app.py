import pandas as pd
from datetime import datetime
from consumers import zabbix, unifi
from pathlib import Path
from utils import util
import openpyxl

## Caminho do arquivo de configuração
config_path = Path() / 'config' / 'config.json'

## Lendo parâmetros de configuração.
configFile = util.read_json_file(config_path)

## Instância e login do módulo zabbix
zabbix = zabbix.Zabbix(configFile.get("zabbix_url"), configFile.get("username"),
                        configFile.get("password"))
auth_token = zabbix.login()

# Executando as funções para obter os dados
for hostname in configFile.get("hostnames"):
    items = zabbix.get_items(auth_token, hostname)

    # Criando um dicionário para armazenar os dados
    data = {}

    for item in items:
        history = zabbix.get_history(auth_token, item["itemid"], configFile.get("last_days"))
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
    util.create_graph(hostname, df)

    #Criando Planiclha Excel
    
    # Caminho para salvar a planilha
    output_dir = Path() / "relatorios"
    output_dir.mkdir(parents=True, exist_ok=True)  # Garante que o diretório exista
    output_file = output_dir / f"{hostname}_relatorio.xlsx"

    # Salvando o DataFrame em uma planilha Excel
    df.to_excel(output_file, index=False)

    print(f"✅ Planilha salva em: {output_file}")
    

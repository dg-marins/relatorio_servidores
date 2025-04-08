import pandas as pd
from datetime import datetime
from consumers import zabbix, unifi
from pathlib import Path
import os
from utils import util
import matplotlib.pyplot as plt

## Diretorio source da aplicação
app_directory = os.path.dirname(os.path.realpath(__file__))

## Caminho do arquivo de configuração
config_path = Path(app_directory) / 'config' / 'config.json'

## Lendo parâmetros de configuração.
configFile = util.readJsonFile(config_path)

## Instância do módulo zabbix
zabbix = zabbix.Zabbix(configFile.get("zabbix_url"), configFile.get("username"),
                        configFile.get("password"))

# Executando as funções para obter os dados
auth_token = zabbix.login()

for hostname in configFile.get("hostnames"):
    items = zabbix.get_items(auth_token, hostname)

    # Criando um dicionário para armazenar os dados
    data = {}
    

    for item in items:
        history = zabbix.get_history(auth_token, item["itemid"])
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

    print(df)
    

import json
from typing import Dict, Any

def readJsonFile(config_file) -> Dict[str, Any]:
    """Lê os dados do arquivo de configuração JSON.

    Returns:
        Dict[str, Any]: Dados da configuração.
    """
    with config_file.open('r') as json_file:
        data = json.load(json_file)
        return data
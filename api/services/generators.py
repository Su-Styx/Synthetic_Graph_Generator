# Model generation calls live here 
from modules.BA_model.BA_endpoint import generate 
from modules.ER_model.ER_endpoint import generate_er_graph


def generate_er(params: dict) -> dict:
    return generate_er_graph(
        n=params["n"],
        p=params["p"],
        directed=params.get("directed", False),
        seed=params.get("seed"),
    )
# generate(n: int, p: float, directed: bool = False, seed: Optional[int] = None) -> dict:
#     G = nx.erdos_renyi_graph(n=n, p=p, directed=directed, seed=seed)


def generate_ba (params: dict) -> dict:
    return generate(
        n=params["n"],
        m=params["m"],
        seed=params.get("seed")
    )




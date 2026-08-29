from pathlib import Path
import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
KPI_CONTRACT_PATH = PROJECT_ROOT / "config" / "kpi_contracts.yaml"


def load_kpi_contract():
    """
    Load the governed KPI semantic contract.
    """

    if not KPI_CONTRACT_PATH.exists():
        raise FileNotFoundError(
            f"KPI contract not found: {KPI_CONTRACT_PATH}"
        )

    with open(
        KPI_CONTRACT_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        contract = yaml.safe_load(file)

    if not contract or "kpis" not in contract:
        raise ValueError(
            "Invalid KPI contract: 'kpis' section is missing."
        )

    return contract


def get_kpi_definition(kpi_name: str):
    """
    Return the semantic definition for a KPI.
    """

    contract = load_kpi_contract()

    kpis = contract["kpis"]

    if kpi_name not in kpis:
        raise KeyError(
            f"KPI '{kpi_name}' is not defined "
            "in the KPI contract."
        )

    return kpis[kpi_name]
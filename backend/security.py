from pathlib import Path

from backend.config_loader import get_kpi_definition


ROLE_MAP = {
    "Executive": "executive",
    "Analyst": "analyst",
    "Manager": "manager"
}


# ============================================================
# PROJECT / DATA SECURITY
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = (PROJECT_ROOT / "data").resolve()


def validate_data_file(file_path: str) -> str:
    """
    Validate that a requested data file exists inside
    the project's controlled data directory.

    Prevents path traversal such as:
        ../../secret.txt
        C:\\Windows\\...
    """

    if not isinstance(file_path, str):
        raise ValueError("File path must be a string.")

    if not file_path.strip():
        raise ValueError("File path cannot be empty.")

    try:
        candidate = Path(file_path).resolve()
    except Exception:
        raise ValueError("Invalid file path.")

    try:
        candidate.relative_to(DATA_DIR)
    except ValueError:
        raise PermissionError(
            "Access denied: file must be inside the project data directory."
        )

    if not candidate.exists():
        raise FileNotFoundError(
            f"Data file not found: {file_path}"
        )

    if not candidate.is_file():
        raise ValueError(
            "Requested path is not a file."
        )

    if candidate.suffix.lower() != ".csv":
        raise ValueError(
            "Only CSV data files are allowed."
        )

    return str(candidate)


# ============================================================
# KPI ACCESS CONTROL
# ============================================================

def check_kpi_access(kpi: str, persona: str) -> bool:
    """
    Check whether the requested persona is authorized
    to access the KPI according to the governed KPI contract.
    """

    role = ROLE_MAP.get(persona)

    if role is None:
        return False

    try:
        kpi_definition = get_kpi_definition(kpi.lower())
    except Exception:
        return False

    allowed_roles = kpi_definition.get(
        "access",
        {}
    ).get(
        "roles",
        []
    )

    return role in allowed_roles


def enforce_kpi_access(kpi: str, persona: str):
    """
    Raise an authorization error when a persona does not
    have access to the requested KPI.
    """

    if not check_kpi_access(kpi, persona):
        raise PermissionError(
            f"Access denied: persona '{persona}' is not authorized "
            f"to access KPI '{kpi}'."
        )
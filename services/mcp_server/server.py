from shared.expenses_client import create_expense
from shared.merkadapp_client import get_bill
from mcp.server.fastmcp import FastMCP
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


mcp = FastMCP("merkadapp")


@mcp.tool()
def create_expense_tool(
    description: str,
    amount: float,
    currency: str,
    date: str,
    paid_by: str,
    merchant: str | None = None,
    group_id: str | None = None,
) -> dict:
    """Registra un nuevo gasto en Merkadapp, opcionalmente dentro de un grupo."""
    return create_expense(description, amount, currency, date, paid_by, merchant, group_id)


@mcp.tool()
def get_bill_tool(bill_id: str) -> dict:
    """Obtiene el detalle de una factura (bill) de Merkadapp por su id."""
    return get_bill(bill_id)


if __name__ == "__main__":
    mcp.run(transport="stdio")

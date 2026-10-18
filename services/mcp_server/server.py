import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mcp.server.fastmcp import FastMCP

from shared.merkadapp_client import get_bill

mcp = FastMCP("merkadapp")


@mcp.tool()
def get_bill_tool(bill_id: str) -> dict:
    """Obtiene el detalle de una factura (bill) de Merkadapp por su id."""
    return get_bill(bill_id)


if __name__ == "__main__":
    mcp.run(transport="stdio")

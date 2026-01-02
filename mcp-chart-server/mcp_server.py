from fastmcp.server.server import FastMCP
import httpx, asyncio
from typing import Any, List, Dict
from datetime import date, timedelta
import os,json
from dotenv import load_dotenv
import base64
from pathlib import Path
from fastmcp.utilities.types import Image
# from starlette.responses import JSONResponse
load_dotenv('.env')

node_server_endpoint=os.getenv('node_server_endpoint')

# Create MCP server (HTTP streamable)
mcp = FastMCP(name="Metric MCP Server", json_response=True, stateless_http=True)

# -----------------------------
# Tool 1: Return time-series
# -----------------------------
@mcp.tool()
def get_metric_timeseries(
    metric_name: str = "cpu_usage"
) -> Dict:
    """
    Returns mock time-series data for a metric
    """

    series = [
        {"date": "2025-01-01","value": 60},{"date": "2025-01-02","value": 35},{"date": "2025-01-03","value": 56}
        ,{"date": "2025-01-04","value": 45},{"date": "2025-01-05","value": 50},{"date": "2025-01-06","value": 20}
        ,{"date": "2025-01-07","value": 60},{"date": "2025-01-08","value": 65},{"date": "2025-01-09","value": 70}
        ,{"date": "2025-01-10","value": 30},{"date": "2025-01-11","value": 80},{"date": "2025-01-12","value": 100}
    ]

     
    return {
        "metric_name": metric_name,
        "unit": "%",
        "series": series
    }
 
        
@mcp.tool()
async def render_metric_chart(
    metric_name: str,
    unit: str,
    series: Any  # Change type hint to Any to accept lists or strings
) -> Image:
    """
    Sends time-series to Node.js and returns chart image as base64
    """
    try:
        # 1. Handle case where 'series' is already a list/dict (passed by agent)
        # or a string (passed by raw JSON input)
        if isinstance(series, str):
            try:
                series_data = json.loads(series)
                # Handle potential double-encoding if necessary
                if isinstance(series_data, str):
                    series_data = json.loads(series_data)
            except json.JSONDecodeError:
                raise ValueError("series must be a valid JSON string or object")
        else:
            series_data = series

        # 2. Extract the series array (handle cases where 'series' is the full dict)
        if isinstance(series_data, dict) and "series" in series_data:
            series_array = series_data["series"]
        else:
            series_array = series_data

        # 3. Payload for your Node.js server
        payload = {
            "metric_name": metric_name,
            "unit": unit,
            "series": series_array
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                node_server_endpoint,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            # base64_str=base64.b64encode(response.content).decode("utf-8")
            image_data=response.content
            return Image(data=image_data, format="png")
    except Exception as e:
        print(f'Exception from mcp_chart_server::::{e}')
        print(f'node server url::::: {node_server_endpoint}')

# ------------------------------------
# Run HTTP Streamable MCP server
# ------------------------------------

async def main():
    await mcp.run_async(transport="streamable-http",host="0.0.0.0",port=9000,path="/mcp")

if __name__ == "__main__":
    asyncio.run(main())  # Run the async main function

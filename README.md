# AGENT-MCP-NODE (Chart Rendering Project)

## Overview

This project demonstrates how to build a **Model Context Protocol (MCP) server** that exposes tools to an AI agent for **rich chart rendering**, using a **Node.js chart server** as a downstream rendering engine.

Instead of generating charts directly in Python (which can be limited in richness and flexibility), this architecture delegates chart rendering to a **Node.js server** (using Chart.js), while keeping orchestration and AI interaction in Python.

At a high level, the flow looks like this:

```
Agent (Chainlit / Copilot)
        ↓
     MCP Server (Python)
        ↓
   Node Chart Server (Chart.js)
        ↓
     MCP Server
        ↓
Agent (Chart displayed as image)
```

---

## Use Case

A user asks a question such as:

> “How is the CPU utilization metric performing over the last 6 months?”

Flow:
1. The **agent** interprets the request.
2. The **MCP server**:
   - Fetches or constructs the metric time-series data.
   - Calls a tool that sends this data to the Node.js chart server.
3. The **Node.js server**:
   - Accepts time-series input.
   - Renders a high-quality chart using Chart.js.
   - Returns the chart as an image (PNG).
4. The **MCP server** returns the image to the agent.
5. The **agent displays the chart inline** in the chat UI.

---

## Repository Structure

```
.
├── frontend-chart-server/
│   ├── app.py
│   ├── chainlit.md
│   ├── .env
│   ├── pyproject.toml
│   └── uv.lock
│
├── mcp-chart-server/
│   ├── mcp_server.py
│   ├── .env
│   ├── pyproject.toml
│   └── uv.lock
│
├── node-chart-server/
│   ├── index.js
│   ├── package.json
│   └── package-lock.json
│
└── README.md
```

---

## Architecture Components

### Node Chart Server (Rendering Engine)
- Written in **Node.js**
- Uses **Chart.js**
- Exposes an HTTP endpoint
- Accepts metric time-series data
- Returns a rendered chart as an image

### MCP Chart Server
- Written in **Python**
- Uses **FastMCP**
- Exposes tools:
  - Tool to return metric time-series data
  - Tool to call the Node.js chart endpoint
- Acts as the bridge between agent and chart renderer

### Frontend / Agent (Chainlit)
- Acts as the AI interface
- Calls MCP tools
- Displays returned chart images inline
- Designed to be replaced later with enterprise copilots

---

## Prerequisites

- macOS / Linux (Windows with minor adjustments)
- Python 3.13+
- Node.js 25+
- NPM 11+
- Homebrew (macOS)
- uv (Python dependency manager)
- OPENAPI or Equivalent
- Chainlit

---

## 1. Node Chart Server Setup

### Install Node.js & npm (macOS)

```bash
brew install node
```

Verify:
```bash
node -v
npm -v
```

### Install Dependencies

```bash
cd node-chart-server
npm install
```

### Start Server

```bash
node index.js
```

---

## 2. MCP Chart Server Setup

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup Environment

```bash
cd mcp-chart-server
uv venv
source .venv/bin/activate
```

### Install Dependencies

```bash
uv sync
```

### Configure Environment Variables

```env
NODE_CHART_SERVER_URL=http://localhost:3000
```

### Run MCP Server

```bash
python mcp_server.py
```

---

## 3. Frontend / Agent (Chainlit) Setup

```bash
cd frontend-chart-server
uv venv
source .venv/bin/activate
uv sync
chainlit run app.py
```

Open:
```
http://localhost:8000
```

---

## End-to-End Flow Validation

Ask:
```
How is CPU Usage?
```

Chart should render inline.

---


# AEMO Energy System - Project Overview

This system consists of two separate repositories that work together to provide real-time analysis of the Australian electricity market:

1. **[aemo-data-updater](https://github.com/davidleitch1/aemo-data-updater)** - Standalone service that downloads and maintains electricity market data
2. **[aemo-energy-dashboard](https://github.com/davidleitch1/aemo-energy-dashboard)** - Web-based visualization platform for data analysis

## Repository Structure

### 📊 aemo-data-updater (Separate Repository)
Independent data collection service:
- Runs continuously every 5 minutes
- Downloads from NEMWEB (generation, prices, transmission, rooftop solar)
- Maintains parquet files in shared location
- Includes status monitoring UI (port 5011)
- Can run on different machine from dashboard
- See [CLAUDE_UPDATER.md](./CLAUDE_UPDATER.md) for details

### 🎯 aemo-energy-dashboard (This Repository)
Visualization and analysis platform:
- Read-only access to parquet files
- No data downloading functionality
- Interactive charts and tables
- Three main analysis tabs
- Runs on port 5010
- See [CLAUDE_DASHBOARD.md](./CLAUDE_DASHBOARD.md) for details

## Quick Start

### Install and Run Data Updater
```bash
# Clone updater repository
git clone https://github.com/davidleitch1/aemo-data-updater.git
cd aemo-data-updater

# Set up environment
uv venv
source .venv/bin/activate
uv pip install -e .

# Configure (edit .env file)
cp .env.example .env

# Run service
python -m aemo_updater service

# Run status UI (separate terminal)
python -m aemo_updater ui
# Access at http://localhost:5011
```

### Install and Run Dashboard
```bash
# Clone dashboard repository
git clone https://github.com/davidleitch1/aemo-energy-dashboard.git
cd aemo-energy-dashboard

# Set up environment
uv venv
source .venv/bin/activate
uv pip install -e .

# Configure (edit .env file)
cp .env.example .env

# Run dashboard
.venv/bin/python -m src.aemo_dashboard.generation.gen_dash
# Access at http://localhost:5010
```

**⚠️ Python Aliasing Issue:** If you encounter `ModuleNotFoundError: No module named 'pandas'` or similar import errors, this is likely due to shell aliases overriding the virtual environment's Python. Use `.venv/bin/python` directly instead of just `python` to ensure you're using the virtual environment's interpreter.

## Architecture Overview

```
┌─────────────────────┐     ┌──────────────────────┐
│   AEMO NEMWEB      │     │  AEMO Energy         │
│   Data Sources     │     │  Dashboard           │
│                    │     │                      │
│ • Generation       │     │ • Generation Tab     │
│ • Prices           │     │ • Price Analysis     │
│ • Transmission     │     │ • Station Analysis   │
│ • Rooftop Solar    │     │                      │
└────────┬───────────┘     └──────────┬───────────┘
         │                            │
         ▼                            ▼
┌─────────────────────┐     ┌──────────────────────┐
│  AEMO Data Updater │     │   Reads Parquet      │
│                    │     │   Files Only         │
│ Downloads every    │────▶│                      │
│ 5 minutes         │     │  No downloads in     │
│                    │     │  dashboard           │
└─────────────────────┘     └──────────────────────┘
         │
         ▼
┌─────────────────────┐
│   Parquet Files    │
│                    │
│ • gen_output       │
│ • spot_hist        │
│ • transmission     │
│ • rooftop_solar    │
└─────────────────────┘
```

## Project Status

### ✅ Completed
- Dashboard with 3 main tabs (Generation, Price Analysis, Station Analysis)
- Real-time data updates every 5 minutes
- Transmission flow integration
- Rooftop solar data with 30→5 minute conversion
- Time range selection controls
- Data validity checking system

### 🚧 In Progress
- Separating updater into standalone service
- Adding data integrity checks to updater
- Implementing automated backfill
- Fixing transmission data overwrites

### 📋 Planned
- Complete service separation
- Docker containerization
- Multi-machine deployment
- Additional dashboard tabs
- WebSocket real-time updates

## Development Guidelines

Before making significant changes:
1. Review the latest HoloViz Panel documentation
2. Use the Material template for UI components
3. Follow good git practices with descriptive commits
4. Create detailed plans with checkpoints
5. Test thoroughly at localhost before deploying

## Contact & Issues

For questions or issues, refer to the specialized documentation files or check the project's git repository.
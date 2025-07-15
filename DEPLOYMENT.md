# Deployment Guide for AEMO Energy Dashboard

## Replacing the Production Dashboard

The new dashboard is designed to replace the existing dashboard running at `/Users/davidleitch/Library/Mobile Documents/com~apple~CloudDocs/snakeplay/AEMO_spot/genhist/gen_dash.py`.

### Key Changes

1. **Port Configuration**: The new dashboard now uses port 5008 by default (same as production)
2. **Cloudflare Tunnel**: Already configured to accept connections from `nemgen.itkservices2.com`
3. **Environment Variable**: Use `DASHBOARD_PORT` to control the port

### Deployment Steps

1. **Stop the old dashboard**:
   ```bash
   # Find the process
   ps aux | grep "genhist/gen_dash.py"
   # Kill the process
   kill -9 <PID>
   ```

2. **Configure the new dashboard**:
   ```bash
   cd /Users/davidleitch/Library/Mobile Documents/com~apple~CloudDocs/snakeplay/AEMO_spot/aemo-energy-dashboard
   
   # Copy environment template
   cp .env.example .env
   
   # Edit .env to ensure:
   # DASHBOARD_PORT=5008  (for production)
   # Or leave blank to default to 5008
   ```

3. **Start the new dashboard**:
   ```bash
   # Activate virtual environment
   source .venv/bin/activate
   
   # Run the dashboard
   .venv/bin/python -m src.aemo_dashboard.generation.gen_dash
   ```

4. **For development** (running alongside production):
   ```bash
   # Set different port in .env
   DASHBOARD_PORT=5010
   
   # Or use environment variable
   DASHBOARD_PORT=5010 .venv/bin/python -m src.aemo_dashboard.generation.gen_dash
   ```

### Running as a Service

For persistent deployment, create a systemd service or use screen/tmux:

```bash
# Using screen
screen -S aemo-dashboard
cd /Users/davidleitch/Library/Mobile Documents/com~apple~CloudDocs/snakeplay/AEMO_spot/aemo-energy-dashboard
source .venv/bin/activate
.venv/bin/python -m src.aemo_dashboard.generation.gen_dash
# Detach with Ctrl+A, D
```

### Verification

1. **Local access**: http://localhost:5008
2. **Remote access**: https://nemgen.itkservices2.com (via Cloudflare tunnel)

### Features in New Dashboard

- **Nem-dash tab**: New primary overview with gauge, generation chart, and price info
- **Generation by Fuel**: Enhanced with better battery handling
- **Price Analysis**: Advanced filtering and analysis
- **Station Analysis**: Detailed station/DUID analysis
- **Improved rooftop solar**: Better interpolation and handling

### Rollback

If needed, restart the old dashboard:
```bash
cd /Users/davidleitch/Library/Mobile Documents/com~apple~CloudDocs/snakeplay/AEMO_spot/genhist
python gen_dash.py
```
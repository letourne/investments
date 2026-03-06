# 🥧 Retirement Dashboard - Raspberry Pi Setup

## Your Configuration

- **Project Location:** `/home/pi/python/invest/`
- **Virtual Environment:** `/opt/venvs/pi_projects/`
- **Port:** `8502`
- **Network Access:** Enabled (accessible from any device)

---

## 📦 Files You Need

Copy these files to `/home/pi/python/invest/`:

### **Python Files** (Required):
```
retirement_dashboard_enhanced.py
monte_carlo_engine.py
optimization.py
retirement_inputs.py
historical_data.py
tax_strategy.py
asset_allocation.py
utils.py
```

### **Scripts** (Required):
```
setup.sh         - One-time setup (checks packages)
start.sh         - Start dashboard (background daemon)
stop.sh          - Stop dashboard
restart.sh       - Restart dashboard
status.sh        - Check if running
install_service.sh - Install as auto-start service
```

### **Config** (Required):
```
.venv_path          (contains: /opt/venvs/pi_projects)
.streamlit_config.toml
```

---

## 🚀 Quick Setup (First Time)

### Step 1: Create .venv_path file

```bash
cd /home/pi/python/invest/
echo '/opt/venvs/pi_projects' > .venv_path
```

This tells the scripts where your virtual environment is located.

### Step 2: Make scripts executable

```bash
chmod +x setup.sh start.sh stop.sh install_service.sh
```

### Step 3: Run setup (optional - checks packages)

```bash
./setup.sh
```

This will:
- Read your venv path from `.venv_path`
- Activate `/opt/venvs/pi_projects/`
- Check if streamlit, numpy, pandas, plotly are installed
- Create Streamlit config for network access

**Since you already have streamlit installed, this step is optional.**

---

## ▶️ Starting the Dashboard

The dashboard runs as a **background daemon** - it won't take over your terminal.

### Start:

```bash
cd /home/pi/python/invest/
./start.sh
```

**You'll see:**
```
✅ Dashboard started successfully!
   PID: 12345

   Access URLs:
     Local:   http://localhost:8502
     Network: http://192.168.1.XXX:8502

   View logs: tail -f retirement.log
   To stop:   ./stop.sh
```

**Your terminal prompt returns immediately** - the dashboard runs in the background!

---

## 🔍 Check Status:

```bash
./status.sh
```

Shows:
- ✅ Running or ❌ Not running
- Process ID (PID)
- CPU/Memory usage
- Access URLs
- Recent log entries

---

## 🛑 Stopping the Dashboard:

```bash
./stop.sh
```

Gracefully stops the background process.

---

## 🔄 Restart:

```bash
./restart.sh
```

Stops and starts in one command.

---

## 📊 View Logs:

**Live log tail:**
```bash
tail -f retirement.log
```

**Last 50 lines:**
```bash
tail -n 50 retirement.log
```

**Search logs:**
```bash
grep "error" retirement.log
```

Press `Ctrl+C` to exit log viewing (dashboard keeps running).

---

## 🔄 Auto-Start on Boot (Recommended)

To make the dashboard start automatically when your Pi boots:

```bash
cd /home/pi/python/invest/
sudo ./install_service.sh
```

This creates a systemd service that:
- ✅ Starts automatically on boot
- ✅ Restarts if it crashes
- ✅ Runs in background (no terminal needed)
- ✅ Uses your existing venv at `/opt/venvs/pi_projects/`

### Service Commands:

```bash
# Check status
sudo systemctl status retirement-dashboard

# Start service
sudo systemctl start retirement-dashboard

# Stop service
sudo systemctl stop retirement-dashboard

# Restart service
sudo systemctl restart retirement-dashboard

# View live logs
sudo journalctl -u retirement-dashboard -f

# Disable auto-start
sudo systemctl disable retirement-dashboard

# Enable auto-start (after disabling)
sudo systemctl enable retirement-dashboard
```

---

## 📱 Mobile Access

### iOS (Safari):
1. Open `http://[pi-ip]:8502`
2. Tap Share → Add to Home Screen
3. Name: "Retirement Planner"
4. Tap "Add"

Now you have an app icon!

### Android (Chrome):
1. Open `http://[pi-ip]:8502`
2. Menu (⋮) → Add to Home screen
3. Name: "Retirement Planner"
4. Tap "Add"

---

## 🔧 How It Works

### The `.venv_path` File

This file contains a single line with your venv path:
```
/opt/venvs/pi_projects
```

All scripts read this file to know which virtual environment to use.

**Why?** So you don't have to hardcode paths in multiple places!

### Script Flow:

1. **start.sh** reads `.venv_path`
2. Activates `/opt/venvs/pi_projects/`
3. Runs: `python -m streamlit run retirement_dashboard_enhanced.py --server.port=8502 --server.address=0.0.0.0`
4. Dashboard accessible at port 8502 from any device

---

## 🐛 Troubleshooting

### "Virtual environment not found"

**Check .venv_path:**
```bash
cat .venv_path
```

Should show: `/opt/venvs/pi_projects`

**Verify venv exists:**
```bash
ls -la /opt/venvs/pi_projects/
```

### "Streamlit not found"

**Activate venv and check:**
```bash
source /opt/venvs/pi_projects/bin/activate
python -c "import streamlit; print(streamlit.__version__)"
```

If not installed:
```bash
pip install streamlit
```

### "File not found: retirement_dashboard_enhanced.py"

**Check you're in the right directory:**
```bash
pwd
```

Should show: `/home/pi/python/invest`

**List files:**
```bash
ls -la *.py
```

### Can't access from phone/computer

**Check firewall:**
```bash
sudo ufw status
```

If active:
```bash
sudo ufw allow 8502/tcp
```

**Verify it's running:**
```bash
sudo netstat -tlnp | grep 8502
```

Should show streamlit listening on port 8502.

**Ping your Pi:**
```bash
# From another device
ping [pi-ip]
```

---

## 📊 Performance

### Simulation Times:
- **Raspberry Pi 3:** ~3-4 minutes for 5,000 simulations
- **Raspberry Pi 4:** ~1-2 minutes for 5,000 simulations

### Speed Up:
In the dashboard sidebar, reduce simulations from 5,000 to 1,000:
- Still statistically accurate
- ~4x faster

---

## 📁 Directory Structure

```
/home/pi/python/invest/
├── .venv_path                         ← Points to /opt/venvs/pi_projects
├── .retirement.pid                    ← Created when running (PID file)
├── retirement.log                     ← Log file
├── .streamlit/
│   └── config.toml                    ← Auto-created by setup.sh
│
├── setup.sh                           ← One-time setup
├── start.sh                           ← Start (background daemon)
├── stop.sh                            ← Stop
├── restart.sh                         ← Restart
├── status.sh                          ← Check status
├── install_service.sh                 ← Install as service
│
├── retirement_dashboard_enhanced.py   ← Main app
├── monte_carlo_engine.py              ← Simulation engine
├── optimization.py                    ← Optimizers
├── retirement_inputs.py               ← Data structures
├── historical_data.py
├── tax_strategy.py
├── asset_allocation.py
└── utils.py
```

### Your Virtual Environment (Separate):
```
/opt/venvs/pi_projects/
├── bin/
│   ├── python
│   ├── pip
│   └── streamlit
├── lib/
│   └── python3.x/
│       └── site-packages/
│           ├── streamlit/
│           ├── numpy/
│           ├── pandas/
│           └── plotly/
└── ...
```

---

## 🎯 Quick Command Reference

```bash
# Navigate to project
cd /home/pi/python/invest/

# First time setup (optional)
./setup.sh

# Start dashboard (background daemon)
./start.sh

# Check status
./status.sh

# View logs
tail -f retirement.log

# Stop dashboard
./stop.sh

# Restart dashboard
./restart.sh

# Install as service (runs on boot)
sudo ./install_service.sh

# Service commands
sudo systemctl status retirement-dashboard
sudo systemctl start retirement-dashboard
sudo systemctl stop retirement-dashboard
sudo systemctl restart retirement-dashboard
sudo journalctl -u retirement-dashboard -f

# Find Pi IP
hostname -I

# Check if running
ps aux | grep streamlit

# Test from Pi
curl http://localhost:8502
```

---

## ✅ Checklist

- [ ] All Python files in `/home/pi/python/invest/`
- [ ] All scripts in `/home/pi/python/invest/`
- [ ] Created `.venv_path` file with `/opt/venvs/pi_projects`
- [ ] Made scripts executable (`chmod +x`)
- [ ] Ran `./start.sh` successfully
- [ ] Can access at `http://localhost:8502` on Pi
- [ ] Got Pi's IP address with `hostname -I`
- [ ] Can access at `http://[pi-ip]:8502` from phone
- [ ] (Optional) Installed as service with `sudo ./install_service.sh`
- [ ] Bookmarked on phone/tablet

---

## 💡 Pro Tips

### Use mDNS for easier access:
```bash
http://raspberrypi.local:8502
```
(Instead of remembering IP address)

### Check service logs in real-time:
```bash
sudo journalctl -u retirement-dashboard -f
```

### Set static IP on your Pi:
```bash
sudo nano /etc/dhcpcd.conf
```
So the URL never changes.

### Monitor resource usage:
```bash
htop
```

### Check temperature:
```bash
vcgencmd measure_temp
```

---

**Project:** `/home/pi/python/invest/`  
**Venv:** `/opt/venvs/pi_projects/`  
**Port:** `8502`  
**Network:** Enabled (0.0.0.0)

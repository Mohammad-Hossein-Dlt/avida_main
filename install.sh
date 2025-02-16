#!/bin/bash

# Variables - modify as needed
REPO_URL="Mohammad-Hossein-Dlt/avida_main"
TARGET_DIR="/home/fastapi-project"
APP_FILE="main"          # Name of the main Python file (without .py extension)
APP_VARIABLE="app"       # Name of the FastAPI instance in the main file

# Ports to open in the firewall for external access
PORTS=("8000" "1234")

# Determine the user to run the service (if the script is executed with sudo)
if [ -n "$SUDO_USER" ]; then
  USER_TO_RUN="$SUDO_USER"
else
  USER_TO_RUN="$(whoami)"
fi

echo "----------------------------------------------------"
echo "Step 1: Updating the system"
echo "----------------------------------------------------"
sudo apt-get update -y
sudo apt-get upgrade -y

echo "----------------------------------------------------"
echo "Step 2: Installing prerequisites (Git, Python3, pip, python3-venv)"
echo "----------------------------------------------------"
sudo apt-get install -y git python3 python3-pip python3-venv

echo "----------------------------------------------------"
echo "Step 3: Cloning the repository from GitHub"
echo "----------------------------------------------------"
# Remove the target directory if it exists (optional)
if [ -d "$TARGET_DIR" ]; then
  echo "Directory $TARGET_DIR exists. Removing it..."
  sudo rm -rf "$TARGET_DIR"
fi

git clone https://github.com/$REPO_URL "$TARGET_DIR"

echo "----------------------------------------------------"
echo "Step 4: Setting up the virtual environment and installing dependencies"
echo "----------------------------------------------------"
cd "$TARGET_DIR" || { echo "Failed to change directory to $TARGET_DIR."; exit 1; }

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip, setuptools, and wheel to avoid build issues
pip install --upgrade pip
pip install wheel

# Install project dependencies if a requirements.txt file exists
if [ -f requirements.txt ]; then
  echo "Installing project dependencies..."
  pip install -r requirements.txt
else
  echo "requirements.txt not found. Please install dependencies manually."
fi

# Deactivate the virtual environment (optional)
deactivate

echo "----------------------------------------------------"
echo "Step 5: Creating a systemd service file for automatic FastAPI startup"
echo "----------------------------------------------------"
SERVICE_FILE="/etc/systemd/system/fastapi.service"

# Create the service file using tee
sudo tee "$SERVICE_FILE" > /dev/null <<EOL
[Unit]
Description=FastAPI Application Service
After=network.target

[Service]
User=$USER_TO_RUN
WorkingDirectory=$TARGET_DIR
Environment="PATH=$TARGET_DIR/venv/bin"
ExecStart=$TARGET_DIR/venv/bin/uvicorn $APP_FILE:$APP_VARIABLE --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

echo "Service file created at $SERVICE_FILE"

echo "----------------------------------------------------"
echo "Step 6: Reloading systemd and enabling the service"
echo "----------------------------------------------------"
sudo systemctl daemon-reload
sudo systemctl enable fastapi.service
sudo systemctl restart fastapi.service

echo "----------------------------------------------------"
echo "Step 7: Configuring the firewall to open ports for external access"
echo "----------------------------------------------------"
# Install ufw if not already installed
sudo apt-get install -y ufw

# Enable ufw if it's not enabled already (this may prompt for confirmation)
sudo ufw --force enable

# Loop over the ports array and open each port for TCP traffic
for port in "${PORTS[@]}"; do
  echo "Allowing TCP traffic on port $port"
  sudo ufw allow "$port/tcp"
done

# Reload ufw to apply changes
sudo ufw reload

echo "----------------------------------------------------"
echo "FastAPI is now running as a systemd service and the firewall is configured."
echo "After a server restart, the application will start automatically."
echo "To check the service status, run:"
echo "  sudo systemctl status fastapi.service"
echo "To check the firewall status, run:"
echo "  sudo ufw status"

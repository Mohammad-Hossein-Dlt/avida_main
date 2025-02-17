#!/bin/bash

colored_text(){
  local color=$1
  local text=$2

  echo -e "\e[${color}m$text\e[0m"
}

# Variables - modify as needed
REPO_URL="Mohammad-Hossein-Dlt/avida_main"
TARGET_DIR="/home/fastapi-project"

# Ports to open in the firewall for external access
PORTS=("8000" "1234")

# Determine the user to run the service (if the script is executed with sudo)
if [ -n "$SUDO_USER" ]; then
  USER_TO_RUN="$SUDO_USER"
else
  USER_TO_RUN="$(whoami)"
fi

colored_text "32" "----------------------------------------------------"
colored_text "32" "Step 1: Updating the system"
colored_text "32" "----------------------------------------------------"
sudo apt-get update -y
sudo apt-get upgrade -y

colored_text "32" "----------------------------------------------------"
colored_text "32" "Step 2: Installing prerequisites (Git, Python3, pip3, python3-venv)"
colored_text "32" "----------------------------------------------------"
sudo apt-get install -y git python3 python3-pip python3-venv

colored_text "32" "----------------------------------------------------"
colored_text "32" "Step 3: Cloning the repository from GitHub"
colored_text "32" "----------------------------------------------------"
# Remove the target directory if it exists (optional)
if [ -d "$TARGET_DIR" ]; then
  colored_text "32" "Directory $TARGET_DIR exists. Removing it..."
  sudo rm -rf "$TARGET_DIR"
fi

git clone https://github.com/$REPO_URL "$TARGET_DIR"

colored_text "32" "----------------------------------------------------"
colored_text "32" "Step 4: Setting up the virtual environment and installing dependencies"
colored_text "32" "----------------------------------------------------"
cd "$TARGET_DIR" || { colored_text "31" "Failed to change directory to $TARGET_DIR."; exit 1; }

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip, setuptools, and wheel to avoid build issues
pip3 install --upgrade pip
pip3 install wheel

# Install project dependencies if a requirements.txt file exists
if [ -f requirements.txt ]; then
  colored_text "32" "Installing project dependencies..."
  pip3 install -r requirements.txt
else
  colored_text "31" "requirements.txt not found. Please install dependencies manually."
fi

# Deactivate the virtual environment (optional)
deactivate

colored_text "32" "----------------------------------------------------"
colored_text "32" "Step 5: Creating a systemd service file for automatic FastAPI startup"
colored_text "32" "----------------------------------------------------"
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
ExecStart=$TARGET_DIR/venv/bin/fastapi run main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

colored_text "32" "Service file created at $SERVICE_FILE"

colored_text "32" "----------------------------------------------------"
colored_text "32" "Step 6: Reloading systemd and enabling the service"
colored_text "32" "----------------------------------------------------"
sudo systemctl daemon-reload
sudo systemctl enable fastapi.service
sudo systemctl restart fastapi.service

colored_text "32" "----------------------------------------------------"
colored_text "32" "Step 7: Configuring the firewall to open ports for external access"
colored_text "32" "----------------------------------------------------"
# Install ufw if not already installed
sudo apt-get install -y ufw

# Allow SSH (port 22) to ensure remote access is not blocked
colored_text "32" "Allowing SSH on port 22"
sudo ufw allow 22/tcp

# Enable ufw if it's not enabled already (this may prompt for confirmation)
sudo ufw --force enable

# Loop over the ports array and open each port for TCP traffic
for port in "${PORTS[@]}"; do
  colored_text "32" "Allowing TCP traffic on port $port"
  sudo ufw allow "$port/tcp"
done

# Reload ufw to apply changes
sudo ufw reload

colored_text "32" "----------------------------------------------------"
colored_text "32" "FastAPI is now running as a systemd service and the firewall is configured."
colored_text "32" "After a server restart, the application will start automatically."
colored_text "32" "To check the service status, run:"
colored_text "32" "   sudo systemctl status fastapi.service"
colored_text "32" "To check the firewall status, run:"
colored_text "32" "  sudo ufw status"

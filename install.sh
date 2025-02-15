# Update system
echo "Updating system..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Docker
echo "Installing Docker..."
sudo apt-get install -y docker.io
sudo systemctl enable --now docker

# Install git (if not already installed)
echo "Installing Git..."
sudo apt-get install -y git

# Clone repository from GitHub (using a private token)
echo "Cloning repository..."

# Replace 'your-token' with your actual GitHub token
REPO_URL="Mohammad-Hossein-Dlt/avida_main"
TOKEN="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"

git clone https://$TOKEN@github.com/$REPO_URL /home/fastapi-project

# Navigate to project directory
cd /home/fastapi-project || exit

# Build Docker image
echo "Building Docker image..."
docker build -t fastapi-app .

# Run Docker container
echo "Running Docker container..."
docker run -d -p 8000:8000 --name fastapi-container fastapi-app

# Output the result
echo "FastAPI is now running on http://localhost:8000"


bash <(curl -Ls -u hosein27d@gmain.com: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 https://raw.githubusercontent.com/Mohammad-Hossein-Dlt/avida_main/master/scripts/install.sh)
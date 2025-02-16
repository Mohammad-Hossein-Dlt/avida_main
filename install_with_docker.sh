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

git clone https://github.com/$REPO_URL /home/fastapi-project

# Navigate to project directory
cd /home/fastapi-project || exit

# Build Docker image
echo "Building Docker image..."
docker build -t fastapi-app .

# Run Docker container
echo "Running the Docker container..."
# Check if the container is already running and remove it if needed
if [ "$(docker ps -aq -f name=fastapi-container)" ]; then
  echo "The container exists. Stopping and removing it..."
  docker stop fastapi-container 2>/dev/null || true
  docker rm fastapi-container
fi

docker run -d --restart always -p 8000:8000 -p 1234:1234 --name fastapi-container fastapi-app

# Output the result
echo "FastAPI is now running on http://localhost:8000"


bash <(curl -H "Authorization: token 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" https://raw.githubusercontent.com/Mohammad-Hossein-Dlt/avida_main/master/install.sh)
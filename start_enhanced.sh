#!/bin/bash

# 🌾 कृषि AI सलाहकार - Enhanced Startup Script
# Built for Bangalore Hackathon 2025

echo "🌾 Starting कृषि AI सलाहकार - Enhanced Agricultural Intelligence Platform"
echo "=================================================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

echo -e "${BLUE}Step 1: Checking Prerequisites...${NC}"

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js found: $NODE_VERSION${NC}"
else
    echo -e "${RED}✗ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

# Check MongoDB
if command_exists mongod; then
    echo -e "${GREEN}✓ MongoDB found${NC}"
else
    echo -e "${YELLOW}⚠ MongoDB not found. Using fallback database${NC}"
fi

# Check Ollama
if command_exists ollama; then
    echo -e "${GREEN}✓ Ollama found${NC}"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Ollama server is running${NC}"
    else
        echo -e "${YELLOW}⚠ Starting Ollama server...${NC}"
        ollama serve &
        sleep 3
    fi
    
    # Check if model is available
    if ollama list | grep -q "llama3.2:3b"; then
        echo -e "${GREEN}✓ Llama 3.2 model found${NC}"
    else
        echo -e "${YELLOW}⚠ Downloading Llama 3.2 model (this may take a few minutes)...${NC}"
        ollama pull llama3.2:3b
    fi
else
    echo -e "${RED}✗ Ollama not found. Please install Ollama first:${NC}"
    echo -e "${BLUE}curl -fsSL https://ollama.ai/install.sh | sh${NC}"
    exit 1
fi

echo -e "\n${BLUE}Step 2: Setting up Backend...${NC}"

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo -e "${RED}✗ Backend directory not found${NC}"
    exit 1
fi

cd backend

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip3 install -r requirements.txt
else
    echo -e "${RED}✗ requirements.txt not found${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ Creating .env file from template...${NC}"
    cat > .env << EOL
MONGO_URL=mongodb://localhost:27017/krishi_ai_advisor_db
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_number
WEATHER_API_KEY=demo_key
CROP_RECOMMENDATION_API=http://localhost:8002
SOIL_ANALYSIS_API=http://localhost:8003
EOL
fi

# Start backend server
echo -e "${YELLOW}Starting backend server...${NC}"
python3 server_enhanced.py &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend server started (PID: $BACKEND_PID)${NC}"

# Wait for backend to start
sleep 5

# Check if backend is running
if curl -s http://localhost:8001/api/health >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend health check passed${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
fi

cd ..

echo -e "\n${BLUE}Step 3: Setting up Frontend...${NC}"

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo -e "${RED}✗ Frontend directory not found${NC}"
    exit 1
fi

cd frontend

# Install Node.js dependencies
if [ -f "package.json" ]; then
    echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
    npm install
else
    echo -e "${RED}✗ package.json not found${NC}"
    exit 1
fi

# Start frontend server
echo -e "${YELLOW}Starting frontend server...${NC}"
npm start &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend server started (PID: $FRONTEND_PID)${NC}"

cd ..

echo -e "\n${GREEN}🎉 कृषि AI सलाहकार is now running!${NC}"
echo -e "=================================================================="
echo -e "${BLUE}🌐 Web Interface:${NC} http://localhost:3000"
echo -e "${BLUE}📚 API Documentation:${NC} http://localhost:8001/docs"
echo -e "${BLUE}🔍 Health Check:${NC} http://localhost:8001/api/health"
echo -e "=================================================================="

echo -e "\n${YELLOW}🚀 Demo Features to Try:${NC}"
echo -e "1. ${BLUE}AI Chat:${NC} Ask 'इस मौसम में कौन सी फसल उगानी चाहिए?' in Chat tab"
echo -e "2. ${BLUE}Crop Advisor:${NC} Enter 'Punjab' and get AI recommendations"
echo -e "3. ${BLUE}Disease Detection:${NC} Upload a plant image for diagnosis"
echo -e "4. ${BLUE}Weather:${NC} Check comprehensive weather data"
echo -e "5. ${BLUE}Market:${NC} View real-time crop prices and trends"

echo -e "\n${YELLOW}📱 For SMS Testing:${NC}"
echo -e "Configure Twilio credentials in backend/.env file"

echo -e "\n${YELLOW}🛑 To stop the application:${NC}"
echo -e "Press Ctrl+C or run: ${BLUE}./stop_enhanced.sh${NC}"

# Create stop script
cat > stop_enhanced.sh << 'EOL'
#!/bin/bash
echo "🛑 Stopping कृषि AI सलाहकार..."

# Kill processes on ports 3000 and 8001
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:8001 | xargs kill -9 2>/dev/null

echo "✓ Application stopped successfully"
EOL

chmod +x stop_enhanced.sh

# Wait for user input
echo -e "\n${GREEN}Press Ctrl+C to stop the application${NC}"
wait
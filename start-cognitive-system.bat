@echo off
echo Starting Cognitive Core AGI System...
echo.

echo Step 1: Starting Docker containers (Qdrant, Neo4j, Redis)...
cd /d "%~dp0"
docker-compose up -d
echo Docker containers started.
echo.

echo Step 2: Waiting for services to be ready...
timeout /t 10 /nobreak
echo.

echo Step 3: Installing Python dependencies...
cd cognitive-core
pip install -r requirements.txt
echo.

echo Step 4: Starting Cognitive Core API...
python main.py
echo.

echo Cognitive Core System started successfully!
echo API available at: http://localhost:8000
echo Qdrant Dashboard: http://localhost:6333/dashboard
echo Neo4j Browser: http://localhost:7474
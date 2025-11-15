#!/bin/bash

echo "===================================================="
echo "Master Creator v3 MVP - Quick Start"
echo "===================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "run_server.py" ]; then
    echo "❌ Error: Must run from master_creator_mvp directory"
    echo "   Try: cd master_creator_mvp && ./start_mvp.sh"
    exit 1
fi

# Step 1: Initialize database if it doesn't exist
if [ ! -f "master_creator.db" ]; then
    echo "📊 Initializing database..."
    python init_content_storage.py
    echo ""
fi

# Step 2: Load sample data if database is empty
echo "📝 Loading sample data..."
python load_sample_data.py 2>&1 | grep -q "already exists" || echo "✓ Sample data loaded"
echo ""

# Step 3: Set environment to use in-memory ChromaDB (no Docker needed)
export USE_CHROMADB_SERVER=false

# Step 4: Start backend server
echo "🚀 Starting backend server on http://localhost:8080"
echo "   API Docs: http://localhost:8080/api/docs"
echo "   Press Ctrl+C to stop"
echo ""
echo "===================================================="
echo ""

python run_server.py

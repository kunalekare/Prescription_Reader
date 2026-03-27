#!/bin/bash
# Quick test launcher for Linux/Mac

echo "============================================"
echo "  PRESCRIPTION READER - QUICK TEST"
echo "============================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python not found!"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[1/3] Checking setup..."
python3 test_setup.py
echo ""

echo "[2/3] Testing OCR API..."
python3 quick_test.py
echo ""

echo "[3/3] Launching demo interface..."
echo ""
echo "Starting Streamlit demo in 3 seconds..."
echo "Press Ctrl+C to cancel..."
sleep 3

streamlit run demo_ocr.py

@echo off
echo ========================================
echo  TESTING SARVAM API ENDPOINTS
echo ========================================
echo.
echo This will test different endpoints to find the correct one...
echo.
python test_sarvam_endpoint.py
echo.
echo ========================================
echo  TEST COMPLETE
echo ========================================
echo.
echo If you found a working endpoint above:
echo 1. Note the URL shown in the success message
echo 2. It's already updated in the code
echo 3. Try: streamlit run demo_ocr.py
echo.
pause

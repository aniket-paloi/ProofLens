@echo off
title ProofLens Test Suite Runner
echo =======================================================
echo          ProofLens - Comprehensive Pytest Runner
echo =======================================================
echo.
echo Running 51/51 pytest integration and unit tests...
echo.
cd /d %~dp0
python -m pytest backend/tests -v
echo.
echo =======================================================
echo Tests completed. Press any key to exit.
echo =======================================================
pause

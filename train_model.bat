@echo off
cd /d "%~dp0ML model"
set FRAUD_MODEL_OUTPUT=%~dp0model
echo Training model... Output: %FRAUD_MODEL_OUTPUT%
python ml_pipeline.py
pause

@echo off
cd /d "%~dp0Tranjaction\src"
echo Starting Java Fraud Analysis Service on http://localhost:8080
echo (Web app will use this for fraud detection when running)
javac -encoding UTF-8 Amount.java FraudAnalysisServer.java 2>nul
java FraudAnalysisServer

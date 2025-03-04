@echo off
echo Setting up Legaluna chatbot on Windows...

:: Create virtual environment
python -m venv venv
call venv\Scripts\activate

:: Install dependencies
pip install -r requirements.txt

:: Create logs directory
mkdir logs

echo Server setup complete!
pause
# Create and activate virtual environment
Write-Host "Creating virtual environment..."
if (Test-Path "venv") {
    Remove-Item -Recurse -Force "venv"
}
python -m venv venv
.\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt

# Create output directory
Write-Host "Creating output directory..."
New-Item -ItemType Directory -Force -Path "output"

Write-Host "`nSetup complete! You can now run the application using:"
Write-Host "python -m src.cli example_topic.txt --title 'Your Title' --platforms instagram linkedin facebook x"
Write-Host "`nExample usage:"
Write-Host "1. Create a text file with your topic (e.g., my_topic.txt)"
Write-Host "2. Run the command with your topic file:"
Write-Host "   python -m src.cli my_topic.txt --title 'My Topic' --platforms instagram linkedin facebook x"
Write-Host "3. Generated posts will be saved in the 'output' directory" 
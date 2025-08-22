#!/usr/bin/env python3
"""
Setup script for AI HR Recruitment Agent
"""

import os
import sys
import subprocess
import shutil

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing Python dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up environment configuration"""
    print("⚙️ Setting up environment configuration...")
    
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✅ Created .env file from template")
            print("📝 Please edit .env file and add your API keys")
            return True
        else:
            print("❌ .env.example file not found")
            return False
    else:
        print("✅ .env file already exists")
        return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating project directories...")
    
    directories = ['data', 'src', 'templates']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created {directory}/ directory")
        else:
            print(f"✅ {directory}/ directory already exists")
    
    return True

def check_ollama():
    """Check if Ollama is installed and running"""
    print("🧠 Checking Ollama installation...")
    
    # Check if ollama command exists
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed")
            
            # Check if ollama is running
            try:
                import requests
                response = requests.get('http://localhost:11434', timeout=5)
                print("✅ Ollama service is running")
                return True
            except:
                print("⚠️ Ollama is installed but not running")
                print("🚀 Please start Ollama with: ollama serve")
                return False
        else:
            print("❌ Ollama command failed")
            return False
    except FileNotFoundError:
        print("❌ Ollama not found")
        print("📥 Please install Ollama from: https://ollama.ai/")
        return False

def pull_ollama_model():
    """Pull the required Ollama model"""
    model_name = "llama3.1:8b"
    print(f"📥 Checking for Ollama model: {model_name}")
    
    try:
        # Check if model exists
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if model_name in result.stdout:
            print(f"✅ Model {model_name} is already available")
            return True
        else:
            print(f"📥 Pulling model {model_name}... (this may take a while)")
            subprocess.check_call(['ollama', 'pull', model_name])
            print(f"✅ Model {model_name} pulled successfully")
            return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to pull model: {e}")
        return False
    except FileNotFoundError:
        print("❌ Ollama command not found")
        return False

def main():
    """Main setup function"""
    print("🤖 AI HR Recruitment Agent - Setup")
    print("=" * 50)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Create directories
    if not create_directories():
        success = False
    
    # Set up environment
    if not setup_environment():
        success = False
    
    # Install dependencies
    if not install_dependencies():
        success = False
    
    # Check Ollama
    if not check_ollama():
        success = False
    else:
        # Pull Ollama model
        if not pull_ollama_model():
            success = False
    
    print("\\n" + "=" * 50)
    
    if success:
        print("🎉 Setup completed successfully!")
        print("\\nNext steps:")
        print("1. 📝 Edit your .env file and add your Google Gemini API key")
        print("2. 🧪 Run quick test: python quickstart.py")
        print("3. 🌐 Launch web interface: python main.py web")
        print("4. 📖 Read README.md for detailed usage instructions")
    else:
        print("❌ Setup incomplete. Please fix the issues above and run setup again.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

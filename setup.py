#!/usr/bin/env python3
"""
Setup script for E-commerce API Test Suite
This script helps set up the test environment and validates the configuration.
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path


def setup_logging():
    """Setup logging for the setup process."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('setup.log')
        ]
    )
    return logging.getLogger(__name__)


def check_python_version():
    """Check if Python version is compatible."""
    logger = logging.getLogger(__name__)
    
    min_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version < min_version:
        logger.error(f"Python {min_version[0]}.{min_version[1]}+ is required. "
                    f"Current version: {current_version[0]}.{current_version[1]}")
        return False
    
    logger.info(f"Python version check passed: {current_version[0]}.{current_version[1]}")
    return True


def create_virtual_environment():
    """Create virtual environment if it doesn't exist."""
    logger = logging.getLogger(__name__)
    
    venv_path = Path('venv')
    if venv_path.exists():
        logger.info("Virtual environment already exists")
        return True
    
    try:
        logger.info("Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        logger.info("Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create virtual environment: {e}")
        return False


def install_dependencies():
    """Install required dependencies."""
    logger = logging.getLogger(__name__)
    
    # Determine the correct pip path
    if os.name == 'nt':  # Windows
        pip_path = Path('venv') / 'Scripts' / 'pip.exe'
    else:  # Linux/Mac
        pip_path = Path('venv') / 'bin' / 'pip'
    
    if not pip_path.exists():
        logger.error("Virtual environment not found. Please create it first.")
        return False
    
    try:
        logger.info("Installing dependencies...")
        subprocess.run([str(pip_path), 'install', '--upgrade', 'pip'], check=True)
        subprocess.run([str(pip_path), 'install', '-r', 'requirements.txt'], check=True)
        logger.info("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False


def create_env_file():
    """Create .env file from template if it doesn't exist."""
    logger = logging.getLogger(__name__)
    
    env_file = Path('.env')
    template_file = Path('.env.template')
    
    if env_file.exists():
        logger.info(".env file already exists")
        return True
    
    if not template_file.exists():
        logger.warning(".env.template not found, skipping .env creation")
        return True
    
    try:
        logger.info("Creating .env file from template...")
        with open(template_file, 'r') as template:
            content = template.read()
        
        with open(env_file, 'w') as env:
            env.write(content)
        
        logger.info(".env file created. Please update it with your actual values.")
        return True
    except Exception as e:
        logger.error(f"Failed to create .env file: {e}")
        return False


def create_reports_directory():
    """Create reports directory if it doesn't exist."""
    logger = logging.getLogger(__name__)
    
    reports_dir = Path('reports')
    if not reports_dir.exists():
        try:
            reports_dir.mkdir(exist_ok=True)
            logger.info("Reports directory created")
        except Exception as e:
            logger.error(f"Failed to create reports directory: {e}")
            return False
    
    return True


def validate_test_data():
    """Validate test data configuration."""
    logger = logging.getLogger(__name__)
    
    test_data_file = Path('data') / 'test_data.json'
    if not test_data_file.exists():
        logger.error("test_data.json not found")
        return False
    
    try:
        with open(test_data_file, 'r') as f:
            test_data = json.load(f)
        
        required_keys = ['base_url', 'endpoints', 'valid_users']
        for key in required_keys:
            if key not in test_data:
                logger.error(f"Required key '{key}' not found in test_data.json")
                return False
        
        logger.info("Test data validation passed")
        return True
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in test_data.json: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to validate test data: {e}")
        return False


def run_sample_test():
    """Run a sample test to verify setup."""
    logger = logging.getLogger(__name__)
    
    # Determine the correct python path
    if os.name == 'nt':  # Windows
        python_path = Path('venv') / 'Scripts' / 'python.exe'
    else:  # Linux/Mac
        python_path = Path('venv') / 'bin' / 'python'
    
    if not python_path.exists():
        logger.error("Virtual environment not found")
        return False
    
    try:
        logger.info("Running sample test to verify setup...")
        result = subprocess.run([
            str(python_path), '-m', 'pytest', 
            '--collect-only', '-q'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Test discovery successful - setup verified!")
            return True
        else:
            logger.error(f"Test discovery failed: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to run sample test: {e}")
        return False


def print_usage_instructions():
    """Print usage instructions after successful setup."""
    logger = logging.getLogger(__name__)
    
    instructions = """
    
🎉 Setup completed successfully!

To get started:

1. Activate the virtual environment:
   Windows: venv\\Scripts\\activate
   Linux/Mac: source venv/bin/activate

2. Update configuration:
   - Edit .env file with your API credentials
   - Update data/test_data.json with your API endpoints

3. Run tests:
   - All tests: pytest
   - Smoke tests: pytest -m smoke
   - With HTML report: pytest --html=reports/pytest_report.html --self-contained-html

4. View reports:
   - Open reports/pytest_report.html in your browser

For more information, see README.md
    """
    
    print(instructions)
    logger.info("Setup instructions displayed")


def main():
    """Main setup function."""
    logger = setup_logging()
    logger.info("Starting E-commerce API Test Suite setup...")
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Creating virtual environment", create_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Creating .env file", create_env_file),
        ("Creating reports directory", create_reports_directory),
        ("Validating test data", validate_test_data),
        ("Running sample test", run_sample_test)
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        logger.info(f"Step: {step_name}")
        try:
            if not step_function():
                failed_steps.append(step_name)
                logger.error(f"Failed: {step_name}")
            else:
                logger.info(f"Completed: {step_name}")
        except Exception as e:
            logger.error(f"Error in {step_name}: {e}")
            failed_steps.append(step_name)
    
    if failed_steps:
        logger.error(f"Setup completed with errors. Failed steps: {', '.join(failed_steps)}")
        logger.error("Please check the setup.log file for details and resolve the issues.")
        sys.exit(1)
    else:
        logger.info("Setup completed successfully!")
        print_usage_instructions()


if __name__ == "__main__":
    main()

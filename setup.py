#!/usr/bin/env python3
"""
GENG 360 Course Setup Script
Automatically configures your development environment
"""

import subprocess
import sys
import importlib
import platform

# Configuration
REQUIRED_PYTHON_VERSION = (3, 8)
UPSTREAM_REPO = "https://github.com/ghoople/GENG360-Student-Template.git"

REQUIRED_PACKAGES = [
    "jupyterlab",
    "ipympl",
    "matplotlib",
    "numpy",
    "pandas",
    "seaborn",
    "scipy",
    "pyserial",
    "mplcursors",
    "sounddevice"
]

PACKAGE_IMPORT_NAMES = {
    "pyserial": "serial"
}

REQUIRED_EXTENSIONS = [
    ("ms-python.python", "Python"),
    ("ms-toolsai.jupyter", "Jupyter"),
    ("ms-toolsai.datawrangler", "Data Wrangler"),
    ("github.copilot", "GitHub Copilot"),
    ("github.copilot-chat", "GitHub Copilot Chat"),
    ("platformio.platformio-ide", "PlatformIO IDE"),
    ("ms-vscode.vscode-serial-monitor", "Serial Monitor")
]

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def run_command(command, capture_output=True):
    """Run a shell command and return success status and output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=capture_output,
            text=True,
            timeout=300
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python_version():
    """Check if Python version meets requirements"""
    print_header("Step 1: Checking Python Version")
    
    current_version = sys.version_info[:2]
    version_string = f"{current_version[0]}.{current_version[1]}"
    required_string = f"{REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]}"
    python_path = sys.executable
    
    # Check if using macOS system Python
    if platform.system() == "Darwin":
        if "/usr/bin/python" in python_path or "/System/Library" in python_path:
            print_error("⚠️  You're using macOS system Python - this won't work!")
            print_error(f"   Current location: {python_path}")
            print_error("")
            print_error("   Please install Python from python.org")
            print_error("   Then close VS Code, reopen it, and run:")
            print_error("   python3 setup.py")
            return False
    
    # Check version
    if current_version >= REQUIRED_PYTHON_VERSION:
        print_success(f"Python {version_string} detected (required: {required_string}+)")
        print(f"   Location: {python_path}")
        return True
    else:
        print_error(f"Python {version_string} detected, but {required_string}+ is required")
        print_error(f"   Location: {python_path}")
        if platform.system() == "Darwin":
            print_error("")
            print_error("   Install Python 3.8+ from python.org")
            print_error("   Then run: python3 setup.py")
        else:
            print_error("")
            print_error("   Install Python 3.8+ from python.org")
        return False

def setup_git_upstream():
    """Add upstream remote for template updates"""
    print_header("Step 2: Configuring Git Upstream Remote")
    
    # Check if we're in a git repository
    success, _, _ = run_command("git rev-parse --git-dir")
    if not success:
        print_error("Not in a git repository. Did you clone the template correctly?")
        return False
    
    # Check if upstream already exists
    success, output, _ = run_command("git remote")
    if "upstream" in output:
        print_warning("Upstream remote already exists. Skipping...")
        return True
    
    # Add upstream remote
    success, _, error = run_command(f"git remote add upstream {UPSTREAM_REPO}")
    if success:
        print_success(f"Upstream remote added: {UPSTREAM_REPO}")
        print(f"  → To get updates later, run: git pull upstream main --allow-unrelated-histories")
        return True
    else:
        print_error(f"Failed to add upstream remote: {error}")
        return False

def install_packages():
    """Install required Python packages"""
    print_header("Step 3: Installing Python Packages")
    print("This may take a few minutes...\n")
    
    pip_command = "pip3" if platform.system() == "Darwin" else "pip"
    packages_str = " ".join(REQUIRED_PACKAGES)
    
    print(f"Installing: {packages_str}\n")
    
    success, output, error = run_command(
        f"{pip_command} install --quiet {packages_str}",
        capture_output=False
    )
    
    if success:
        print_success("All packages installed successfully")
        return True
    else:
        print_error("Package installation encountered issues")
        print_error(f"Error: {error}")
        return False

def test_package_imports():
    """Test that all required packages can be imported"""
    print_header("Step 4: Testing Package Imports")
    
    failed_imports = []
    
    for package in REQUIRED_PACKAGES:
        import_name = PACKAGE_IMPORT_NAMES.get(package, package)
        try:
            importlib.import_module(import_name)
            print_success(f"{package} imported successfully")
        except ImportError as e:
            print_error(f"{package} failed to import: {e}")
            failed_imports.append(package)
    
    return len(failed_imports) == 0, failed_imports

def check_vscode_extensions():
    """Check if required VS Code extensions are installed"""
    print_header("Step 5: Checking VS Code Extensions")
    
    # Check if 'code' command exists
    success, _, _ = run_command("code --version")
    if not success:
        print_warning("Cannot detect 'code' command in PATH")
        print_warning("VS Code might not be installed, or the CLI tool isn't configured")
        print_warning("If you just installed VS Code:")
        print_warning("  - Windows: Restart your terminal")
        print_warning("  - Mac: Run 'Shell Command: Install code command in PATH' from VS Code")
        return False, []
    
    # Get installed extensions
    success, output, _ = run_command("code --list-extensions")
    if not success:
        print_warning("Could not list VS Code extensions")
        return False, []
    
    installed_extensions = output.lower().split('\n')
    missing_extensions = []
    
    for ext_id, ext_name in REQUIRED_EXTENSIONS:
        if ext_id.lower() in installed_extensions:
            print_success(f"{ext_name} ({ext_id})")
        else:
            print_error(f"{ext_name} ({ext_id}) - NOT INSTALLED")
            missing_extensions.append((ext_id, ext_name))
    
    return len(missing_extensions) == 0, missing_extensions

def print_summary(results):
    """Print final summary of setup status"""
    print_header("Setup Summary")
    
    all_passed = (
        results['python_version'] and
        results['git_upstream'] and
        results['packages_installed'] and
        results['imports_successful'] and
        results['vscode_check_possible'] and
        results['extensions_installed']
    )
    
    if all_passed:
        print_success("🎉 All checks passed! Your environment is ready.")
        print("\nYou're all set for GENG 360!")
    else:
        print_warning("⚠️  Some issues need attention:\n")
        
        if not results['python_version']:
            print_error("Python version issue - see Step 1 above for instructions")
        
        if not results['git_upstream']:
            print_error("Git upstream not configured - you won't be able to get template updates")
        
        if not results['packages_installed']:
            print_error("Some packages failed to install - see errors above")
        
        if not results['imports_successful']:
            print_error("Some packages can't be imported - see errors above")
            if results['failed_imports']:
                print(f"  Failed: {', '.join(results['failed_imports'])}")
        
        if not results['vscode_check_possible']:
            print_warning("Could not check VS Code extensions - please verify manually")
        elif not results['extensions_installed']:
            print_error("Missing VS Code extensions:")
            for ext_id, ext_name in results['missing_extensions']:
                print(f"  • {ext_name} ({ext_id})")
            print("\nTo install missing extensions:")
            print("  1. Open VS Code Extensions panel (Ctrl+Shift+X or Cmd+Shift+X)")
            print("  2. Search for each extension by name")
            print("  3. Click 'Install'")
        
        print(f"\n{Colors.YELLOW}Raise your hand - we'll troubleshoot together!{Colors.END}")

def main():
    print(f"{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          GENG 360 Environment Setup Script                 ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(Colors.END)
    
    results = {
        'python_version': False,
        'git_upstream': False,
        'packages_installed': False,
        'imports_successful': False,
        'failed_imports': [],
        'vscode_check_possible': False,
        'extensions_installed': False,
        'missing_extensions': []
    }
    
    # Run all checks
    results['python_version'] = check_python_version()
    results['git_upstream'] = setup_git_upstream()
    results['packages_installed'] = install_packages()
    results['imports_successful'], results['failed_imports'] = test_package_imports()
    results['vscode_check_possible'], results['missing_extensions'] = check_vscode_extensions()
    results['extensions_installed'] = len(results['missing_extensions']) == 0
    
    # Print summary
    print_summary(results)
    
    # Exit with appropriate code
    all_critical_passed = (
        results['python_version'] and
        results['git_upstream'] and
        results['packages_installed'] and
        results['imports_successful']
    )
    
    sys.exit(0 if all_critical_passed else 1)

if __name__ == "__main__":
    main()
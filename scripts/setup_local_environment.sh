#!/bin/bash
# Setup Local Grading Environment for CSC3301
# Run this once to prepare your grading infrastructure
#
# Usage: ./setup_local_environment.sh

set -e

echo "=============================================="
echo "CSC3301 Grading Environment Setup"
echo "=============================================="
echo ""

# Configuration
GRADING_HOME="${GRADING_HOME:-$HOME/course-grading}"
GITHUB_ORG="${GITHUB_ORG:-unza-cs-courses}"
JPLAG_VERSION="5.1.0"

echo "Grading home: $GRADING_HOME"
echo "GitHub org: $GITHUB_ORG"
echo ""

# 1. Create directory structure
echo "=== Step 1: Creating directory structure ==="
mkdir -p "$GRADING_HOME"/{scripts,submissions,hidden-tests,plagiarism-reports,grades,tools,config}
echo "Created directories under $GRADING_HOME"

# 2. Detect OS and install dependencies
echo ""
echo "=== Step 2: Installing system dependencies ==="

if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS"

    # Check for Homebrew
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi

    # Install dependencies
    brew install python@3.11 git gh openjdk@17 || true

    # Set up Java
    echo 'export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux"

    sudo apt update
    sudo apt install -y python3.11 python3.11-venv python3-pip git openjdk-17-jdk curl

    # Install GitHub CLI
    if ! command -v gh &> /dev/null; then
        curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
        sudo apt update && sudo apt install gh
    fi
fi

# 3. Create Python virtual environment
echo ""
echo "=== Step 3: Setting up Python environment ==="
cd "$GRADING_HOME"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Created virtual environment"
fi

source venv/bin/activate
pip install --upgrade pip
pip install pytest pytest-json-report pytest-asyncio pandas openpyxl gitpython requests

echo "Python packages installed"

# 4. GitHub CLI authentication
echo ""
echo "=== Step 4: GitHub CLI Setup ==="
if ! gh auth status &> /dev/null; then
    echo "Please authenticate with GitHub:"
    gh auth login
else
    echo "Already authenticated with GitHub"
fi

# Install GitHub Classroom extension
gh extension install github/gh-classroom 2>/dev/null || echo "Classroom extension already installed or not available"

# 5. Download JPlag
echo ""
echo "=== Step 5: Downloading JPlag ==="
JPLAG_PATH="$GRADING_HOME/tools/jplag.jar"

if [ ! -f "$JPLAG_PATH" ]; then
    echo "Downloading JPlag v$JPLAG_VERSION..."
    curl -L -o "$JPLAG_PATH" \
        "https://github.com/jplag/jplag/releases/download/v${JPLAG_VERSION}/jplag-${JPLAG_VERSION}-jar-with-dependencies.jar"
    echo "JPlag downloaded to $JPLAG_PATH"
else
    echo "JPlag already exists at $JPLAG_PATH"
fi

# 6. MOSS setup instructions
echo ""
echo "=== Step 6: MOSS Setup (Optional) ==="
cat > "$GRADING_HOME/tools/moss_setup.txt" << 'EOF'
To set up MOSS (Measure of Software Similarity):

1. Email moss@moss.stanford.edu with subject line "registeruser"
   (No body text needed)

2. You will receive an email with a Perl script (moss.pl)

3. Save the script to this directory:
   ~/course-grading/tools/moss.pl

4. Make it executable:
   chmod +x ~/course-grading/tools/moss.pl

5. Usage:
   ./moss.pl -l python -d submissions/*/src/*.py
EOF

echo "MOSS setup instructions saved to $GRADING_HOME/tools/moss_setup.txt"

# 7. Create configuration file
echo ""
echo "=== Step 7: Creating configuration ==="
cat > "$GRADING_HOME/config/grading_config.json" << EOF
{
    "grading_home": "$GRADING_HOME",
    "organization": "$GITHUB_ORG",
    "hidden_tests_repo": "$GRADING_HOME/hidden-tests",
    "submissions_dir": "$GRADING_HOME/submissions",
    "reports_dir": "$GRADING_HOME/plagiarism-reports",
    "grades_dir": "$GRADING_HOME/grades",
    "jplag_path": "$GRADING_HOME/tools/jplag.jar",
    "moss_path": "$GRADING_HOME/tools/moss.pl",
    "weights": {
        "visible_tests": 0.40,
        "hidden_tests": 0.30,
        "code_quality": 0.20,
        "plagiarism_penalty_max": 0.10
    },
    "plagiarism_thresholds": {
        "warning": 40,
        "penalty_start": 50,
        "severe": 80
    }
}
EOF

echo "Configuration saved to $GRADING_HOME/config/grading_config.json"

# 8. Create activation script
cat > "$GRADING_HOME/activate.sh" << EOF
#!/bin/bash
# Activate CSC3301 grading environment
export GRADING_HOME="$GRADING_HOME"
export JPLAG_JAR="$GRADING_HOME/tools/jplag.jar"
export PATH="$GRADING_HOME/scripts:\$PATH"
source "$GRADING_HOME/venv/bin/activate"
cd "$GRADING_HOME"
echo "CSC3301 grading environment activated"
echo "Grading home: \$GRADING_HOME"
EOF
chmod +x "$GRADING_HOME/activate.sh"

# 9. Summary
echo ""
echo "=============================================="
echo "SETUP COMPLETE"
echo "=============================================="
echo ""
echo "Directory structure:"
echo "  $GRADING_HOME/"
echo "  ├── config/           # Configuration files"
echo "  ├── grades/           # Generated grade CSVs"
echo "  ├── hidden-tests/     # Clone hidden tests repo here"
echo "  ├── plagiarism-reports/"
echo "  ├── scripts/          # Grading scripts"
echo "  ├── submissions/      # Cloned student repos"
echo "  ├── tools/            # JPlag, MOSS"
echo "  └── venv/             # Python virtual environment"
echo ""
echo "Next steps:"
echo ""
echo "1. Clone the hidden tests repository:"
echo "   git clone git@github.com:$GITHUB_ORG/csc3301-hidden-tests.git $GRADING_HOME/hidden-tests"
echo ""
echo "2. Copy grading scripts from course-admin:"
echo "   cp csc3301-course-admin/scripts/*.py $GRADING_HOME/scripts/"
echo "   cp csc3301-course-admin/scripts/*.sh $GRADING_HOME/scripts/"
echo ""
echo "3. Activate the environment:"
echo "   source $GRADING_HOME/activate.sh"
echo ""
echo "4. Run grading pipeline:"
echo "   python scripts/full_grading_pipeline.py --course csc3301 --assignment lab01-scope-binding"
echo ""

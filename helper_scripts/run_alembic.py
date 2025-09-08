#!/usr/bin/env python3
"""
Helper script to run Alembic commands with environment variables loaded from .env.local
"""
import os
import sys
import subprocess
from pathlib import Path


def load_env_file(env_file=".env"):
    """Load environment variables from .env file"""
    env_path = Path(env_file)
    if not env_path.exists():
        print(f"Error: {env_file} not found")
        sys.exit(1)

    print(f"Loading environment variables from {env_file}")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            key, value = line.split("=", 1)
            # Strip quotes if present
            value = value.strip().strip('"').strip("'")
            os.environ[key] = value

    print(f"Loaded environment variables: {list(os.environ.keys())}")


def main():
    """Main function to run Alembic commands"""
    # Load environment variables
    load_env_file()

    # Get Alembic command from command line arguments
    alembic_args = sys.argv[1:] if len(sys.argv) > 1 else ["--help"]
    cmd = ["alembic"] + alembic_args

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()

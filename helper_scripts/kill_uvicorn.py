#!/usr/bin/env python3
"""
Script to find and kill all running uvicorn processes.
This is useful for cleaning up development servers that might be running in the background.
"""

import subprocess
import sys
import re
from typing import List, Dict, Tuple


def find_uvicorn_processes() -> List[Dict[str, str]]:
    """
    Find all running uvicorn processes using the ps command.

    Returns:
        List of dictionaries containing process information (pid, command, port)
    """
    try:
        # Run ps command to get all processes
        result = subprocess.run(["ps", "-ef"], capture_output=True, text=True, check=True)

        # Process the output
        processes = []
        for line in result.stdout.splitlines():
            if "uvicorn" in line and "python" in line:
                # Extract PID and command
                parts = line.split()
                if len(parts) < 8:
                    continue

                pid = parts[1]
                command = " ".join(parts[7:])

                # Try to extract port
                port_match = re.search(r"--port[= ](\d+)", command)
                port = port_match.group(1) if port_match else "unknown"

                processes.append({"pid": pid, "command": command, "port": port})

        return processes

    except subprocess.SubprocessError as e:
        print(f"Error finding uvicorn processes: {e}", file=sys.stderr)
        return []


def kill_processes(processes: List[Dict[str, str]], force: bool = False) -> Tuple[int, int]:
    """
    Kill the specified processes.

    Args:
        processes: List of process dictionaries with pid, command, port
        force: Whether to use SIGKILL (-9) instead of SIGTERM

    Returns:
        Tuple of (success_count, failure_count)
    """
    success_count = 0
    failure_count = 0

    for process in processes:
        pid = process["pid"]
        signal = "-9" if force else "-15"  # SIGKILL vs SIGTERM

        try:
            subprocess.run(["kill", signal, pid], check=True)
            print(f"Successfully killed process {pid} (port {process['port']})")
            success_count += 1
        except subprocess.SubprocessError as e:
            print(f"Failed to kill process {pid}: {e}", file=sys.stderr)
            failure_count += 1

    return success_count, failure_count


def main():
    """Main function to find and kill uvicorn processes."""
    # Find uvicorn processes
    processes = find_uvicorn_processes()

    if not processes:
        print("No uvicorn processes found.")
        return

    # Display found processes
    print(f"Found {len(processes)} uvicorn processes:")
    for i, process in enumerate(processes, 1):
        print(f"{i}. PID: {process['pid']}, Port: {process['port']}")
        print(f"   Command: {process['command']}")

    # Ask for confirmation
    try:
        response = input("\nDo you want to kill these processes? (y/n/f for force kill): ").lower()

        if response == "y":
            success, failure = kill_processes(processes)
            print(f"\nKilled {success} processes. Failed to kill {failure} processes.")
        elif response == "f":
            success, failure = kill_processes(processes, force=True)
            print(f"\nForce killed {success} processes. Failed to kill {failure} processes.")
        else:
            print("Operation cancelled.")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")


if __name__ == "__main__":
    main()

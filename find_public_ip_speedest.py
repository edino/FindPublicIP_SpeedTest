# Copyright
# Original author: Edino De Souza
# Repository: https://github.com/edino/SpeedTest-Interface
# License: GPL-3.0 license - https://github.com/edino/SpeedTest-Interface/blob/main/LICENSE
# Script Summary: This script simplifies network speed testing, fetching the public IP, determining the interface, and running 'speedtest-cli'. Users customize output visibility, and specify the directory, and results are saved with interface details and a timestamp.
# Purpose: To offer a user-friendly interface for network speed testing, making it accessible and customizable. Users input preferences and the script automates the speed test, providing both display and file output.
# Build Date: 1:29 AM EST 2024-01-14

# Execute with: curl -s https://raw.githubusercontent.com/edino/SpeedTest-Interface/main/speedtest_interface.py | python3 -
# Another option: curl -sLo /tmp/speedtest_interface.py https://raw.githubusercontent.com/edino/SpeedTest-Interface/main/speedtest_interface.py && python3 /tmp/speedtest_interface.py

import subprocess
import datetime
import logging

def log_info(message, display=True):
    if display:
        print(message)
    logging.info(message)

def log_error(message, display=True):
    if display:
        print(f"Error: {message}")
    logging.error(message)

def get_user_input(prompt):
    try:
        return input(prompt)
    except EOFError:
        return None
    except KeyboardInterrupt:
        return None

def get_public_ip():
    try:
        result = subprocess.run(['curl', '-s', 'ifconfig.me/all'], stdout=subprocess.PIPE, text=True, check=True)
        ip_addr_line = [line for line in result.stdout.split('\n') if 'ip_addr:' in line][0]
        public_ip = ip_addr_line.split()[1]
        return public_ip
    except subprocess.CalledProcessError as e:
        log_error(f"Error getting public IP: {e.stderr}")
        return None

def get_interface_for_ip(public_ip):
    try:
        result = subprocess.run(['ip', 'route', 'get', public_ip], stdout=subprocess.PIPE, text=True, check=True)
        interface = result.stdout.split('dev')[1].split()[0]
        return interface
    except subprocess.CalledProcessError as e:
        log_error(f"Error getting interface for IP: {e.stderr}")
        return None

def run_speedtest(interface, output_directory, show_output=True):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    public_ip = get_public_ip()

    if not public_ip:
        log_error("Unable to fetch the public IP. Exiting.", show_output)
        return

    log_info(f"\nYour Public IP address is: {public_ip}\n", show_output)

    log_info("Finding the interface for the Public IP...\n", show_output)

    bound_interface = get_interface_for_ip(public_ip)

    if not bound_interface:
        log_error(f"Unable to determine the network interface for {public_ip}. Exiting.", show_output)
        return

    log_info(f"The network interface bound to {public_ip} is: {bound_interface}\n", show_output)

    output_directory = get_user_input("\nEnter the directory to save the output file (press Enter for /var/): ") or "/var/"

    output_filename = f"{bound_interface}_{public_ip}_{timestamp}.speedtestcap"
    output_path = f"{output_directory.rstrip('/')}/{output_filename}"

    log_info("\nRunning speed test...\n", show_output)

    speedtest_command = [
        'curl', '-s', f'--interface {bound_interface}', 'https://raw.githubusercontent.com/edino/speedtest-cli/master/speedtest.py',
        '|', 'python3', '-', '--share'
    ]

    try:
        speedtest_output = subprocess.check_output(' '.join(speedtest_command), shell=True, executable='/bin/bash', text=True)
        if show_output:
            print(speedtest_output)
        with open(output_path, 'a') as output_file:
            output_file.write(speedtest_output)
        log_info(f"\nSpeed test results saved to: {output_path}\n", show_output)
    except subprocess.CalledProcessError as e:
        log_error(f"Error running speed test: {e.stderr}", show_output)

def main():
    logging.basicConfig(filename='speedtest_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    show_output = get_user_input("\nDo you want to see the output while the script is running? (y/n): ").lower() == 'y'

    log_info("\nFetching public IP address...\n", show_output)

    run_speedtest("eth0", "/var/", show_output)  # Replace "eth0" with the default interface

if __name__ == "__main__":
    main()

# Shodan API Host Information Script

This script uses the Shodan API to retrieve information about a specific IP address and uses all the end points within shodan api which is of free access.

## Requirements

You will need:
- Python 3.x installed
- A Shodan API key (sign up at https://account.shodan.io/register if you don't have one)

## Installation

1. Clone or download this repository to your local machine.

2. Install required dependencies by running:

3. pip install -r requirements.txt


## Usage

1. Replace the `YOUR_API_KEY_HERE` in the script with your actual Shodan API key.

2. Run the script from the terminal:

      python3 shodan_host_lookup.py


3. The script will fetch and display details about the given IP address.

## Example Output
Example output for IP `8.8.8.8` might look like:

IP: 8.8.8.8
Organization: Google LLC
Operating System: None
Ports: 53


## Notes
- Make sure you have an active internet connection while running the script.
- The free Shodan API plan has usage limits — check your account for details.

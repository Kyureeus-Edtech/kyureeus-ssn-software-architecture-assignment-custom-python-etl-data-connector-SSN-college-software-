# Blocklist.de ETL Connector

This ETL script fetches threat intelligence data from blocklist.de using public, no-auth endpoints (IP lookup, export lists, and DNS/RBL check).

## Quick README — How to run & test (step-by-step)

### Clone repo & branch

```bash
git clone https://github.com/Kyureeus-Edtech/custom-python-etl-data-connector-saaaathvik.git
cd custom-python-etl-data-connector-saaaathvik
git checkout -b 3122225001115_CSE_C_ETLConnector
```

### Create venv & install deps

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run IP mode

```bash
python etl_blocklist.py --mode ip --items 1.1.1.1 8.8.8.8
```

This calls `http://api.blocklist.de/api.php?ip=<ip>&format=json`.

### Run list mode (download export lists)

```bash
python etl_blocklist.py --mode list --items ssh mail apache
```

This downloads `https://lists.blocklist.de/lists/ssh.txt` etc.

### Run RBL/DNS mode

```bash
python etl_blocklist.py --mode rbl --items 1.2.3.4
```

This performs DNS queries against `<reversed-ip>.bl.blocklist.de`.

### Dry-run (no writes to DB)

```bash
python etl_blocklist.py --mode list --items ssh --dry-run
```

### Run all modes with defaults

```bash
python etl_blocklist.py --run-all
```

### Commit & push

```bash
git add etl_blocklist.py requirements.txt README.md .gitignore
git commit -m "Assignment 2 - Saathvik - 115"
git push origin 3122225001115_CSE_C_ETLConnector
# then open a PR
```

## Output Screenshots

![IP Mode Output](./4.png)
![List Mode Output](./5.png)
![RBL Mode Output](./6.png)

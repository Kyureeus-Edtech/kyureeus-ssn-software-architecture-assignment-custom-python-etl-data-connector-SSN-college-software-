# Cloudflare & HTTPBin ETL Connector

**Author:** Harinishree Kumar  
**Roll No:** 3122225001035

---

## Overview

This ETL connector is a Python-based pipeline that extracts data from **Cloudflare** and **HTTPBin** public APIs, transforms it for MongoDB compatibility, and loads it into a MongoDB collection.

The pipeline follows best practices for secure coding, error handling, and audit logging.

---

## Project Structure

/your-branch-name/
│
├── etl_connector.py # Main ETL script
├── .env # Environment variables (MongoDB URI) - IGNORE in git
├── requirements.txt # Python dependencies
└── README.md # Documentation

## Environment Variables (.env)

Create a `.env` file in the project folder to store sensitive credentials:

> **Important:** Do not commit `.env` to Git. Add it to `.gitignore`.

---

## API Endpoints Used

| Module Name         | Endpoint URL                             | Description                                        |
| ------------------- | ---------------------------------------- | -------------------------------------------------- |
| trace_info          | /cdn-cgi/trace (Cloudflare)              | Cloudflare trace diagnostic info                   |
| ip_info             | https://www.cloudflare.com/cdn-cgi/trace | Retrieves public IP from Cloudflare                |
| httpbin_info        | https://httpbin.org/get                  | Public testing API showing IP & user-agent info    |
| dns_resolve_example | https://cloudflare-dns.com/dns-query     | Cloudflare DNS-over-HTTPS resolver for example.com |

---

## Setup Instructions

1. **Clone the repository** and checkout your branch:

```bash
git clone <repo_url>
cd <repo_folder>
git checkout <your_branch_name>


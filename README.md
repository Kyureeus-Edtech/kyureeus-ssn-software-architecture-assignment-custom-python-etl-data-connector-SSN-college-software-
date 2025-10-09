# SSN-college-software-architecture-Assignments
Assignment repository for building custom Python ETL data connectors (Kyureeus EdTech, SSN CSE). Students: Submit your ETL scripts here. Make sure your commit message includes your name and roll number.

# Software Architecture Assignment: Custom Python ETL Data Connector (IP Geolocation Connector)

Welcome to the official repository for submitting your Software Architecture assignment on building custom ETL data connectors in Python. This project demonstrates a Python connector for fetching geolocation data from the [ip-api.com](http://ip-api.com/) API and storing it in MongoDB.  

This assignment is part of the Kyureeus EdTech program for SSN CSE students.

---

## 📋 Assignment Overview

**Goal:**  
Develop a Python ETL pipeline that connects with the IP Geolocation API, extracts data, transforms it for MongoDB compatibility, and loads it into a MongoDB collection. Follow secure coding and project structure practices.

---

## 🔹 Project Highlights

- Connects to [ip-api.com](http://ip-api.com/) to fetch geolocation data for IP addresses or domain names.  
- Supports JSON response format for easy MongoDB storage.  
- Stores API responses in MongoDB with timestamps.  
- Secure credentials management using `.env` (for MongoDB URI, database, and collection).  
- Easily extendable to handle multiple queries or separate collections per IP/domain.  

---

## ✅ Submission Checklist

- [ ] Understand the IP Geolocation API documentation  
- [ ] Secure MongoDB credentials using `.env`  
- [ ] Build a complete ETL pipeline: Extract → Transform → Load  
- [ ] Test and validate your pipeline (handle invalid responses, empty payloads, rate limits, etc.)  
- [ ] Follow the project folder structure  
- [ ] Write a descriptive `README.md` in your folder with API details, usage instructions, and example output  
- [ ] Include your name and roll number in commit messages  
- [ ] Push code to your branch and submit a Pull Request  


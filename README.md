README.md – RIPEstat ETL Pipeline (Assignment 2)

 Project Overview
 ----------------

This project implements an ETL (Extract, Transform, Load) pipeline using data from the RIPEstat API.
It connects to three different endpoints of a single data source (RIPEstat), processes the data, and loads it into MongoDB for storage and analysis.

This fulfills the  Assignment 2 requirement of:

Using a minimum of three endpoints

Performing transformations

Loading data into a database

🚀 ETL Workflow
-----------------

Extract
--------
Data is fetched from three RIPEstat API endpoints:

/as-overview — Provides general AS information

/as-routing-consistency — Gives routing status details

/asns-neighbours — Shows network neighbor ASNs

Transform
-----------
The raw data is cleaned and restructured into a unified JSON format:

Adds timestamps

Filters key details

Handles missing or invalid responses

Load
-----
The transformed data is inserted into a MongoDB collection (ripe_data) using PyMongo.

⚙️ Tech Stack
-------------
Component	Technology
Language	Python 3
Database	MongoDB (via MongoDB Compass / local instance)
Libraries	requests, pymongo, datetime
Data Source	RIPEstat API (https://stat.ripe.net/)

📁 Project Structure
---------------------

ripe_connector/
│
├── etl_connector.py       # Main ETL pipeline script
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation



MongoDB:
---------

{
  "_id": {
    "$oid": "68f36b044716d37002e551d1"
  },
  "endpoint": "as-overview",
  "timestamp": {
    "$date": "2025-10-18T10:25:08.634Z"
  },
  "data_call_name": "as-overview",
  "data": {
    "type": "as",
    "resource": "3333",
    "block": {
      "resource": "3154-3353",
      "desc": "Assigned by RIPE NCC",
      "name": "IANA 16-bit Autonomous System (AS) Numbers Registry"
    },
    "holder": "RIPE-NCC-AS - Reseaux IP Europeens Network Coordination Centre (RIPE NCC)",
    "announced": true,
    "query_starttime": "2025-10-18T00:00:00",
    "query_endtime": "2025-10-18T00:00:00"
  },
  "metadata": {}
}


{
  "_id": {
    "$oid": "68f36b054716d37002e551d2"
  },
  "endpoint": "as-routing-consistency",
  "timestamp": {
    "$date": "2025-10-18T10:25:09.535Z"
  },
  "data_call_name": "as-routing-consistency",
  "data": {
    "prefixes": [
      {
        "in_bgp": true,
        "in_whois": true,
        "irr_sources": [
          "RIPE"
        ],
        "prefix": "193.0.0.0/21"
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "irr_sources": [
          "RIPE"
        ],
        "prefix": "193.0.10.0/23"
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "irr_sources": [
          "RIPE"
        ],
        "prefix": "193.0.12.0/23"
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "irr_sources": [
          "RIPE"
        ],
        "prefix": "193.0.18.0/23"
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "irr_sources": [
          "RIPE"
        ],
        "prefix": "193.0.20.0/23"
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "irr_sources": [
          "RIPE"
        ],
        "prefix": "193.0.22.0/23"
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "irr_sources": [
          "RIPE"
        ],
        "prefix": "2001:67c:2e8::/48"
      }
    ],
    "imports": [
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 1299
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 1103
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 1136
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 1257
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 1273
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 12859
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 286
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 3257
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 3320
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 6762
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 6939
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 12310
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 12989
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 13237
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 20562
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 21219
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 23393
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 2603
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 3209
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 3267
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 3292
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 3303
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 34224
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 39792
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 41095
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 50384
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 5400
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 5580
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 6774
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 6830
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 702
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 8220
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 8359
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 9002
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 112
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 1126
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 1140
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 1200
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 12306
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 12399
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 12414
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 12496
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 12759
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 12779
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 12871
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 12902
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 13101
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 13127
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 15133
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 15426
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 15435
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 15542
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 16243
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 16265
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 16276
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 16298
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 16509
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 1836
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 197000
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 20495
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 20640
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 20847
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 20886
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 20932
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 20940
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 20953
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 2119
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 21221
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 21478
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 22822
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 24167
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 24586
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 24642
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 24875
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 24940
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 25074
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 25148
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 25151
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 25152
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 25542
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 2611
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 2686
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 28788
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 29119
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 29208
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 29263
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 29396
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 29438
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 30132
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 30740
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 30889
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 30925
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 31042
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 31216
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 31477
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 3262
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 3265
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 34288
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 34305
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 35574
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 3856
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 39120
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 41692
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 42184
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 42525
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 43821
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 4589
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 49405
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 49544
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 5390
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 5413
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 5524
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 5568
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 5583
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 5615
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 6667
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 6724
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 6730
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 6805
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 7342
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 8365
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 8426
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 8447
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 8560
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 8608
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 8918
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 9143
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 9150
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 12322
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 15169
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 2828
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 2914
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 31383
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 8657
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 64597
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 12654
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 6447
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 65517
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 6777
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 36864
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57344
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 38915
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20485
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 204805
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12297
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 30736
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47121
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 32787
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20504
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8218
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 55329
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 40999
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12329
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47147
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 26667
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45102
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 28725
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49206
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47160
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 213050
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6204
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 213052
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6206
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 208959
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20546
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12355
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47172
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 10310
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 38983
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8262
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 208972
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 139341
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200781
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20559
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 208976
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 211024
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41041
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51276
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47195
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8283
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 211037
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 213092
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202855
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8298
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198763
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8302
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34927
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12400
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 204911
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8304
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8309
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57463
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8315
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 30844
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 209022
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34942
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 36994
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41090
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 61573
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 4230
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198792
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34953
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51333
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 262287
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 196752
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 24724
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 30870
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39063
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12440
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34968
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 24730
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59545
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 61599
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59554
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 32934
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20647
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47272
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 22697
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51375
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8368
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 24753
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39090
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59570
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202932
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 43190
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35000
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202941
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 137409
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 209090
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 204995
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 14537
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202954
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8399
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 215248
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 24785
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39122
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8400
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 207063
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 135391
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8422
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59624
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 37100
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 196844
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 28917
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 18678
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 213241
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 250
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59642
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 16637
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 215296
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 14593
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8452
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12552
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39180
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51468
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8462
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198930
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 30999
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6424
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8473
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57626
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20764
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 209181
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20766
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 213279
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12578
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 293
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 14630
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8487
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45352
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31019
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49453
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59692
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 205103
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51505
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31027
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198967
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49463
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 196922
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51514
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59711
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20804
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 207176
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29001
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8529
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 211286
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 43350
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 196954
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12637
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 203101
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41313
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29028
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 43366
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 4455
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35179
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 139628
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41327
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31084
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6507
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 211316
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 203126
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45430
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29049
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 213373
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45437
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 24961
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 196997
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 55685
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29063
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8587
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 213392
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29075
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 215444
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12693
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 205206
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12695
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35224
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 43414
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31133
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57758
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12703
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 201119
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 37282
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45474
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12713
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 328112
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45489
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 207283
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 2484
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59827
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39351
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199095
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59832
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 63927
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12731
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8632
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41405
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8637
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49600
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49605
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12741
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35280
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29140
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29141
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59865
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39386
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49627
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 270814
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35297
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8674
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20969
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 133613
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 23028
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49653
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 14840
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35320
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 4601
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 43519
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49666
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 25091
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 61955
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6661
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6663
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41480
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 55818
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199181
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 207375
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 205329
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 21013
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49685
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6677
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 215577
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6681
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8732
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 4637
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 197156
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 213543
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6696
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51752
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 55850
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 4651
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 25133
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 43566
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51758
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 559
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 64049
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 4657
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62005
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8758
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41529
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 14907
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8763
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8764
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 215615
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 21056
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 23106
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8767
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 25160
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 213576
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 201290
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 2635
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12876
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 33353
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47689
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59985
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31319
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12888
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62041
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 37468
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35421
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 25182
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62044
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12897
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39521
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8801
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39526
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35432
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 21100
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57965
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8821
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60022
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 209528
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 43641
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57976
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6775
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 139901
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 207487
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29314
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 25220
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 211588
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 215685
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45701
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49800
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8839
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62097
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60051
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 4761
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62105
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8859
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 201372
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49820
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60064
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51873
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8866
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199332
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 211623
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 4775
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12969
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6823
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 215724
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 328366
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8881
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 4788
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 197301
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 201401
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45758
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31424
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12993
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41666
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 4800
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13000
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13002
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 43727
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60111
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39637
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62167
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31449
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39642
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 58075
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47836
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8926
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 21215
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39647
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 203489
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8932
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 207594
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199408
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 209650
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 211713
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39686
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60167
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51978
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 11019
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31500
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35598
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 21263
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39702
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39704
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 25369
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 58138
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29467
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31515
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 201502
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 37662
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62240
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 64289
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 2852
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 264997
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 2854
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31529
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199471
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 23344
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9008
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9009
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39737
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 52025
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199483
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49981
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 213822
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 197440
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13122
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29505
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9031
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45899
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13132
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9036
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9123
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 215887
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45903
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9044
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 25428
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47957
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 37721
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 2906
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9050
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41820
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13150
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 54113
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199524
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 205668
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47973
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 209768
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 52075
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 25455
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 211826
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 131958
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 205689
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50050
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 58243
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 54148
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60294
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 7049
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13194
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35729
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 271253
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31638
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 917
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39832
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50072
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9115
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13213
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 209823
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39839
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 21409
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41887
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50083
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 58272
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9119
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 43942
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60326
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9120
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35753
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 136106
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 11179
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 211882
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 207790
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35758
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9136
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 201650
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 58291
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62390
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31673
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199610
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 58299
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 205755
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 207803
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41913
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60350
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29632
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13249
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9145
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 209859
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39878
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9158
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 203724
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35793
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 64475
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29670
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41960
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13289
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39923
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60404
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 207866
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 201723
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 25595
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44034
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 216071
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41998
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13335
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 23576
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 216092
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 216107
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13360
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31800
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48185
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 197692
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 214076
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56381
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 201791
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56382
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60476
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50245
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60486
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199752
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48200
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56396
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 1101
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 138322
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9299
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 17494
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15447
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50263
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9304
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50266
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 205915
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 11358
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 19551
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 52320
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 197727
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50272
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 33891
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44134
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15466
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 132203
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29802
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42093
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 394354
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 210036
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 205943
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50295
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60539
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50300
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 214145
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 33921
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 398465
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13445
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50309
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56457
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 201866
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 3212
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50316
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 3214
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 58511
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 3216
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50324
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 201877
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 3223
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 38040
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31898
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15516
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 203932
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 197790
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48284
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 208034
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 46244
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50340
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9381
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42156
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48314
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15547
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 216251
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 33986
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 38082
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 23764
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15576
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 1241
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 25818
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48345
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9434
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50399
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 1248
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34019
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 17639
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 210152
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48362
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50414
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 132337
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 1267
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15605
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48374
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62713
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62715
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 3326
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 19711
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 214271
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 3327
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199938
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199939
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 212232
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 197899
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 38158
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48399
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 5394
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 214294
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9498
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 204059
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 5404
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 5405
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 32035
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202022
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34087
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 38182
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 5416
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50474
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 5418
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 38193
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56630
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42295
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199995
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 204092
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202053
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 7500
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15693
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15694
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56655
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15695
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56654
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200020
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 36182
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15703
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200023
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 38230
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50522
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 5466
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56665
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 197981
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 58715
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 7522
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 21859
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56675
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50533
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 28008
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 30058
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 214380
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9583
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200052
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 204151
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198011
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198016
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 30081
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34177
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56704
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 7552
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9605
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 3462
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 216455
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 216456
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48519
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48522
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 23947
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 36236
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62856
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42385
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50581
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60822
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 30103
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 46489
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198046
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62902
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 206264
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15802
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200132
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50629
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198089
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 206281
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 40401
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 206292
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48596
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15830
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 5606
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62955
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202224
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50673
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200184
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48635
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 212477
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 36351
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 7679
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 212483
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200197
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198150
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 1547
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42517
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15895
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 7713
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 54825
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42541
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44592
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50737
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200242
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 208434
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44600
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200249
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44608
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34373
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15943
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42567
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50763
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44620
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 30286
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56911
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 5713
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 18001
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198225
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 61013
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15958
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15966
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15967
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 206446
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 61049
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 28283
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34428
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 63113
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 1680
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42649
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56987
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 212635
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13984
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 138915
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 204457
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50858
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9902
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202418
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 40627
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200372
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200373
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202425
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 18106
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202427
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 206521
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 396986
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 11967
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44735
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57029
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50889
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 3786
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 136907
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9930
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198352
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 54994
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42707
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57043
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48858
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 212703
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 1764
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 214757
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 210667
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50923
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 14061
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44788
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48886
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 46844
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42755
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 132876
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 61200
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48919
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57112
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 214809
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 1820
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200478
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48927
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57118
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 1828
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57124
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 14127
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 212793
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44858
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 210752
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57154
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48972
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 32590
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 3920
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57169
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 22356
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 36692
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202585
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 16218
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42841
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202591
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 26464
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34655
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44901
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20326
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8038
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51050
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 24429
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42861
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 10099
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 212855
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 38778
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34696
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 10122
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 206735
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51088
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200596
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44949
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12189
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 212895
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 24482
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 61349
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 63399
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 208808
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6057
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 208814
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 55219
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42947
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34756
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34758
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 210890
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 208844
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 210897
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51154
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45014
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 55256
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47065
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34779
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 206813
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 137182
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 16350
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 38880
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49121
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 2018
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 215011
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49127
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51184
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51185
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 206836
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 55285
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20473
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198651
      }
    ],
    "exports": [
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 1299
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 1103
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 1136
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 1257
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 1273
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 12859
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 286
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 3257
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 3320
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 6762
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 6939
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 12310
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 12989
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 13237
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 20562
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 21219
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 23393
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 2603
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 3209
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 3267
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 3292
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 3303
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 34224
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 39792
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 41095
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 50384
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 5400
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 5580
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 6774
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 6830
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 702
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 8220
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 8359
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 9002
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 112
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 1126
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 1140
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 1200
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 12306
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 12399
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 12414
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 12496
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 12759
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 12779
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 12871
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 12902
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 13101
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 13127
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 15133
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 15426
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 15435
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 15542
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 16243
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 16265
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 16276
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 16298
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 16509
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 1836
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 197000
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 20495
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 20640
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 20847
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 20886
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 20932
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 20940
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 20953
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 2119
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 21221
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 21478
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 22822
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 24167
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 24586
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 24642
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 24875
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 24940
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 25074
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 25148
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 25151
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 25152
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 25542
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 2611
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 2686
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 28788
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 29119
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 29208
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 29263
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 29396
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 29438
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 30132
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 30740
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 30889
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 30925
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 31042
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 31216
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 31477
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 3262
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 3265
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 34288
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 34305
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 35574
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 3856
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 39120
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 41692
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 42184
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 42525
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 43821
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 4589
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 49405
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 49544
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 5390
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 5413
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 5524
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 5568
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 5583
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 5615
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 6667
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 6724
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 6730
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 6805
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 7342
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 8365
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 8426
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 8447
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 8560
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 8608
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 8918
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 9143
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 9150
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 12322
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 15169
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 2828
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 2914
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 31383
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 8657
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 64597
      },
      {
        "in_bgp": true,
        "in_whois": true,
        "peer": 12654
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 6447
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 65517
      },
      {
        "in_bgp": false,
        "in_whois": true,
        "peer": 6777
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 36864
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57344
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 38915
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20485
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 204805
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12297
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 30736
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47121
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 32787
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20504
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8218
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 55329
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 40999
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12329
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47147
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 26667
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45102
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 28725
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49206
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47160
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 213050
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6204
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 213052
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6206
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 208959
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20546
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12355
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47172
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 10310
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 38983
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8262
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 208972
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 139341
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200781
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20559
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 208976
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 211024
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41041
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51276
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47195
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8283
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 211037
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 213092
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202855
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8298
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198763
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8302
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34927
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12400
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 204911
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8304
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8309
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57463
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8315
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 30844
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 209022
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34942
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 36994
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41090
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 61573
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 4230
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198792
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34953
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51333
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 262287
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 196752
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 24724
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 30870
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39063
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12440
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34968
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 24730
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59545
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 61599
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59554
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 32934
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20647
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47272
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 22697
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51375
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8368
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 24753
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39090
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59570
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202932
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 43190
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35000
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202941
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 137409
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 209090
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 204995
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 14537
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202954
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8399
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 215248
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 24785
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39122
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8400
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 207063
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 135391
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8422
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59624
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 37100
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 196844
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 28917
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 18678
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 213241
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 250
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59642
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 16637
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 215296
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 14593
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8452
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12552
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39180
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51468
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8462
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198930
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 30999
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6424
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8473
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57626
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20764
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 209181
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20766
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 213279
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12578
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 293
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 14630
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8487
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45352
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31019
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49453
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59692
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 205103
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51505
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31027
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198967
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49463
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 196922
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51514
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59711
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20804
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 207176
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29001
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8529
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 211286
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 43350
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 196954
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12637
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 203101
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41313
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29028
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 43366
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 4455
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35179
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 139628
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41327
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31084
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6507
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 211316
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 203126
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45430
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29049
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 213373
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45437
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 24961
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 196997
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 55685
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29063
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8587
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 213392
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29075
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 215444
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12693
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 205206
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12695
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35224
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 43414
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31133
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57758
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12703
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 201119
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 37282
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45474
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12713
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 328112
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45489
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 207283
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 2484
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59827
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39351
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199095
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59832
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 63927
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12731
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8632
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41405
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8637
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49600
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49605
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12741
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35280
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29140
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29141
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59865
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39386
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49627
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 270814
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35297
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8674
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20969
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 133613
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 23028
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49653
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 14840
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35320
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 4601
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 43519
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49666
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 25091
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 61955
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6661
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6663
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41480
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 55818
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199181
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 207375
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 205329
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 21013
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49685
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6677
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 215577
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6681
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8732
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 4637
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 197156
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 213543
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6696
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51752
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 55850
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 4651
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 25133
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 43566
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51758
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 559
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 64049
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 4657
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62005
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8758
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41529
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 14907
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8763
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8764
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 215615
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 21056
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 23106
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8767
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 25160
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 213576
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 201290
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 2635
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12876
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 33353
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47689
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 59985
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31319
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12888
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62041
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 37468
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35421
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 25182
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62044
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12897
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39521
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8801
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39526
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35432
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 21100
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57965
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8821
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60022
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 209528
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 43641
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57976
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6775
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 139901
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 207487
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29314
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 25220
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 211588
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 215685
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45701
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49800
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8839
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62097
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60051
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 4761
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62105
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8859
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 201372
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49820
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60064
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51873
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8866
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199332
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 211623
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 4775
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12969
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6823
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 215724
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 328366
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8881
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 4788
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 197301
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 201401
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45758
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31424
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12993
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41666
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 4800
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13000
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13002
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 43727
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60111
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39637
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62167
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31449
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39642
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 58075
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47836
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8926
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 21215
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39647
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 203489
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8932
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 207594
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199408
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 209650
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 211713
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39686
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60167
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51978
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 11019
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31500
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35598
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 21263
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39702
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39704
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 25369
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 58138
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29467
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31515
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 201502
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 37662
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62240
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 64289
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 2852
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 264997
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 2854
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31529
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199471
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 23344
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9008
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9009
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39737
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 52025
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199483
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49981
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 213822
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 197440
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13122
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29505
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9031
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45899
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13132
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9036
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9123
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 215887
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45903
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9044
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 25428
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47957
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 37721
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 2906
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9050
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41820
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13150
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 54113
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199524
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 205668
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47973
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 209768
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 52075
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 25455
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 211826
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 131958
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 205689
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50050
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 58243
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 54148
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60294
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 7049
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13194
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35729
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 271253
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31638
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 917
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39832
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50072
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9115
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13213
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 209823
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39839
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 21409
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41887
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50083
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 58272
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9119
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 43942
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60326
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9120
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35753
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 136106
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 11179
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 211882
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 207790
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35758
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9136
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 201650
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 58291
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62390
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31673
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199610
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 58299
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 205755
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 207803
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41913
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60350
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29632
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13249
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9145
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 209859
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39878
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9158
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 203724
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 35793
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 64475
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29670
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41960
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13289
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 39923
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60404
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 207866
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 201723
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 25595
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44034
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 216071
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 41998
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13335
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 23576
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 216092
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 216107
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13360
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31800
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48185
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 197692
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 214076
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56381
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 201791
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56382
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60476
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50245
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60486
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199752
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48200
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56396
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 1101
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 138322
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9299
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 17494
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15447
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50263
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9304
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50266
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 205915
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 11358
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 19551
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 52320
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 197727
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50272
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 33891
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44134
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15466
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 132203
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 29802
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42093
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 394354
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 210036
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 205943
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50295
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60539
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50300
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 214145
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 33921
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 398465
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13445
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50309
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56457
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 201866
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 3212
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50316
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 3214
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 58511
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 3216
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50324
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 201877
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 3223
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 38040
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 31898
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15516
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 203932
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 197790
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48284
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 208034
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 46244
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50340
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9381
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42156
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48314
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15547
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 216251
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 33986
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 38082
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 23764
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15576
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 1241
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 25818
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48345
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9434
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50399
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 1248
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34019
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 17639
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 210152
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48362
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50414
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 132337
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 1267
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15605
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48374
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62713
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62715
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 3326
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 19711
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 214271
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 3327
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199938
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199939
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 212232
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 197899
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 38158
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48399
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 5394
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 214294
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9498
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 204059
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 5404
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 5405
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 32035
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202022
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34087
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 38182
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 5416
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50474
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 5418
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 38193
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56630
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42295
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 199995
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 204092
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202053
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 7500
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15693
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15694
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56655
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15695
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56654
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200020
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 36182
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15703
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200023
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 38230
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50522
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 5466
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56665
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 197981
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 58715
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 7522
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 21859
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56675
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50533
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 28008
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 30058
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 214380
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9583
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200052
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 204151
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198011
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198016
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 30081
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34177
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56704
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 7552
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9605
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 3462
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 216455
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 216456
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48519
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48522
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 23947
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 36236
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62856
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42385
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50581
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 60822
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 30103
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 46489
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198046
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62902
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 206264
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15802
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200132
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50629
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198089
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 206281
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 40401
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 206292
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48596
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15830
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 5606
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 62955
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202224
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50673
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200184
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48635
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 212477
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 36351
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 7679
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 212483
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200197
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198150
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 1547
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42517
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15895
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 7713
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 54825
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42541
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44592
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50737
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200242
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 208434
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44600
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200249
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44608
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34373
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15943
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42567
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50763
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44620
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 30286
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56911
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 5713
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 18001
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198225
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 61013
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15958
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15966
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 15967
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 206446
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 61049
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 28283
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34428
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 63113
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 1680
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42649
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 56987
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 212635
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 13984
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 138915
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 204457
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50858
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9902
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202418
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 40627
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200372
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200373
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202425
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 18106
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202427
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 206521
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 396986
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 11967
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44735
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57029
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50889
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 3786
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 136907
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 9930
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198352
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 54994
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42707
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57043
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48858
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 212703
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 1764
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 214757
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 210667
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 50923
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 14061
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44788
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48886
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 46844
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42755
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 132876
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 61200
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48919
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57112
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 214809
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 1820
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200478
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48927
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57118
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 1828
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57124
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 14127
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 212793
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44858
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 210752
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57154
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 48972
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 32590
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 3920
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 57169
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 22356
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 36692
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202585
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 16218
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42841
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 202591
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 26464
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34655
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44901
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20326
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 8038
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51050
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 24429
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42861
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 10099
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 212855
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 38778
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34696
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 10122
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 206735
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51088
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 200596
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 44949
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 12189
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 212895
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 24482
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 61349
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 63399
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 208808
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 6057
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 208814
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 55219
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 42947
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34756
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34758
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 210890
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 208844
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 210897
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51154
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 45014
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 55256
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 47065
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 34779
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 206813
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 137182
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 16350
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 38880
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49121
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 2018
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 215011
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 49127
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51184
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 51185
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 206836
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 55285
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 20473
      },
      {
        "in_bgp": true,
        "in_whois": false,
        "peer": 198651
      }
    ],
    "authority": "ripe",
    "resource": "3333",
    "parameters": {
      "resource": "3333",
      "query_time": "2025-10-18T00:00:00",
      "cache": ""
    },
    "query_starttime": "2025-10-18T00:00:00",
    "query_endtime": "2025-10-18T00:00:00"
  },
  "metadata": {}
}


{
  "_id": {
    "$oid": "68f36b084716d37002e551d3"
  },
  "endpoint": "asn-neighbours",
  "timestamp": {
    "$date": "2025-10-18T10:25:12.541Z"
  },
  "data_call_name": "asn-neighbours",
  "data": {
    "resource": "3333",
    "query_starttime": "2025-10-18T00:00:00",
    "query_endtime": "2025-10-18T00:00:00",
    "latest_time": "2025-10-18T00:00:00",
    "earliest_time": "2018-09-08T00:00:00",
    "neighbour_counts": {
      "left": 44,
      "right": 1,
      "unique": 883,
      "uncertain": 838
    },
    "neighbours": [
      {
        "asn": 1103,
        "type": "left",
        "power": 18672,
        "v4_peers": 121964,
        "v6_peers": 9911
      },
      {
        "asn": 1136,
        "type": "left",
        "power": 17328,
        "v4_peers": 188177,
        "v6_peers": 13269
      },
      {
        "asn": 12859,
        "type": "left",
        "power": 3944,
        "v4_peers": 27257,
        "v6_peers": 1475
      },
      {
        "asn": 15576,
        "type": "left",
        "power": 54,
        "v4_peers": 180,
        "v6_peers": 41
      },
      {
        "asn": 15802,
        "type": "left",
        "power": 55,
        "v4_peers": 236,
        "v6_peers": 214
      },
      {
        "asn": 1764,
        "type": "left",
        "power": 3,
        "v4_peers": 70,
        "v6_peers": 16
      },
      {
        "asn": 20485,
        "type": "left",
        "power": 960,
        "v4_peers": 4522,
        "v6_peers": 228
      },
      {
        "asn": 20764,
        "type": "left",
        "power": 1393,
        "v4_peers": 7869,
        "v6_peers": 1048
      },
      {
        "asn": 209022,
        "type": "left",
        "power": 7,
        "v4_peers": 0,
        "v6_peers": 24
      },
      {
        "asn": 209090,
        "type": "left",
        "power": 4,
        "v4_peers": 9,
        "v6_peers": 5
      },
      {
        "asn": 22356,
        "type": "left",
        "power": 2,
        "v4_peers": 11,
        "v6_peers": 1
      },
      {
        "asn": 24961,
        "type": "left",
        "power": 188,
        "v4_peers": 319,
        "v6_peers": 293
      },
      {
        "asn": 29632,
        "type": "left",
        "power": 102,
        "v4_peers": 259,
        "v6_peers": 193
      },
      {
        "asn": 30844,
        "type": "left",
        "power": 4,
        "v4_peers": 196,
        "v6_peers": 0
      },
      {
        "asn": 3216,
        "type": "left",
        "power": 460,
        "v4_peers": 2179,
        "v6_peers": 0
      },
      {
        "asn": 3303,
        "type": "left",
        "power": 395,
        "v4_peers": 1546,
        "v6_peers": 242
      },
      {
        "asn": 3320,
        "type": "left",
        "power": 39716,
        "v4_peers": 318870,
        "v6_peers": 23779
      },
      {
        "asn": 33891,
        "type": "left",
        "power": 3,
        "v4_peers": 12,
        "v6_peers": 14
      },
      {
        "asn": 34019,
        "type": "left",
        "power": 25,
        "v4_peers": 58,
        "v6_peers": 32
      },
      {
        "asn": 34927,
        "type": "left",
        "power": 210,
        "v4_peers": 72,
        "v6_peers": 480
      },
      {
        "asn": 35280,
        "type": "left",
        "power": 5,
        "v4_peers": 64,
        "v6_peers": 8
      },
      {
        "asn": 37100,
        "type": "left",
        "power": 534,
        "v4_peers": 2548,
        "v6_peers": 237
      },
      {
        "asn": 37282,
        "type": "left",
        "power": 2,
        "v4_peers": 12,
        "v6_peers": 0
      },
      {
        "asn": 37468,
        "type": "left",
        "power": 2084,
        "v4_peers": 4618,
        "v6_peers": 1861
      },
      {
        "asn": 41327,
        "type": "left",
        "power": 2,
        "v4_peers": 12,
        "v6_peers": 0
      },
      {
        "asn": 4230,
        "type": "left",
        "power": 2,
        "v4_peers": 83,
        "v6_peers": 6
      },
      {
        "asn": 4455,
        "type": "left",
        "power": 90,
        "v4_peers": 327,
        "v6_peers": 31
      },
      {
        "asn": 47147,
        "type": "left",
        "power": 79,
        "v4_peers": 421,
        "v6_peers": 109
      },
      {
        "asn": 48362,
        "type": "left",
        "power": 19,
        "v4_peers": 63,
        "v6_peers": 12
      },
      {
        "asn": 5405,
        "type": "left",
        "power": 15,
        "v4_peers": 72,
        "v6_peers": 71
      },
      {
        "asn": 55850,
        "type": "left",
        "power": 5,
        "v4_peers": 38,
        "v6_peers": 2
      },
      {
        "asn": 56655,
        "type": "left",
        "power": 24,
        "v4_peers": 47,
        "v6_peers": 0
      },
      {
        "asn": 5713,
        "type": "left",
        "power": 8,
        "v4_peers": 83,
        "v6_peers": 3
      },
      {
        "asn": 6057,
        "type": "left",
        "power": 3,
        "v4_peers": 27,
        "v6_peers": 3
      },
      {
        "asn": 6204,
        "type": "left",
        "power": 118,
        "v4_peers": 712,
        "v6_peers": 79
      },
      {
        "asn": 64049,
        "type": "left",
        "power": 1116,
        "v4_peers": 8430,
        "v6_peers": 821
      },
      {
        "asn": 6663,
        "type": "left",
        "power": 4,
        "v4_peers": 58,
        "v6_peers": 2
      },
      {
        "asn": 6696,
        "type": "left",
        "power": 26,
        "v4_peers": 108,
        "v6_peers": 0
      },
      {
        "asn": 6762,
        "type": "left",
        "power": 11499,
        "v4_peers": 70956,
        "v6_peers": 12786
      },
      {
        "asn": 6939,
        "type": "left",
        "power": 27496,
        "v4_peers": 62786,
        "v6_peers": 86536
      },
      {
        "asn": 8220,
        "type": "left",
        "power": 960,
        "v4_peers": 3227,
        "v6_peers": 473
      },
      {
        "asn": 8932,
        "type": "left",
        "power": 61,
        "v4_peers": 276,
        "v6_peers": 49
      },
      {
        "asn": 9002,
        "type": "left",
        "power": 6003,
        "v4_peers": 30924,
        "v6_peers": 5943
      },
      {
        "asn": 9044,
        "type": "left",
        "power": 15,
        "v4_peers": 92,
        "v6_peers": 9
      },
      {
        "asn": 12654,
        "type": "right",
        "power": 2,
        "v4_peers": 0,
        "v6_peers": 3
      },
      {
        "asn": 1140,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 12637,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 12779,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 18,
        "v6_peers": 3
      },
      {
        "asn": 12969,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 0
      },
      {
        "asn": 13237,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 0
      },
      {
        "asn": 14630,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 0
      },
      {
        "asn": 14840,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 18,
        "v6_peers": 0
      },
      {
        "asn": 14907,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 15547,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 12,
        "v6_peers": 0
      },
      {
        "asn": 15605,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 17639,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 1
      },
      {
        "asn": 18106,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 1828,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 198150,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 0
      },
      {
        "asn": 199524,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 199938,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 204092,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 20932,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 212483,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 12,
        "v6_peers": 2
      },
      {
        "asn": 213241,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 24482,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 18,
        "v6_peers": 3
      },
      {
        "asn": 25091,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 18,
        "v6_peers": 3
      },
      {
        "asn": 25160,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 25220,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 271253,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 28917,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 2
      },
      {
        "asn": 29049,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 0
      },
      {
        "asn": 29075,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 29140,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 31019,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 0
      },
      {
        "asn": 31027,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 12,
        "v6_peers": 2
      },
      {
        "asn": 3212,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 0
      },
      {
        "asn": 34288,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 36236,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 37721,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 0
      },
      {
        "asn": 39122,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 39351,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 41666,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 42541,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 45489,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 48919,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 49544,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 12,
        "v6_peers": 2
      },
      {
        "asn": 49605,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 0
      },
      {
        "asn": 50300,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 50763,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 51184,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 12,
        "v6_peers": 2
      },
      {
        "asn": 51185,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 18,
        "v6_peers": 2
      },
      {
        "asn": 51873,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 52320,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 56457,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 56987,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 58299,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 61573,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 62167,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 12,
        "v6_peers": 2
      },
      {
        "asn": 6424,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 64475,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 8218,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 42,
        "v6_peers": 7
      },
      {
        "asn": 8529,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 2
      },
      {
        "asn": 10099,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 0
      },
      {
        "asn": 10122,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 41,
        "v6_peers": 3
      },
      {
        "asn": 10310,
        "type": "uncertain",
        "power": 54,
        "v4_peers": 322,
        "v6_peers": 102
      },
      {
        "asn": 11019,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 2,
        "v6_peers": 0
      },
      {
        "asn": 1101,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 17,
        "v6_peers": 2
      },
      {
        "asn": 11179,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 0
      },
      {
        "asn": 1126,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 1
      },
      {
        "asn": 112,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 2
      },
      {
        "asn": 11358,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 2
      },
      {
        "asn": 1140,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 1
      },
      {
        "asn": 11967,
        "type": "uncertain",
        "power": 12,
        "v4_peers": 0,
        "v6_peers": 31
      },
      {
        "asn": 1200,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 1
      },
      {
        "asn": 12189,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 12297,
        "type": "uncertain",
        "power": 67,
        "v4_peers": 286,
        "v6_peers": 0
      },
      {
        "asn": 12322,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 0,
        "v6_peers": 14
      },
      {
        "asn": 12329,
        "type": "uncertain",
        "power": 15,
        "v4_peers": 66,
        "v6_peers": 0
      },
      {
        "asn": 12355,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 11,
        "v6_peers": 9
      },
      {
        "asn": 12399,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 7,
        "v6_peers": 1
      },
      {
        "asn": 12400,
        "type": "uncertain",
        "power": 99,
        "v4_peers": 441,
        "v6_peers": 42
      },
      {
        "asn": 12414,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 20,
        "v6_peers": 5
      },
      {
        "asn": 1241,
        "type": "uncertain",
        "power": 33,
        "v4_peers": 119,
        "v6_peers": 23
      },
      {
        "asn": 12440,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 10,
        "v6_peers": 5
      },
      {
        "asn": 1248,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 5,
        "v6_peers": 0
      },
      {
        "asn": 12552,
        "type": "uncertain",
        "power": 250,
        "v4_peers": 1038,
        "v6_peers": 191
      },
      {
        "asn": 12578,
        "type": "uncertain",
        "power": 133,
        "v4_peers": 304,
        "v6_peers": 63
      },
      {
        "asn": 12637,
        "type": "uncertain",
        "power": 14,
        "v4_peers": 70,
        "v6_peers": 15
      },
      {
        "asn": 1267,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 139,
        "v6_peers": 2
      },
      {
        "asn": 12693,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 16,
        "v6_peers": 1
      },
      {
        "asn": 12695,
        "type": "uncertain",
        "power": 45,
        "v4_peers": 196,
        "v6_peers": 17
      },
      {
        "asn": 12703,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 53,
        "v6_peers": 7
      },
      {
        "asn": 12713,
        "type": "uncertain",
        "power": 37,
        "v4_peers": 248,
        "v6_peers": 0
      },
      {
        "asn": 12731,
        "type": "uncertain",
        "power": 10,
        "v4_peers": 120,
        "v6_peers": 14
      },
      {
        "asn": 12741,
        "type": "uncertain",
        "power": 369,
        "v4_peers": 939,
        "v6_peers": 57
      },
      {
        "asn": 12759,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 5,
        "v6_peers": 1
      },
      {
        "asn": 12779,
        "type": "uncertain",
        "power": 66,
        "v4_peers": 336,
        "v6_peers": 39
      },
      {
        "asn": 12876,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 15,
        "v6_peers": 4
      },
      {
        "asn": 12888,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 9,
        "v6_peers": 0
      },
      {
        "asn": 12897,
        "type": "uncertain",
        "power": 10,
        "v4_peers": 39,
        "v6_peers": 8
      },
      {
        "asn": 12902,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 15,
        "v6_peers": 3
      },
      {
        "asn": 12969,
        "type": "uncertain",
        "power": 11,
        "v4_peers": 48,
        "v6_peers": 4
      },
      {
        "asn": 12993,
        "type": "uncertain",
        "power": 8,
        "v4_peers": 45,
        "v6_peers": 3
      },
      {
        "asn": 13000,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 1
      },
      {
        "asn": 13002,
        "type": "uncertain",
        "power": 7,
        "v4_peers": 21,
        "v6_peers": 4
      },
      {
        "asn": 13101,
        "type": "uncertain",
        "power": 13,
        "v4_peers": 80,
        "v6_peers": 11
      },
      {
        "asn": 13122,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 16,
        "v6_peers": 0
      },
      {
        "asn": 13132,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 1
      },
      {
        "asn": 13150,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 0
      },
      {
        "asn": 13194,
        "type": "uncertain",
        "power": 104,
        "v4_peers": 848,
        "v6_peers": 94
      },
      {
        "asn": 131958,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 13213,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 225,
        "v6_peers": 22
      },
      {
        "asn": 132203,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 69,
        "v6_peers": 0
      },
      {
        "asn": 132337,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 33,
        "v6_peers": 1
      },
      {
        "asn": 13237,
        "type": "uncertain",
        "power": 213,
        "v4_peers": 596,
        "v6_peers": 158
      },
      {
        "asn": 13249,
        "type": "uncertain",
        "power": 31,
        "v4_peers": 45,
        "v6_peers": 3
      },
      {
        "asn": 132876,
        "type": "uncertain",
        "power": 47,
        "v4_peers": 228,
        "v6_peers": 47
      },
      {
        "asn": 13289,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 1
      },
      {
        "asn": 13335,
        "type": "uncertain",
        "power": 892,
        "v4_peers": 6587,
        "v6_peers": 618
      },
      {
        "asn": 13360,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 0
      },
      {
        "asn": 133613,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 6,
        "v6_peers": 0
      },
      {
        "asn": 13445,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 8
      },
      {
        "asn": 135391,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 71,
        "v6_peers": 3
      },
      {
        "asn": 136106,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 0
      },
      {
        "asn": 136907,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 3
      },
      {
        "asn": 137182,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 137409,
        "type": "uncertain",
        "power": 790,
        "v4_peers": 4504,
        "v6_peers": 1859
      },
      {
        "asn": 138322,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 6,
        "v6_peers": 0
      },
      {
        "asn": 138915,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 35,
        "v6_peers": 2
      },
      {
        "asn": 139341,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 41,
        "v6_peers": 6
      },
      {
        "asn": 139628,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 61,
        "v6_peers": 0
      },
      {
        "asn": 13984,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 25,
        "v6_peers": 1
      },
      {
        "asn": 139901,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 6,
        "v6_peers": 0
      },
      {
        "asn": 14061,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 269,
        "v6_peers": 5
      },
      {
        "asn": 14127,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 0
      },
      {
        "asn": 14537,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 68,
        "v6_peers": 0
      },
      {
        "asn": 14593,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 57,
        "v6_peers": 36
      },
      {
        "asn": 14630,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 3
      },
      {
        "asn": 14907,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 2
      },
      {
        "asn": 15169,
        "type": "uncertain",
        "power": 16,
        "v4_peers": 0,
        "v6_peers": 557
      },
      {
        "asn": 15435,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 15,
        "v6_peers": 8
      },
      {
        "asn": 15447,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 11,
        "v6_peers": 1
      },
      {
        "asn": 15466,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 1
      },
      {
        "asn": 1547,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 15516,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 10,
        "v6_peers": 3
      },
      {
        "asn": 15547,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 36,
        "v6_peers": 3
      },
      {
        "asn": 15605,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 23,
        "v6_peers": 1
      },
      {
        "asn": 15693,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 1
      },
      {
        "asn": 15694,
        "type": "uncertain",
        "power": 19,
        "v4_peers": 87,
        "v6_peers": 5
      },
      {
        "asn": 15695,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 30,
        "v6_peers": 3
      },
      {
        "asn": 15703,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 17,
        "v6_peers": 2
      },
      {
        "asn": 15830,
        "type": "uncertain",
        "power": 218,
        "v4_peers": 752,
        "v6_peers": 124
      },
      {
        "asn": 15895,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 24,
        "v6_peers": 2
      },
      {
        "asn": 15943,
        "type": "uncertain",
        "power": 7,
        "v4_peers": 76,
        "v6_peers": 2
      },
      {
        "asn": 15958,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 1
      },
      {
        "asn": 15966,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 2,
        "v6_peers": 2
      },
      {
        "asn": 15967,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 52,
        "v6_peers": 1
      },
      {
        "asn": 16218,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 0
      },
      {
        "asn": 16265,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 722,
        "v6_peers": 247
      },
      {
        "asn": 16276,
        "type": "uncertain",
        "power": 111,
        "v4_peers": 716,
        "v6_peers": 28
      },
      {
        "asn": 16298,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 1
      },
      {
        "asn": 16350,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 1
      },
      {
        "asn": 16509,
        "type": "uncertain",
        "power": 47,
        "v4_peers": 2623,
        "v6_peers": 1397
      },
      {
        "asn": 16637,
        "type": "uncertain",
        "power": 92,
        "v4_peers": 886,
        "v6_peers": 21
      },
      {
        "asn": 1680,
        "type": "uncertain",
        "power": 153,
        "v4_peers": 442,
        "v6_peers": 116
      },
      {
        "asn": 17494,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 29,
        "v6_peers": 2
      },
      {
        "asn": 17639,
        "type": "uncertain",
        "power": 72,
        "v4_peers": 655,
        "v6_peers": 56
      },
      {
        "asn": 18001,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 27,
        "v6_peers": 4
      },
      {
        "asn": 18106,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 16,
        "v6_peers": 3
      },
      {
        "asn": 1820,
        "type": "uncertain",
        "power": 121,
        "v4_peers": 369,
        "v6_peers": 19
      },
      {
        "asn": 1828,
        "type": "uncertain",
        "power": 329,
        "v4_peers": 1396,
        "v6_peers": 92
      },
      {
        "asn": 18678,
        "type": "uncertain",
        "power": 163,
        "v4_peers": 410,
        "v6_peers": 127
      },
      {
        "asn": 19551,
        "type": "uncertain",
        "power": 160,
        "v4_peers": 1401,
        "v6_peers": 226
      },
      {
        "asn": 196752,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 10,
        "v6_peers": 1
      },
      {
        "asn": 196844,
        "type": "uncertain",
        "power": 150,
        "v4_peers": 392,
        "v6_peers": 22
      },
      {
        "asn": 196922,
        "type": "uncertain",
        "power": 8,
        "v4_peers": 19,
        "v6_peers": 4
      },
      {
        "asn": 196954,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 14,
        "v6_peers": 2
      },
      {
        "asn": 196997,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 1
      },
      {
        "asn": 197000,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 4
      },
      {
        "asn": 19711,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 43,
        "v6_peers": 0
      },
      {
        "asn": 197156,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 0
      },
      {
        "asn": 197301,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 1
      },
      {
        "asn": 197440,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 197692,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 7,
        "v6_peers": 8
      },
      {
        "asn": 197727,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 2
      },
      {
        "asn": 197790,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 10,
        "v6_peers": 0
      },
      {
        "asn": 197899,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 197981,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 0
      },
      {
        "asn": 198011,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 198016,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 5
      },
      {
        "asn": 198046,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 198089,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 42,
        "v6_peers": 7
      },
      {
        "asn": 198225,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 198352,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 0
      },
      {
        "asn": 198651,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 17,
        "v6_peers": 0
      },
      {
        "asn": 198763,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 198792,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 198930,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 5,
        "v6_peers": 0
      },
      {
        "asn": 198967,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 21,
        "v6_peers": 1
      },
      {
        "asn": 199095,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 12,
        "v6_peers": 1
      },
      {
        "asn": 199181,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 0
      },
      {
        "asn": 199332,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 0
      },
      {
        "asn": 199408,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 1
      },
      {
        "asn": 199471,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 3
      },
      {
        "asn": 199483,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 11,
        "v6_peers": 2
      },
      {
        "asn": 199524,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 181,
        "v6_peers": 21
      },
      {
        "asn": 199610,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 44,
        "v6_peers": 0
      },
      {
        "asn": 199752,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 1
      },
      {
        "asn": 199938,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 17,
        "v6_peers": 5
      },
      {
        "asn": 199939,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 12,
        "v6_peers": 4
      },
      {
        "asn": 199995,
        "type": "uncertain",
        "power": 56,
        "v4_peers": 156,
        "v6_peers": 1
      },
      {
        "asn": 200020,
        "type": "uncertain",
        "power": 13,
        "v4_peers": 17,
        "v6_peers": 2
      },
      {
        "asn": 200023,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 39,
        "v6_peers": 0
      },
      {
        "asn": 200052,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 200132,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 200184,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 1
      },
      {
        "asn": 200197,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 200242,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 4
      },
      {
        "asn": 200249,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 200372,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 5
      },
      {
        "asn": 200373,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 68,
        "v6_peers": 0
      },
      {
        "asn": 200478,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 200596,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 200781,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 10,
        "v6_peers": 4
      },
      {
        "asn": 201119,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 0
      },
      {
        "asn": 201290,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 23,
        "v6_peers": 2
      },
      {
        "asn": 201372,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 1
      },
      {
        "asn": 201401,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 10,
        "v6_peers": 4
      },
      {
        "asn": 201502,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 29,
        "v6_peers": 1
      },
      {
        "asn": 201650,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 5,
        "v6_peers": 5
      },
      {
        "asn": 201723,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 2
      },
      {
        "asn": 201791,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 1
      },
      {
        "asn": 201866,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 201877,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 13,
        "v6_peers": 0
      },
      {
        "asn": 2018,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 322,
        "v6_peers": 13
      },
      {
        "asn": 202022,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 0
      },
      {
        "asn": 202053,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 18,
        "v6_peers": 5
      },
      {
        "asn": 202224,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 5
      },
      {
        "asn": 202418,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 202425,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 1
      },
      {
        "asn": 202427,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 5
      },
      {
        "asn": 202585,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 4
      },
      {
        "asn": 202591,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 3
      },
      {
        "asn": 202855,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 202932,
        "type": "uncertain",
        "power": 7,
        "v4_peers": 13,
        "v6_peers": 4
      },
      {
        "asn": 202941,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 0,
        "v6_peers": 4
      },
      {
        "asn": 202954,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 203101,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 9,
        "v6_peers": 0
      },
      {
        "asn": 203126,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 20326,
        "type": "uncertain",
        "power": 18,
        "v4_peers": 237,
        "v6_peers": 35
      },
      {
        "asn": 203489,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 203724,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 0
      },
      {
        "asn": 203932,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 204059,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 3,
        "v6_peers": 2
      },
      {
        "asn": 204092,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 5,
        "v6_peers": 4
      },
      {
        "asn": 204151,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 7,
        "v6_peers": 3
      },
      {
        "asn": 204457,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 16,
        "v6_peers": 0
      },
      {
        "asn": 20473,
        "type": "uncertain",
        "power": 120,
        "v4_peers": 218,
        "v6_peers": 161
      },
      {
        "asn": 204805,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 1,
        "v6_peers": 3
      },
      {
        "asn": 204911,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 20495,
        "type": "uncertain",
        "power": 39,
        "v4_peers": 55,
        "v6_peers": 72
      },
      {
        "asn": 204995,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 1
      },
      {
        "asn": 20504,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 205103,
        "type": "uncertain",
        "power": 44,
        "v4_peers": 170,
        "v6_peers": 8
      },
      {
        "asn": 205206,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 1
      },
      {
        "asn": 205329,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 1
      },
      {
        "asn": 20546,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 2
      },
      {
        "asn": 20559,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 30,
        "v6_peers": 7
      },
      {
        "asn": 20562,
        "type": "uncertain",
        "power": 41,
        "v4_peers": 113,
        "v6_peers": 22
      },
      {
        "asn": 205668,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 10,
        "v6_peers": 3
      },
      {
        "asn": 205689,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 205755,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 1
      },
      {
        "asn": 205915,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 1
      },
      {
        "asn": 205943,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 206264,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 34,
        "v6_peers": 2
      },
      {
        "asn": 206281,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 10,
        "v6_peers": 3
      },
      {
        "asn": 206292,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 206446,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 7,
        "v6_peers": 1
      },
      {
        "asn": 20647,
        "type": "uncertain",
        "power": 10,
        "v4_peers": 30,
        "v6_peers": 11
      },
      {
        "asn": 206521,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 7,
        "v6_peers": 3
      },
      {
        "asn": 206735,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 8,
        "v6_peers": 2
      },
      {
        "asn": 206813,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 2,
        "v6_peers": 3
      },
      {
        "asn": 206836,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 207063,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 2
      },
      {
        "asn": 207176,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 8,
        "v6_peers": 1
      },
      {
        "asn": 207283,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 0
      },
      {
        "asn": 207375,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 73,
        "v6_peers": 3
      },
      {
        "asn": 207487,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 3
      },
      {
        "asn": 207594,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 12,
        "v6_peers": 2
      },
      {
        "asn": 20766,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 14,
        "v6_peers": 7
      },
      {
        "asn": 207790,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 9,
        "v6_peers": 1
      },
      {
        "asn": 207803,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 1,
        "v6_peers": 4
      },
      {
        "asn": 207866,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 1
      },
      {
        "asn": 208034,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 5,
        "v6_peers": 0
      },
      {
        "asn": 20804,
        "type": "uncertain",
        "power": 296,
        "v4_peers": 866,
        "v6_peers": 45
      },
      {
        "asn": 208434,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 4
      },
      {
        "asn": 20847,
        "type": "uncertain",
        "power": 7,
        "v4_peers": 19,
        "v6_peers": 11
      },
      {
        "asn": 208808,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 23,
        "v6_peers": 0
      },
      {
        "asn": 208814,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 4
      },
      {
        "asn": 208844,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 20886,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 5,
        "v6_peers": 1
      },
      {
        "asn": 208959,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 1
      },
      {
        "asn": 208972,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 208976,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 4,
        "v6_peers": 3
      },
      {
        "asn": 209181,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 14,
        "v6_peers": 7
      },
      {
        "asn": 20932,
        "type": "uncertain",
        "power": 7,
        "v4_peers": 11,
        "v6_peers": 3
      },
      {
        "asn": 20940,
        "type": "uncertain",
        "power": 7,
        "v4_peers": 248,
        "v6_peers": 6
      },
      {
        "asn": 209528,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 2
      },
      {
        "asn": 209650,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 4
      },
      {
        "asn": 20969,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 5,
        "v6_peers": 0
      },
      {
        "asn": 209768,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 4,
        "v6_peers": 0
      },
      {
        "asn": 209823,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 6
      },
      {
        "asn": 209859,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 4
      },
      {
        "asn": 210036,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 2,
        "v6_peers": 4
      },
      {
        "asn": 21013,
        "type": "uncertain",
        "power": 52,
        "v4_peers": 178,
        "v6_peers": 23
      },
      {
        "asn": 210152,
        "type": "uncertain",
        "power": 19,
        "v4_peers": 0,
        "v6_peers": 44
      },
      {
        "asn": 21056,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 39,
        "v6_peers": 0
      },
      {
        "asn": 210667,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 10
      },
      {
        "asn": 210752,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 210890,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 0
      },
      {
        "asn": 210897,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 0
      },
      {
        "asn": 21100,
        "type": "uncertain",
        "power": 8,
        "v4_peers": 33,
        "v6_peers": 9
      },
      {
        "asn": 211024,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 2
      },
      {
        "asn": 211037,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 211286,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 9
      },
      {
        "asn": 211316,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 0
      },
      {
        "asn": 211588,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 13,
        "v6_peers": 7
      },
      {
        "asn": 211623,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 211713,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 211826,
        "type": "uncertain",
        "power": 6,
        "v4_peers": 29,
        "v6_peers": 0
      },
      {
        "asn": 211882,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 3,
        "v6_peers": 3
      },
      {
        "asn": 2119,
        "type": "uncertain",
        "power": 151,
        "v4_peers": 656,
        "v6_peers": 114
      },
      {
        "asn": 21215,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 10,
        "v6_peers": 0
      },
      {
        "asn": 21221,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 13,
        "v6_peers": 5
      },
      {
        "asn": 212232,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 212477,
        "type": "uncertain",
        "power": 24,
        "v4_peers": 144,
        "v6_peers": 39
      },
      {
        "asn": 212483,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 4
      },
      {
        "asn": 212635,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 3,
        "v6_peers": 7
      },
      {
        "asn": 21263,
        "type": "uncertain",
        "power": 13,
        "v4_peers": 54,
        "v6_peers": 13
      },
      {
        "asn": 212703,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 2
      },
      {
        "asn": 212793,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 1
      },
      {
        "asn": 212855,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 212895,
        "type": "uncertain",
        "power": 31,
        "v4_peers": 3,
        "v6_peers": 52
      },
      {
        "asn": 213050,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 1
      },
      {
        "asn": 213052,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 2
      },
      {
        "asn": 213092,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 0,
        "v6_peers": 9
      },
      {
        "asn": 213241,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 14,
        "v6_peers": 2
      },
      {
        "asn": 213279,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 213373,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 12,
        "v6_peers": 3
      },
      {
        "asn": 213392,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 2
      },
      {
        "asn": 213543,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 1
      },
      {
        "asn": 213576,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 2
      },
      {
        "asn": 213822,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 214076,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 1
      },
      {
        "asn": 21409,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 16,
        "v6_peers": 1
      },
      {
        "asn": 214145,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 4
      },
      {
        "asn": 214271,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 214294,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 1
      },
      {
        "asn": 214380,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 214757,
        "type": "uncertain",
        "power": 12,
        "v4_peers": 0,
        "v6_peers": 32
      },
      {
        "asn": 214809,
        "type": "uncertain",
        "power": 8,
        "v4_peers": 1,
        "v6_peers": 27
      },
      {
        "asn": 215011,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 215248,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 5
      },
      {
        "asn": 215296,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 3
      },
      {
        "asn": 215444,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 4
      },
      {
        "asn": 215577,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 3
      },
      {
        "asn": 215615,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 2
      },
      {
        "asn": 215685,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 4
      },
      {
        "asn": 215724,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 215887,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 5
      },
      {
        "asn": 216071,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 241,
        "v6_peers": 0
      },
      {
        "asn": 216092,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 0
      },
      {
        "asn": 216107,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 1,
        "v6_peers": 4
      },
      {
        "asn": 216251,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 216455,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 1
      },
      {
        "asn": 216456,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 7,
        "v6_peers": 1
      },
      {
        "asn": 21859,
        "type": "uncertain",
        "power": 31,
        "v4_peers": 272,
        "v6_peers": 24
      },
      {
        "asn": 22697,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 2
      },
      {
        "asn": 23028,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 7,
        "v6_peers": 2
      },
      {
        "asn": 23106,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 23344,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 3
      },
      {
        "asn": 23576,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 22,
        "v6_peers": 0
      },
      {
        "asn": 23764,
        "type": "uncertain",
        "power": 235,
        "v4_peers": 4300,
        "v6_peers": 122
      },
      {
        "asn": 23947,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 33,
        "v6_peers": 0
      },
      {
        "asn": 24429,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 37,
        "v6_peers": 18
      },
      {
        "asn": 24482,
        "type": "uncertain",
        "power": 140,
        "v4_peers": 1294,
        "v6_peers": 493
      },
      {
        "asn": 24586,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 17,
        "v6_peers": 5
      },
      {
        "asn": 24724,
        "type": "uncertain",
        "power": 156,
        "v4_peers": 513,
        "v6_peers": 30
      },
      {
        "asn": 24730,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 1
      },
      {
        "asn": 24753,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 14,
        "v6_peers": 0
      },
      {
        "asn": 24785,
        "type": "uncertain",
        "power": 64,
        "v4_peers": 138,
        "v6_peers": 30
      },
      {
        "asn": 2484,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 24875,
        "type": "uncertain",
        "power": 44,
        "v4_peers": 392,
        "v6_peers": 19
      },
      {
        "asn": 24940,
        "type": "uncertain",
        "power": 36,
        "v4_peers": 162,
        "v6_peers": 28
      },
      {
        "asn": 25091,
        "type": "uncertain",
        "power": 90,
        "v4_peers": 257,
        "v6_peers": 64
      },
      {
        "asn": 250,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 0
      },
      {
        "asn": 25133,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 52,
        "v6_peers": 0
      },
      {
        "asn": 25151,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 23,
        "v6_peers": 3
      },
      {
        "asn": 25152,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 3
      },
      {
        "asn": 25160,
        "type": "uncertain",
        "power": 12,
        "v4_peers": 72,
        "v6_peers": 3
      },
      {
        "asn": 25182,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 25220,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 15,
        "v6_peers": 4
      },
      {
        "asn": 25369,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 32,
        "v6_peers": 7
      },
      {
        "asn": 25428,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 0
      },
      {
        "asn": 25455,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 2
      },
      {
        "asn": 25595,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 1
      },
      {
        "asn": 25818,
        "type": "uncertain",
        "power": 8,
        "v4_peers": 34,
        "v6_peers": 4
      },
      {
        "asn": 2603,
        "type": "uncertain",
        "power": 325,
        "v4_peers": 1310,
        "v6_peers": 139
      },
      {
        "asn": 2611,
        "type": "uncertain",
        "power": 12,
        "v4_peers": 54,
        "v6_peers": 7
      },
      {
        "asn": 262287,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 2635,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 26,
        "v6_peers": 8
      },
      {
        "asn": 26464,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 11,
        "v6_peers": 0
      },
      {
        "asn": 264997,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 3,
        "v6_peers": 2
      },
      {
        "asn": 26667,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 1
      },
      {
        "asn": 2686,
        "type": "uncertain",
        "power": 91,
        "v4_peers": 417,
        "v6_peers": 0
      },
      {
        "asn": 270814,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 17,
        "v6_peers": 2
      },
      {
        "asn": 28008,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 28283,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 7,
        "v6_peers": 2
      },
      {
        "asn": 2852,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 26,
        "v6_peers": 2
      },
      {
        "asn": 2854,
        "type": "uncertain",
        "power": 81,
        "v4_peers": 119,
        "v6_peers": 6
      },
      {
        "asn": 28725,
        "type": "uncertain",
        "power": 52,
        "v4_peers": 78,
        "v6_peers": 33
      },
      {
        "asn": 28788,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 6,
        "v6_peers": 2
      },
      {
        "asn": 28917,
        "type": "uncertain",
        "power": 162,
        "v4_peers": 468,
        "v6_peers": 86
      },
      {
        "asn": 29001,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 29028,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 12,
        "v6_peers": 2
      },
      {
        "asn": 29049,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 80,
        "v6_peers": 0
      },
      {
        "asn": 29063,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 15,
        "v6_peers": 1
      },
      {
        "asn": 2906,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 29075,
        "type": "uncertain",
        "power": 98,
        "v4_peers": 252,
        "v6_peers": 88
      },
      {
        "asn": 29119,
        "type": "uncertain",
        "power": 318,
        "v4_peers": 2745,
        "v6_peers": 88
      },
      {
        "asn": 29140,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 7,
        "v6_peers": 5
      },
      {
        "asn": 29141,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 16,
        "v6_peers": 2
      },
      {
        "asn": 2914,
        "type": "uncertain",
        "power": 7011,
        "v4_peers": 0,
        "v6_peers": 42373
      },
      {
        "asn": 29263,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 29314,
        "type": "uncertain",
        "power": 87,
        "v4_peers": 360,
        "v6_peers": 11
      },
      {
        "asn": 293,
        "type": "uncertain",
        "power": 34,
        "v4_peers": 160,
        "v6_peers": 6
      },
      {
        "asn": 29467,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 21,
        "v6_peers": 2
      },
      {
        "asn": 29505,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 8,
        "v6_peers": 2
      },
      {
        "asn": 29670,
        "type": "uncertain",
        "power": 20,
        "v4_peers": 22,
        "v6_peers": 32
      },
      {
        "asn": 29802,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 3
      },
      {
        "asn": 30058,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 149,
        "v6_peers": 18
      },
      {
        "asn": 30081,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 3,
        "v6_peers": 1
      },
      {
        "asn": 30103,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 30132,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 2
      },
      {
        "asn": 30286,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 0
      },
      {
        "asn": 30736,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 30870,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 4
      },
      {
        "asn": 30925,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 13,
        "v6_peers": 1
      },
      {
        "asn": 30999,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 161,
        "v6_peers": 6
      },
      {
        "asn": 31019,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 31027,
        "type": "uncertain",
        "power": 321,
        "v4_peers": 1376,
        "v6_peers": 195
      },
      {
        "asn": 31084,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 1
      },
      {
        "asn": 31133,
        "type": "uncertain",
        "power": 1078,
        "v4_peers": 6041,
        "v6_peers": 292
      },
      {
        "asn": 31319,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 10,
        "v6_peers": 2
      },
      {
        "asn": 31424,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 12,
        "v6_peers": 6
      },
      {
        "asn": 31449,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 0
      },
      {
        "asn": 31477,
        "type": "uncertain",
        "power": 10,
        "v4_peers": 70,
        "v6_peers": 13
      },
      {
        "asn": 31500,
        "type": "uncertain",
        "power": 194,
        "v4_peers": 884,
        "v6_peers": 50
      },
      {
        "asn": 31515,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 60,
        "v6_peers": 0
      },
      {
        "asn": 31529,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 11,
        "v6_peers": 14
      },
      {
        "asn": 31638,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 62,
        "v6_peers": 0
      },
      {
        "asn": 31673,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 35,
        "v6_peers": 10
      },
      {
        "asn": 31800,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 0
      },
      {
        "asn": 31898,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 3
      },
      {
        "asn": 32035,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 20,
        "v6_peers": 2
      },
      {
        "asn": 3209,
        "type": "uncertain",
        "power": 114,
        "v4_peers": 643,
        "v6_peers": 0
      },
      {
        "asn": 3212,
        "type": "uncertain",
        "power": 43,
        "v4_peers": 96,
        "v6_peers": 15
      },
      {
        "asn": 3214,
        "type": "uncertain",
        "power": 43,
        "v4_peers": 119,
        "v6_peers": 133
      },
      {
        "asn": 3223,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 96,
        "v6_peers": 0
      },
      {
        "asn": 32590,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 5,
        "v6_peers": 3
      },
      {
        "asn": 32787,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 86,
        "v6_peers": 4
      },
      {
        "asn": 328112,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 328366,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 78,
        "v6_peers": 1
      },
      {
        "asn": 3292,
        "type": "uncertain",
        "power": 73,
        "v4_peers": 384,
        "v6_peers": 48
      },
      {
        "asn": 32934,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 12,
        "v6_peers": 10
      },
      {
        "asn": 3326,
        "type": "uncertain",
        "power": 273,
        "v4_peers": 1122,
        "v6_peers": 67
      },
      {
        "asn": 3327,
        "type": "uncertain",
        "power": 35,
        "v4_peers": 188,
        "v6_peers": 14
      },
      {
        "asn": 33353,
        "type": "uncertain",
        "power": 9,
        "v4_peers": 82,
        "v6_peers": 77
      },
      {
        "asn": 33921,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 33986,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 7,
        "v6_peers": 1
      },
      {
        "asn": 34087,
        "type": "uncertain",
        "power": 25,
        "v4_peers": 92,
        "v6_peers": 18
      },
      {
        "asn": 34177,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 93,
        "v6_peers": 8
      },
      {
        "asn": 34224,
        "type": "uncertain",
        "power": 85,
        "v4_peers": 294,
        "v6_peers": 36
      },
      {
        "asn": 34288,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 8,
        "v6_peers": 3
      },
      {
        "asn": 34373,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 19,
        "v6_peers": 5
      },
      {
        "asn": 34428,
        "type": "uncertain",
        "power": 11,
        "v4_peers": 44,
        "v6_peers": 4
      },
      {
        "asn": 3462,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 28,
        "v6_peers": 3
      },
      {
        "asn": 34655,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 23,
        "v6_peers": 2
      },
      {
        "asn": 34696,
        "type": "uncertain",
        "power": 21,
        "v4_peers": 88,
        "v6_peers": 6
      },
      {
        "asn": 34756,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 11,
        "v6_peers": 2
      },
      {
        "asn": 34758,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 31,
        "v6_peers": 2
      },
      {
        "asn": 34779,
        "type": "uncertain",
        "power": 78,
        "v4_peers": 124,
        "v6_peers": 31
      },
      {
        "asn": 34942,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 34953,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 22,
        "v6_peers": 9
      },
      {
        "asn": 34968,
        "type": "uncertain",
        "power": 8,
        "v4_peers": 20,
        "v6_peers": 6
      },
      {
        "asn": 35000,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 45,
        "v6_peers": 0
      },
      {
        "asn": 35179,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 29,
        "v6_peers": 0
      },
      {
        "asn": 35224,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 36,
        "v6_peers": 0
      },
      {
        "asn": 35297,
        "type": "uncertain",
        "power": 161,
        "v4_peers": 687,
        "v6_peers": 29
      },
      {
        "asn": 35320,
        "type": "uncertain",
        "power": 168,
        "v4_peers": 479,
        "v6_peers": 66
      },
      {
        "asn": 35421,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 0
      },
      {
        "asn": 35432,
        "type": "uncertain",
        "power": 29,
        "v4_peers": 82,
        "v6_peers": 9
      },
      {
        "asn": 35574,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 8
      },
      {
        "asn": 35598,
        "type": "uncertain",
        "power": 478,
        "v4_peers": 1801,
        "v6_peers": 166
      },
      {
        "asn": 35729,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 0
      },
      {
        "asn": 35753,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 249,
        "v6_peers": 4
      },
      {
        "asn": 35758,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 35793,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 5,
        "v6_peers": 3
      },
      {
        "asn": 36182,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 0
      },
      {
        "asn": 36236,
        "type": "uncertain",
        "power": 28,
        "v4_peers": 86,
        "v6_peers": 88
      },
      {
        "asn": 36351,
        "type": "uncertain",
        "power": 16,
        "v4_peers": 372,
        "v6_peers": 88
      },
      {
        "asn": 36692,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 29,
        "v6_peers": 0
      },
      {
        "asn": 36864,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 11,
        "v6_peers": 1
      },
      {
        "asn": 36994,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 67,
        "v6_peers": 5
      },
      {
        "asn": 37662,
        "type": "uncertain",
        "power": 479,
        "v4_peers": 3638,
        "v6_peers": 222
      },
      {
        "asn": 3786,
        "type": "uncertain",
        "power": 65,
        "v4_peers": 4327,
        "v6_peers": 0
      },
      {
        "asn": 38040,
        "type": "uncertain",
        "power": 7,
        "v4_peers": 47,
        "v6_peers": 0
      },
      {
        "asn": 38082,
        "type": "uncertain",
        "power": 74,
        "v4_peers": 323,
        "v6_peers": 0
      },
      {
        "asn": 38158,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 1
      },
      {
        "asn": 38182,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 13,
        "v6_peers": 0
      },
      {
        "asn": 38193,
        "type": "uncertain",
        "power": 172,
        "v4_peers": 1131,
        "v6_peers": 91
      },
      {
        "asn": 38230,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 3
      },
      {
        "asn": 3856,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 38778,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 7,
        "v6_peers": 0
      },
      {
        "asn": 38880,
        "type": "uncertain",
        "power": 8,
        "v4_peers": 95,
        "v6_peers": 14
      },
      {
        "asn": 38915,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 18
      },
      {
        "asn": 38983,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 11,
        "v6_peers": 4
      },
      {
        "asn": 39063,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 5,
        "v6_peers": 11
      },
      {
        "asn": 39090,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 1
      },
      {
        "asn": 39120,
        "type": "uncertain",
        "power": 25,
        "v4_peers": 98,
        "v6_peers": 53
      },
      {
        "asn": 39122,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 26,
        "v6_peers": 5
      },
      {
        "asn": 39180,
        "type": "uncertain",
        "power": 17,
        "v4_peers": 41,
        "v6_peers": 3
      },
      {
        "asn": 3920,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 19,
        "v6_peers": 3
      },
      {
        "asn": 39351,
        "type": "uncertain",
        "power": 43,
        "v4_peers": 57,
        "v6_peers": 84
      },
      {
        "asn": 39386,
        "type": "uncertain",
        "power": 193,
        "v4_peers": 6802,
        "v6_peers": 2671
      },
      {
        "asn": 394354,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 90,
        "v6_peers": 88
      },
      {
        "asn": 39521,
        "type": "uncertain",
        "power": 8,
        "v4_peers": 133,
        "v6_peers": 11
      },
      {
        "asn": 39526,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 39637,
        "type": "uncertain",
        "power": 16,
        "v4_peers": 42,
        "v6_peers": 0
      },
      {
        "asn": 39642,
        "type": "uncertain",
        "power": 12,
        "v4_peers": 66,
        "v6_peers": 13
      },
      {
        "asn": 39647,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 59,
        "v6_peers": 5
      },
      {
        "asn": 39686,
        "type": "uncertain",
        "power": 50,
        "v4_peers": 185,
        "v6_peers": 46
      },
      {
        "asn": 396986,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 1
      },
      {
        "asn": 39702,
        "type": "uncertain",
        "power": 10,
        "v4_peers": 36,
        "v6_peers": 11
      },
      {
        "asn": 39704,
        "type": "uncertain",
        "power": 11,
        "v4_peers": 33,
        "v6_peers": 10
      },
      {
        "asn": 39737,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 58,
        "v6_peers": 4
      },
      {
        "asn": 39832,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 10,
        "v6_peers": 4
      },
      {
        "asn": 39839,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 1
      },
      {
        "asn": 398465,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 0
      },
      {
        "asn": 39878,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 7,
        "v6_peers": 1
      },
      {
        "asn": 39923,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 14,
        "v6_peers": 7
      },
      {
        "asn": 40401,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 4,
        "v6_peers": 5
      },
      {
        "asn": 40627,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 13,
        "v6_peers": 0
      },
      {
        "asn": 40999,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 0
      },
      {
        "asn": 41041,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 41090,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 7,
        "v6_peers": 2
      },
      {
        "asn": 41095,
        "type": "uncertain",
        "power": 90,
        "v4_peers": 613,
        "v6_peers": 0
      },
      {
        "asn": 41313,
        "type": "uncertain",
        "power": 41,
        "v4_peers": 287,
        "v6_peers": 8
      },
      {
        "asn": 41405,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 1
      },
      {
        "asn": 41480,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 10,
        "v6_peers": 2
      },
      {
        "asn": 41529,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 41666,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 41692,
        "type": "uncertain",
        "power": 27,
        "v4_peers": 114,
        "v6_peers": 14
      },
      {
        "asn": 41820,
        "type": "uncertain",
        "power": 17,
        "v4_peers": 60,
        "v6_peers": 3
      },
      {
        "asn": 41887,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 50,
        "v6_peers": 11
      },
      {
        "asn": 41913,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 17,
        "v6_peers": 3
      },
      {
        "asn": 41960,
        "type": "uncertain",
        "power": 14,
        "v4_peers": 101,
        "v6_peers": 15
      },
      {
        "asn": 41998,
        "type": "uncertain",
        "power": 22,
        "v4_peers": 91,
        "v6_peers": 19
      },
      {
        "asn": 42093,
        "type": "uncertain",
        "power": 9,
        "v4_peers": 20,
        "v6_peers": 9
      },
      {
        "asn": 42156,
        "type": "uncertain",
        "power": 9,
        "v4_peers": 25,
        "v6_peers": 8
      },
      {
        "asn": 42184,
        "type": "uncertain",
        "power": 12,
        "v4_peers": 25,
        "v6_peers": 12
      },
      {
        "asn": 42295,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 10,
        "v6_peers": 2
      },
      {
        "asn": 42385,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 1
      },
      {
        "asn": 42517,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 5,
        "v6_peers": 1
      },
      {
        "asn": 42541,
        "type": "uncertain",
        "power": 10,
        "v4_peers": 15,
        "v6_peers": 22
      },
      {
        "asn": 42567,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 4,
        "v6_peers": 1
      },
      {
        "asn": 42649,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 12,
        "v6_peers": 4
      },
      {
        "asn": 42707,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 30,
        "v6_peers": 5
      },
      {
        "asn": 42755,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 13,
        "v6_peers": 1
      },
      {
        "asn": 42841,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 1
      },
      {
        "asn": 42861,
        "type": "uncertain",
        "power": 15,
        "v4_peers": 61,
        "v6_peers": 11
      },
      {
        "asn": 42947,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 71,
        "v6_peers": 19
      },
      {
        "asn": 42,
        "type": "uncertain",
        "power": 7,
        "v4_peers": 97,
        "v6_peers": 88
      },
      {
        "asn": 43190,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 1
      },
      {
        "asn": 43350,
        "type": "uncertain",
        "power": 20,
        "v4_peers": 179,
        "v6_peers": 38
      },
      {
        "asn": 43366,
        "type": "uncertain",
        "power": 8,
        "v4_peers": 22,
        "v6_peers": 4
      },
      {
        "asn": 43414,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 26,
        "v6_peers": 12
      },
      {
        "asn": 43519,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 10,
        "v6_peers": 11
      },
      {
        "asn": 43566,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 1
      },
      {
        "asn": 43641,
        "type": "uncertain",
        "power": 15,
        "v4_peers": 39,
        "v6_peers": 383
      },
      {
        "asn": 43727,
        "type": "uncertain",
        "power": 237,
        "v4_peers": 1724,
        "v6_peers": 182
      },
      {
        "asn": 43942,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 0
      },
      {
        "asn": 44034,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 10,
        "v6_peers": 1
      },
      {
        "asn": 44134,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 1
      },
      {
        "asn": 44592,
        "type": "uncertain",
        "power": 99,
        "v4_peers": 500,
        "v6_peers": 38
      },
      {
        "asn": 44600,
        "type": "uncertain",
        "power": 38,
        "v4_peers": 85,
        "v6_peers": 5
      },
      {
        "asn": 44608,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 0
      },
      {
        "asn": 44620,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 44735,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 15,
        "v6_peers": 4
      },
      {
        "asn": 44788,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 1
      },
      {
        "asn": 44858,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 13,
        "v6_peers": 1
      },
      {
        "asn": 44901,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 75,
        "v6_peers": 4
      },
      {
        "asn": 44949,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 2
      },
      {
        "asn": 45014,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 0
      },
      {
        "asn": 45102,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 18,
        "v6_peers": 0
      },
      {
        "asn": 45352,
        "type": "uncertain",
        "power": 8,
        "v4_peers": 156,
        "v6_peers": 0
      },
      {
        "asn": 45430,
        "type": "uncertain",
        "power": 74,
        "v4_peers": 1000,
        "v6_peers": 4
      },
      {
        "asn": 45437,
        "type": "uncertain",
        "power": 22,
        "v4_peers": 82,
        "v6_peers": 14
      },
      {
        "asn": 45474,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 7,
        "v6_peers": 0
      },
      {
        "asn": 45489,
        "type": "uncertain",
        "power": 38,
        "v4_peers": 715,
        "v6_peers": 40
      },
      {
        "asn": 45701,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 53,
        "v6_peers": 0
      },
      {
        "asn": 45758,
        "type": "uncertain",
        "power": 38,
        "v4_peers": 170,
        "v6_peers": 29
      },
      {
        "asn": 45899,
        "type": "uncertain",
        "power": 25,
        "v4_peers": 1343,
        "v6_peers": 0
      },
      {
        "asn": 45903,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 52,
        "v6_peers": 0
      },
      {
        "asn": 4601,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 1
      },
      {
        "asn": 46244,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 0
      },
      {
        "asn": 4637,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 21,
        "v6_peers": 0
      },
      {
        "asn": 46489,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 4
      },
      {
        "asn": 4651,
        "type": "uncertain",
        "power": 244,
        "v4_peers": 3805,
        "v6_peers": 158
      },
      {
        "asn": 4657,
        "type": "uncertain",
        "power": 126,
        "v4_peers": 658,
        "v6_peers": 55
      },
      {
        "asn": 46844,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 1
      },
      {
        "asn": 47065,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 15,
        "v6_peers": 2
      },
      {
        "asn": 47121,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 47160,
        "type": "uncertain",
        "power": 45,
        "v4_peers": 69,
        "v6_peers": 61
      },
      {
        "asn": 47172,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 21,
        "v6_peers": 1
      },
      {
        "asn": 47195,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 1
      },
      {
        "asn": 47272,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 2,
        "v6_peers": 7
      },
      {
        "asn": 4761,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 7
      },
      {
        "asn": 47689,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 5
      },
      {
        "asn": 4775,
        "type": "uncertain",
        "power": 13,
        "v4_peers": 357,
        "v6_peers": 262
      },
      {
        "asn": 47836,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 0
      },
      {
        "asn": 4788,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 5,
        "v6_peers": 0
      },
      {
        "asn": 47957,
        "type": "uncertain",
        "power": 10,
        "v4_peers": 255,
        "v6_peers": 0
      },
      {
        "asn": 47973,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 1
      },
      {
        "asn": 4800,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 272,
        "v6_peers": 1
      },
      {
        "asn": 48185,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 47,
        "v6_peers": 13
      },
      {
        "asn": 48200,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 41,
        "v6_peers": 5
      },
      {
        "asn": 48284,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 13,
        "v6_peers": 3
      },
      {
        "asn": 48314,
        "type": "uncertain",
        "power": 8,
        "v4_peers": 78,
        "v6_peers": 28
      },
      {
        "asn": 48345,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 4
      },
      {
        "asn": 48374,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 4,
        "v6_peers": 2
      },
      {
        "asn": 48399,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 2
      },
      {
        "asn": 48519,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 4,
        "v6_peers": 4
      },
      {
        "asn": 48522,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 1
      },
      {
        "asn": 48596,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 3,
        "v6_peers": 3
      },
      {
        "asn": 48635,
        "type": "uncertain",
        "power": 11,
        "v4_peers": 69,
        "v6_peers": 28
      },
      {
        "asn": 48858,
        "type": "uncertain",
        "power": 18,
        "v4_peers": 55,
        "v6_peers": 0
      },
      {
        "asn": 48886,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 8,
        "v6_peers": 0
      },
      {
        "asn": 48919,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 4,
        "v6_peers": 1
      },
      {
        "asn": 48927,
        "type": "uncertain",
        "power": 29,
        "v4_peers": 4,
        "v6_peers": 49
      },
      {
        "asn": 48972,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 4,
        "v6_peers": 3
      },
      {
        "asn": 49121,
        "type": "uncertain",
        "power": 6,
        "v4_peers": 0,
        "v6_peers": 14
      },
      {
        "asn": 49127,
        "type": "uncertain",
        "power": 40,
        "v4_peers": 140,
        "v6_peers": 42
      },
      {
        "asn": 49206,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 5,
        "v6_peers": 2
      },
      {
        "asn": 49453,
        "type": "uncertain",
        "power": 8,
        "v4_peers": 86,
        "v6_peers": 16
      },
      {
        "asn": 49463,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 7,
        "v6_peers": 2
      },
      {
        "asn": 49544,
        "type": "uncertain",
        "power": 28,
        "v4_peers": 218,
        "v6_peers": 58
      },
      {
        "asn": 49600,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 10,
        "v6_peers": 2
      },
      {
        "asn": 49605,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 22,
        "v6_peers": 3
      },
      {
        "asn": 49627,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 3,
        "v6_peers": 1
      },
      {
        "asn": 49653,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 0
      },
      {
        "asn": 49666,
        "type": "uncertain",
        "power": 9,
        "v4_peers": 710,
        "v6_peers": 0
      },
      {
        "asn": 49685,
        "type": "uncertain",
        "power": 18,
        "v4_peers": 95,
        "v6_peers": 40
      },
      {
        "asn": 49800,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 11,
        "v6_peers": 2
      },
      {
        "asn": 49820,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 2
      },
      {
        "asn": 49981,
        "type": "uncertain",
        "power": 29,
        "v4_peers": 152,
        "v6_peers": 34
      },
      {
        "asn": 50050,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 13,
        "v6_peers": 0
      },
      {
        "asn": 50072,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 0
      },
      {
        "asn": 50083,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 13,
        "v6_peers": 7
      },
      {
        "asn": 50245,
        "type": "uncertain",
        "power": 6,
        "v4_peers": 20,
        "v6_peers": 8
      },
      {
        "asn": 50263,
        "type": "uncertain",
        "power": 463,
        "v4_peers": 3241,
        "v6_peers": 203
      },
      {
        "asn": 50266,
        "type": "uncertain",
        "power": 23,
        "v4_peers": 209,
        "v6_peers": 36
      },
      {
        "asn": 50272,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 11,
        "v6_peers": 2
      },
      {
        "asn": 50295,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 5,
        "v6_peers": 2
      },
      {
        "asn": 50300,
        "type": "uncertain",
        "power": 8,
        "v4_peers": 42,
        "v6_peers": 10
      },
      {
        "asn": 50309,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 50316,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 137,
        "v6_peers": 0
      },
      {
        "asn": 50324,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 1
      },
      {
        "asn": 50340,
        "type": "uncertain",
        "power": 9,
        "v4_peers": 365,
        "v6_peers": 17
      },
      {
        "asn": 50384,
        "type": "uncertain",
        "power": 65,
        "v4_peers": 236,
        "v6_peers": 5
      },
      {
        "asn": 50399,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 17,
        "v6_peers": 8
      },
      {
        "asn": 50414,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 3
      },
      {
        "asn": 50474,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 11,
        "v6_peers": 0
      },
      {
        "asn": 50522,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 19,
        "v6_peers": 1
      },
      {
        "asn": 50533,
        "type": "uncertain",
        "power": 6,
        "v4_peers": 21,
        "v6_peers": 7
      },
      {
        "asn": 50581,
        "type": "uncertain",
        "power": 34,
        "v4_peers": 181,
        "v6_peers": 24
      },
      {
        "asn": 50629,
        "type": "uncertain",
        "power": 54,
        "v4_peers": 199,
        "v6_peers": 73
      },
      {
        "asn": 50673,
        "type": "uncertain",
        "power": 161,
        "v4_peers": 884,
        "v6_peers": 224
      },
      {
        "asn": 50737,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 50763,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 6,
        "v6_peers": 3
      },
      {
        "asn": 50858,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 1
      },
      {
        "asn": 50889,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 0
      },
      {
        "asn": 50923,
        "type": "uncertain",
        "power": 15,
        "v4_peers": 47,
        "v6_peers": 6
      },
      {
        "asn": 51050,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 7,
        "v6_peers": 2
      },
      {
        "asn": 51088,
        "type": "uncertain",
        "power": 26,
        "v4_peers": 329,
        "v6_peers": 34
      },
      {
        "asn": 51154,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 0
      },
      {
        "asn": 51184,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 10,
        "v6_peers": 5
      },
      {
        "asn": 51185,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 18,
        "v6_peers": 14
      },
      {
        "asn": 51276,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 2,
        "v6_peers": 2
      },
      {
        "asn": 51333,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 5,
        "v6_peers": 3
      },
      {
        "asn": 51375,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 11
      },
      {
        "asn": 51468,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 23,
        "v6_peers": 6
      },
      {
        "asn": 51505,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 2,
        "v6_peers": 2
      },
      {
        "asn": 51514,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 1
      },
      {
        "asn": 51752,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 1
      },
      {
        "asn": 51758,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 0
      },
      {
        "asn": 51873,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 2
      },
      {
        "asn": 51978,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 7,
        "v6_peers": 1
      },
      {
        "asn": 52025,
        "type": "uncertain",
        "power": 42,
        "v4_peers": 18,
        "v6_peers": 95
      },
      {
        "asn": 52075,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 16,
        "v6_peers": 4
      },
      {
        "asn": 5390,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 1
      },
      {
        "asn": 5394,
        "type": "uncertain",
        "power": 7,
        "v4_peers": 34,
        "v6_peers": 3
      },
      {
        "asn": 5400,
        "type": "uncertain",
        "power": 169,
        "v4_peers": 866,
        "v6_peers": 69
      },
      {
        "asn": 5404,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 39,
        "v6_peers": 1
      },
      {
        "asn": 54113,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 18,
        "v6_peers": 22
      },
      {
        "asn": 54148,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 3
      },
      {
        "asn": 5416,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 388,
        "v6_peers": 1039
      },
      {
        "asn": 5418,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 5466,
        "type": "uncertain",
        "power": 14,
        "v4_peers": 51,
        "v6_peers": 8
      },
      {
        "asn": 54825,
        "type": "uncertain",
        "power": 7,
        "v4_peers": 11,
        "v6_peers": 5
      },
      {
        "asn": 54994,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 19,
        "v6_peers": 2
      },
      {
        "asn": 55219,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 1
      },
      {
        "asn": 5524,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 16,
        "v6_peers": 0
      },
      {
        "asn": 55256,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 16,
        "v6_peers": 0
      },
      {
        "asn": 55285,
        "type": "uncertain",
        "power": 12,
        "v4_peers": 62,
        "v6_peers": 21
      },
      {
        "asn": 55329,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 1
      },
      {
        "asn": 55685,
        "type": "uncertain",
        "power": 54,
        "v4_peers": 217,
        "v6_peers": 13
      },
      {
        "asn": 55818,
        "type": "uncertain",
        "power": 123,
        "v4_peers": 480,
        "v6_peers": 41
      },
      {
        "asn": 5583,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 35,
        "v6_peers": 6
      },
      {
        "asn": 559,
        "type": "uncertain",
        "power": 7,
        "v4_peers": 137,
        "v6_peers": 11
      },
      {
        "asn": 5606,
        "type": "uncertain",
        "power": 82,
        "v4_peers": 371,
        "v6_peers": 9
      },
      {
        "asn": 56381,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 1,
        "v6_peers": 5
      },
      {
        "asn": 56382,
        "type": "uncertain",
        "power": 13,
        "v4_peers": 26,
        "v6_peers": 21
      },
      {
        "asn": 56396,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 56457,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 4
      },
      {
        "asn": 56630,
        "type": "uncertain",
        "power": 24,
        "v4_peers": 211,
        "v6_peers": 26
      },
      {
        "asn": 56654,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 9,
        "v6_peers": 1
      },
      {
        "asn": 56665,
        "type": "uncertain",
        "power": 16,
        "v4_peers": 61,
        "v6_peers": 17
      },
      {
        "asn": 56675,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 56704,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 56911,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 28,
        "v6_peers": 11
      },
      {
        "asn": 56987,
        "type": "uncertain",
        "power": 10,
        "v4_peers": 21,
        "v6_peers": 10
      },
      {
        "asn": 57029,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 1
      },
      {
        "asn": 57043,
        "type": "uncertain",
        "power": 11,
        "v4_peers": 235,
        "v6_peers": 10
      },
      {
        "asn": 57112,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 25,
        "v6_peers": 3
      },
      {
        "asn": 57118,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 6,
        "v6_peers": 2
      },
      {
        "asn": 57124,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 57154,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 7,
        "v6_peers": 1
      },
      {
        "asn": 57169,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 30,
        "v6_peers": 6
      },
      {
        "asn": 57344,
        "type": "uncertain",
        "power": 213,
        "v4_peers": 1332,
        "v6_peers": 85
      },
      {
        "asn": 57463,
        "type": "uncertain",
        "power": 185,
        "v4_peers": 1362,
        "v6_peers": 85
      },
      {
        "asn": 57626,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 3
      },
      {
        "asn": 57758,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 8,
        "v6_peers": 10
      },
      {
        "asn": 57965,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 57976,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 12,
        "v6_peers": 3
      },
      {
        "asn": 58075,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 26,
        "v6_peers": 1
      },
      {
        "asn": 58138,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 0
      },
      {
        "asn": 58243,
        "type": "uncertain",
        "power": 11,
        "v4_peers": 82,
        "v6_peers": 14
      },
      {
        "asn": 58272,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 159,
        "v6_peers": 0
      },
      {
        "asn": 58291,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 8,
        "v6_peers": 5
      },
      {
        "asn": 58299,
        "type": "uncertain",
        "power": 39,
        "v4_peers": 33,
        "v6_peers": 56
      },
      {
        "asn": 58511,
        "type": "uncertain",
        "power": 69,
        "v4_peers": 424,
        "v6_peers": 54
      },
      {
        "asn": 58715,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 37,
        "v6_peers": 36
      },
      {
        "asn": 59545,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 14,
        "v6_peers": 2
      },
      {
        "asn": 59554,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 10,
        "v6_peers": 6
      },
      {
        "asn": 59570,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 59624,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 1
      },
      {
        "asn": 59642,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 24,
        "v6_peers": 0
      },
      {
        "asn": 59692,
        "type": "uncertain",
        "power": 115,
        "v4_peers": 421,
        "v6_peers": 0
      },
      {
        "asn": 59711,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 14,
        "v6_peers": 3
      },
      {
        "asn": 59827,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 59832,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 59865,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 8,
        "v6_peers": 4
      },
      {
        "asn": 59985,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 60022,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 21,
        "v6_peers": 18
      },
      {
        "asn": 60051,
        "type": "uncertain",
        "power": 26,
        "v4_peers": 592,
        "v6_peers": 0
      },
      {
        "asn": 60064,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 22,
        "v6_peers": 1
      },
      {
        "asn": 60111,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 9,
        "v6_peers": 6
      },
      {
        "asn": 60167,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 60294,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 22,
        "v6_peers": 0
      },
      {
        "asn": 60326,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 0,
        "v6_peers": 6
      },
      {
        "asn": 60350,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 7,
        "v6_peers": 0
      },
      {
        "asn": 60404,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 16,
        "v6_peers": 6
      },
      {
        "asn": 60476,
        "type": "uncertain",
        "power": 7,
        "v4_peers": 113,
        "v6_peers": 2
      },
      {
        "asn": 60486,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 1
      },
      {
        "asn": 60539,
        "type": "uncertain",
        "power": 6,
        "v4_peers": 4,
        "v6_peers": 2035
      },
      {
        "asn": 60822,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 16,
        "v6_peers": 0
      },
      {
        "asn": 61013,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 1
      },
      {
        "asn": 61049,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 16,
        "v6_peers": 2
      },
      {
        "asn": 61200,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 1
      },
      {
        "asn": 61349,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 23,
        "v6_peers": 0
      },
      {
        "asn": 61573,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 13
      },
      {
        "asn": 61599,
        "type": "uncertain",
        "power": 58,
        "v4_peers": 80,
        "v6_peers": 38
      },
      {
        "asn": 61955,
        "type": "uncertain",
        "power": 7,
        "v4_peers": 55,
        "v6_peers": 4
      },
      {
        "asn": 62005,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 7,
        "v6_peers": 2
      },
      {
        "asn": 62041,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 9,
        "v6_peers": 0
      },
      {
        "asn": 62044,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 30,
        "v6_peers": 0
      },
      {
        "asn": 6206,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 8,
        "v6_peers": 1
      },
      {
        "asn": 62097,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 62105,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 13,
        "v6_peers": 1
      },
      {
        "asn": 62167,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 3
      },
      {
        "asn": 62240,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 240,
        "v6_peers": 101
      },
      {
        "asn": 62390,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 0
      },
      {
        "asn": 62713,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 62715,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 62856,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 5,
        "v6_peers": 0
      },
      {
        "asn": 62902,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 1
      },
      {
        "asn": 62955,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 22,
        "v6_peers": 1
      },
      {
        "asn": 63113,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 7,
        "v6_peers": 0
      },
      {
        "asn": 63399,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 63927,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 4
      },
      {
        "asn": 6424,
        "type": "uncertain",
        "power": 18,
        "v4_peers": 177,
        "v6_peers": 20
      },
      {
        "asn": 64289,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 11
      },
      {
        "asn": 64475,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 3
      },
      {
        "asn": 6507,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 10,
        "v6_peers": 1
      },
      {
        "asn": 6661,
        "type": "uncertain",
        "power": 40,
        "v4_peers": 137,
        "v6_peers": 17
      },
      {
        "asn": 6667,
        "type": "uncertain",
        "power": 94,
        "v4_peers": 418,
        "v6_peers": 55
      },
      {
        "asn": 6677,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 8,
        "v6_peers": 1
      },
      {
        "asn": 6681,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 3,
        "v6_peers": 0
      },
      {
        "asn": 6774,
        "type": "uncertain",
        "power": 61,
        "v4_peers": 626,
        "v6_peers": 0
      },
      {
        "asn": 6775,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 4,
        "v6_peers": 3
      },
      {
        "asn": 6823,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 32,
        "v6_peers": 65
      },
      {
        "asn": 6830,
        "type": "uncertain",
        "power": 1557,
        "v4_peers": 12052,
        "v6_peers": 2044
      },
      {
        "asn": 702,
        "type": "uncertain",
        "power": 312,
        "v4_peers": 4353,
        "v6_peers": 2131
      },
      {
        "asn": 7049,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 12,
        "v6_peers": 1
      },
      {
        "asn": 7342,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 17,
        "v6_peers": 17
      },
      {
        "asn": 7500,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 7522,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 54,
        "v6_peers": 1
      },
      {
        "asn": 7552,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 281,
        "v6_peers": 6
      },
      {
        "asn": 7679,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 1
      },
      {
        "asn": 7713,
        "type": "uncertain",
        "power": 90,
        "v4_peers": 384,
        "v6_peers": 382
      },
      {
        "asn": 8038,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 4,
        "v6_peers": 3
      },
      {
        "asn": 8218,
        "type": "uncertain",
        "power": 156,
        "v4_peers": 549,
        "v6_peers": 82
      },
      {
        "asn": 8262,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 17,
        "v6_peers": 0
      },
      {
        "asn": 8283,
        "type": "uncertain",
        "power": 25,
        "v4_peers": 17,
        "v6_peers": 30
      },
      {
        "asn": 8298,
        "type": "uncertain",
        "power": 8,
        "v4_peers": 10,
        "v6_peers": 7
      },
      {
        "asn": 8302,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 7,
        "v6_peers": 7
      },
      {
        "asn": 8304,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 12,
        "v6_peers": 3
      },
      {
        "asn": 8309,
        "type": "uncertain",
        "power": 18,
        "v4_peers": 49,
        "v6_peers": 11
      },
      {
        "asn": 8315,
        "type": "uncertain",
        "power": 6,
        "v4_peers": 70,
        "v6_peers": 17
      },
      {
        "asn": 8359,
        "type": "uncertain",
        "power": 466,
        "v4_peers": 2615,
        "v6_peers": 148
      },
      {
        "asn": 8365,
        "type": "uncertain",
        "power": 13,
        "v4_peers": 108,
        "v6_peers": 16
      },
      {
        "asn": 8368,
        "type": "uncertain",
        "power": 21,
        "v4_peers": 136,
        "v6_peers": 29
      },
      {
        "asn": 8399,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 27,
        "v6_peers": 3
      },
      {
        "asn": 8400,
        "type": "uncertain",
        "power": 151,
        "v4_peers": 861,
        "v6_peers": 27
      },
      {
        "asn": 8422,
        "type": "uncertain",
        "power": 34,
        "v4_peers": 106,
        "v6_peers": 39
      },
      {
        "asn": 8426,
        "type": "uncertain",
        "power": 18,
        "v4_peers": 113,
        "v6_peers": 25
      },
      {
        "asn": 8447,
        "type": "uncertain",
        "power": 228,
        "v4_peers": 715,
        "v6_peers": 77
      },
      {
        "asn": 8452,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 10,
        "v6_peers": 0
      },
      {
        "asn": 8462,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 26,
        "v6_peers": 1
      },
      {
        "asn": 8473,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 104,
        "v6_peers": 10
      },
      {
        "asn": 8487,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 12,
        "v6_peers": 1
      },
      {
        "asn": 8529,
        "type": "uncertain",
        "power": 33,
        "v4_peers": 14,
        "v6_peers": 107
      },
      {
        "asn": 8560,
        "type": "uncertain",
        "power": 16,
        "v4_peers": 451,
        "v6_peers": 30
      },
      {
        "asn": 8587,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 8,
        "v6_peers": 2
      },
      {
        "asn": 8632,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 12,
        "v6_peers": 1
      },
      {
        "asn": 8637,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 4
      },
      {
        "asn": 8657,
        "type": "uncertain",
        "power": 70,
        "v4_peers": 251,
        "v6_peers": 16
      },
      {
        "asn": 8674,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 4,
        "v6_peers": 4
      },
      {
        "asn": 8732,
        "type": "uncertain",
        "power": 136,
        "v4_peers": 453,
        "v6_peers": 10
      },
      {
        "asn": 8758,
        "type": "uncertain",
        "power": 30,
        "v4_peers": 113,
        "v6_peers": 33
      },
      {
        "asn": 8763,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 1
      },
      {
        "asn": 8764,
        "type": "uncertain",
        "power": 15,
        "v4_peers": 0,
        "v6_peers": 70
      },
      {
        "asn": 8767,
        "type": "uncertain",
        "power": 71,
        "v4_peers": 247,
        "v6_peers": 69
      },
      {
        "asn": 8801,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 9,
        "v6_peers": 1
      },
      {
        "asn": 8821,
        "type": "uncertain",
        "power": 8,
        "v4_peers": 24,
        "v6_peers": 7
      },
      {
        "asn": 8839,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 4,
        "v6_peers": 1
      },
      {
        "asn": 8859,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 7,
        "v6_peers": 0
      },
      {
        "asn": 8866,
        "type": "uncertain",
        "power": 103,
        "v4_peers": 1225,
        "v6_peers": 45
      },
      {
        "asn": 8881,
        "type": "uncertain",
        "power": 153,
        "v4_peers": 843,
        "v6_peers": 233
      },
      {
        "asn": 8918,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 2,
        "v6_peers": 0
      },
      {
        "asn": 8926,
        "type": "uncertain",
        "power": 47,
        "v4_peers": 248,
        "v6_peers": 5
      },
      {
        "asn": 9008,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 13,
        "v6_peers": 6
      },
      {
        "asn": 9009,
        "type": "uncertain",
        "power": 11,
        "v4_peers": 200,
        "v6_peers": 47
      },
      {
        "asn": 9031,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 11,
        "v6_peers": 1
      },
      {
        "asn": 9036,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 9,
        "v6_peers": 0
      },
      {
        "asn": 9050,
        "type": "uncertain",
        "power": 166,
        "v4_peers": 411,
        "v6_peers": 16
      },
      {
        "asn": 9115,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 1
      },
      {
        "asn": 9119,
        "type": "uncertain",
        "power": 46,
        "v4_peers": 141,
        "v6_peers": 17
      },
      {
        "asn": 9120,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 6,
        "v6_peers": 1
      },
      {
        "asn": 9123,
        "type": "uncertain",
        "power": 7,
        "v4_peers": 276,
        "v6_peers": 21
      },
      {
        "asn": 9136,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 9,
        "v6_peers": 10
      },
      {
        "asn": 9145,
        "type": "uncertain",
        "power": 19,
        "v4_peers": 0,
        "v6_peers": 32
      },
      {
        "asn": 9150,
        "type": "uncertain",
        "power": 4,
        "v4_peers": 16,
        "v6_peers": 4
      },
      {
        "asn": 9158,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 32,
        "v6_peers": 2
      },
      {
        "asn": 917,
        "type": "uncertain",
        "power": 5,
        "v4_peers": 9,
        "v6_peers": 9
      },
      {
        "asn": 9299,
        "type": "uncertain",
        "power": 2,
        "v4_peers": 145,
        "v6_peers": 10
      },
      {
        "asn": 9304,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 0,
        "v6_peers": 9
      },
      {
        "asn": 9381,
        "type": "uncertain",
        "power": 6,
        "v4_peers": 0,
        "v6_peers": 9
      },
      {
        "asn": 9434,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 9498,
        "type": "uncertain",
        "power": 17,
        "v4_peers": 4430,
        "v6_peers": 101
      },
      {
        "asn": 9583,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 1,
        "v6_peers": 0
      },
      {
        "asn": 9605,
        "type": "uncertain",
        "power": 1,
        "v4_peers": 744,
        "v6_peers": 325
      },
      {
        "asn": 9902,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 96,
        "v6_peers": 0
      },
      {
        "asn": 9930,
        "type": "uncertain",
        "power": 3,
        "v4_peers": 57,
        "v6_peers": 2
      }
    ]
  },
  "metadata": {}
}



Example Output (Console)
------------------------

✅ Connected to MongoDB successfully!
🚀 Starting RIPEstat ETL pipeline (3-endpoint version)...

[EXTRACT] Fetching data from as-overview endpoint...
[EXTRACT] Successfully fetched data from as-overview.
[TRANSFORM] Data transformed for as-overview.
[LOAD] Inserted document ID: 68f36c83119d18c1765cadb8

[EXTRACT] Fetching data from as-routing-consistency endpoint...
[EXTRACT] Successfully fetched data from as-routing-consistency.
[TRANSFORM] Data transformed for as-routing-consistency.
[LOAD] Inserted document ID: 68f36c84119d18c1765cadb9

[EXTRACT] Fetching data from asn-neighbours endpoint...
[EXTRACT] Successfully fetched data from asn-neighbours.
[TRANSFORM] Data transformed for asn-neighbours.
[LOAD] Inserted document ID: 68f36c87119d18c1765cadba

✅ ETL pipeline completed successfully!

📊 Architecture Diagram
--------------------------
     ┌────────────┐       ┌─────────────┐       ┌──────────────┐
     │  RIPEstat  │  →→→  │  Transform  │  →→→  │  MongoDB     │
     │  API (3x)  │       │  (Clean/Map)│       │  ripe_data   │
     └────────────┘       └─────────────┘       └──────────────┘
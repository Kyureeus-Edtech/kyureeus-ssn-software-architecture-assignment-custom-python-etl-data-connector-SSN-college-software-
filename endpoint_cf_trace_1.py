ENDPOINT_CONFIG = {
    "name": "CF Trace for example.com",
    "api_type": "cf_trace",
    "host": "example.com",           # <-- change this to your host behind Cloudflare
    "format": "json",
    "collection": "cf_trace_example",# <-- collection for this endpoint
    "data_key_path": [],             
    "id_key": "host_ts"
}

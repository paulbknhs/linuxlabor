#!/home/paul/uni/linux/connect/venv/bin/python
from proteus import config

print("Connecting to the server...")
# First direct connection test (will be changed for later tests):
conf = config.set_xmlrpc("https://admin:trytond-pass@ll-web-02.incus:443/health/")
print("Success")

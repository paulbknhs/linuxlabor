## 5.3 GNU Health Deployment Part II

### 5.3.1 Reverse proxy: HTTP

- Reconfigure your Nginx on ll-web to act as reverse proxy for GNU Health. Use HTTP
  for now to only test the reverse proxy setup without TLS.

  ```
  debian@ll-web-02:~$ sudo cat /etc/nginx/sites-available/gnuhealth
  server {
      listen 80 default_server;
      server_name ll-web-02.incus;

      location / {
          proxy_pass https://10.100.30.23:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
      }
  }
  ```

- Adjust your proteus script connect_to_server.py on ll-admin to test if the reverse
  proxy works.
  ```
  conf = config.set_xmlrpc("https://admin:trytond-pass@ll-web-02.incus:80/health/")
  ```
- Test the reverse proxy with the GNU Health client on your laptop.

### 5.3.2 Setup with TLS

- ll-db: Configure the paths of the certificate and key in postgresql.conf

```
ssl = on
ssl_ca_file = '/etc/ssl/certs/cacert.pem'
ssl_cert_file = '/etc/ssl/certs/ll-db-02.incus.crt'
ssl_key_file = '/etc/ssl/private/postgresql.key'
```

- ll-db: Change the access policy configuration to only allow encrypted connections

```
hostssl    health          gnuhealth    10.100.30.23/32         md5
```

- Test and verify that the connection is encrypted with psql from ll-admin and ll-app

```
psql "sslmode=require host=10.100.30.24 user=gnuhealth dbname=health"
```

- ll-app: Add query strings to the PostgreSQL URI so that the certificate will be fully
  verified. **Tip:** Read the chapter 34.19.1 Client Verification of Server Certificates of the
  PostgreSQL documentation to identify the _two_ parameters you have to set in the query
  string. The goal is to use the configuration ”[…] recommended in most security-sensitive
  environments”.
  `sslmode=verify-full&sslrootcert=/etc/ssl/certs/cacert.crt`
- Test that the connection to the DB still works after setting up encryption by using the
  proteus script on ll-admin and the GNU Health client on your laptop.
  `  conf = config.set_xmlrpc("https://admin:trytond-pass@ll-web-02.incus:8443/health/")`

- ll-app: Activate HTTPS for GNU Health and set the paths to the certificate and key in
  uwsgi_trytond.ini
  `https = 0.0.0.0:8443,/etc/ssl/certs/gnuhealth.crt,/etc/ssl/private/gnuhealth.key,HIGH`

**Tip:** Verify that the gnuhealth user can access the certificate _and_ the key. If this does not
work, then check if all the directory access rights are correct.

- Test the encrypted connection with the proteus script on ll-admin and with the GNU
  Health client on your laptop.
- ll-web: Reconfigure Nginx so that connections from clients via HTTPS will be proxied to
  GNU Health. The certificate of the GNU Health server must be verified. Configure Nginx to
  pass the client IP to GNU Health (see e.g. Passing Request Headers, proxy_set_header,
  embedded variables).

```
  server {
    listen 443 ssl default_server;
    server_name ll-web-02.incus;

    include snippets/ssl.conf;
    include snippets/linuxlab.conf;
    location / {
        proxy_pass https://10.100.30.23:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
  }
```

- Explain all proxy*… and ssl*… settings that you use briefly; add links to sources if it is necessary or useful.

```
proxy_pass: where to proxy the connection through
proxy_set_header: set the headers for the proxied request
#ssl.conf: contains the SSL configuration, e.g. paths to certificates
```

- Test the connection again with the proteus script and the GNU Health client

- Test the TLS connections with openssl including the verification of the certificates for …
- … Nginx on ll-web,
- … GNU Health on ll-app,
- … PostgreSQL on ll-db. **Tip:** Because _opportunistic TLS_ (what is this?) is used, an additional parameter is here needed.

```
-starttls postgres
# opportunistic tls starts unencrypted and then switches to encrypted but not from the beginning
```

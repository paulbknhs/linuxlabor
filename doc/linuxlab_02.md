# 4 Webserver, TLS and CA

## 4.1 Webserver: HTTP

Install the nginx software on **ll-web** and make sure the default page is accessible over HTTP
via the following methods:

```bash
sudo apt install nginx
```

- From **ll-web** itself using curl(1)

```bash
curl 127.0.0.1:80
```

- From **ll-admin** using curl(1)

```bash
curl ll-web-02.incus
```

> set incus as no_proxy

- From your computer/laptop via the SOCKSv5 proxy using curl(1)

```bash
curl --socks5-hostname localhost:3300 ll-web-02.incus
```

- Repeat the three tests above with ”netcat”

```bash
# from ll-admin
echo -e "GET / HTTP/1.1\nHost: ll-web-02.incus\n\n" | nc ll-web-02.incus 80
```

```bash
# from ll-web
echo -e "GET / HTTP/1.1\nHost: localhostn\n" | nc localhost 80
```

```bash
# from home laptop

```

- From your computer/laptop via a SOCKSv5 proxy using a browser. Use the fully qualified
  domain name for this, not the IP of your server (resp. VM). (Refer to the introductory talk
  for information and further questions regarding the use of a SOCKSv5 proxy for testing.)

  > ssh with option DynamicForward on Port 3300, same Port set in librefox

## 4.2 Webserver: HTTPS

### 4.2.1 Snakeoil Certificates

1. Which package do you need to install on debian in order to get an auto-generated ”snakeoil”
   certificate (and corresponding private key)? **Hint:** Look at the various config files of nginx
   that are installed with the nginx package.
   > ssl-cert in `/etc/nginx/snippets/snakeoil.conf`
2. Install this ”snakeoil” certs package and find out where the cert and key are located. What
   are their file permissions, owner and group?
   > in `/etc/ssl/certs/ssl-cert-snakeoil.pem` and `/etc/ssl/private/ssl-cert-snakeoil.key`
   > with -rw-r--r-- and -rw-r-----
3. Activate HTTPS for nginx by using the already installed config files, including the snippets
   file to use the ”snakeoil” certificate
   > commenting out lines in `/etc/nginx/sites-available/default`
4. Use the same tests that you used for HTTP above to see if HTTPS works properly. Does
   your browser complain about something?
   > ll-web-02.incus uses an invalid security certificate.
   > The certificate is not trusted because it is self-signed.
5. Use curl(1) to get the SSL/TLS certificate of the webserver and save it in a file.

```bash
curl --insecure -w %{certs} https://ll-web-02.incus > cacert.pem
```

6. Inspect this certificate file with openssl(1) and answer the following questions: - For which hostname is this cert valid? - What is the meaning of the certificate extension where the hostname appears again? - How long can the cert be used and who issued it? - From which config are all these values set during generation of the snakeoil cert?
   (For this, openssl is not needed.)
   > Hostname: `ll-web-02`
   > The same cert can be used for other hostnames
   > Not Before: May 9 13:08:18 2025 GMT; Not After : May 7 13:08:18 2035 GMT
   > Issuer: CN = ll-web-02
   > `/usr/sbin/make-ssl-cert`
7. Configure nginx to automatically and permanently redirect from HTTP to HTTPS and test
   this behaviour afterwards

   ```
   server {
     listen 80;
     server_name _;
     return 301 https://$host$request_uri;
   }
   ```

8. Configure nginx to use secure protocols and ciphers. One possible ressource that might
   help you is the mozilla ssl configuration generator.

```
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ecdh_curve X25519:prime256v1:secp384r1;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-CHACHA20-POLY1305;
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:MozSSL:10m;  # about 40000 sessions

    ssl_stapling on;
    ssl_stapling_verify on;

    resolver 127.0.0.1;
```

### 4.2.2 Creating a private CA

1. In general you can follow the guide from the Ubuntu server documentation but there are
   a few things that you should keep in mind when configuring the CA: - Set the _copy_extensions_ option so that certain values, like _subjectAltName_, are not
   ignored when signing a CSR. Read the section about _copy_extensions_ and the WARN-
   INGS section in the openssl-ca manpage. - Set unique_subject so that several valid certificate entries may have the exact
   same subject (This is convenient for testing, e.g. when iterating a CSR until the
   corresponding signed cert is correct)

   ```
   sudo mkdir /etc/ssl/CA
   sudo mkdir /etc/ssl/newcerts
   sudo sh -c "echo '01' > /etc/ssl/CA/serial"
   sudo touch /etc/ssl/CA/index.txt
   ```

   > changed the following in /etc/ssl/openssl.cnf
   > dir = /etc/ssl # Where everything is kept
   > database = $dir/CA/index.txt # database index file.
   > certificate = $dir/certs/cacert.pem # The CA certificate
   > serial = $dir/CA/serial # The current serial number
   > private_key = $dir/private/cakey.pem# The private key
   > copy_extensions = copy
   > unique_subject = no

   ```
   openssl req -new -x509 -extensions v3_ca -keyout cakey.pem -out cacert.pem -days 3650
   sudo mv cakey.pem /etc/ssl/private/
   sudo mv cacert.pem /etc/ssl/certs/
   ```

2. How do you prevent your CA from signing CSRs where the option basicConstraints
   is set to CA:TRUE?
3. Expore the **CA cert** with openssl-x509(1). Are all entries as they should be? Copy
   the full certificate information (not the cert itself!) into your markdown documentation.

---

Certificate:
Data:
Version: 3 (0x2)
Serial Number:
72:71:e0:6e:3d:17:23:8b:05:d3:96:c1:8e:cc:1a:91:fe:8f:36:54
Signature Algorithm: sha256WithRSAEncryption
Issuer: C = DE, ST = Niedersachsen, L = Hannover, O = Leibniz Universitaet Hannover, OU = LinuxLab, CN = ll-admin-02.incus, emailAddress = krojanski@chi.uni-hannover.de
Validity
Not Before: May 12 13:54:00 2025 GMT
Not After : May 10 13:54:00 2035 GMT
Subject: C = DE, ST = Niedersachsen, L = Hannover, O = Leibniz Universitaet Hannover, OU = LinuxLab, CN = ll-admin-02.incus, emailAddress = krojanski@chi.uni-hannover.de
Subject Public Key Info:
Public Key Algorithm: rsaEncryption
Public-Key: (2048 bit)
Modulus:
00:b1:cb:94:71:9b:ca:05:0d:7b:5e:d7:55:f2:a3:
24:65:68:d4:38:36:f7:22:d7:3d:28:9a:a9:e5:f7:
60:95:00:e8:ba:61:a3:ed:86:82:04:32:4e:fa:c6:
f8:08:18:21:28:dc:fe:ad:1b:03:e1:ac:72:91:16:
9b:8e:c5:5e:92:55:8a:ab:ed:7e:ce:6c:66:25:ad:
ce:f6:bb:ed:e4:91:01:ea:d7:56:18:fe:59:b6:fd:
42:13:e6:23:89:32:84:bb:b5:e1:54:41:b6:15:32:
a9:e4:6d:7e:a4:48:88:60:c5:bd:e7:9b:7c:31:28:
32:3c:b2:7e:59:58:e7:d3:41:5d:9e:ab:dc:75:b4:
f9:8e:80:6a:cc:eb:f9:47:0e:a3:4b:ac:32:10:c4:
18:28:6e:fc:73:61:fb:25:43:de:51:74:70:43:28:
b2:c9:af:9f:bb:33:39:4a:f3:bb:f8:bc:56:f3:70:
be:6d:64:fd:59:37:76:79:fa:50:f3:ac:59:82:b2:
20:35:a2:55:1d:cd:fc:85:ee:14:c3:d6:dd:c2:94:
9e:0b:6d:da:25:d8:38:d7:fd:29:7e:21:4c:92:94:
25:3d:2b:61:2a:6b:a8:de:61:be:61:30:25:17:6e:
1e:a2:e0:64:dc:a0:3d:0c:16:d6:7e:56:67:43:6e:
8b:5d
Exponent: 65537 (0x10001)
X509v3 extensions:
X509v3 Subject Key Identifier:
86:A3:74:27:05:67:85:F1:23:68:3B:C2:11:CF:44:FC:DF:24:03:6C
X509v3 Authority Key Identifier:
86:A3:74:27:05:67:85:F1:23:68:3B:C2:11:CF:44:FC:DF:24:03:6C
X509v3 Basic Constraints: critical
CA:TRUE
Signature Algorithm: sha256WithRSAEncryption
Signature Value:
03:ec:aa:e5:bc:ba:3a:1b:c4:28:c1:cc:30:4a:6b:9c:bc:63:
ed:04:f7:78:42:80:96:f8:cd:62:d1:b7:c4:45:9c:0e:19:58:
a3:b5:1b:bd:97:9d:36:a1:46:91:d5:a1:2d:e4:6d:38:e0:27:
6b:39:80:4a:df:6d:88:50:46:82:63:f5:52:86:be:45:e2:75:
4a:ea:2b:ba:67:28:cb:94:95:5a:4f:9e:5d:b6:84:7b:1a:22:
ec:5f:d9:31:7e:0f:c9:0f:45:92:8d:ce:4c:3d:cb:2e:e8:19:
fd:c3:03:be:36:1e:46:f9:df:9d:67:ce:48:4a:5c:a7:a9:ab:
18:8f:5c:dc:05:30:54:b3:b4:b3:16:80:fa:c0:a8:2c:64:03:
94:65:dc:63:71:54:03:bb:6a:55:9b:35:6d:8a:b2:d5:3e:bc:
64:33:ad:97:69:92:d0:1d:2f:9c:7c:86:38:eb:0b:7d:a5:07:
88:ca:33:8a:52:8b:94:85:ea:e1:3c:fa:64:83:55:1f:b7:f1:
6c:c5:c3:34:6e:e4:7f:79:b2:08:57:34:80:d7:8f:cb:d0:9b:
1b:cc:94:83:16:30:14:d7:23:95:56:32:bb:92:e4:46:29:1c:
cf:12:82:ca:4f:ad:d7:9d:e9:68:a5:15:df:99:6e:bb:22:e8:
a3:dc:bc:e0

---

### 4.2.3 Generating a CSR

- Specify the values for the CSR in a config file and use that, especially when you need to
  generate multiple CSRs.

  ```
  [ req ]
  default_bits = 4096
  default_keyfile = server-key.pem
  default_md = sha256
  distinguished_name = req_distinguished_name
  req_extensions = v3_req
  prompt = no


  [ req_distinguished_name ]
  countryName = DE
  stateOrProvinceName = Niedersachsen
  localityName = Hannover
  organizationName = Leibniz Universitaet Hannover
  organizationalUnitName = LinuxLab
  commonName = ll-web-02.incus
  emailAddress = paul.bakenhus@stud.uni-hannover.de

  [ v3_req ]
  basicConstraints = CA:FALSE
  keyUsage = nonRepudiation, digitalSignature, keyEncipherment
  subjectAltName = @alt_names

  [ alt_names ]
  DNS.1 = ll-web-02.incus
  ```

- When specifying the address (no matter if in the CN, the _subjectAltName_ or elsewhere)
  always append the TLD (e.g. ‘.incus’). This ensures that name resolution works correctly
  in all cases and that the address in the certificate always matches the address used to
  connect to a server.
- Set a _subjectAltName_ extension. This is needed by some applications, like browsers, to
  actually accept the certificate. See the manpages openssl-req and x509v3_config
  for how to accomplish this. In addition, listing 1 shows a template for a certificate signing
  request config file.

1. What command did you use to generate a CSR on one of your machines?

```bash
  openssl genrsa -des3 -out server.key 2048
  openssl rsa -in server.key -out server.key.insecure
  mv server.key server.key.secure
  mv server.key.insecure server.key
  openssl req -new -key server.key -out server.csr
```

2. Check that the generated CSR is correct
3. What command can you use to check the values (e.g. validity timestamps, common name
   or extensions) of your signed certificates?

```bash
  openssl req -in server.csr -text -noout
```

4. Check all the values of the certificate before using it for the web server

### 4.2.4 Using your new certificates

1. Use the standard paths for the server certificate, server key and CA certificate. Think
   before you change access rights to folders or files. There are several ways to accomplish
   that the files can be accessed by services (service users). Use the safest one, do not
   use something like 0777 for files and folders. For inspiration, refer to the tasks (and their
   solutions) above regarding the snakeoil certificates.
   ```bash
   chmod 600 /etc/ssl/private/server.key
   chown root:root /etc/ssl/private/server.key
   chmod 644 /etc/ssl/certs/server.crt
   chown root:root /etc/ssl/certs/server.crt
   chmod 644 /etc/ssl/certs/cacert.pem
   chown root:root /etc/ssl/certs/cacert.pem
   ```
2. How do you ensure that the web server can use the private key, which by default may be
   password protected?
3. Where do you have to put the CA certificate on the machines other than **ll-admin** so that
   tools like curl can use them?
   ```
   /usr/local/share/ca-certificates/
   ```
4. Where do you have to put the CA certificate on your computer/laptop so that your browser
   uses it to verify the webserver certificate?
   ```
   /usr/local/share/ca-certificates/
   ```
5. Check carefully that the web server presents the correct certificate and that HTTPS works: - Use curl(1) and openssl-s_client(1) on **ll-web** - Use curl(1) and openssl-s_client(1) on **ll-admin** - Use curl(1), openssl-s_client(1) and your browser on your laptop. Which
   program does **not** have an option to use a socks proxy? In this case, use proxychains-
   ng in combination with a proxychains.conf file where you e.g. specify the SOCKS
   version, IP and Port. If you use linux, be careful to install the correct package!
   This test with proxychains is needed again for the final task and final report.
   added the cacert `sudo cp ca.crt /usr/local/share/ca-certificates/my-ca.crt`
   reload certificates with `sudo update-ca-certificates`
   in browser i added into librewolf as a certificate authority
   `openssl-s_client -connect ll-web-02.incus:443 -CAfile /etc/ssl/certs/cacert.pem`

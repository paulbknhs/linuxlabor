# 5 GNU Health

## 5.1 GNU Health

1. Installation of the GNU Health application with DB backend, but **without** a reverse proxy
   and **without** encryption of the database connection
2. **Using** Nginx as **reverse proxy** with certificates from own CA for **HTTPS** and for **SSL/TLS**

**encryption** of the database connection

## 5.2 GNU Health Deployment Part I

1. Install PostgreSQL server
2. What is the path where all configuration files are located? (some of them maybe inside
   subdirectories)
   `sudo -u postgres psql -c 'SHOW config_file'`
   `/etc/postgresql/15/main/postgresql.conf`
3. Explain all defaults in the **PostgreSQL Client Authentication Configuration File**
4. Create a new user/role ”gnuhealth”
   ```
   sudo su - postgres
   createuser gnuhealth
   ```
5. Create a new database called ”health” with owner ”gnuhealth”
   `createdb health`

```SQL
ALTER DATABASE health OWNER TO gnuhealth
```

6. Change the **PostgreSQL Access Policy File** to allow access to the database ”health”
   from ll-app
   `listen_addresses = '*' #in postgresql.conf`
   `host    health          gnuhealth       10.100.30.23/32         md5 in /etc/postgresql/15/main/pg_hba.conf`

7. Check with nmap and netcat if the database is accessible from ll-app
   `nmap -p 5432 10.100.30.24`
8. Install the PostgreSQL client and connect to the database server
   `sudo apt install postgresql-client`
   `psql -h 10.100.30.24 -U gnuhealth -d health`
9. Install python3-pip, python3-venv, libssl-dev and libpq-dev
   `sudo apt install python3-pip python3-venv libssl-dev libpq-dev`
10. Create a service user ”gnuhealth” with /opt/gnuhealth as $HOME and no login shell
    `sudo useradd --system --home /opt/gnuhealth --shell /usr/sbin/nologin gnuhealth`
11. Open a shell as the new ”gnuhealth” user and … - Create a python virtual environment (venv) in /opt/gnuhealth/venv, activate it
    and install the pip packages gnuhealth-all-modules and uwsgi - Create the folders etc, var/log and var/lib inside the ”gnuhealth” user home
    directory - Copy the following files from Stud.IP to the new /opt/gnuhealth/etc folder: - trytond.conf - gnuhealth_log.conf - uwsgi_trytond.ini - In the file trytond.conf … - Replace <URI> with the correct URI - Set the <DATA PATH> to /opt/gnuhealth/var/lib - Set the file access mode to read & write for owner and group - Initialize the database ”health” within the python venv by using trytond-admin.
    to use your
    Which flags of this command are necessary to accomplish this (e.g.
    tryton config file)? If the command works, it runs for a while and at the end appears
    a password prompt; what is this password for? - Exit the ”gnuhealth” user shell

    ```bash
      sudo mkdir /opt/gnuhealth
      sudo chown gnuhealth:gnuhealth /opt/gnuhealth
      pip --proxy http://web-proxy.rrzn.uni-hannover.de:3128 gnuhealth-all-modules uwsgi
      mkdir -p var/log var/lib etc
      chmod 660 /opt/gnuhealth/etc/trytond.conf
      chown gnuhealth:gnuhealth /opt/gnuhealth/etc/trytond.conf
      trytond-admin -c /opt/gnuhealth/etc/trytond.conf -d health --all
      mail: paul.bakenhus@stud.uni-hannover.de
      pw: trytond-pass
    ```

12. Use the unit file gnuhealth.service from Stud.IP to create a new systemd service
    (running in system mode!); see e.g. Debian Wiki
    ` sudo vim /etc/systemd/system/gnuhealth.service`
13. Enable and activate this new service, check it’s status

```bash
sudo systemctl daemon-reload
sudo systemctl enable gnuhealth.service
sudo systemctl start gnuhealth.service
sudo systemctl status gnuhealth.service
```

14. Check if a GNU Health process is listening on the service port

```bash
sudo netstat -tuln | grep 8000
```

15. Test the GNU Health application with a small python script which uses proteus, a python
    library to connect the the GNU Health server (which is also used by the GTK GNU Health
    GUI client). Install the proteus PyPI package in a venv on your ll-admin server and use
    the script in listing 2 for testing.
16. Test the application with the GNU Health client on your laptop. Use again a python venv
    and install the gnuhealth-client pip package. **Before**, install all requirements for Py-
    GObject/GTK: python3-gi python3-gi-cairo gir1.2-gtk-3.0 libcairo2-dev
    libgirepository1.0-dev python3-dev (deb package names)
    To successfully connect to the GNU Health application on your server (ll-app), use ssh
    dynamic port forwarding (i.e. a SOCKSv5 proxy connection). Because the GNU Health
    client (and the proteus script if you use this also on your laptop) cannot use a SOCKSv5
    proxy directly, you have to use e.g. proxychains-ng (”… a preloader which hooks calls to
    sockets in dynamically linked programs and redirects it through one or more socks/http
    proxies.”).

## 5.3 GNU Health Deployment Part II

# 6 Backup & Restore

## 6.1 Terms and concepts

## 6.2 (Relational) Database Backups

## 6.3 PostgreSQL & Barman

## 6.4 Backup & Restore of GNU Health

### 6.4.1 Barman & GNU Health

- Install barman and cron on ll-admin

```bash
  sudo apt install barman cron
```

- What is the system user for Barman?

```bash
  cat /etc/passwd | grep barman
```

- Where is the home directory of the Barman system user?

```bash
  /var/lib/barman
```

- Make a copy of the barman template file for the backup_method=postgres in order to
  modify it.

```bash
   sudo cp /etc/barman.d/ssh-server.conf-template /var/lib/barman/
```

- In the Barman configuration file …

  - change the name of the config section and description in your copy;
  - change the host parameters to your DB server;
  - set the minimum number of backups to retain to 3
  - set the retention policy so that the maximum age of the last backup is **one month**
    and that only backups are kept which are needed to perform a PITR in this period

    ```bash
      [psql]
      description =  "PostgresQL DB for gnuhealth"

      conninfo = host=ll-db-02.incus user=health dbname=gnuhealth

      streaming_conninfo = host=pg user=streaming_barman

      backup_method = postgres

      streaming_archiver = on
      slot_name = barman

      minimum_redundancy = 3
      last_backup_maximum_age = 1 MONTHS
      retention_policy = RECOVERY WINDOW OF 30 DAYS
    ```

- Generate a ssh-keypair for the Barman system user
- Generate a ssh-keypair for the postgres user
- Test that both users can login as each other on the corresponding server via ssh _without_
  _a password_ (these logins are used for automation, not interactively)

```bash
  sudo su barman
  ssh-keygen -t ed25519
  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHA+5kL5nbiXFSpVNux3y+SPHzKmSr2Dt5KvhJhZLQlU barman@ll-admin-02
  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICVup3PFNP4HLGL3fbn6QtRvL14nvtznBGqzXOg4iX0v postgres@ll-db-02
```

- Use a PostgreSQL password file to be able to connect to your database server; the first
  username should be barman, the second username streaming_barman
- On your DB server, create a _superuser_ for the Barman connection. Then create another
  user for backup and WAL streaming; consult the Barman configuration file which type of
  PostgreSQL user this is and what privilege it needs.
- Configure two corresponding authentication records for PostgreSQL. **Tipp from the con-**

**fig file:** The ”all” keyword does not match ”replication”.

- Install the package barman-cli on your DB server.
- Which binaries are installed with this package?
- Read their (short) man pages or the command reference in the Barman user guide to
  configure the archive_command and restore_command parameters of the main Post-
  greSQL config file.
- In the main PostgreSQL config file … - enable archiving - check that the wallreplica - in the archive_command command, use the %p placeholder for WAL_PATH
  and the same for WAL_DEST in the restore_command - use the %f placeholder for WAL_NAM in the restore_command - in the restore_command, configure that also partial WAL files are
  received
- Start the barman backup job in the background if necessary: sudo -u barman barman
  cron (backup server)
- Create enough base backups to fulfill your configured minimum requirements by running
  barman backup <SERVER_NAME> as the Barman user three times
- Use Barman check to see if everything works
- Set up a cronjob to create a new base backup (running barman backup … to adhear to
  your last_backup_maximum_age policy set in the Barman config
- Testing the restore: Stop the PostgreSQL service and move its data directory
  /var/lib/postgresql/15/main
  to simulate data loss
- Restore from the latest backup
- Check if the restore was successful in <data_directory>/postgresql.auto.conf
- Start PostgreSQL again and check if GNU Health is still/again working

## 6.5 Restic

- ll-app: Create a ssh-keypair for the gnuhealth user
- ll-admin: Create a new user restic-backup (for backup connection and storage)
- Ensure that the gnuhealth user can login a the restic-backup user
- Install restic on ll-app and initialize the backup repository in a folder called restic-
  repo inside the home directory of the restic-backup user
- Set the encryption password and store it in a hidden file of this home directory to be able
  to specify it automatically. Set the file permissions accordingly! Restic documentation
- Create a test file with known content inside the folder which will be backed up
- Create your first backup manually
- Setup a cronjob to backup every 5 minutes
- Change the content of the file and create new ones over some time to get versioned
  backups (restic snapshots) with different content
- List all snapshots stored in the repo
- List all files in a specific snapshot
- Check the structural consistency and integrity of your repo
- Check the integrity of the actual data that you backed up
- Move /opt/gnuhealth/var/lib to simulate data loss
- Restore the last snapshot with restic
- Check if all the files with their latest content are restored
- Create a new daily cronjob to remove older backup snapshots by using a policy with the
  following rules: - Keep all hourly snapshots during a day - Keep all daily snapshots during a week - Keep all weekly snapshots during a three week period - Keep all monthly snapshots for three months - Keep all yearly snapshots for two years

# 7 Listings

## 7.1 Listings

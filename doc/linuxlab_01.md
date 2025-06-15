# 1 Introduction

# 2 Linux and shell basics

# 3 Basic server security

## 3.1 nftables

- Install nftables and configure it (→ nftables Wiki) on all VMs  
  ```bash
  sudo apt install nftables
  ```
- Do not use legacy xtables, do not use firewalld or any similar software on top of nftables
- Use the debian standard configuration file to make your firewall rules permanent  
  `/etc/nftables.conf`
- Remember not only to start the corresponding systemd service for nftables, but also to enable it for automatic start after a reboot  
  ```bash
  sudo systemctl enable --now nftables
  ```
- Find out the IP address of the jumphost VM (which is not the IP of the ”studserv” server itself). How did you achieve this?  
  `10.100.30.3 #check SSH env`
- Allow ssh login to ll-admin only from this jumphost IP  
  configured `allowed_ssh_ips` to the jumphost IP and `ssh_port` to 22  
  ```nft
  type filter hook input priority 0;
        policy drop;
        ct state established, related accept
        iif "lo" accept
        tcp dport $ssh_port ip saddr @allowed_ssh_ips accept
        tcp dport $ssh_port log prefix "SSH blocked: " drop
  ```
- Allow ssh login to the other VMs only from ll-admin  
  configured `allowed_ssh_ips` to the admin-ll IP  
  ```nft
  type filter hook input priority 0;
        policy drop;
        ct state established, related accept
        iif "lo" accept
        tcp dport $ssh_port ip saddr @allowed_ssh_ips accept
        tcp dport $ssh_port log prefix "SSH blocked: " drop
  ```

## 3.2 sshd

- Important precaution when making changes to the ssh service on a remote (i.e. not otherwise accessible) system:  
  – Split your tmux window to get another pane  
  ```text
  ^C+b %
  ```  
  – In this new pane, run temporarily another ssh process on port 2222, but take care that this does not run as a daemon (which sshd(8) option does that?)  
  ```bash
  sudo /usr/sbin/sshd -p 2222 -D
  ```  
  – Verify that you can login via this second ssh port 2222; you’ll need this (only) in an emergency if the usual sshd is not working anymore  
  – Don’t forget to open the firewall (temporarily) for this new ssh port  
  added 2222 to ssh ports
- Use ssh-copy-id(1) to copy your ssh public key, that you already created for this lab, to ll-admin. Which command options do you need for this (e.g. to use the ProxyJump option passed through to ssh, which ssh-copy-id uses)?  
  ```bash
  ssh-copy-id -o ProxyJump=...
  ```
- Test if the login with your ssh key works  
  yep
- If it does, configure sshd to only allow login with ssh keys  
  ```text
  PasswordAuthentication no  
  PublicKeyAuthentication yes
  ```
- Use the sshd(8) test mode to check the validity of the config files before restarting the daemon. What is the output if there is an error in the config file? What is the output if there isn’t (how can you verify this)?  
  ```bash
  sudo sshd -t
  ```
  No output: fine config  
  Example output with error:  
  ```
  /etc/ssh/sshd_config: terminating, 1 bad configuration options
  ```
- Output the effective ssh configuration to stdout, including default values; redirect this to a file and answer the following questions:  
  ```bash
  sudo sshd -T > sshd_config_dump.txt
  ```
  – Which port is used?  
  ```bash
  grep port sshd_config_dump.txt
  # port 22
  ```
  – Is root login allowed?  
  ```bash
  grep root sshd_config_dump.txt
  # permitrootlogin yes
  ```
  – Are empty passwords allowed?  
  ```bash
  grep empty sshd_config_dump.txt
  # permitemptypasswords no
  ```
- Try to login with the password, not with the key (how can you enforce password usage on the client?). What error message do you get? Try running ssh with maximum verbosity.  
  ```bash
  ssh -vvv -o PubkeyAuthentication=no -o PreferredAuthentications=password ll-db-02.incus
  ```
  Output:
  ```
  ... No more authentication methods to try
  ```
- How can you see after the login on the remote system from which IP the connection was made and which ports (remote and local) are used?  
  ```bash
  env | grep SSH
  ```
- If everything works, don’t forget to stop the temporary ssh process listening on port 2222 (how did you do that?) and close this port on the firewall again  
  ```bash
  ps aux | grep sshd
  sudo kill -6 {PID}
  ```
- Finally test if your settings and configurations are still working after a reboot of the VM

- Create a new ssh keypair on ll-admin and copy the corresponding public key to all the other VMs  
  ```bash
  ssh-copy-id -i ~/.ssh/id_ed25519.pub web  
  ssh-copy-id -i ~/.ssh/id_ed25519.pub db  
  ssh-copy-id -i ~/.ssh/id_ed25519.pub app
  ```

  `~/.ssh/config`:  
  ```sshconfig
  Host web
      HostName ll-web-02.incus
      user debian

  Host db
      HostName ll-db-02.incus
      user debian

  Host app
      HostName ll-app-02.incus
      user debian
  ```

- Test if the login with this new ssh key works from your admin VM to all the other VMs
- Configure the sshd(8) daemons on all VMs to allow only logins with ssh keys
- Test that the login with ssh key still works on all VMs
- Test copying a file from ll-admin to another VM with scp(1)  
  ```bash
  scp <file> debian@ll-web-02.incus:/home/debian/<file>
  ```
- How could you copy a file from your laptop through the jumphost and through your admin VM directly to e.g. ll-web?  

- Write a $HOME/.ssh/config file on ll-admin to use simpler commands to log into the other VMs:  
  – `ssh ll-web`  
  – `ssh ll-app`  
  – `ssh ll-db`  

  ```sshconfig
  Host web
      HostName ll-web-02.incus
      user debian
      Port 22
      IdentityFile ~/.ssh/id_ed25519

  Host db
      HostName ll-db-02.incus
      user debian
      Port 22
      IdentityFile ~/.ssh/id_ed25519

  Host app
      HostName ll-app-02.incus
      user debian
      Port 22
      IdentityFile ~/.ssh/id_ed25519
  ```

- Specify that your ssh key is automatically added to the ssh-agent(1) as if done by running ssh-add(1)  
  ```text
  AddKeysToAgent yes
  ```
- Is the ssh-agent(1) even running? If not, how can you do this and ensure that this is done automatically after a reboot?  
  ```bash
  ps aux | grep ssh-agent # not running
  ```

  ```bash
  mkdir -p ~/.config/systemd/user
  vim ~/.config/systemd/user/ssh-agent.service
  ```

  Service content:
  ```ini
  [Unit]
  Description=SSH key agent

  [Service]
  Type=simple
  Environment=SSH_AUTH_SOCK=%t/ssh-agent.socket
  ExecStart=/usr/bin/ssh-agent -D -a $SSH_AUTH_SOCK

  [Install]
  WantedBy=default.target
  ```

  Start the service:
  ```bash
  systemctl --user daemon-reexec
  systemctl --user enable --now ssh-agent.service
  ```

  In `.bashrc`:
  ```bash
  export SSH_AUTH_SOCK="$XDG_RUNTIME_DIR/ssh-agent.socket"
  ```

- Configure your login to ll-admin from your laptop by using a ssh_config(5) file. Use two different host specifications in this file, one for the jumphost connection and another one for the VM login.

  ```sshconfig
  Host jumphost
      HostName studserv03.chi.uni-hannover.de
      user linuxlab02
      Port 2222

  Host linuxlab
      HostName ll-admin-02.incus
      Port 22
      ProxyJump jumphost
      AddKeysToAgent yes
      user debian
  ```

What are the recommended or necessary file permissions for ...

- ... the $HOME/.ssh/ directory?  
  `700`
- ... the $HOME/.ssh/config file?  
  `600`
- ... the $HOME/.ssh/authorized_keys file?  
  `600`
- ... the $HOME/.ssh/PUBLICKEY file?  
  `644`
- ... the $HOME/.ssh/PRIVATEKEY file?  
  `600`  
  Change one of the necessary file permissions and report what the corresponding error messages are if you are trying to use ssh in this case. (Don’t forget to revert this afterwards.)

  ```
  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  Permissions 0777 for '/home/debian/.ssh/id_ed25519' are too open.
  It is required that your private key files are NOT accessible by others.
  This private key will be ignored.
  Load key "/home/debian/.ssh/id_ed25519": bad permissions
  debian@ll-web-02.incus: Permission denied (publickey).
  ```

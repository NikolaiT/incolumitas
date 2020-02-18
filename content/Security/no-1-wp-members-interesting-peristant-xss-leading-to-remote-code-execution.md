Title: No 1. -  wp-members: Interesting peristant XSS leading to remote code execution.
Date: 2013-03-15 23:12
Author: Nikolai Tschacher
Category: Security
Tags: Security, Programming
Slug: no-1-wp-members-interesting-peristant-xss-leading-to-remote-code-execution
Status: published

Hey you there!

**Type:** Stored cross site scripting  
**Risk:** Medium to high  
**Affecting:** <http://wordpress.org/extend/plugins/wp-members/>
**Vendor site:** <http://rocketgeek.com>

### Preface

It has been quite some time since I took concern of my blog, although I
would have had some content ready (maybe even worth) to be published.
Around six weeks ago, I rummaged (wow - new word!) through endless lines
of wordpress plugin code, in the hope to get my hands on some low
hanging fruits (In the likely case you don't have a clue what I am
talking about: I was searching for easyily detectable security bugs in
plugin applications written for wordpress). After analysing for several
hours the architecture and design of a randomly chosen target -
[wp-members](http://wordpress.org/extend/plugins/wp-members/), a plugin
providing the site owner with the functionality to password protect
content on his wordpress site - I was able to detect a pretty nasty bug.

### The bug

Alongside with the access restriction mechanism, the plugin furthermore
allows users to register. The potential user is presented a nice form,
which would transfer an array of registration data to the web server
when submitted. Considering this, there is only one possibile location
for a sink source and therefore origin of tainted data. The PHP file
handling the registration logic is not unsurprisingly called
wp-members-register.php. The vulnerable wp-members version can be found
[here](http://downloads.wordpress.org/plugin/wp-members.2.8.0.zip) (zip
file of the youngest vulnerable version).

The herein aforementioned wp-members-register.php-file contains a
unsound function named `wpmem_registration( $toggle )` which was
affected from two kinds of XSS flaws: Reflected and persistent (or
stored) XSS vulnerability. Whereas the reflected isn't really dangerous
(modern browsers easily spot them and filter them out by recognizing
script tags and html entities in the URL), the peristent on the other
hand might become rather unpleasant.

This first code snippet shows the preparation of the input and some
parsing. We learn that the input is written into a two dimensional array
named `$fields`.

    :::PHP
    // build array of the posts
    $wpmem_fields = get_option( 'wpmembers_fields' );
    for( $row = 0; $row < count( $wpmem_fields ); $row++ ) {
        $wpmem_fieldval_arr[$row] = $_POST[$wpmem_fields[$row][2]];
        // add for _data hooks
        if( $wpmem_fields[$row][2] != 'password' && $wpmem_fields[$row][4] == 'y' ) {
              $fields[$wpmem_fields[$row][2]] = $wpmem_fieldval_arr[$row];
        }
    }

The program logic continues with some checks for obligatory data:

    :::PHP
    // check for required fields    
    $wpmem_fields_rev = array_reverse( $wpmem_fields );
    $wpmem_fieldval_arr_rev = array_reverse( $wpmem_fieldval_arr );

    for( $row = 0; $row < count($wpmem_fields); $row++ ) {
        $pass_chk = ( $toggle == 'update' && $wpmem_fields_rev[$row][2] == 'password' ) ? true : false;
        if( $wpmem_fields_rev[$row][5] == 'y' && $pass_chk == false ) {
            if( !$wpmem_fieldval_arr_rev[$row] ) { $wpmem_themsg = sprintf( __('Sorry, %s is a required field.', 'wp-members'), $wpmem_fields_rev[$row][1] ); }
        }
    }

Then, the we find ourselves in a big switch statement which states the
whole remainder of the function. It basically consists of two cases:
register and update. Since we are only interested in the register
functionality, we ingore the update branch.

Now the coder implements some counter action against injection attacks.
He checks the supplied username if the corresponding user exists, has
valid characters and so on. When some of these checks fail, the script
denies further execution. It makes essentially the same with the
supplied email address.

    :::PHP
    if( !$username ) { $wpmem_themsg = __( 'Sorry, username is a required field', 'wp-members' ); return $wpmem_themsg; exit(); } 
    if( !validate_username( $username ) ) { $wpmem_themsg = __( 'The username cannot include non-alphanumeric characters.', 'wp-members' ); return $wpmem_themsg; exit(); }
    if( !is_email( $user_email) ) { $wpmem_themsg = __( 'You must enter a valid email address.', 'wp-members' ); return $wpmem_themsg; exit(); }
    if( $wpmem_themsg ) { return "empty"; exit(); }
    if( username_exists( $username ) ) { return "user"; exit(); } 
    if( email_exists( $user_email ) ) { return "email"; exit(); }

At this point, our `$fields` array is partly sanitized, the rest is still
populated with arbitrary raw data we are able to control.


    Array
    (
        [username] => uuuuuuuu                      SANITIZED
        [user_email] => uuuuuuuu@uuuuuuuu.com       SANITIZED
        [first_name] => uuuuuuuu
        [last_name] => uuuuuuuu
        [addr1] => uuuuuuuu
        [addr2] => uuuuuuuu
        [city] => uuuuuuuu
        [thestate] => uuuuuuuu
        [zip] => uuuuuuuu
        [country] => uuuuuuuu
        [phone1] => uuuuuuuu
    )


We finally come to the first part of the vulnerability. The raw post
data is inserted into the database through the wordpress API function
`update_user_meta()`.

    :::PHP
    // set remaining fields to wp_usermeta table
    for( $row = 0; $row < count( $wpmem_fields ); $row++ ) {
        if( $wpmem_fields[$row][2] != 'password' ) {
            if( $wpmem_fields[$row][2] == 'user_url' ) { // if the field is user_url, it goes in the wp_users table
                wp_update_user( array ( 'ID' => $user_id, 'user_url' $wpmem_fieldval_arr[$row] ) );
            } else {
                if( $wpmem_fields[$row][2] != 'user_email' ) { // email is already done above, so if it's not email...
                    if( $wpmem_fields[$row][4] == 'y' ) { // are we using this field?
                                          update_user_meta( $user_id, $wpmem_fields[$row][2], $wpmem_fieldval_arr[$row] );
                    }
                }
            }
        }
    } 

Unfortunately, these family of wordpress API functions
(`update_user_meta()`) don't strip html meta characters (no
`htmlspecialchars()` functionality!). Maybe the author assumed that they
would.

However, now we know that we can insert arbitrary data (thus also html
and javascript code) into the database. This is nothing special or even
insecure yet, because the application could still sanitize the data when
retrieving it from the database and processing it further. Unfortunately
this doesn't happen.

Well. The next idea of mine was too look at the admin panel. I mean,
this panel may show the tainted user data in a table or something
similar. And that's what it does:

An wordpress administrator can access the wordpress plugin wp-members
over the general admin panel => Plugins => Users => WP-members. Then
he sees a table overview of all registered users. The corresponding URL
to obtain this view is
http://localhost/wp/wp-admin/users.php?page=wpmem-users (*localhost/wp*
is my document root in this case...)

Well, the table consits of 5 columns:

    Username   
    Name    
    E-mail  
    Phone   
    Country

Remember that our investigations revealed that we are able to insert
html/javascript into the database for the Name, Phone and Country field?
Let's check, where this admin panel is made and wheter the data is
sanitized:

The view is generated through the function `wpmem_admin_users()` in the
/wp-content/plugins/wp-members/user.php file. The actual  
value submitted at registration time is then echoed to the page at line
261:  
Excerpt:

    :::PHP
    echo "  ID}&" . esc_attr( stripslashes( $_SERVER['REQUEST_URI'] ) ) . "\">" . $user->user_login . "\n";
    echo "  \n";
    echo "  " . get_user_meta( $user->ID, 'first_name', 'true' ) . " " . get_user_meta( $user->ID, 'last_name', 'true' ) . "\n";
    echo "  " . $user->user_email . "\n";
            
            if( $col_phone == true ) {
    echo "  " . get_user_meta( $user->ID, 'phone1', 'true' ) . "\n";
            }
            
            if( $col_country == true ) {
    echo "  " . get_user_meta( $user->ID, 'country', 'true' ) . "\n";
            }

The value isn't propperly escaped, neither at the time when inserted
into the database, nor when selected with `get_user_meta()`. Maybe the
coder thought that `get_user_meta()` is XSS safe?!

The code is only triggered when a user with a field containing the
exploit code is shown in the admin table. This is normally not the case,
because there are a vast amount of of users and they are distributed
over many sites in the panel. Why is that no reduce the threat level of
the attack vector?  
Users are listed in alphabetical order in the admin panel, according to
the usernames alphabetical position submitted at registration. So we can
force with a username like 'aaaaaaaaaaaaaaa' (of course not so
suspicous) that we are shown (echoed) easily at the first page! This
means our exploit code is always triggered when the admin access the
plugin panel, therefore the exploitation chances are pretty good!

### How would a blackhat design the exploit?

The original data shouldn't look suspicous, no suspicion at all should
be provocated (sneaky stealth mode enabled). The javascript code
shouldn't take long to execute or alter the front end surface. The code
must be maximally redundant and should be obfuscated and of course well
tested!  
Wikipedia says:

> The persistent (or stored) XSS vulnerability is a more devastating
variant of a cross-site scripting flaw: it occurs when the data provided
by the attacker is saved by the server, and then permanently displayed
on "normal" pages returned to other users in the course of regular
browsing, without proper HTML escaping.  

When the payload is triggered, we automatically have the admin cookie.
So we could steal the cookie and send it to the attackers server to log
in from there and upload a shell. This is ways too strenuous and
verbose, so we directly manipulate a existing plugin via the built-in
plugin-editor of wordpress. The nonce is no further problem, since we
just know it (XSS eliminates XSRF prevention!) At the exectution time
the exploit could send a little notification message to our server and
then that blackhat, knows that his shell is ready for him to access.

​### How can we find vulnerable sites including the plugin?

Google dork of wp-members:

> This content is restricted to site members.

I recenty published a python script to scan pages with google:
<http://incolumitas.com/2013/01/06/googlesearch-a-rapid-python-class-to-get-search-results>  
We could scan pages with the above dork and find lots of sites with the
installed vulnerable plugin.

### The consequences

On every server where wp-members is installed and when the registration
is open (which is the normal case, since a sane website never refuses
users\^\^), a malicious user can register with valid data (to pass
several registration checks) and the additional exploit code in the
*phone* or *country* field in the registration form.  
Whenever a admin looks at the overview in his admin panel from
wp-members, the injected code is executed. Because the javascript code
runs in the context of the admin, the code is absolutely TRUSTED (stored
XSS):The code can do whatever action the wordpress admin panel provides.
For example: Change the PHP code of another plugin over the standard
edit function provided in the wordpress admin panel
(/wp/wp-admin/plugin-editor.php) to something like

    :::PHP
    /* Bet you get the idea */
    <?php
    echo system($_GET['cmd']);
    ?>

and gain a remote shell on the server. This means the server is fully
compromised (at least http/sql). No need to crack salted md5 hashes,
like in boring sql injections. Direct RCE.

The plugin currently has (271,196) downloads (242,142 when I found the
bug 6 weeks ago), 600 downloads on a daily base. I estimate the number
of servers who actually installed the plugin at around 30.000 (is this
actually very modest guessing). Due to the nature of the flaw:  
I guess that a determined blackhat could find 80% of all vulnerable
servers through spiders. Furthmore, modestly guessing, on 30% of these
servers the  
exploit would be triggered. This makes: `0.8*0.3*30.000 = 7200`. After
adjusting downwards, realisticly 5000 servers could be compromised
(shell access) within a short period of time (few days to a week).
These  
servers could act as a neat DOS-Botnet; servers have lot's of
networking power, don't they?

### Prevention

Sanitizing untrusted data. It's always the same story. Wheter it's a
command execution, buffer overflows, sqli injections, XSS, there is one
simple approach to chocke off the root of the problem: Allow only data
into the application, which compares positvly with a whitelist. This
sounds easy, indeed it is, but under the financial pressure of greedy
organizations and general coding stress, security is often ignored and
missed.

On the technical side, htmlspecialchars() over the \$fields[] array in
wp-members-register.php.  
htmlspecialchars() over every data the user is able to manipulate and
craft!

### Last words

This was only the most gaping flaw, the other became (yeah, they exist)
rather uninteresting, since I had already a way to get on the server.
Chad Butler, the author, fixed the bugs very quickly and professionaly.
He took all my suggestions/concerns very serious and it was generally a
nice experience working with him!

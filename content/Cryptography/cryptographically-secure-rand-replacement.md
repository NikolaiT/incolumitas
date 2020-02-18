Title: Cryptographically secure rand() replacement
Date: 2013-11-14 22:55
Author: Nikolai Tschacher
Category: Cryptography
Tags: Cryptography, Php, Security, Programming
Slug: cryptographically-secure-rand-replacement
Status: published

If you are a programmer, you sometimes find yourself in the need for
random numbers. There are many possible use cases:

-   Generate data for unit-tests.
-   Build secure passwords or keys as input for ciphers like AES,
    Twofish and its colleagues.
-   Simulating the real world for modelling applications.
-   A prominent use case: Lot's of gambling sites depend on good random
    number generators.

Now if you code in PHP, there are quite some different ways to obtain
random numbers. There is the [`rand ( int $min , int $max
)`](http://www.php.net/manual/en/function.rand.php "rand") function for
instance: It yields a random number within the range specified by the
`$min` and `$max` parameters.

The documentation states that this approach isn't particularly secure
and shouldn't be used for applications that need to feed algorithms with
cryptographically secure random data. Then there's [`mt_rand ( int
$min , int $max )`](http://www.php.net/manual/en/function.mt-rand.php)
that apparently creates *better* random values. Certainly not suitable
for crypto purposes as well.  
There were/are quite some applications concerned with security bugs
because of using `rand()` or `mt_rand()` for passwords, encryption keys,
session cookies, CSRF tokens and the like. See also this link to a
related discussion on
[security.stackexchange.com](http://security.stackexchange.com/questions/18033/how-insecure-are-phps-rand-functions).

But because of convenience of the `$min`, `$max` interfaces of `rand()` and
`mt_rand()` and it's intuitive handling, I implemented the same interface
for a cryptographically secure pseudo random number generator:
[*openssl_random_pseudo_bytes ( int $length [, bool
&$crypto_strong ]
)*](http://www.php.net/manual/en/function.openssl-random-pseudo-bytes.php).

Here is the function that does the job:

     :::PHP
     * 
     * Generates cryptographically secure random numbers including the range $start to $stop with 
     * good performance (especiall for ranges from 0-255)!
     * Calls to openssl_random_pseudo_bytes() are cached in a array $LUT. 
     * For instance, you need only around 2 calls to openssl_random_pseudo_bytes in order to obtain 
     * 1000 random values between 0 and 200. This ensures good performance!
     *
     * Both parameters need to be positive. If you need a negative random value, just pass positiv values
     * to the function and then make the return value negative on your own.
     *
     * If the function returns False, something went wrong.
     * Always check for false with "===" operator, otherwise a fail might shadow a valid
     * random value: zero. You can pass the boolean parameter $secure. If it is true, the random value is
     * cryptographically secure, else it was generated with rand().
     * 
     * @staticvar array $LUT A lookup table to store bytes from calls to secure_random_number
     * @param int $start The bottom border of the range.
     * @param int $stop The top border of the range.
     * @param in bool $secure Whether the call to openssl_random_pseudo_bytes was made securely.
     * @param int $calls The number of calls already made.
     * @return int A random integer within the range (including the edges).
     * @throws InvalidArgumentException Thrown if the input range is invalid.
     * @throws UnexpectedValueException Thrown if openssl_random_pseudo_bytes was called unsecurely.
     * @throws ErrorException Thrown if unpack fails.
     */
    function secure_rand($start, $stop, &$secure = "True", $calls = 0) {
        if ($start < 0 || $stop < 0 || $stop < $start) {
            throw new InvalidArgumentException("Either stop= 65536 && $range < 4294967296) {
            $format = 'L';
            $num_bytes <<= 3;
        }
        
        /* Before we do anything, lets see if we have a random value in the LUT within our range */
        if (is_array($LUT) && !empty($LUT) && $last_lu === $format) {
            foreach ($LUT as $key => $value) {
                if ($value >= $start && $value <= $stop) {
                    $secure = True;
                    unset($LUT[$key]); // Next run, next value, as my dad always said!
                    return $value;
                }
            }
        }

        /* Get a blob of cryptographically secure random bytes */
        $binary = openssl_random_pseudo_bytes($num_bytes, $crypto_strong);

        if ($crypto_strong == False) {
            throw new UnexpectedValueException("openssl_random_bytes cannot access secure PRNG");
        }

        /* unpack data into previously determined format */
        $data = unpack($format . '*', $binary);
        if ($data == False) {
            throw new ErrorException("unpack() failed.");
        }

        //Update lookup-table
        $LUT = $data;
        $last_lu = $format;

        foreach ($data as $value) {
            $value = intval($value, $base = 10);
            if ($value <= $range) {
                $secure = True;
                return ($start + $value);
            }
        }

        $calls++;
        if ($calls >= 50) { /* Fall back to rand() if the numbers of recursive calls exceed 50 */
            $secure = False;
            return rand($start, $stop);
        } else {/* If we could't locate integer in the range, try again as long as we do not try more than 50 times. */
            return secure_rand($start, $stop, $secure, $calls);
        }
    }
    /*
     * $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
     * $                 Some tests. Ignore.                 $
     * $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
     */


    function test($start, $stop) {
        static $num_called = 1;
        $val = secure_rand($start, $stop, $secure);
        echo "Random Value #$num_called is: ";
        var_dump($val);
        echo "Generated securely: " . (($secure == True) ? "yes" : "no") . "";
        $num_called++;
    }

    function performance() {
        // My appraoch
        $start = microtime(true);
        // That is also very fast!
        foreach (range(0, 20000) as $i) {
            secure_rand(0, 200);
        }
        $stop = microtime(true);
        printf("Elapsed time with secure_random_number(): %.6f seconds", $stop - $start);
        
        // With rand()
        $start = microtime(true);
        foreach (range(0, 20000) as $i) {
            rand(0, 200);
        }
        $stop = microtime(true);
        printf("Elapsed time with rand(): %.6f seconds", $stop - $start);
    }

    test(100000000, 100100000); // Critical call. There's a high probability that the function will fail.
    test(500, 2000000);
    test(0, 60);

    performance();

It essentially prompts for 2^13 random bytes and then splits this blob
of data either in bytes, shorts or longs depending on your specified
range. It then just iterates over these tokens and looks whether we
found a candidate. If not, we call the function again (recursive step).
For further calls, we collect all unused bytes in a look-up table to
avoid making to much calls to the slow `openssl_random_pseudo_bytes()`
function. This increases performance a bit.

We try to find a random value in the obtained range maximally 50 times.
If we exceed a recursive depth of 50, we just return the weak and
insecure rand(). You can verify with the $secure boolean parameter
whether we found such a candidate securely or if we needed to fall back
to rand().

There is no guarantee that the function will always find a value that
fits, especially in the ranges up to 2^32. If we search for a value in
the range (100000000, 100070000) for instance, we actually look for a
long value that is between 0 and 70000. There are maximally 50*2^13/4
long values where we can search such a value (Because we request 8192/4
long values per function call and all in all, we have maximally 50
recursive calls).  
But the probability that a single random long value lies in this range
is roughly around `1/(2^32/2^16) = 1/(2^16)`, which in turn means that
with our 50*2^13/4 long values we have a `2^16/50*2^13/4 ~= 1:1`
chance that we will find one (The calculation is a rough estimate
though).

The worst (rare) case that can happen: You end up using rand(). But as
mentioned, you can check for this (rare) case with the boolean input
parameter...

But in most cases you don't have this concerns and you are good to go!

To finish, here is a picture that illustrates the distribution of
secure_rand() output:

({static}/uploads/2013/11/out.png)]({static}/uploads/2013/11/out.png)
[distribution of secure_rand()]
The output of secure_rand() visualized as points in a canvas.
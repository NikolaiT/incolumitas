Title: The dangers of a poorly planned project
Date: 2013-11-21 00:48
Author: Nikolai Tschacher
Category: Philosophical
Tags: Architecture, Captcha, Philosophical, Programming, Php, Uncategorized, Wordpress
Slug: the-dangers-of-a-badly-planned-project
Status: published

### Preface

Do you like to fiddle around with programming projects in your spare
time? And do you sometimes start endeavors ambitiously, but you never
actually finish them? Are you fucking tired of stacking unsuccessful
projects, doing mediocre work while never being thoroughly satisfied in
what you do?

If yes, you may be inclined to listen to some words I have to say over
my most recent failed project:

The idea was to create my own *little* captcha plugin for wordpress. You
can learn more about the idea by delving into some of my accompanying
investigations in the following blog posts:

-   [Plotting Bézier curves directly and with De Casteljau’s
    algorithm](http://incolumitas.com/2013/10/06/plotting-bezier-curves/)
-   [Create your own font the hard
    way!](http://incolumitas.com/2013/10/16/create-your-own-font-the-hard-way/)

Honestly I started this project because back in the time I was using
[this](wordpress.org/plugins/captcha/‎ "captcha") plugin and I was
unsatisfied because for
[these](http://incolumitas.com/2013/11/04/a-tale-of-a-twofold-broken-wordpress-captcha-plugin/ "captcha is broken")
reason. So this context information hopefully points out some of my
motivations to start the project in the first place.

### The destiny of every badly planned project

As with many spontaneously started projects in came up with in the past,
I first was convinced that it was an awesome idea and subsequently
started programming head-first without having a clear path or at least a
slight vision of what the project should look like in the end.

But after reaching first milestones, it slowly began to dawn on me that
there might be several issues inherent to the architecture and concept
itself. This kind of coming back down to earth with a bang is nothing
new for me, actually it's a pattern I observed several times in the
past.

It's really annoying, because you invested blood, sweat and tears into
your project. Let me analyze how such a idea get's wrecked over its
unfortunate evolution:

### Avoid quickstarts

The first development stage of a fresh project is mostly euphorically:
You're able to make progress virtually without making big efforts. You
just code thoughtlessly without having the big picture in front of you.  
The reason for that is, that your motivation is intrinsic and you don't
have to convince yourself that what you are doing is right; you're just
doing it.  
In this phase, you're unconsciously laying the foundation of your
project (Defining classes, choosing a concrete design pattern) and the
quality and solidness of what you do *now* determines the amount of
headache and time you have to invest *later* to fix architectural
mistakes.  
**Learn:** Before you begin to write a single line of code, make sure
that you can answer the following questions: Am I implementing something
that I will actively user later, or am I just doing it for the learning
sake? Is the end product important, or the path itself?

### Use existing solutions

If you are like me, then you love to do reinvent things: Rasterizing
Bézier curves? Plotting Lines? Writing PNG's (Involves the whole
re-implementation of the pretty complex PNG specification)? Should I use
ImageMagick? Nahh, let's not use a imaging library, let's do it on my
own!  
The avoidance of a imaging library is a concrete example and a part of
the reason for the failure of my aforementioned project idea.  
Reinventing and re-implementing essential building blocks is mostly a
bad idea!  
Don't get me wrong: Doing so is highly educational and in the process
you're going to learn a hell of a lot (Example: How else would I know
now how to approximate the derivation of n-th order bezier curves
numerically with the Newton-Raphson algorithm?).  
But if you create elemental code on your own, you should either have
professional knowledge of the subject or a huge willpower/effort and
most importantly, lots of time on your hand, to invest into your
endeavor.

**Understand:** Ask yourself whether you want to focus on the unique,
innovative part of your application, that needs to absorb all of your
imagination and creativity, or if you prefer spending a lot of time on
parts that already exist in a better form than you would ever be able to
do it?  
It's mostly a rhetorical question, but the paradoxical part lies here:
If you never appreciate the thinking process that accommodates the
building process of a elemental software block and you always do the
part that's completely new, you mightn't learn *enough* to do actually a
worthy, unique and new part. The road to a brilliant idea is paved by
many failures and dull re-implementations of existing ideas!

### Do not bury your aborted ideas.

It's bad, believe me.  
You don't need to pursue a project at all costs even though it was
doomed to fail right from the beginning. But if you try to forget it and
let your code rot in some shady places on your hard-drive, you're
unconsciously reinforcing a very bad feeling: That you still have
something to complete, but you do not really know what.  
Make a clear decision to finish your project. Just mark it as completed
and as a failure, but put an end to it! This allows you to start over
and do better in the future! Not everything needs to be a success. Most
projects end as a failure. Such is life!

### Rethinking about motivation and discipline

In being fully aware of the danger of sounding corny (Does this word fit
here?): You only need to be right very few times in life:

-   Theoretically, you need to command up the courage only once to find
    the woman of your life.
-   You only need to try very few times in your life to apply for a job
    of your dreams.
-   Once realized that Python is the very best programming language (In
    combination with C) you don't need wasting your precious time on
    other languages anymore ;)

You can endure thousand failures, but if you just succeed once with an
idea, you made it.  
If there's a single project that doesn't end in the corner of failures,
you succeeded! So every stranding you encounter in life brings you
closer to a success. The worst thing you can do: Stop trying.  
I honestly don't think that this is motivational nonsense: Try hard
enough, end you eventually succeed. As simple as that.  
**Learn:** Be aware of motivation. Everybody is motivated. Anyone wants
to get in formidable physical shape, learn a lot and achieve great
things. But only few to so. It's not a question of intellectual ability
and fluid intelligence that keeps you from reaching mastery, it's the
addiction of being comfortable and shirking, that makes it impossible
for you to do what you want.  
Ask yourself: Who will rise higher: A committed, hard working,
averagely gifted person, that spends a year on a particular task, or a
genius that expects from himself to do great things in a short time?

### Getting concrete: What was wrong with my idea? And what did I actually learn?

The initial idea was to make a (nother) Captcha plugin for Wordpress.

Maybe the first mistake was to consider doing my own version, without
even inspecting the existing solutions.  
But there are quite some good wordpress captcha plugins out there. For
instance the one I am using now: It prevents all forms of spam so far
and fulfills its purpose perfectly.  
That's all you expect from such a plugin.  
A [quick
search](http://wordpress.org/plugins/search.php?q=captcha "captcha alternatives")
yields many good alternatives that I wasn't aware of.

Furthermore, I wanted to to everything on my own: Rasterizing my own
lines (Bresenham line algorithm, Midpoint algorithm), plotting Bézier
splines on my own (Casteljau's algorithm, several different
approximations, ...), generating bitmap graphics on my own and I could
continue this list indefinitely.

All these patchwork approaches ended in a very unstable captcha
implementation on witch I couldn't built further. This meant, that every
future I tried to integrate, needed exhaustive debugging while
maintaining an general overview of where the bug could be possibly
situated.

To state an example: I tried to implement glyph filling. This involves
line/line and line/curve intersection checking. The algorithm that finds
the intersection point needs the roots of Bézier curves (Which were
cubic in my case).  
Thus I had to implement the Raphson-Newton algorithm in order to
compute the roots. That alone was a new field for me. But combined with
my repulsion for PHP and a really unstable testing environment (I could
have made a better debugging environment, but apparently I was to lazy),
it was a pain in the ass to implement things correctly.

I soon started to solve the problems in Python and after the logic was
working there, ported it back to PHP. I did so simply out of the reason
that debugging the plugin directly, involved generating bitmap captchas
every run, which was a rather tedious process. Hence I underestimated
the complexity completely and failed to set up a productive environment
(I better don't start elaborating on my attempts to get xdebug installed
in a xampp environment).

While the former issue wasn't the reason I decided to stop the
development, there were other problems with the architecture itself:

My captcha plugin calculates randomly placed splines and glyphs on a
bitmap (that constitute the glyphs) and saves the rather large (no
compression) netbpm bitmap file on disk, which is then converted to a
PNG with the command line utility pnmtopng.  

All this requires a lot memory and CPU power, since the algorithms to
rasterize lines and Bézier splines are rather expensive. Therefore I
just fire the captcha factory once in intervals of 2 hours (With web
cronjobs or real cronjobs if necessary) in order to feed a finite pool
of captcha images, that's is slowly but constantly renewing itself.  
All users that visit the plugin, get a randomly chosen captchas served.
But this approach exhibits a big drawback: The captcha exists to prevent
spammers from posting comments. But due to this captcha-image-pool
design, every malicious user could just request a large amount of
captchas until he obtains the majority of captchas in the pool. Then he
could manually map the obtained pictures to it's solution and teach his
attacking script the answer and BOOM the captcha is bypassed.  
Of course he'd need to update the mappings every two hours, but this
wouldn't hinder a motivated attacker to do so.

In short: Because plotting bitmaps and computing splines is a very
expensive task, I simply can't manufacture fresh captchas for every
user. I need to have a collection of pre built captcha pictures that are
randomly chosen to be presented to visitors. But this is a weak design
from a security point of view.  
Although there are countermeasures, they cannot neutralize the root
problem and hinder evil mind's from finding a circumvention.

Here have an example of how I implemented that "pool feeding":

    :::php
    /*
     * Only the cronjob calls this file directly. The cronjob must have the same
     * IP address as the webserver, otherwise it won't be executed. This prevents
     * users from calling this file directly and DDOSing the server
     */
    if (basename(__FILE__) == basename($_SERVER["SCRIPT_FILENAME"])) {
        if (in_array($_SERVER['REMOTE_ADDR'], array('127.0.0.1', '::1'))) {
            require_once('cunning_captcha_lib.php');
            /* Bring the wordpress API into play */
            define('WP_USE_THEMES', false);
            require('../../../wp-blog-header.php'); /* Assuming we're in plugin directory */
            ccaptcha_feed_pool(); /* Feed the little monster */
        } else {
            wp_die(__('Error: Dont call CunningCaptcha directly. It does not like it :(.', 'CunningCaptcha'));
        }
    }

    // ...
    /*
     * Adds new captcha images to the pool.
     */

    function ccaptcha_feed_pool() {
        /* First of all check if pnmtopng is available on the system */

        $handle = popen('/usr/bin/which pnmtopng 2>&1', 'r');
        $read = fread($handle, 2096);
        pclose($handle);
        if (!file_exists(trim($read))) {
            print("pnmtopng is not installed on the system.");
            return false;
        }

        /* Check if target dir exists, if not, create it */
        if (!file_exists(trailingslashit(TARGET_DIR)) && !is_dir(trailingslashit(TARGET_DIR))) {
            if (!mkdir(trailingslashit(TARGET_DIR), $mode = 0755))
                print("Couldn't create image directory");
            return false;
        }

        /* If there are no png files in the target directory, unset the option */
        if (false === strpos(implode('', array_values(scandir(trailingslashit(TARGET_DIR)))), 'png')) {
            echo "deleted options";
            delete_option('ccaptcha_path_captcha_a');
        }

        $captchas = cclib_generateCaptchas($path = trailingslashit(TARGET_DIR), $number = 10, $captchalength = 5);

        /* Convert them to png using pnmtopng */
        foreach (array_keys($captchas) as $path) {
            $path = escapeshellarg($path);
            system(sprintf("pnmtopng %s > %s && rm %s;", $path . '.ppm', $path . '.png', $path . '.ppm'));
        }
        /*
         * If the pool size is now too large, delete the superfluous (redundant) files from the directory
         * and the options database.
         */
        $cnt = 0;
        foreach (glob(trailingslashit(TARGET_DIR) . "*.png") as $filename) {
            $filetimes[$filename] = filectime($filename);
            $cnt++;
        }

        if ($cnt > POOL_SIZE) {
            $num_to_delete = $cnt - POOL_SIZE;
            /* Sort the array by value (unix timestamp) */
            if (!asort($filetimes, SORT_NUMERIC)) {
                print("couldn't sort images by modification time.");
                return false;
            }
            $keys = array_keys($filetimes);
            $savedcaptchas = get_option('ccaptcha_path_captcha_a'); /* This array cannot (should't) be empty */
            foreach (range(0, $num_to_delete - 1) as $i) {
                unlink($keys[$i]);
                unset($savedcaptchas[rtrim($keys[$i], '.png')]);
            }
            /* Synchronize the deletions with the options database */
            if (false === update_option('ccaptcha_path_captcha_a', $savedcaptchas)) {
                /* update failed or the option didn't change */
            }
        }

        $savedcaptchas = get_option('ccaptcha_path_captcha_a');

        if (!$savedcaptchas) // Create
            update_option('ccaptcha_path_captcha_a', $captchas);
        else { // Add
            update_option('ccaptcha_path_captcha_a', array_merge($savedcaptchas, $captchas));
        }

        /* Check if the directory and the options database are synchronized */
        $a = get_option('ccaptcha_path_captcha_a');
        foreach (array_keys($a) as $key)
            if (!file_exists($key . '.png'))
                wp_die("Options database doesn't match with FS");

        D($a);

        return true;
    }

### What now?

It's not all bad. The plugin that I see as a failure is even working.
The estimated amount of 3000 lines of code (including python sources)
wasn't for nothing. You can dig it on [my github
account](https://github.com/NikolaiT/CunningCaptcha) if you like. I
learned a lot and I have come up with another idea that is better (I
need to watch out that I don't fall in the same mistakes I pointed out
above). But before I begin with the new idea, I will profoundly think
about it! You can be damn sure of that!

### Epilogue

To conclude this post about my failed attempt, let's actually show how
the plugin works in it's current unfinished form. Let me repeat: It
works. It's a rather bad captcha (Would be easy to crack with OCR), but
one could use it in wordpress.

Here are some captchas generated in distinct forms:

[![The captcha in the comment form. Note: The error message reveals that I was
pretty frustrated while coding
:D]({static}/uploads/2013/11/captcha_in_action2.png)

[![The captcha embedded in the comment
form...]({static}/uploads/2013/11/captcha_in_action1-300x300.png)

Let me know what you think...

Cheers
Title: Major Redesign of incolumitas.com
Date: 2013-07-24 00:39
Author: Nikolai Tschacher
Category: Learning
Tags: Themeprojectsnewredesigncsshtml, Meta, Learning, Uncategorized
Slug: redesign-of-incolumitas
Status: published

Hello everybody!

I finally found some motivation and time to give my blog a design
upgrade - Basically an endavour that was overdue since this blog has
seen the light of the day ;)

On the technical side, this theme is a complete redevelopment. It's not
finished yet, on the contrary, it's the very first version and there
remain a lot of issues that need to be resolved. For instance: The
majority of the CSS code is still rather dirty and of experimental
nature. Additionally, I want to include an image slideshow based on
[unslider.js](http://unslider.com/ "unslider"). Your template function
in the your theme would then look something like the following:

    :::PHP
    if ( ! function_exists( 'clearcontent_header_slider' )):
    /*
     * This function includes a minimal jquery slideshow into the header of the site. It uses unslider.js in 
     * order to achieve this objective. Link to github site: https://github.com/idiot/unslider
     */
    function clearcontent_header_slider() {
        ?>
       
        <div class="header-slideshow">
            <ul>
                <li style="background-image: url('<?php echo get_template_directory_uri() . '/pics/slideshow/1.png' ?>');"></li>
                <li style="background-image: url('<?php echo get_template_directory_uri() . '/pics/slideshow/2.png' ?>');"></li>
                <li style="background-image: url('<?php echo get_template_directory_uri() . '/pics/slideshow/3.png' ?>');"></li>
            </ul>
        </div>
        <script type="text/javascript">
            var $j = jQuery.noConflict();

            // Use jQuery via $j(...) instead of $(..) to prevent name clashes.
            $j(document).ready(function(){
                $j('.header-slideshow').unslider({
                        arrows: true,
                        fluid: true,
                        dots: true
                });
            });
        </script>
        <?php
    }
    endif;
        
        
Furthermore, the theme is based on _s, a raw theme ment to be customized and extended. The big advantage are the good coding standards and a robust architecture, which really helps if you're new to wordpress theme development. The authors are partly from the automaticc team, essentially the founders of wordpress, which supports the  reputation of _s further...
Anyways, expect that the design of incolumitas.com slightly changes over the next weeks and months. A few key points I want to incorporate as soon as possible:

+ A static front page (Yes, using front-page.php)
+ A complete overhaul of my own captcha plugin. It's really hard to decipher them :D
+ Making the theme design responsive. This is easily said, but hard to achieve.
+ Uploading all my projects on my GitHub site. And ... 
+ Finally updating GoogleScraper.py

That's it for the moment. Stay tuned!
Nikolai

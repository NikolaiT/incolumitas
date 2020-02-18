Title: Create your own font the hard way!
Date: 2013-10-16 15:06
Author: Nikolai Tschacher
Category: Learning
Tags: Captcha, Programming, Design, Glyphs, Learning, Font
Slug: create-your-own-font-the-hard-way
Status: published

*Last major update on 23.10.2013*  

### Preface

As promised previously in my last article, I will guide you through the
creation process of a rudimentary font. I will use the glyphs of my font
to draw captchas and incorportate the implementation in my brand new
captcha plugin for wordpress. There are already quite a few captcha
plugins out there, some of them are better than mine
([RECAPTCHA](http://www.google.com/recaptcha)for instance translates
books and thus solves two problems at the same time),
[others](http://wordpress.org/plugins/captcha/) are worse, because the
math equations can simply be parsed (As far as I can judge without
inspecting the code further).

In this article however, I will center the focus entirely on the font
and abstract from it's future usage in the captcha.

### Technical background of fonts

A logical start of font creation is to answer the question what type of
font we are going to create. But lets first introduce some concepts that
are of importance when it comes to font design.

In short: A font is a collection of glyphs. Each glyph has a shape and
there are various ways of describing that shape. You can imagine a glyph
as a instanteation of a character. Whereas a character is a conecpt a
glyph is a reification of that concept. When we speak of glyphs, we are
interested in the form, design and view of the character, not the
character itself as a carrier of information. Now in our latin font,
there is a one-to-one mapping of glyphs to characters. But in some other
languages there might be different glyphs for a character depending on
the adjacent characters (For instance in arabic some characters have
four or more different glyphs).

Now lets answer the question which font format we are going to choose.
Essentially, there are three different font types, each of them with
different advantages and drawbacks. They are:

-   #### Bitmap fonts

    Fonts in this format are described in a array of pixels (a bitmap).
    You can imagine the array as a two-dimensional coordinate system and
    when rasterizing the font you just copy that array in the coordinate
    system of the output canvas. The glyph information is rather
    unflexible, because there is not an easy and intuitive way to resize
    the single glyphs and therefore there are usually different bitmaps
    for the different sizes and stlyes of penmanships such as cursive,
    bold or normal.

-   #### Outline fonts

    This format takes a different approach. Here we won't store the
    actual coordinates of glyphs. Instead we store the information of
    how to draw the glyphs as a mathematical function with different
    paramters which control the shape (cursive, bold, normal) and size
    (12px, 36px, npx) and other aspects of the appearance of each glyph.
    An outline is a set of contours or paths, and the paths consist of
    Bézier splines and simple lines. The splines are normally quadratic
    or cubic bezier curves. Therefore the glyphs are only rastered when
    the application already determined all the parameters. Outline fonts
    are very dynamic and powerful, but require a lot more of processing
    power compared to bitmap fonts. Postscript and truetype fonts are
    examples of this format.

-   #### Stroke fonts

    Are stroked fonts, where each stem of the glyph is represented by
    one line down the center of the stem, and the line is later drawn
    with a certain widt. I am not particularly
    interested in stroke fonts, but in the case you are, just read it up
    in the interwebs.

I will develop a outline font, but compared to
TrueType/OpenType/PostScript fonts, it will be in a very basic format
and not even include the full alphabet (Just around 10-15 characters).
Furthermore I will use quadratic and cubic Bézier splines. The glyphs
will be of very very easy shape (Each glyph will essentially be only a
path), but for some characters I will add some additional parameters to
illustrate the entire possibilities. The final plugin written in PHP
will be able to save the captchas to png and bbm files, both of them are
bitmap formats.  
It'd be certainly possible to directly use vector graphic techniques
(Such as scalable vector graphics) and let the plugin just generate
them. As a layman, I think this would be considerably faster and a
*better* solution, since I can use the high level language SVG and the
rasterization process will happen on the client-side and not on the
server as in my intentional approach.

### Why is this faster?

Because the most time consuming process is the rasterization of the
specific Bézier splines and simple lines that define the single glyphs
of the font. SVG files just describe the shape of these characters, but
the final drawing process to the monitor happens in the browser of the
client.  
But on the other side, I guess that .svg captchas are more easily
deciphered (OCR in short), because the cracker does not have to remove
noise and guess the bitmap structure which comprises the actual letters
(Please leave a comment if you think differently).  
That being said, I will still use the latter way (Plotting my captcha
directly and producing bitmap pictures like PNG's) in the full
conscience that it might be the worse solution (Heck, writing captcha
software in 2013 *is* certainily a bad idea). But all this is legitmated
with the fruitful learning process that accompanies the coding process.

Now in the case you shrug your shoulders when I mention Bézier curves,
consider reading my [previous blog
article](http://incolumitas.com/2013/10/06/plotting-bezier-curves/) that
also includes a bunch of links to very nice resources. Be aware that
quite a bit of math hides behind Bézier splines and that I won't use
heavily optimized algorithms for plotting the splines, simply out of the
reason that I don't have the mathematical/algorithmic knowledge and
skill to do so.

If I got you hooked and you also want to create your own fonts and you
want to really use them everywhere and save them in a offical format
such as PostScript, SVG or TrueType/OpenType, consider the application
FontForge [Link goes here], that helps you quite a lot and bewares you
of the quirky low level plotting algorithms. For my font, I just use
FontForge and Inkscape to get a look and feel experience of how my
glyphs sould look like, since it's kinda hard to think entirely in
points and control points of Bézier splines without actually drawing
them ;)

### Approach

Because I needed some kind of sketch board to develop and design my
glyphs, I looked for a vector graphics application.
[Inkscape](http://inkscape.org) really fit perfectly and it generates
easy parsable .svg files. Then I created a little script that was
capable of exporting the Bézier points and line points of the .svg files
generated by Inkscape. That wasn't too hard, since .svg is a W3C
standard and the <path> element is perfectly described
[here](http://www.w3.org/TR/SVG/paths.html#Introduction).

The export script I made looks like this (Please consider that only
closed paths and cubic/quadratic and lines are properly parsed! If this
is not enough for your pupose, the script is easy extendable tough):

    :::python
    # Parse inkscap svg files and tries to obtain all bezier curves points and lines.
    # Assumes that only one glyph is drawn and extracts ALL bezier points 
    # in the main  (called 'layer1' in inkscape). Only heterogenous bezier 
    # paths and straight lines are parsed correctly.
    # Read: http://www.w3.org/TR/SVG/paths.html#Introduction
    # Author: Nikolai Tschacher
    # Date: 14.10.2013
    # Site: incolumitas.com

    import sys
    try:
        from lxml import etree
    except ImportError:
        sys.stderr.write('Ohh boy, it seems that you didn\'t install lxml. Try "pip install lxml"\n')
        sys.exit(0)

    class InvalidGlyphShape(Exception):
        '''
        This Exception is raised when the parser discovers a  element
        that he cannot read.
        '''
        
    # lxml is awesome   
    def parse_glyph(fname):
        for event, element in etree.iterparse(fname, tag='{*}g'): # "{*}" includes the whole xml namespace
            if element.get('id') == 'layer1': # Inkscape packs all the shapes in a  container and calls it "layer1" by default
                for path in element.iter(tag='{*}path'): # Find ALL(!) path elements
                    yield path.get('d')

    def parse_path(fname):
        # What format do we need? List of sequence of tuples
        # like [[(43,233), (4434, 222), (87, 387)], [(63,23), (44, 12), (87, 337)], ...]
        # each of them constituting points of a cubic Bézier spline.
        # ... Analogeous for the other shapes...
        for d in parse_glyph(fname):
            lines = []
            c_splines = []
            q_splines = []
            data = d.split(' ')
            
            if data[-1] != 'z':
                raise InvalidGlyphShape('Path is not a closed shape')
            
            # If a moveto is followed by multiple pairs of coordinates,
            # the subsequent pairs are treated as implicit lineto commands.
            cmd = data.pop(0)   
            if cmd not in ('M', 'm'):
                raise InvalidGlyphShape('No move command Mm')
            else: # Check for implicit lineto cmd.
                if (not is_cmd(data[0]) and not is_cmd(data[1])):
                    lines.extend([c for c in chunks(sublist(data[0:]), 2)]) # Lil hack here :)
                    
            # Magic parsing begins. Very basic parser.
            for i, e in enumerate(data):
                if e in 'Cc':
                    data.pop(i)
                    c_splines.extend([c for c in chunks(sublist(data[i-1:]), 4)])
                if e in 'Qq':
                    data.pop(i)
                    q_splines.extend([c for c in chunks(sublist(data[i-1:]), 3)])
                if e in 'Ll':
                    data.pop(i)
                    lines.extend([c for c in chunks(sublist(data[i-1:]), 2)])
                if e in 'Zz' and i == len(data)-1: # closepath (close the current shape by drawing a line to the last moveto)
                    # With "closepath", the end of the final segment of the subpath is "joined"
                    # with the start of the initial segment of the subpath.
                    lines.append([data[i-1], data[0]])
            
            cleaned = clean(cubic_bezier=c_splines,
                         quadratic_bezier=q_splines,
                         simple_lines=lines)
                
            yield cleaned
                         
    # clean the data. For some reason my algorithm yields single points. Just
    # remove them and the data is solid.     
    def clean(**args):
        keys = sorted(args.keys())
        for kw in keys:
            args[kw] = [e for e in args[kw] if len(e) > 1]

        
        # Make integer coordinates ready to be rasterized.   
        for kw in keys:
            args[kw] = [[tuple([int(float(i)) for i in p.split(',')]) for p in geo_el] for geo_el in args[kw]]
            
        return args
                
    # print the glyph data.
    def pretty_print(args):
        keys = sorted(args.keys())
        print('----------------------- Next  data -------------------------')
        
        for kw in keys:
            print('\n***********\nPoint data for %s' % kw)
            print(args[kw])
                    
    # Returns a sublist up to the next cmd.
    def sublist(l):
        for i, e in enumerate(l):
            if e in 'CcQqLlZz': # SVG path commands
                return l[0:i]
                
    # Check if element is a command within d attribute in  element.
    def is_cmd(e):
        if e in 'CcQqLlZzMm':
            return True
        else:
            return False
            
    # Make chunks                          
    def chunks(l, n):
        for i in range(0, len(l), n-1):
            yield l[i:i + n]
        
    if __name__ == '__main__':
        try:
            open(sys.argv[1], 'r') # raises an exception if file can't be located
            for i in parse_path(sys.argv[1]):
                pretty_print(i)
        except FileNotFoundError as e:
            print('[-] No such file, sir')
        except IndexError:
            print('[-] Usage: %s SvgFile' % sys.argv[0])

Now the font design can finally begin! I searched for inspiration at
googlefonts and tried to redraw the glyphs freehand. This is of course
really unprofessional, because if you actually want to implement a
*real* font, you're better off using FontForge, a nice open source
program that incorporates many tools that help you create a
sophisticated font. I won't get down that path, instead I just
implemented some cool glyphs according to my taste and after a short
design period, I imported them with the script listed above into my
python font module that was already equipped with the plotting
algorithms I discussed in the [previous
article](http://incolumitas.com/2013/10/06/plotting-bezier-curves/). In
the aforementioned module, I am also going to store the glyph data
(Implemented as a list of points).

Here are some screenshots that you guys can get a impression how my
workflow was.

First I roughly outline the shape of the glyph and it looks like this:  

[![raw-shaping a glyph]({static}/uploads/2013/10/unedited-1024x576.png)

Then after some reshaping:  

[![fine-tuning the glyph]({static}/uploads/2013/10/better-1024x576.png)

And finally after I exported it and redrawn it using my own
module: [![plotting with own implementation]({static}/uploads/2013/10/Drawing_myself-1024x576.png)

And to end this post, I will present you my final alphabet all drawn on
a tkinter canvas with my own plotting algorithms. There are also
variants where the alphabet is skewed and a shear operations ar applied.
Here are the screenshots:

[![All Glyphs]({static}/uploads/2013/10/all_glyphs-1024x576.png)

All the glyphs drawn in a scatter. They are imported from the Inkscape
.svg files and plotted using the algorithms developed in the
[last](http://incolumitas.com/2013/10/06/plotting-bezier-curves/) blot
post.

And after applying some linear transformations:

[![Shear
transformation]({static}/uploads/2013/10/shear_applied-1024x576.png)

In this picture all glyphs moved using shear operations

[![Skew transformation]({static}/uploads/2013/10/skew-1024x576.png)
Skew linear transformation.

My glyphs are far from beautiful or even consistent, but this isn't
really a drawback either, since I will use them for my captcha plugin
(Whose implementation in PHP will be presented in the next blog post).
But the clear advantage is obviously that all my glyphs (although they
don't really look so) consist of simple lines and Bézier splines, which
means that we can express them as a mathematical function and therefor
apply a wide range of transformations on them without any loss of
information! After blurring the glyphs to our liking, we can finally
export it as a raster grafics format (such as png) and they eventually
become immutable. Maybe I will add in the PHP imlementation a way to
fill the glyphs with color in order to obliterate pattern recognition
methods.  
As mentioned before, If you are interested in professional font/glyph
design, visit [fontforge.org](http://fontforge.org) and read the great
resources over there.

And that's the end! Stay tuned for the final article of my series, that
will talk about the captcha plugin!

### Links

-   [The github repository that contains all of the above code
    snippets](https://github.com/NikolaiT/CunningCaptcha)
-   [The fontforge home page](http://fontforge.org)
-   [The great vector drawing program Inkscape](http://inkscape.org/)
-   [A wonderful insight into the applications of Bézier curves. Really
    high quality stuff!](http://pomax.github.io/bezierinfo/)
-   [All possible ways to move/rotate/shear
    points](http://en.wikipedia.org/wiki/Transformation_matrix)
    -   [Computer Fonts](http://en.wikipedia.org/wiki/Computer_font)
    -   [Rastering
        lines](http://en.wikipedia.org/wiki/Bresenham's_line_algorithm)
    -   [Wikipedia about Bézier
        curves](http://en.wikipedia.org/wiki/B%C3%A9zier_curve)
    -   [SVG w3
        standard](http://en.wikipedia.org/wiki/Scalable_Vector_Graphics)

  -   [Rastering
        lines](http://en.wikipedia.org/wiki/Bresenham's_line_algorithm)
    -   [Wikipedia about Bézier
        curves](http://en.wikipedia.org/wiki/B%C3%A9zier_curve)
    -   [SVG w3
        standard](http://en.wikipedia.org/wiki/Scalable_Vector_Graphics)


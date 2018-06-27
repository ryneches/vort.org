Title: Why doesn't your lab have a 3D printer yet?
Date: 2012-11-20 06:30:22
Category: science
Slug: why-doesnt-your-lab-have-3d-printer-yet
Author: Russell Neches
Tags: code, free, software, hardware, science, eisenlab, research
Summary: Use a 3D printer to make your own gel combes. Here's the code to design your own.


Electrophoresis setups are like Tupperware. You can never find the right
lid when you need it, and someone always seems to be borrowing the
doohicky you need.

Here in the Eisen Lab, it turns out we've been using Marc Facciotti's
electrophoresis stuff for years. He keeps his stuff organized, and,
well... that's not been our strong suit lately. John, our lab manager,
has been gently but inexorably herding us towards a semblance of
respectability in our lab behavior. As part of this, he decided that it
was time for us to get our electrophoresis stuff straightened out. So,
he ordered a bunch nice of gel combs from one of our suppliers. They
cost [$51
each](http://www.krackeler.com/products/1986-Systems/13300-Model-B2-EasyCast-Mini-Gel-Electrophoresis-System.htm)
(see the "12 tooth double-sided comb", catalog number 669-B2-12, for the
exact one pictured below). We bought six of them with different sizes
and spacing, for a total exceeding $300.

While I appreciate that companies need to make money, this is a
ridiculous price for a lousy little scrap of plastic. $300 for a couple
of gel combs is cartel pricing, not market pricing. Fortunately, we
happen to have a very nice [3D printer](http://ultimaker.com). It is
very good at making little scraps of plastic. So, I busted out the
calipers and tossed together some models of gel combs in
[OpenSCAD](http://www.openscad.org/). A few minutes of printing later,
and the $51 gel combs are heading back to the store.

![Original and 3D printed gel combs](http://vort.org/media/images/gel_combs_ultimaker.jpg)

Here's the code for the six well 1.5mm by 9mm comb :

```
f=0.01;
difference(){
  difference(){
    union(){
      cube( [ 80, 27, 3 ] );
      translate( [ 5.25, 14.3, f ] ) cube( [ 68, 9.3, 7.25 ] );
    }
    for ( i = [ 0:5 ] ) {
      translate( [ 17.1+i*11.0, -f, -f ] ) cube( [ 1.75, 12, 5 ] );
    }
  }
  union(){
    translate( [ -f,   -f, -f ] ) cube( [ 7,  12, 7] );
    translate( [ 73+f, -f, -f ] ) cube( [ 7,  12, 7] );
    translate( [ 0,    -f, 1.6] ) cube( [ 80, 12, 8] );
  }
}
```

Pretty easy to grasp, even if you've never seen SCAD before.

So, how much did this cost?

I ordered this plastic from ProtoParadigm at [$42 for a
kilogram](http://www.protoparadigm.com/products/filament/3mm-white-pla-plastic-filament-2-2lb-1kg-spool-1/).
That's about four pennies a gram. Each of these gel combs cost about 21
cents to print. That's 1/243rd the price.

The 3D printer cost &euro;1194.00 ($1524.62), which is less than the laptop
I use for most of my work. The savings on just these gel combs has
recuperated 18% of the cost of the printer.

It's also important that I was able to make some minor improvements to
the design. The printed combs fit into the gel mold a bit better than
the "official" ones. I also made separate combs for the 1.0mm and 1.5mm
versions, and the labels are easier to read. If I wanted, tiny tweaks to
my SCAD file would let me make all sorts of fun combinations of
thicknesses and widths that aren't available from the manufacturer. So,
these gel combs are not only $\frac{1}{243}$'rd the price, but they are also
better.

If you read the media hype about 3D printing, you will undoubtedly
encounter a lot of fantastical-sounding speculation about how consumers
will someday be able to print living goldfish, or computers, or
bicycles. Maybe so. Maybe not. However, *right now*, you can print basic
lab supplies and save a pile of money.

Buy your lab manager a little FDM printer and hook them up with some
basic CAD training. Yes, the printer will probably mostly get used to
make [bottle openers](http://www.thingiverse.com/thing:26299) and
[Tardis cookie cutters](http://www.thingiverse.com/thing:14533). So
what? Your paper-printer, if you will excuse the
[retronym](http://en.wikipedia.org/wiki/Retronym), mostly gets used for
non-essential stuff too. I'd wager that for every important document
printed in your lab, a hundred sheets have gone to Far Side cartoons and
humorous notices taped up in the bathroom. It's a negligible expense
compared to the benefits of having a machine that spits out documents
when you really need them, and the social value of those the Far Side
cartoons probably sums to a net positive anyway.

Conclusion : If you have a lab, and you don't have a 3D printer, you are
wasting your money. Seriously.

In the time it took write this post, I printed $150 worth of gel combs,
and it cost less than a cup of coffee.

**Updates** : Here is the tweet [I originally posted about this
article](https://twitter.com/ryneches/status/270803509186809856#),
before the URL for it vanishes into Twitter's memory hole. Here's an
encouraging post [from the Genome Web
blog](http://www.genomeweb.com/blog/practically-printing-money), and a
nice [article by Tim Dean at Australian Life
Scientist](http://www.lifescientist.com.au/article/444288/3d_printers_enter_lab/).
My article here seems to have [spawned a thread on
BioStar](http://biostars.org/p/57425/). Also, it made Ed Yong's [Missing
Links](http://blogs.discovermagazine.com/notrocketscience/2012/11/24/ive-got-your-missing-links-right-here-24-november-2012/)
for November 24 over at Discover, and Megan Treacy did a really spiffy
article over at
[Treehugger](http://www.treehugger.com/clean-technology/3-d-printing-lab.html).

Many people have asked, and so I decided to see how well these kinds of
3D printed parts do in the autoclave. I tried it out with a couple of
bad prints, and they seemed to hold up just fine after one or two
cycles. Very thin parts did warp a bit, though, so I recommend printing
parts you plan to autoclave nice and solid. Here is a
[before](https://twitter.com/ryneches/status/276132833108574209) and
[after](https://twitter.com/ryneches/status/276149084438540288) of a
single-wall part (less than half a millimeter thick). I was expecting a
puddle.

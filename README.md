<h2> Seattle Local Music web app</h2>
<p>This is a web app built with Flask that will find and display the next musical act 
performing at any given stage in Seattle.</p>
<p>Let me start by saying yes, I know the front end code for this website is an abhorrent mess.  No,
I do not plan to clean it up any time soon, but maybe one day once I really buckle down on learning 
front-end development more thoroughly.  Writing the Python was a blast</p>


<h3>How does it work?</h3>
<p>This program works by visiting the websites for all of the listed venues once per day and
sends back the text from the soonest upcoming event.  Then it saves that information into a CSV file
on Google Cloud, which is reference whenever a user visits the site.  This way, we are not scraping
these websites every single time a user visits, cutting down on our resource consumption as well as 
the burden to the venues' websites.</p>

<p>When a user visits the site, the program pulls the information stored on the CSV file, formats
 it into a dictionary, and sends it over to index.html to be presented to the user.</p>

<p>I designed the map using Figma, which I then exported to in-line SVG code.  To make it
interactive, I used knowledge I ganed from Peter Collingridge's website, which can be found at 
<a href="https://www.petercollingridge.co.uk/">PeterCollingridge.co.uk</a>.  Peter, thanks
for making this wonderful resource!  This was invaluable and SO much fun to implement and play
around with.</p>

<h3>Know BeforeYou Go...</h3>
<p>This project utilizes TicketMaster's API to pull event data for two venues whose website's do not
allow for any kind of web scraping. This is deeply unfortunate. If you want to use
that same functionality, you'll need to sign up for a key; there is a free version. In the name of 
full transparency, I must declare that TicketMaster must die, both in this project and the world
at large, and Michael Rapino, who is a leech on the human race and everything that makes life worth 
living, may kindly go fuck himself.</p>

<p>The shows are now almost all sourced through scraping the calendars of each venue's website. Each 
website gets its own scraping code block since the HTML structure for each site is unique.  I used the
SelectorLib library and browser tool to help me the select specific elements needed and to compose the 
YAML files needed to extrat the desired information, then wrote modules for each venue to parse and 
format the data into a consistent format - no pre-packaged scraping bots are used here.</p>
<p>All in all, the code behind this project is nothing spectacular or special.  It has, however, 
been thoroughly gratifying to look back on how the project evolved from a command line print-out to 
a pretty nice looking tool as I got deeper in relearning how to program.  I'm very happy to have 
this tool, and I hope that it will allow other music-lovers to get deeper into the local scene, 
either here in Seattle, or in other regions should they choose to build on what I have made.</p>
<p>If you're wondering why I didn't program this in an object-oriented manner, it's because I felt
that was unnecessary given the fact that each scraping module is different.</p>
<p></p>
<p></p>
<p></p>
<p></p>
<p></p>
<p></p>
<p></p>
<p></p>
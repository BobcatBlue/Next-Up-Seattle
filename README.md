<h2> Seattle Local Music web app</h2>
<p>This is a web app built with Flask that will find and display the next musical act 
performing at any given stage in Seattle.</p>
<p>This project used to utilize TicketMaster's API to find shows at certain venues, but this was
proven to be ineffective since not every show at a given venue is ticketed through 
TicketMaster.  The call_shows() function in cronjob.py, however, is still there - commented out - 
for your reference if you'd like to use that information.</p>
<p>The shows are now all sourced through scraping the calendars of each venue's website.  Each 
website gets its own scraping code block since the HTML for each site is unique.</p>
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
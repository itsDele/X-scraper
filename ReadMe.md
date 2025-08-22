V1.0.0 released check it out

This project is about scraper that extracts Accounts/profiles in X platform who retweeted and qouted certain public posts.
key features contain:

1-file input for start(like a json file)-why file input so we avoid hardcoding it by doing this we make it user friendy you can change the proxy settings in the file easily or change the targeted urls for posts

2-results output should be saved into a acceptable format of file which im planning to have multiple formats(JSON,CSV/Excel,Pandas,TXT)

3-im using Selenium why? X relies on JavaScript to load content ,Traditional scraping tools like requests or BeautifulSoup can’t execute JS Selenium can:
Click buttons,Scroll pages to trigger lazy loading,Wait for elements to appear and other stuff like pervent ip ban using proxys and support for Authentication

4-being able to use proxy which is explained in (3-)

5-using CLI to make it more user friendly and Automation why?:CLI allows you to Run the scraper without modifying the source code,CLI works headlessly which works with Docker containers and Cloud servers

these were the main features of the project
feature that could make perfomance better is using async so we can maybe half the time to process i have it in mind to implant it(its now implanted)

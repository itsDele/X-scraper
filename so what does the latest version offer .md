so our project was about scraper that targets certain x post urls and extracts accounts that retweeted and quoted the post 
version 1.0.0 which is functional but the code is written in sync so multiple urls takes too much time and the code is all written into the scraper.py without good information about functions and i wanted to implant async so i left v1 as it is.
version 2.0.0 right now offers the code in async which you can adjust the workers by python main.py --input-file input.json --max-concurrent 2 or change the hardcoded MAX_CONCURRENT_DEFAULT = 2 to the number you want
in the input file you have the options to use proxy,set your x creds,change the output directory,change the output formats to(["json", "csv", "excel", "txt"]) and thats it.
make sure to correctly config the input file or you get silent crashes 
this was a fun project for me i learned some new features i hope you enjoy it too.
for now im out of ideas for this project but if you have any suggestions feel free to contact me.
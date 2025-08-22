create venv via: python -m venv venv
to install requirements.txt after creating venv use: pip install -r requirements.txt
dont forget to download the latest version of chrome for our webdriver
now config the input.json like below and after that run this command to use the scraper:

python main.py --input-file input.json --max-concurrent 2
you can adjust the max concurrent to 1 or more based on your network and system spec(2 for 8 GB RAM, 4 for 16 GB RAM)
while you are adjusting your input file keep in mind that the username,password,email must be correct and valid or the code will not run
in browser.py at the setup_driver function you can add the headless argument for reduced gpu use and its better perfomance if you are using a server just remove my # and the comment after chrome_options.add_argument("--headless")
in utils.py you can adjust the class Constants to your like their info is commnted infront of them
hope you enjoy!
--------------------------------------------------------------------------------------------------------------------------------------------------------
Example input.json:
{
  "urls": [
    "https://x.com/clcoding/status/1957509803057574278"
  ],
  "output_formats": ["json", "csv"],
  "credentials": {
    "TWITTER_USERNAME": "your_username",
    "TWITTER_PASSWORD": "your_password",
    "TWITTER_EMAIL": "your_email"
  },
  "proxy": {
    "host": "proxy.example.com",
    "port": 8080,
    "username": "proxy_user",
    "password": "proxy_pass"
  },
  "output_dir": "results"
}
-----------------------------------------------------------------------------------------------------------------------------------------------------------------
urls example:
"urls": [
  "https://x.com/clcoding/status/1957509803057574278",
  "https://x.com/another_user/status/123456789"
]
------------------------------------------------------------------------------------------------------------------------------------------------------------------
output_formats:
["json", "csv", "excel", "txt"]
Example:
"output_formats": ["json", "csv"]
------------------------------------------------------------------------------------------------------------------------------------------------------------------

credentials must be valid or you get errors
"credentials": {
  "TWITTER_USERNAME": "your_username",
  "TWITTER_PASSWORD": "your_password",
  "TWITTER_EMAIL": "your_email"
}
------------------------------------------------------------------------------------------------------------------------------------------------------------------

proxy Example:
"proxy": {
  "host": "proxy.example.com",
  "port": 8080,
  "username": "proxy_user",
  "password": "proxy_pass"
}

username (optional): Proxy authentication username.
password (optional): Proxy authentication password.

 
"proxy": {} (no proxy).
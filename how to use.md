




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

urls example:
"urls": [
  "https://x.com/clcoding/status/1957509803057574278",
  "https://x.com/another_user/status/123456789"
]

output_formats:
["json", "csv", "excel", "txt"]
Example:
"output_formats": ["json", "csv"]

credentials must be valid or you get errors
"credentials": {
  "TWITTER_USERNAME": "your_username",
  "TWITTER_PASSWORD": "your_password",
  "TWITTER_EMAIL": "your_email"
}

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
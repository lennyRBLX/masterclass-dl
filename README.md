# masterclass-dl

## DISCLAIMER

I am in no way condoning usage and/or support downloading materials from Masterclass! I am not responsible for any usage before, current, and after release of this source. This repository is purely educational in nature. Please take great care in confirming usage of this source is legal and allowed by the parties involved.

## Requirements

- Account
- Paid Subscription
 = For most courses, some free lessons are provided by Masterclass
- Cookie Editing extension
 = https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg
 = https://addons.mozilla.org/en-US/firefox/addon/etc2/?utm_source=addons.mozilla.org&utm_medium=referral&utm_content=search
- Python (3.7+)
 
## Explanation

1. Install the required packages
 - Run "python -m pip -q install -r /root/.Skillshare-DL/requirements.txt" in System/Admin-Privileged Console
2. Log in to Masterclass
3. Open your Cookie Editor
4. Copy the '_mc_session' cookie
5. Paste & replace "PASTEHERE" in dl.py
6. Run the program
 - python dl.py "SITE_URL_HERE"
 - ex: python dl.py "https://www.masterclass.com/classes/gordon-ramsay-teaches-cooking"

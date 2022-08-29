# Automate Kendo -> Facebook ->  Youtube -> Whatsapp
some shitty scripts to achieve the task above where we record the live videos in Facebook and upload the live video to Youtube and finally posting the youtube link to Whatsapp group

# To execute...
First you have to be an admin of the FB page, get from MC kun
Then go to facebook developer graph api explorer and populate the constant.py variables...

then run the command below:
```
python .\automate_fb_kendo.py
```
Please take note that whenever you run a new instance, should get the latest user short lived access token again. I think permanenent token only works if the program is running without stopping because generating the permanent token is only ran once during startup

## Requirements
pip install -r requirements.txt
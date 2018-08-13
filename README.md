# paymo-tasker
## About
This tool is for users of Paymo project management and time keeping app.

* For personal use only because of no password protection

* Mark batch time entries as billed

* Generate and download invoices from time entries (.xlsx format)


I wrote this tool because I did not want to manually mark my time entries as billed.

There is another feature in this tool that allows one to create payment and subscription portals. It uses Stripe as backend and payment processing. I do not recommend hosting any of this code online since it is not password protected.

This tool is meant to be run locally and only when needed.

## Setup
```
# Clone repo and cd into it.
# Create and activate virtual environment.
$virtualenv env
$. env/bin/activate
# Install requirements
$pip install -r requirements.txt
```
### The config file
Create `settings.sh` file
```
#!/bin/sh
export API_KEY_STRIPE="your stripe api key";
export API_KEY_STRIPE_PUBLIC="your public stripe api key";
export API_KEY_PAYMO="your paymo API key";

export COMPANY_ADDRESS1="Your company or office address";
export COMPANY_ADDRESS2="Bell Gardens, CA (putting my city on the map)";
export COMPANY_PHONE="555-555-55555";
export COMPANY_URL="www.cisko3000.com";

```
`chmod +x settings.sh`
## How to run
`$export APP_SETTINGS="config.DevConfig"`

`. settings.sh`

`python run.py`
# Screenshots

<img src="https://imgur.com/XIZsDAA.jpg" width="350px">


<img src="https://imgur.com/JdS63l1.jpg" width="350px">


<img src="https://imgur.com/1js6RLH.jpg" width="350px">

My web dev portfolio:
* <https://www.losangelescoder.com>

My music:
* <https://soundcloud.com/cisko3000>

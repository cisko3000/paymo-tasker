# paymo-tasker
## Setup
```
# Clone repo and cd into it.
# Create and activate virtual environment.
virtualenv env
. env/bin/activate
# Install requirements
pip install -r requirements.txt
```
### The config file
Create `settings.sh` file
```
#!/bin/sh
export API_KEY_STRIPE="your stripe api key";
export API_KEY_STRIPE_PUBLIC="your public stripe api key";
export API_KEY_PAYMO="your paymo API key";

```
`chmod +x settings.sh`
## How to run
`$export APP_SETTINGS="config.DevConfig"`
`. settings.sh`
`python run.py`
# Screenshots

![alt text](https://imgur.com/XIZsDAA "Index")


![alt text](https://imgur.com/JdS63l1 "Clients List")


![alt text](https://imgur.com/1js6RLH "Mark Billed")

[My web dev portfolio](https://www.losangelescoder.com)

[My music](https://soundcloud.com/cisko3000)

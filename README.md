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

![Index](https://imgur.com/XIZsDAA.jpg | width=200)


<img src="https://imgur.com/JdS63l1.jpg" width="200px">


![Mark Billed](https://imgur.com/1js6RLH.jpg)

My web dev portfolio:
<https://www.losangelescoder.com>

My music:
<https://soundcloud.com/cisko3000>
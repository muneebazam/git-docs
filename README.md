# Automated Documentation Pipeline

This repository features a collection of lambda functions which power the automated documentation pipeline to build my projects website located [here](http://muneebazam.com/projects/)

<br/>

## Setup

1. Install Python 3 **(Python 2 will not work)** 

```
brew install python3
```

Alternatively you can download the Python installer here: https://realpython.com/installing-python/ 

<br/>

2. Install Hugo

``` 
brew install hugo
```

Alternatively you can download the executable here: https://github.com/gohugoio/hugo/releases

<br/>

3. Clone Repository and Download Dependencies

```
git clone https://github.com/LoyaltyOne/dev-portal-lambdas.git
pip install -r requirements.txt
```

<br/>

4. Set Secret Environment Variable

```
export AWS_SECRET_MANAGER=developer-portal-publisher
```

*This is set on our lambda instances as well and allows us to retrieve secrets from AWS Secret Manager*

<br/>

## Usage

To run the complete build pipeline locally:

```
python site_publisher.py 
```

- This will create a `tmp/` directory folder for the repository site that was built.

_Note: the `tmp/` folder must be manually deleted, this is done to prevent accidental deletes between successive runs.

<br/>

## CD

When a commit is made to the master branch of this repository a Jenkins job is triggered to run `deploy.sh`, which deploys the updated code changes to the respective AWS lambda functions. 

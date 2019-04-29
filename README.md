# Automated Documentation Pipeline

This repository features a collection of lambda functions which power the automated documentation pipeline for the developer portal. 

The `tardis_bot/` directory also contains a set of lambda functions which power the TARDIS slackbot used to onboard/remove repositories and trigger builds for the developer portal. 

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
python external_portal_wrapper.py 
```
 
- This will create a `tmp/` directory with a folder for each hugo site created during the build process.
- When running locally, each microsite is built synchronously rather than the asynchoronous builds on lambda instances.

To build a microsite for a specific repository locally:

```
python external_portal_publisher.py <repo_name> <repo_url_to_docs_folder>
```

- This will create a `tmp/` directory containing a `<repo_name>` folder for the microsite that was built.

_Note: the `tmp/` folder must be manually deleted, this is done to prevent accidental deletes between successive runs.

<br/>

## CD

When a commit is made to the master branch of this repository a Jenkins job is triggered to run `deploy.sh`, which deploys the updated code changes to the respective AWS lambda functions. 

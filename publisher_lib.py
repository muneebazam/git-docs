# A collection of common functions used by the git docs framework 

import os
import logging
import json
import boto3
import subprocess
import base64
import sys
import re
import shutil
import requests
from botocore.exceptions import ClientError

# Generates a swagger page and moves the swagger spec, if required
def move_repository_icon(name, content_dir, image_dir):
    image_file = "{0}{1}/{1}.png".format(content_dir, name)
    if (os.path.isfile(image_file)):
        print("attempting move")
        print(image_dir)
        shutil.move(image_file, image_dir)
        return 0
    return 1

# Wrapper function to subprocess.run (pipes all stdout/stderr to log file)
def run_subcommand(command, print_output=True):

    try:
        completed_process = subprocess.run(command)
        if print_output and completed_process.stdout:
            logging.info(completed_process.stdout)
        if print_output and completed_process.stderr:
            logging.error(completed_process.stderr)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        logging.error(e)
        raise e

    return completed_process.returncode

# Client to retrieve envars from AWS Secret Manager
def secret_manager_client(secret_name):

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name="us-east-1"
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        logging.error(e)
        raise e
    else:
        if 'SecretString' in get_secret_value_response:
            return get_secret_value_response['SecretString']
        else:
            return base64.b64decode(get_secret_value_response['SecretBinary'])


# Clone developer portal repository and configure Git environment
def git_env_setup(repo_url, repo_name): 

    try:
        run_subcommand(["git", "clone", repo_url])
        os.chdir('./{}'.format(repo_name)) 
        run_subcommand(["git", "pull", "--force"])
    except (OSError, FileNotFoundError, subprocess.CalledProcessError) as e:
        logging.error(e)
        raise e

    return 0

# Retrieves repository config file and returns contents as type:dict
def repository_configuration(config_file):

    try:
        with open(config_file) as json_file:
            data = json.load(json_file)
            return data
    except (FileNotFoundError, IOError) as e:
        logging.error(e)
        raise(e)

    return 0

# pulls content(s) from specificed url with svn client
def svn_client(svn_url, user, password):

    try:
        run_subcommand(["svn", "export", "--force", svn_url, "--username", user, "--password", password])
    except subprocess.CalledProcessError:
        logging.warn("Could not pull contents from {}".format(svn_url))
        return 1

    return 0

# Modify git url to be compatible with svn client
def svn_urlify(git_url):

    # svn requires 'trunk'/'branch' to explicitly be in the url
    matches = re.findall("tree/master", git_url)
    if (len(matches)):
        return re.sub("tree/master", "trunk", git_url, 1)
    else:
        return re.sub("tree", "branches", git_url, 1) 

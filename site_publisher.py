"""
AWS Lambda function to dynamically build a web page from git documentation.
"""

import os
import logging
import json
import boto3
import subprocess
import sys
import shutil
import publisher_lib as portal

# Retrieve environment variables 
git_user = os.environ["GIT_USER"]
git_password = os.environ["GIT_PASSWORD"]
repo_name = os.environ["REPO_NAME"]
s3_bucket = os.environ["S3_BUCKET"]
base_url = os.environ["BASE_URL"]
output_dir = os.environ["OUTPUT_DIR"]

def build_website(data, context, base_dir="/tmp", local=False):

     # Configure logger and extract data
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Define global read-only variables 
    repo_dir = "{}/{}/".format(base_dir, repo_name)
    config_file = "{}config.json".format(repo_dir)
    content_dir = "{}content/".format(repo_dir)
    image_dir = "{}static/images/".format(repo_dir)

    # Clone and setup central repository, will terminate upon failure 
    try:
        repo_url = 'https://{}:{}@github.com/{}/{}.git'.format(git_user, git_password, git_user, repo_name)
        os.chdir(base_dir)
        portal.git_env_setup(repo_url, repo_name)
        logging.info("Cloned {} repository into tmp.".format(repo_name))
    except Exception as e:
        logging.error(e)
        sys.exit(1)

    # Retrieve JSON config file, will terminuate upon failure 
    try:
        config = portal.repository_configuration(config_file)
        logging.info("Read configuration file containing {} repositories.".format(len(config)))
    except Exception as e:
        logging.error(e)
        sys.exit(1)

    # Use svn client to pull in contents from each user repository 
    os.chdir(content_dir)
    for name, url in config.items(): 

        try:
            if (portal.svn_client(portal.svn_urlify(url), git_user, git_password)):
                logging.warn("Svn client functionality error.\n")
            os.rename("./docs", name)
            if (portal.move_repository_icon(name, content_dir, image_dir)):
                logging.warn("Could not locate repository icon.\n")
        except (FileNotFoundError, shutil.Error, subprocess.CalledProcessError):
            logging.error("Unable to successfully pull contents for {} repository.\n".format(name))
    

    # Build site and push to s3
    os.chdir(repo_dir)
    try: 
        if (local):
            portal.run_subcommand(["hugo", "-b", base_url])
        else:
            portal.run_subcommand(["/opt/hugo", "-b", base_url, "--destination", output_dir])
            portal.run_subcommand(["/opt/aws", "s3", "sync", output_dir, "s3://{}/{}/".format(s3_bucket, output_dir)])
            os.chdir(content_dir)
            for name, url in config.items():
                shutil.rmtree("./{}".format(name), ignore_errors=True)
                image_file = "{0}/{1}.png".format(image_dir, name)
                try:
                    os.remove(image_file)
                except OSError:
                    pass
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        logging.error(e)
        sys.exit(1)

    logging.info("Successfully generated static site.")
    return "200 OK"

# local testing
if __name__ == "__main__":
    base = "{}/tmp".format(os.getcwd())
    os.makedirs(base)
    class Context:
        function_name = "local-site-publisher"
        aws_request_id = "local"
    build_website({}, Context(), base_dir=base, local=True)


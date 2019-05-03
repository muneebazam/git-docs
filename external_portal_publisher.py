"""
AWS Lambda function to rebuild my personal website at muneebazam.com 
"""

import os
import logging
import json
import boto3
import subprocess
import sys
import shutil
import portal_common_lib as portal

# Retrieve environment variables 
secret_name = os.environ["AWS_SECRET_MANAGER"]

def build_website(data, context, base_dir="/tmp", local=False):

     # Configure logger and extract data
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Retrieve secrets from AWS Secret Manager, will terminate upon failure
    try:
        secrets_json = portal.secret_manager_client(secret_name)
        secrets = json.loads(secrets_json)
        git_user = secrets["git_user"]
        git_password = secrets["git_password"]
        repo_name = secrets["repo_name"]
        s3_bucket = secrets["s3_bucket"]
        logging.info("Retrieved {} secret from AWS Secret Manager.".format(secret_name))
    except Exception as e:
        logging.error(e)
        sys.exit(1)

    # Define global read-only variables 
    repo_dir = "{}/{}/".format(base_dir, repo_name)
    content_dir = "{}content/".format(repo_dir)
    swagger_dir = "{}static/swagger-ui/".format(repo_dir)
    spec_file_path = 0

    # Clone and setup central repository, will terminate upon failure 
    try:
        repo_url = 'https://{}:{}@github.com/{}/{}.git'.format(git_user, git_password, git_user, repo_name)
        os.chdir(base_dir)
        portal.git_env_setup(repo_url, repo_name)
        logging.info("Cloned {} repository into /tmp.".format(repo_name))
    except Exception as e:
        logging.error(e)
        sys.exit(1)

    # Use svn client to pull in contents from user repository 
    try:
        shutil.rmtree(content_dir, ignore_errors=True)
        if (portal.svn_client(url, git_user, git_password)):
            print("svn client error.\n")
            sys.exit(1)
        os.rename("./docs", "./content")
        spec_file_path = portal.move_swagger_file(name, content_dir, swagger_dir)
    except (FileNotFoundError, shutil.Error, subprocess.CalledProcessError):
        print("Unable to pull all contents for {} repository.\n".format(name))
    finally:
        os.chdir(repo_dir)

    # Build site and push to s3
    try: 
        if (local):
            portal.run_subcommand(["hugo", "--environment", "microsite"])
        else:
            portal.run_subcommand(["/opt/hugo", "-b", "http://{}/{}/".format(s3_bucket, name), "--environment", "microsite", "--destination", "./generated/{}".format(name)])
            portal.run_subcommand(["/opt/aws", "s3", "sync", "./generated/{}".format(name), "s3://{}/{}/".format(s3_bucket, name), "--acl", "public-read", "--only-show-errors"])
            # File cleanup to avoid OSError - since Lambda can reuse same instances
            shutil.rmtree(content_dir, ignore_errors=True)
            if (spec_file_path):
                os.remove(spec_file_path)
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
        function_name = "local-external-portal-publisher"
        aws_request_id = "local"
    build_website({}, Context(), base_dir=base, local=True)


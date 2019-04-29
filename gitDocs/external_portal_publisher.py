"""
Lambda function to rebuild a microsite on the AIR MILES developer portal.
Created by TARDIS (#rtc-workstream).
"""

import os
import logging
import json
import boto3
import subprocess
import sys
import shutil
sys.path.insert(0, '..')
import portal_common_lib as portal

# Retrieve environment variables 
secret_name = os.environ["AWS_SECRET_MANAGER"]

# lambda entry point
def build_microsite(data, context, base_dir="/tmp", local=False):

     # Configure logger and extract data
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    name = data["repo_name"]
    url = data["repo_url"]
    logging.info("Function invoked to build microsite for {}".format(name))

    # Retrieve secrets from AWS Secret Manager, will terminate upon failure
    try:
        secrets_json = portal.secret_manager_client(secret_name)
        secrets = json.loads(secrets_json)
        git_user = secrets["gitUser"]
        git_password = secrets["gitPassword"]
        slack_token = secrets["slackToken"]
        log_channel = secrets["logChannel"]
        repo_name = secrets["repoName"]
        s3_bucket = secrets["s3ExternalBucket"]
        logging.info("Retrieved {} secret from AWS Secret Manager.".format(secret_name))
    except Exception:
        portal.terminate_program("Terminating due to failed attempt at retrieving secrets.", slack_token, log_channel, context)
        sys.exit(1)

    # Define global read-only variables 
    repo_dir = "{}/{}/".format(base_dir, repo_name)
    content_dir = "{}content/".format(repo_dir)
    swagger_dir = "{}static/swagger-ui/".format(repo_dir)
    spec_file_path = 0

    # Clone and setup central repository, will terminate upon failure 
    try:
        repo_url = 'https://{}:{}@github.com/LoyaltyOne/{}.git'.format(git_user, git_password, repo_name)
        os.chdir(base_dir)
        portal.git_env_setup(repo_url, repo_name)
        logging.info("Cloned {} repository into /tmp.".format(repo_name))
    except Exception:
        portal.terminate_program("Terminating due to failure in setting up git environment.", slack_token, log_channel, context)
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
        portal.terminate_program("Terminating due to error in generating static site.", slack_token, log_channel, context)
        sys.exit(1)

    logging.info("Successfully generated static site.")
    return "200 OK"

# local testing
if __name__ == "__main__":
    if (len(sys.argv) != 3):
        print("Incorrect number of arguments.")
        print("USAGE: python external_portal_publisher.py <repo_name> <repo_url>")
        sys.exit(1)
    data = { 
        "repo_name" : sys.argv[1],
        "repo_url" : portal.svn_urlify(sys.argv[2])
    }
    base = "{}/tmp/{}/".format(os.getcwd(), sys.argv[1])
    os.makedirs(base)
    class Context:
        function_name = "local-external-portal-publisher"
        aws_request_id = "local"
    build_microsite(data, Context(), base_dir=base, local=True)


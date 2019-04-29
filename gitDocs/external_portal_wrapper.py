"""
Lambda function to trigger a rebuld of the AIR MILES developer portal.
Created by TARDIS (#rtc-workstream).
"""

import os
import logging
import json
import boto3
import sys
import shutil
import subprocess
import external_portal_publisher as publisher
sys.path.insert(0, '..')
import portal_common_lib as portal


# Retrieve environment variables 
secret_name = os.environ["AWS_SECRET_MANAGER"]

# lambda entry point
def build_wrapper(data, context, base_dir="/tmp", local=False):

    # Configure logger and lambda client
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    lam = boto3.client('lambda')

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
        secrets_json = portal.secret_manager_client(secret_name)
        secrets = json.loads(secrets_json)
        logging.info("Retrieved {} secret from AWS Secret Manager.".format(secret_name))
    except Exception:
        portal.terminate_program("Terminating due to failed attempt at retrieving secrets.", slack_token, log_channel, context)
        sys.exit(1)

    # Define global read-only variables 
    repo_dir = "{}/{}/".format(base_dir, repo_name)
    content_dir = "{}content/".format(repo_dir)
    generated_dir = "{}/public/".format(repo_dir)
    config_file = "{}external_config.json".format(repo_dir)
    landing_frontmatter = "+++\ntitle = \"AIR MILES Developer Portal\"\n+++\n"
        
    # Clone and setup central repository, will terminate upon failure 
    try:
        repo_url = 'https://{}:{}@github.com/LoyaltyOne/{}.git'.format(git_user, git_password, repo_name)
        os.chdir(base_dir)
        portal.git_env_setup(repo_url, repo_name)
        logging.info("Cloned {} repository into /tmp.".format(repo_name))
    except Exception:
        portal.terminate_program("Terminating due to failure in setting up git environment.", slack_token, log_channel, context)
        sys.exit(1)

    # Retrieve JSON config file, will terminuate upon failure 
    try:
        config = portal.repository_configuration(config_file)
        logging.info("Read config file containing {} repositories.".format(len(config)))
    except Exception:
        portal.terminate_program("Terminating due to failure in reading {}.\n".format(config_file), slack_token, log_channel, context)
        sys.exit(1)

    # Construct landing page with list of repositories
    site_index = open("{}_index.md".format(content_dir), "w+")
    site_index.write(landing_frontmatter)

    # Invoke micro-publisher lambda for each repository
    for name, contents in config.items():

        svn_url = portal.svn_urlify(contents["site_url"])
        payload = {
            "repo_name" : name,
            "repo_url" : svn_url,
        }
        if (local):
            os.chdir('../..')
            base = "{}/{}/".format(os.getcwd(), name)
            os.makedirs(base)
            publisher.build_microsite(payload, context, base, local)
        else:
            try:
                response = lam.invoke(FunctionName='external-portal-publisher',
                            InvocationType='Event',
                            Payload=json.dumps(payload))
            except Exception as e:
                logging.error("Error in invoking external-portal-publisher lambda function for {}.".format(name))
        site_index.write("{{{{% home-grid title=\"{}\" description=\"{}\" url=\"{}\" %}}}}\n".format(contents["site_title"], contents["site_description"], name))
    site_index.close()

    try: 
        if (local):
            os.chdir(repo_dir)
            portal.run_subcommand(["hugo", "--environment", "home"])
        else:
            portal.run_subcommand(["/opt/hugo", "--environment", "home"])
            os.chdir(generated_dir)
            portal.run_subcommand(["/opt/aws", "s3", "cp", generated_dir, "s3://{}/".format(s3_bucket), "--recursive", "--acl", "public-read"], print_output=False)
            # File cleanup to avoid OSError - since Lambda can reuse same instances
            os.remove("{}_index.md".format(content_dir))
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        logging.error(e)
        portal.terminate_program("Terminating due to error in generating static site.", slack_token, log_channel, context)
        sys.exit(1)

    logging.info("Successfully generated static site.")
    return "200 OK"

# local testing
if __name__ == "__main__":
    base = "{}/tmp/home/".format(os.getcwd())
    os.makedirs(base)
    class Context:
        function_name = "local-external-portal-wrapper"
        aws_request_id = "local"
    build_wrapper({}, Context(), base_dir=base, local=True)


---
title : Execution Overview
description : High level overview of the execution flow and configuration file.
weight : 1
---

## Execution Flow

The following is a list of chronological events that occur when the pipeline is triggered:

1. Repository containing site assets and configuration file is cloned 

2. Configuration file is parsed to determine repositories to pull from

3. Documentation contents are aggregated from all repositories

4. Hugo executable outputs a folder containing newly built static site

5. Folder containing generated content is published to a hosted location

<br/>

## Compononents

<br/>

### Configuration File

The configuration file is a JSON object with key/value pairs representing the name and URL for each repository. Below is the configuration file that builds this website:

```
{
    "git-docs" : "https://github.com/muneebazam/git-docs/tree/master/docs",
    "coffee-bot" : "https://github.com/muneebazam/coffee-bot/tree/master/docs",
    "automation-wizards" : "https://github.com/muneebazam/automation-wizards/tree/master/docs"
}
```

{{% notice warning %}} 
The URL must point to a `docs` folder in your repository. Git Docs does not make any assumptions on the file structure of your repository. Passing the generic URL to the root of your repository will result in Git Docs being unable to find your `docs/` folder (even if it exists in the root). 
{{% /notice %}}


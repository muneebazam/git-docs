---
title : Git Docs
description : Automatically updates a website in real-time using documentation that lives in your git repository.
weight : 97
---

Git Docs is a pipeline written in Python which pulls a `docs` folder containing markdown documentation from a git repository and publishes the contents onto a website in real-time. 

It works by cloning a repository containing site assets (html templates, images, css) and a configuration file listing repositories, pulling in documentation contents from each of the repositories, and building and publishing the static site to a hosted location. The pipeline has been built to work with [Hugo](https://gohugo.io/), the worlds fastest static site generation engine. 

This pipeline significantly reduces the amount of time required to update and deploy a webpage, leaving only the task of content creation to the user. Simply make a change to any markdown file in the `docs/` folder of your repository, and the pipeline will kick in and do the rest. 

{{% notice note %}}
The webpage you are currently viewing has been built using Git Docs. Navigating to the repositories for any of the projects listed on this page, you will notice a `docs/` folder in the root, which is the exact content that is published on this webpage. For example, the markdown file containing this pages content is pulled directly from the Git Docs repository [here](https://github.com/muneebazam/git-docs/blob/master/docs/_index.md).
{{% /notice %}}

For more detailed explanations on the various aspects of Git Docs check out the pages below:

{{% children description="true" %}}

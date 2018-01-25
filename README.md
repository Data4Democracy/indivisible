# indivisible
Aggregating call to action sites into a single application.

## Indivisible:

**Slack:** #indivisible

**Project Description:**
A variety of civic activism organizations have sprung up in the wake of the election to help mobilize and empower people. The organizations often operate by sending out daily or weekly “actions” that their supporters partake in – whether calling a Member of Congress’s office, attending an event, or reading a key piece of information. As these sites proliferate, it becomes difficult to effectively signal boost and target actions appropriately. 
For this project, we will build tools to 
* Identify various actions available for users by aggregating different sources of data
* Provide a clean user interface to filter and select actions they are interested in
* Build a dashboard and track action progress/effectiveness over time
* Engage user interest through social media or similar means to identify tasks for more effective actions

**Project Lead:**  
* [@bonfiam](https://datafordemocracy.slack.com/messages/@bonfiam )
* [@pg](https://datafordemocracy.slack.com/messages/@pg) 

**Maintainers (people with write access):**
We need people; please ping @pg or @bonfiam for your interest. 
Scroll down for an overview of current issues!

**Data:** [https://data.world/data4democracy/indivisible](https://data.world/data4democracy/indivisible)   
_Note: Create dataset for project in data.world and link it here._

### Getting started: 
* We welcome contributions from first timers
* Browse our help wanted issues, which are [summarized below](#current-issues). See if there is anything that interests you. [Tag Definitions](https://github.com/bstarling/gh-labels-template)
* Core maintainers and project leads are responsible for reviewing and merging all pull requests. In order to prevent frustrations with your first PR we recommend you reach out to our core maintainers who can help you through your first PR.
* Need to practice working with github in a group setting? Checkout [github-playground](https://github.com/Data4Democracy/github-playground)
* Updates to documentation or readme are greatly appreciated and make for a great first PR. They do not need to be discussed in advance and will be merged as soon as possible.

#### Project setup
* [Create an Anaconda virtual environment](https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/20/conda/).
* Clone the repository and work on the modules.
* Use [Pylint](https://www.pylint.org/) for code formatting.

#### Current Issues
Docker infrastructure for development ([#6](https://github.com/Data4Democracy/indivisible/issues/6)) is needed.

After that, the first priority is to handle data ingestion.

* [ ] Establish polling service for incoming emails. See [#10](https://github.com/Data4Democracy/indivisible/issues/10) and `ingest/listener.py`.
* [ ] Consume incoming emails for persistence and feature extraction.
See [#1](https://github.com/Data4Democracy/indivisible/issues/1), [#8](https://github.com/Data4Democracy/indivisible/issues/8), and `ingest/scraper.py`.
* [ ] Implement storage.
    - See [#3](https://github.com/Data4Democracy/indivisible/issues/3) and [#9](https://github.com/Data4Democracy/indivisible/issues/9) for discussion of schema.
    - See [#13](https://github.com/Data4Democracy/indivisible/issues/13) for related implementation details.
* [ ] Develop feature extraction pipeline to support classification of email contents. See [#2](https://github.com/Data4Democracy/indivisible/issues/2) for general discussion on this.
    - [#7](https://github.com/Data4Democracy/indivisible/issues/7) Discuss potential features of interest.
    - [#11](https://github.com/Data4Democracy/indivisible/issues/11) Actual implementation of feature extraction.
    - [#12](https://github.com/Data4Democracy/indivisible/issues/12) Classification strategies. Requires completion of [#7](https://github.com/Data4Democracy/indivisible/issues/7) and [#11](https://github.com/Data4Democracy/indivisible/issues/11).

### Updating wiki
See the [github wiki update guide](https://help.github.com/articles/adding-and-editing-wiki-pages-locally/).

#### Using issues
* When picking up an issue leave a comment/ mark as in progress and assign yourself. 
* Issue comments can be used for communication 
* The wiki should be used for different documentation purposes. That will include
    1. Meeting minutes
    2. Design choices
    3. Further reading/tutorials

### Skills
* Python : backend for ingesting data that is built in Python.
* JavaScript : the website is built with JavaScript.

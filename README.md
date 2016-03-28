# Build your KIT .public_html webpage

This is a minimalistic and lightweight workframe for adopting the official KIT website design with static HTML pages and jQuery.
All the configurations comes within one simple [config.yml](template/config.yml). Content of pages is separated in single [files](pages/start.html).
The resulting page is build from a jinja2 template with a simple python run.

## Requirements
 * python3 (python3-jinja2, python3-yaml),
 * a webserver with .htaccess support.

## Usecases
Many institutes at the KIT provide a ``.public_html`` directory in the homedir of their members. There you can put static htmls only. Mostly, this leads to a chaos of many html files... 
The intention of this project is, to have a minimalistic framework for building simple website structures without batteling with thousands of html files and just concentrating on the content.

## Quickstart
 * get a clone of this repository: ``git clone https://github.com/particleKIT/StaticKIT.git`` and join the directory.
 * create a new branch ``git checkout -b online`` that will contain your work.
 * Put your personal data/config in the [template/config.yml](template/config.yml),
 * for every page create a ``.html`` file at ``/pages/`` and fill it with your (html) content,
 * every page that has to be shown in the navigation needs an entry in the config.yml, the syntax is as follows: 
  
  ```yaml
   - file: filename (without html extension)
      title: filetitle (the name shown in the navigation)
      order: 1  (the position of the page in the navigation)
  ```
  
 * join the template dir and run the [publish.py](template/publish.py)
 * thats it! The complete page is navigated from the newly created ``index.html``.

## Infobox
You can add additional infoboxes on the right side of the page. Fill the ``infobox`` dict with appropriate informations, every new subdict (starting with a ``-``) marks a new infobox:
```yaml
infobox:
    - title: Info-Box
      text: "A simple list
          <ul>
          <li>item 1</li>
          <li>another item</li>
          <li>third item</li>
          </ul>
          "
    - title: Info-Box2
      text: "another infobox"
```
If you need more space and dont want to show the right column at all, simply set the ``showboxes: false`` variable the config.yml. 

## Linking your pages
Loading page content from specific files under ``/pages/*.html`` is triggered by appending a ``#filename`` (without .html extension) in the addressbar. Thus you can give others a link to one of your pages by copy&paste the resulting url from the navigation/browser address bar.


## Recycling variables
People using ansible (which mixes yaml and jinja2) may be confused, because standalone YAML does not come with a feature to concatenate variables.
However, we introduced a simple variable parser that replaces ``{{vars}}`` with their values. So far it is only possible to replace with simple vars, no list/dict items. E.g:
```yaml
mail: my@email.de
text: 'contact me at {{mail}}'
```
will lead to the desired result.

## Branches

We suggest to have at least one additional branch, like shown in the quickstart. This way you can pull and watch out changes from this repo without changing (or even breaking) your published website.

## Subpages
At the moment it is not possible to have foldable sub categories in the navigation. We`ll investigate in some, if there are enough requests.

# Build your KIT .public_html webpage

## Quickstart
 * Put your personal data/config in the [config.yml](template/config.yml),
 * for every page create a ``.html`` file at ``/pages/`` and fill it with your (html) content,
 * every page that has to be shown in the navigation needs an entry in the config.yml, the syntax is as follows: 
  
  ```yaml
   - file: filename (without html extension)
      title: filetitle (the name shown in the navigation)
      order: 1  (the position of the page in the navigation)
  ```
  
 * join the template dir and run the [publish.py](template/publish.py)
 * thats it!


## Infobox
You can add a additional infoboxe on the right side of the page. If you dont want this, simply remove the ``infobox``  variable from the config.yml. 
 

# OctoPrint PSU Control - Webhooks
Adds webhooks/API request support to OctoPrint-PSUControl as a sub-plugin.

## Setup
- Install the plugin using Plugin Manager from Settings
- Configure this plugin
- Select this plugin as a Switching and/or Sensing method in [PSU Control](https://github.com/kantlivelong/OctoPrint-PSUControl)

> **NOTE:** script Python can be written in order to manage the API response. You just
> need to setup `psu_state` with `on` or `off` (the response is stored in `response`).
>
> For example :
> ```python
> # the API responds with this JSON `{"psu_is_on?": true}`
> psu_state = 'on' if response.json()['psu_is_on?'] else 'off'
> ```

## Support
Help can be found at the [OctoPrint Community Forums](https://community.octoprint.org)

## Credits
This repository is mainly based on the [OctoPrint-PSUControl - TPLink](https://github.com/kantlivelong/OctoPrint-PSUControl-TPLink) plugin.
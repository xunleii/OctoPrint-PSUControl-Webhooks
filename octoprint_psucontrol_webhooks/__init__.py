# coding=utf-8
from __future__ import absolute_import

__author__ = "Alexandre Nicolaie <alexandre.nicolaie+octoprint@gmail.com>"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"
__copyright__ = "Copyright (C) 2021 Alexandre Nicolaie - Released under terms of the AGPLv3 License"

import json
import octoprint.plugin
import requests

class PSUControl_Webhooks(octoprint.plugin.StartupPlugin,
                          octoprint.plugin.RestartNeedingPlugin,
                          octoprint.plugin.TemplatePlugin,
                          octoprint.plugin.SettingsPlugin):

    def __init__(self):
        self.config = dict()

    # -------------------------------------------------------------------------
    # --- Plugin implementation

    # This handler contains an example of how we can use the Python handler
    DEFAULT_PYTHON_HANDLER="""# 'response' variable contains the response of the API request (Python request module)
# and the state must be set to 'psu_state' with 'on' or 'off'
psu_state = 'on' if response.status_code == 200 else 'off'"""

    def get_settings_defaults(self):
        return dict(
            address="",
            get_psu_state=dict(method="", path="", payload="", on_if_ok=False, python_handler=PSUControl_Webhooks.DEFAULT_PYTHON_HANDLER),
            turn_psu_on=dict(method="", path="", payload=""),
            turn_psu_off=dict(method="", path="", payload=""),
        )

    def get_template_configs(self):
        return [dict(type="settings", custom_bindings=False)]

    def get_settings_version(self):
        return 1

    def on_settings_initialized(self):
        self.reload_settings()

    def on_settings_migrate(self, target, current=None):
        pass

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.reload_settings()

    def on_startup(self, host, port):
        psucontrol_helpers = self._plugin_manager.get_helpers("psucontrol")
        if not psucontrol_helpers or 'register_plugin' not in psucontrol_helpers.keys():
            self._logger.warning("The version of PSUControl that is installed does not support plugin registration.")
            return

        self._logger.debug("Registering plugin with PSUControl")
        psucontrol_helpers['register_plugin'](self)

    # -------------------------------------------------------------------------
    # -- Configuration management

    def reload_settings(self):
        for k, v in self.get_settings_defaults().items():
            if type(v) == str or type(v) == dict:
                v = self._settings.get([k])
            elif type(v) == int:
                v = self._settings.get_int([k])
            elif type(v) == float:
                v = self._settings.get_float([k])
            elif type(v) == bool:
                v = self._settings.get_boolean([k])
            else:
                self._logger.warning("{}: {} ({})".format(k, v, type(v)))

            self.config[k] = v
            self._logger.debug("{}: {}".format(k, v))
        self._logger.debug("{}".format(self.config))

    # -------------------------------------------------------------------------
    # -- PSUControl sub-plugin implementation

    def turn_psu_on(self):
        self._logger.debug("Switching PSU on")
        response = self.execute_request(self.config.get('turn_psu_on'))
        self._logger.debug(response)

    def turn_psu_off(self):
        self._logger.debug("Switching PSU off")
        response = self.execute_request(self.config.get('turn_psu_off'))
        self._logger.debug(response)

    def get_psu_state(self) -> bool:
        self._logger.debug("Fetching PSU state")
        response = self.execute_request(self.config.get('get_psu_state'))
        self._logger.debug(response)

        if self.config.get('get_psu_state').get('on_if_ok'):
            return response.ok

        self._logger.debug("Use custom Python handler to detect the PSU state")
        python_handler = self.config.get('get_psu_state').get('python_handler')
        if python_handler is None:
            python_handler = PSUControl_Webhooks.DEFAULT_PYTHON_HANDLER
        if not type(python_handler) == str:
            self._logger.error("Python handler must be a string")
            return False

        try:
            locals = {
                'response': response,
                'psu_state': 'off'
            }
            exec(python_handler, globals(), locals)
            return locals['psu_state'] == 'on'
        except Exception as err:
            self._logger.error("Failed to run Python handler: {}".format(err))
            return False

    def execute_request(self, cmd) -> requests.Response:
        method = cmd['method']
        url = self.config['address'] + ("" if cmd.get('path') is None else cmd['path'])

        if method in ['POST', 'PUT'] and cmd.get('payload'):
            payload = cmd.get('payload')
            try:
                payload = json.loads(payload)
                return requests.request(method, url, json=payload)
            except:
                return requests.request(method, url, data=payload)
        else:
            return requests.request(method, url)

    # -------------------------------------------------------------------------
    # -- Update information

    def get_update_information(self):
        return dict(
            psucontrol_tplink=dict(
                displayName="PSU Control - Webhooks",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="xunleii",
                repo="OctoPrint-PSUControl-Webhooks",
                current=self._plugin_version,

                # update method: pip w/ dependency links
                pip="https://github.com/xunleii/OctoPrint-PSUControl-Webhooks/archive/{target_version}.zip"
            )
        )


__plugin_name__ = "PSU Control - Webhooks"
__plugin_pythoncompat__ = ">=2.7,<4"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = PSUControl_Webhooks()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }

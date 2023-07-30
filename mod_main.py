from datetime import datetime
import os
from tool import ToolUtil
from flask import Response
from .setup import *

try:
    if os.path.exists(os.path.join(os.path.dirname(__file__), "source_reystream_handler.py")):
        from .source_reystream_handler import REYSTREAM_Handler

    else:
        from support import SupportSC

        REYSTREAM_Handler = SupportSC.load_module_f(__file__, "source_reystream_handler").REYSTREAM_Handler
except:
    pass


class ModuleMain(PluginModuleBase):
    def __init__(self, P):
        super(ModuleMain, self).__init__(P, name="main", first_menu="setting", scheduler_desc="REYSTREAM")
        self.db_default = {
            f"{self.name}_db_version": "1",
            f"{self.name}_auto_start": "False",
            f"{self.name}_interval": "5",
            f"{self.name}_yaml_path": "",
            f"{self.name}_plex_server_url": "http://localhost:32400",
            f"{self.name}_plex_token": "",
            f"{self.name}_plex_meta_item": "",
        }

    def process_menu(self, sub, req):
        arg = P.ModelSetting.to_dict()
        arg["api_m3u"] = ToolUtil.make_apikey_url(f"/{P.package_name}/api/m3u")
        arg["api_yaml"] = ToolUtil.make_apikey_url(f"/{P.package_name}/api/yaml")
        if sub == "setting":
            arg["is_include"] = F.scheduler.is_include(self.get_scheduler_name())
            arg["is_running"] = F.scheduler.is_running(self.get_scheduler_name())
        return render_template(f"{P.package_name}_{self.name}_{sub}.html", arg=arg)

    def process_command(self, command, arg1, arg2, arg3, req):
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if command == "broad_list":
            return jsonify({"list": REYSTREAM_Handler.ch_list(), "updated_at": updated_at})
        elif command == "play_url":
            url = arg3 if arg3 else ToolUtil.make_apikey_url(f"/{P.package_name}/api/url.m3u8?ch_id={arg1}")
            ret = {"ret": "success", "data": url, "title": arg2}
        return jsonify(ret)

    def process_api(self, sub, req):
        try:
            if sub == "m3u":
                return REYSTREAM_Handler.make_m3u()
            elif sub == "yaml":
                return REYSTREAM_Handler.make_yaml()
            elif sub == "url.m3u8":
                return REYSTREAM_Handler.url_m3u8(req)
            elif sub == "segment":
                return REYSTREAM_Handler.segment(req)

        except Exception as e:
            P.logger.error(f"Exception:{str(e)}")
            P.logger.error(traceback.format_exc())

    def scheduler_function(self):
        try:
            REYSTREAM_Handler.sync_yaml_data()
        except Exception as e:
            P.logger.error(f"Exception:{str(e)}")
            P.logger.error(traceback.format_exc())

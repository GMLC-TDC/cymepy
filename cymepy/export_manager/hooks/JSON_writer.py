from cymepy.export_manager.base_definations import ExportManager
from cymepy.common import EXPORT_FILENAME
import json
import os

class Writer(ExportManager):
    def __init__(self, sim_instance, solver, options, logger, **kwargs):
        super(Writer, self).__init__(sim_instance, solver, options, logger, **kwargs)
        self.results = []
        if not self.settings["project"]['append_to_exported_files']:
            self.path = os.path.join(
                self.settings["project"]['project_path'],
                'exports',
                f"{EXPORT_FILENAME}.json"
            )
        else:
            self.path = os.path.join(
                self.settings["project"]['project_path'],
                'exports',
                f"{self.settings['project']['append_to_exported_files']}_{EXPORT_FILENAME}.json"
            )
        pass

    def update(self):
        results = super().update()
        self.results.append(results)
        return

    def export(self):
        with open(self.path, "w") as write_file:
            json.dump(self.results, write_file, indent=4, sort_keys=True)

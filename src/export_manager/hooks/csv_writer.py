from src.export_manager.base_definations import ExportManager
import os

class Writer(ExportManager):
    def __init__(self, sim_instance, solver, options, logger, **kwargs):
        super(Writer, self).__init__(sim_instance, solver, options, logger, **kwargs)
        self.results = ["Timestamp,Class,Element,Property,Value\n"]

        self.path = os.path.join(
            self.settings["project"]['project_path'],
            'exports',
        )
        self.results = []
        self.step=0
        return

    def update(self):
        results = super().update()
        self.results.append(results)
        return

    def export(self):
        FileHandles = {}
        for results in self.results:
            for timestamp, cInfo in results.items():
                for cName, eInfo in cInfo.items():
                    if cName not in FileHandles:
                        FileHandles[cName] = open(
                            os.path.join(
                                self.path, f"{cName}.csv"
                            ),
                            "w"
                        )
                        self.writeHeader = True
                    else:
                        self.writeHeader = False
                    headers = ["Timestamp"]
                    values = [timestamp]
                    for eName, pptyInfo in eInfo.items():
                        for ppty, value in pptyInfo.items():
                            headers.append(f"{eName}.{ppty}")
                            values.append(value)
                    if self.writeHeader:
                        headers = ",".join(headers)
                        FileHandles[cName].write(headers + "\n")
                    values = ",".join(values)
                    FileHandles[cName].write(values + "\n")

        for cNama, handler in FileHandles.items():
            handler.flush()
            handler.close()


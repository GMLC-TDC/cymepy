from cymepy.export_manager.base_definations import ExportManager
from cymepy.common import EXPORT_FILENAME
import numpy as np
import h5py
import os


class Writer(ExportManager):
    def __init__(self, sim_instance, solver, options, logger, **kwargs):
        super(Writer, self).__init__(sim_instance, solver, options, logger, **kwargs)
        self.i = 0
        self.columnLength,_ , _ = solver.SimulationSteps()
        self.logger = logger
        self.basepath = os.path.join(
            self.settings["project"]['project_path'],
            'exports',
            f"{EXPORT_FILENAME}.h5"
        )

        self.logger.info("Creating new h5 store")
        self.store = h5py.File(self.basepath, "w")
        self.Timestamp = self.store.create_dataset(
            "Timestamp",
            shape=(self.columnLength,),
            maxshape=(None,),
            chunks=True,
            compression="gzip",
            compression_opts=4,
            shuffle=True,
            dtype="S30",
        )
        self.store_groups = {}
        for cName, eInfo in self.Exports.items():
            cGroup = self.store.create_group(cName)
            if cName not in self.store_groups:
                self.store_groups[cName] = {}
            for eName, pInfo in eInfo.items():
                eGroup = cGroup.create_group(eName)
                if eName not in self.store_groups[cName]:
                    self.store_groups[cName][eName] = {}
                for ppty in pInfo["properties"]:
                    self.store_groups[cName][eName][ppty] = eGroup.create_dataset(
                        str(ppty),
                        shape=(self.columnLength, ),
                        maxshape=(None, ),
                        chunks=True,
                        compression="gzip",
                        compression_opts=4,
                        shuffle=True
                )
        return

    def update(self):
        results = super().update()
        for timestamp, cInfo in results.items():
            self.Timestamp[self.i] = np.string_(timestamp)
            for cName, eInfo in cInfo.items():
                for eName, pptyInfo in eInfo.items():
                    for ppty, value in pptyInfo.items():
                        try:
                            self.store_groups[cName][eName][ppty][self.i] = float(value)
                        except:
                            self.store_groups[cName][eName][ppty][self.i] = np.NaN
        self.i += 1
        return

    def export(self):
        self.store.flush()
        self.store.close()
        return

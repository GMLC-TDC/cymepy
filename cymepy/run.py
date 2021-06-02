from TPtoolbox.CymeInstance.HelperFuncs import FitUnimodalDist
from TPtoolbox.CymeInstance.HelperFuncs import GetReleventData
from TPtoolbox.CymeInstance.HelperFuncs import SliceTimeRange
import TPtoolbox.CymeInstance.ProfileDatabase as ProDB
import TPtoolbox.CymeInstance.Instance as Instance
from multiprocessing import Pool
import pandas as pd
import logging
import time
import os

InstanceSettings = {
    'CymeInstallationDir' : r'C:\Program Files (x86)\CYME\CYMEv8.0Rev08',
    'CymeProjectPath'     : r'C:\Users\alatif\Desktop\IEEE_13.sxst',
}

LoggerOptions =  {
        'Logging Level'          : logging.DEBUG,
        'Log to external file'   : True,
        'Display on screen'      : True,
        'Clear old log files'    : True,
}

SampleWindowSize = 5
NumMCsamples = 8760
DataSlices = 2
HourShift = 2

def runParallel(WorkerData):
    # This code is run for each parallel run (CYME instance should be created here)
    time.sleep(WorkerData)
    cymeInstance = Instance.Create(InstanceSettings, LoggerOptions, WorkerData)
    #cymeInstance.runMCsimulations(1000)

if __name__ == "__main__":
    startTime = time.time()
    # Delete old MS-Access file if it exists
    filename = os.path.join(r'C:\Users\alatif\Desktop\NetworkIterator', 'test.mdb')
    if os.path.exists(filename): os.remove(filename)
    # Create empty MSaccess database at the given location
    ProfilesDatabase = ProDB.Create(r'C:\Users\alatif\Desktop\NetworkIterator', 'test.mdb')
    # Load_data = pd.read_excel(r'C:\Users\alatif\Desktop\Load_profiles.xlsx', 0)
    # ProfilesDatabase.CreateProfiles(profilesDF=Load_data,loadPF=95,ProfileType='LOAD',ProfileResolution='Hourly')

    # Create load profile in the access database
    Load_data = pd.read_csv(r'C:\Users\alatif\Desktop\C591loadmult_Jan01toDec31.csv')
    Load_data.columns = ['c591_load']
    LDprofile = ProfilesDatabase.CreateProfiles(profilesDF=Load_data, loadPF=95, ProfileType='LOAD',
                                                ProfileResolution='1 min')
    # Create PV profile in the access database
    PV_data = pd.read_csv(r'C:\Users\alatif\Desktop\C591PVgenmult_Jan01toDec31.csv')
    PV_data.columns = ['c591_pv']
    PVprofile = ProfilesDatabase.CreateProfiles(profilesDF=PV_data, loadPF=95, ProfileType='GENERATOR',
                                                ProfileResolution='1 min')
    # Close database
    #del ProfilesDatabase

    # Get times where profiles need to be split
    SliceTimes, ProfileLens = SliceTimeRange(LDprofile, DataSlices, SampleWindowSize, HourShift)
    # Create work data for each parallel run
    MCsettings = list(zip(SliceTimes, ProfileLens, range(DataSlices),[LDprofile] * len(SliceTimes)))

    for splitTime, nDays, InstanceNumber, LDprofile in MCsettings:
        trainDF, testDF = GetReleventData(LDprofile, SplitDateTime=splitTime,
                                          MinSampleWindow=30, DaySampleWindow=SampleWindowSize)
        MCsamples = FitUnimodalDist(trainDF, testDF, MCsamples=NumMCsamples, nBins=50, split_time=splitTime, plot=True,
                            index=InstanceNumber, path=r'C:\Users\alatif\Desktop\Cyme results\Distribution fitting')
        Loads = ['Load611', 'Load634', 'Load645', 'Load646', 'Load652', 'Load671', 'Load675', 'Load692', 'L632-671-1']
        for load in Loads:
            MCsamples.columns = [load]
            LDprofile = ProfilesDatabase.CreateProfiles(profilesDF=MCsamples, loadPF=95, ProfileType='LOAD',
                                                        ProfileResolution='Hourly')
        quit()
    del ProfilesDatabase
    WorkerData = range(DataSlices)
    print('Profile sliced at : ',  str(SliceTimes))
    # Run parallel simulations
    pool = Pool(processes=DataSlices)
    pool.map(runParallel, WorkerData)
    pool.close()
    print('Total time is - ' + str(time.time() - startTime) + ' seconds.')

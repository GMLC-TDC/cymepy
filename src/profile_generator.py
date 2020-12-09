from win32com.client import Dispatch
import pandas as pd
import random
import os

ODBC_ADD_DSN = 1        # Add data source
ODBC_CONFIG_DSN = 2     # Configure (edit) data source
ODBC_REMOVE_DSN = 3     # Remove data source
ODBC_ADD_SYS_DSN = 4    # add a system DSN
ODBC_CONFIG_SYS_DSN = 5 # Configure a system DSN
ODBC_REMOVE_SYS_DSN = 6 # remove a system DSN

class Create:
    ProfilesTypes = {
        0  : 'LOAD_E_1HOUR',
        1  : 'GENERATOR_E_1HOUR',
        2  : 'NETWORK_E_1HOUR',
        3  : 'LOAD_E_15MINUTES',
        4  : 'GENERATOR_E_15MINUTES',
        5  : 'NETWORK_E_15MINUTES',
        6  : 'LOAD_E_5MINUTES',
        7  : 'GENERATOR_E_5MINUTES',
        8  : 'NETWORK_E_5MINUTES',
        9  : 'LOAD_E_1MINUTE',
        10 : 'GENERATOR_E_1MINUTE',
        11 : 'NETWORK_E_1MINUTE',
    }

    ProfileTypes = ['LOAD', 'GENERATOR', 'NETWORK']
    ProfileResolution = {
        'Hourly' : '_E_1HOUR',
        '15 min' : '_E_15MINUTES',
        '5 min'  : '_E_5MINUTES',
        '1 min'  : '_E_1MINUTE',
    }

    Catagory = {
        'LOAD'      : 4,
        'GENERATOR' : 2,
    }

    def __init__(self, FilePath, FileName):
        #Profiles = self.CreateProfileDict(FilePath)
        self.__CreateEmptyDatabase(FilePath, FileName)

        #self.WriteToDatabase(FilePath, FileName, Profiles)

    def CreateProfileDict(self, FilePath):
        FileList = [x.lower() for x in os.listdir(FilePath)]
        csvFiles = []
        for file in FileList:
            if '.csv' not in file:
                print('Deleting file: ', file)
                os.remove(file)
        return

    def __split_profile(self, l, n):
        # For item i in a range that is a length of l,
        for i in range(0, len(l), n):
            # Create an index range for l of n items:
            yield l[i:i + n]

    def __writeProfileToDB(self, ProfileName, TableName, PF, DailyProfiles, ProfileType):
        ColumnNames = 'ID,ProfileYear,YearIntervalNumber,Daytype,Unit,Phase,ValuesX'
        for i, DailyProfile in enumerate(DailyProfiles):
            ProfileLength = len(DailyProfile)
            for j in [4, 11]:
                if j == 4:
                    Values = str([PF] * ProfileLength).strip('[').strip(']').replace(', ', ';')
                else:
                    Values = str(DailyProfile).strip('[').strip(']').replace(', ', ';')

                Values = "'{}',{},{},'{}',{},{},'{}'".format(ProfileName, 2018, i, 'null', j, 3, Values)

                self.newdb.Execute('''INSERT INTO {} ({}) VALUES ({})'''.format(
                    TableName, ColumnNames, Values))
        return

    def __updateNetworkTable(self, profileID, Category, NetworkID, TableName, NumberOfValue, DayInterVal):
        ColumnNames = 'ID,Category,NetworkID,TableName,YearInterval,' \
                      'WeekInterval,DayInterVal,NumberOfValue,Unit,IsTotal,Version'
        Values = "'{}',{},'{}','{}',{},{},{},{},{},{},{}".format(
            profileID, Category, NetworkID, TableName, 0, 3, DayInterVal, NumberOfValue, 3, 1, 1)

        self.newdb.Execute('''INSERT INTO CYMLPNETWORK ({}) VALUES ({})'''.format(ColumnNames, Values))
        return

    def CreateProfiles(self, profilesDF, loadPF, ProfileType, ProfileResolution):

        if ProfileType in self.ProfileTypes and ProfileResolution in self.ProfileResolution:
            TableName = ProfileType + self.ProfileResolution[ProfileResolution]
            print('Writing to table: ', TableName)
        else:
            quit()

        ProfileNames =  profilesDF.columns
        for ProfileName in ProfileNames:
            Profile = profilesDF[ProfileName].tolist()
            if ProfileResolution == 'Hourly':
                DailyProfiles = list(self.__split_profile(Profile, 24))
                self.__writeProfileToDB(ProfileName, TableName, loadPF, DailyProfiles, ProfileType)
                self.__updateNetworkTable(ProfileName, self.Catagory[ProfileType], 'IEEE13', TableName, 24, 3)
                self.ProfileTS = pd.DataFrame(profilesDF.values, columns=['Data'],
                                         index=pd.period_range('2017-01-01', freq='1h', periods=len(profilesDF)))

            elif ProfileResolution == '15 min':
                DailyProfiles = list(self.__split_profile(Profile, 96))
                self.__writeProfileToDB(ProfileName, TableName, loadPF, DailyProfiles, ProfileType)
                self.__updateNetworkTable(ProfileName, self.Catagory[ProfileType], 'IEEE13', TableName, 96, 1)
                self.ProfileTS = pd.DataFrame(profilesDF.values, columns=['Data'],
                                         index=pd.period_range('2017-01-01', freq='15min', periods=len(profilesDF)))
            elif ProfileResolution == '5 min':
                DailyProfiles = list(self.__split_profile(Profile, 288))
                self.__writeProfileToDB(ProfileName, TableName, loadPF, DailyProfiles, ProfileType)
                self.__updateNetworkTable(ProfileName, self.Catagory[ProfileType], 'IEEE13', TableName, 288, 0)
                self.ProfileTS = pd.DataFrame(profilesDF.values, columns=['Data'],
                                        index=pd.period_range('2017-01-01', freq='5min', periods=len(profilesDF)))
            elif ProfileResolution == '1 min':
                DailyProfiles = list(self.__split_profile(Profile, 1440))
                self.__writeProfileToDB(ProfileName, TableName, loadPF, DailyProfiles, ProfileType)
                self.__updateNetworkTable(ProfileName, self.Catagory[ProfileType], 'IEEE13', TableName, 1440, 5)
                self.ProfileTS = pd.DataFrame(profilesDF.values, columns=['Data'],
                                         index=pd.period_range('2017-01-01', freq='1min', periods=len(profilesDF)))
        return self.ProfileTS

    def __CreateEmptyDatabase(self, FilePath, FileName):
        try:
            dbname = os.path.join(FilePath, FileName)
            self.accApp = Dispatch("Access.Application")
            self.dbEngine = self.accApp.DBEngine
            self.workspace = self.dbEngine.Workspaces(0)
            dbLangGeneral = ';LANGID=0x0409;CP=1252;COUNTRY=0'
            self.newdb = self.workspace.CreateDatabase(dbname, dbLangGeneral, 64)

            self.newdb.Execute("""CREATE TABLE CYMLPNETWORK (
                              ID varchar(128),
                              Category byte,
                              NetworkID varchar(128),
                              TableName varchar(128),
                              YearInterval byte,
                              WeekInterval byte,
                              DayInterVal byte,
                              NumberOfValue int,
                              Unit byte,
                              IsTotal byte,
                              Version double);""")

            for key, TableName in self.ProfilesTypes.items():
                self.newdb.Execute("""CREATE TABLE {} (
                      ID varchar(128),
                      ProfileYear int,
                      YearIntervalNumber int,
                      Daytype  varchar(32),
                      Unit byte,
                      Phase byte,
                      ValuesX memo);""".format(TableName))
        except Exception as e:
            print(e)

    def __del__(self):
        self.accApp.DoCmd.CloseDatabase
        self.accApp.Quit
        self.newdb = None
        self.workspace = None
        self.dbEngine = None
        self.accApp = None





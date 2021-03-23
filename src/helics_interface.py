#import asd as asdasdas
from src.common import CORE_CYMEPY_PROJECT_FILES
import helics as h
import toml
import os
import re

class HELICS:

    n_states = 5
    init_state = 1

    type_info = {
        'complex': 'complex ',
        'text': 'string',
        'number': 'int64',
        'real': 'double',
        '': 'double',
    }

    def __init__(self, settings, cymepy, Solver, logger):
        self.__Logger = logger
        self.cympy = cymepy
        self.settings = settings
        self.Solver = Solver
        lf = cymepy.sim.LoadFlow()
        lf.Run()

        self.itr = 0
        self.c_seconds = 0
        self.c_seconds_old = -1

        self.validTypes = []
        for k, v in self.cympy.enums.DeviceType.__dict__.items():
            if isinstance(v, int):
                self.validTypes.append(k)

        self.create_helics_federate()
        self.registerPublications()
        self.registerSubscriptions()

        h.helicsFederateEnterExecutingModeIterative(
            self.cymeFederate,
            h.helics_iteration_request_iterate_if_needed
        )
        logger.info('Entered HELICS execution mode')

    def registerSubscriptions(self):
        subpath = os.path.join(
            self.settings["project"]['project_path'],
            CORE_CYMEPY_PROJECT_FILES.SUBSCRIPTION_FILE.value
        )
        subscriptionDict = toml.load(open(subpath, "r"))
        self.Subscriptions = {}
        for elmCN, subInfo in subscriptionDict.items():
            cName, eName = elmCN.split(".")
            if cName not in self.validTypes:
                raise Exception(f"{cName} is not a valid CYME device type. "
                                f"For valid device type, see cympy.enums.DeviceType")
            else:
                devType = getattr(self.cympy.enums.DeviceType, cName)
                devices = self.cympy.study.ListDevices(devType)
                found = False
                fDevice = None
                for device in devices:
                    if eName == device.DeviceNumber:
                        found = True
                        fDevice = device
                        break
                if not found:
                    raise Exception(f"Element {eName} for class {cName} not found. See subscriptions")
                else:
                    found, pUnits, pDefaultValue, pType = self.isProperty(fDevice, subInfo["Property"])

                    if not found:
                        raise Exception("{} is not a valid property for {}.\nValid options are:\n{}".format(
                            subInfo['Property'],
                            cName,
                            self.listProperties(cName)
                        ))

                    subname = subInfo["Subscription ID"]
                    self.Subscriptions[subname] = {
                        "elementObj": fDevice,
                        "subscriptionObj": h.helicsFederateRegisterSubscription(
                            self.cymeFederate,
                            subInfo["Subscription ID"],
                            pUnits
                        ),
                        "class": cName,
                        "name": eName,
                        "property": subInfo["Property"],
                        "unit": pUnits,
                        "dType": pType,
                        "dStates": [self.init_state] * self.n_states,
                        "mult" : subInfo["Multiplier"]
                    }
                    self.__Logger.debug(
                        f"Object {cName}.{eName}'s {subInfo['Property']} property has subscribed to {subInfo['Subscription ID']}.")

        return

    def listProperties(self, cName):
        properties = self.cympy.dm.Describe(cName)
        string = ""
        for i, p in enumerate(properties):
            string += f"{i}. {p.Name}\n"
        return string

    def create_helics_federate(self):
        self.fedName = self.settings['helics']['federate_name']
        self.fedinfo = h.helicsCreateFederateInfo()
        h.helicsFederateInfoSetCoreName(self.fedinfo, self.settings['helics']['federate_name'])
        h.helicsFederateInfoSetCoreTypeFromString(self.fedinfo, self.settings['helics']['core_type'])
        h.helicsFederateInfoSetCoreInitString(self.fedinfo, f"--federates=1")
        h.helicsFederateInfoSetBroker(self.fedinfo, self.settings['helics']['broker'])
        h.helicsFederateInfoSetBrokerPort(self.fedinfo ,self.settings['helics']['broker_port'])
        h.helicsFederateInfoSetTimeProperty(self.fedinfo, h.helics_property_time_delta,
                                                 self.settings['helics']['time_delta'])
        h.helicsFederateInfoSetIntegerProperty(self.fedinfo, h.helics_property_int_log_level,
                                                    self.settings['helics']['helics_logging_level'])

        h.helicsFederateInfoSetFlagOption(self.fedinfo, h.helics_flag_uninterruptible, True)
        h.helicsFederateInfoSetIntegerProperty(self.fedinfo, h.helics_property_int_max_iterations,
                                                    self.settings["helics"]["max_coiter"])
        self.cymeFederate = h.helicsCreateValueFederate(self.settings['helics']['federate_name'], self.fedinfo)

        return

    def registerPublications(self):
        pubpath = os.path.join(
            self.settings["project"]['project_path'],
            CORE_CYMEPY_PROJECT_FILES.PUBLICATION_FILE.value
        )

        publicationDict = toml.load(open(pubpath, "r"))
        self.Publications = {}

        for cName, pubInfo in publicationDict.items():
            if cName not in self.validTypes:
                raise Exception(f"{cName} is not a valid CYME device type. "
                                f"For valid device type, see cympy.enums.DeviceType")
            else:
                devType = getattr(self.cympy.enums.DeviceType, cName)
                devices = self.cympy.study.ListDevices(devType)
                if devices:
                    for device in devices:
                        eName = device.DeviceNumber
                        if pubInfo["regex filter"]:
                            pattern = re.compile(pubInfo["regex filter"])
                            matches = pattern.search(eName)
                            if matches:
                                self.create_publication(pubInfo, device, cName, eName)
                        else:
                            self.create_publication(pubInfo, device, cName, eName)
                else:
                    self.__Logger.warn(f"Model of type {cName} not found in the distribution model")
        return

    def isProperty(self,device, property):
        properties = self.cympy.dm.Describe(device.GetObjType())
        found = False
        for p in properties:
            if p.Name == property:
                found = True
                return found, p.Units, p.DefaultValue, p.Type

        return found, None, None, None


    def create_publication(self, pubInfo, device, cName, eName):
        for propertyX in pubInfo["properties"]:
            keyword = self.cympy.app.GetKeyword(propertyX)
            if keyword is None:
                found, units, defaultValue, cType = self.isProperty(device, propertyX)
                if not found:
                    raise Exception(f"{propertyX} is neither a valid keyword not a valid property of object type {cName}")
                res = device.GetValue(propertyX)
            else:
                res = self.cympy.study.QueryInfoDevice(propertyX, device.DeviceNumber, device.DeviceType)
            pubname = f"{self.fedName}.{cName}.{eName}.{propertyX}"
            T = self.type_info[keyword.Type.lower()] if keyword is not None else self.type_info[cType]
            if res:
                self.Publications[pubname] = {
                    "elementObj": device,
                    "publicationObj": h.helicsFederateRegisterGlobalTypePublication(
                        self.cymeFederate,
                        pubname,
                        T,
                        keyword.Unit if keyword is not None else units
                    ),
                    "class": cName,
                    "name": eName,
                    "property": propertyX,
                    "unit": keyword.Unit if keyword is not None else units,
                    "dType": keyword.Type if keyword is not None else cType,
                    "isKeyword": True if keyword is not None else False
                }
                self.__Logger.debug(
                    f"Publication {pubname} of type {T} registered successfully.")
            else:
                self.__Logger.warning(f"Property {propertyX} for publication {pubname} not valid")
        return

    def update_publications(self):
        for pubName, pubInfo in self.Publications.items():
            device = pubInfo["elementObj"]
            pub = pubInfo["publicationObj"]
            if pubInfo["isKeyword"]:
                res = self.cympy.study.QueryInfoDevice(pubInfo["property"], device.DeviceNumber, device.DeviceType)
            else:
                res = pubInfo["elementObj"].GetValue(pubInfo["property"])
            #print(pubInfo["property"], res, type(res), pubInfo["dType"], pubInfo["unit"])
            if pubInfo["dType"].lower() == "complex":
                h.helicsPublicationPublishComplex(pub, complex(res).real, complex(res).imag)
            elif pubInfo["dType"].lower() == 'real':
                h.helicsPublicationPublishDouble(pub, float(res))
            elif pubInfo["dType"].lower() == 'text':
                h.helicsPublicationPublishString(pub, str(res))
            elif pubInfo["dType"].lower() == "number":
                h.helicsPublicationPublishInteger(pub, int(res))
        return

    def update_subscriptions(self):
        for subName, subInfo in self.Subscriptions.items():
            device = subInfo["elementObj"]
            sub = subInfo["subscriptionObj"]

            value = None

            if subInfo["dType"].lower() == "complex":
                value = h.helicsInputGetComplex(sub)
            elif subInfo["dType"].lower() == 'real':
                value = h.helicsInputGetDouble(sub)
            elif subInfo["dType"].lower() == 'text':
                value = h.helicsInputGetString(sub)
            elif subInfo["dType"].lower() == "number":
                value = h.helicsInputGetInteger(sub)

            if value:
                value = value * subInfo["mult"]
                subInfo["elementObj"].SetValue(value, subInfo["property"])
                self.__Logger.debug(f"{subInfo['class']}.{subInfo['name']}.{subInfo['property']} updated to {value}")
                if self.settings['helics']['coiter_mode']:
                    if self.c_seconds != self.c_seconds_old:
                        subInfo["dStates"] = [self.init_state] * self.n_states
                    else:
                        subInfo["dStates"].insert(0, subInfo["dStates"].pop())
                    subInfo["dStates"][0] = value
        return

    def request_time_increment(self):
        error = sum([abs(x["dStates"][0] - x["dStates"][1]) for k, x in self.Subscriptions.items()])
        r_seconds = self.Solver.GetTotalSeconds()
        if not self.settings['helics']['coiter_mode']:
            while self.c_seconds < r_seconds:
                self.c_seconds = h.helicsFederateRequestTime(self.cymeFederate, r_seconds)
            self.__Logger.info('Time requested: {} - time granted: {} '.format(r_seconds, self.c_seconds))
            return True, self.c_seconds
        else:
            self.c_seconds, iteration_state = h.helicsFederateRequestTimeIterative(
                self.cymeFederate,
                r_seconds,
                h.helics_iteration_request_iterate_if_needed
            )
            self.__Logger.info('Time requested: {} - time granted: {} error: {} it: {}'.format(
                r_seconds, self.c_seconds, error, self.itr))
            if error > -1 and self.itr < self.settings['helics']["max_coiter"]:
                self.itr += 1
                return False, self.c_seconds
            else:
                self.itr = 0
                return True, self.c_seconds

    # def __del__(self):
    #     h.helicsFederateFinalize(self.cymeFederate)
    #     #state = h.helicsFederateGetState(self.cymeFederate)
    #     h.helicsFederateInfoFree(self.fedinfo)
    #     h.helicsFederateFree(self.cymeFederate)
    #     self.__Logger.info('HELICS federate for PyDSS destroyed.')
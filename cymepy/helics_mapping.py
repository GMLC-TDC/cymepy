import helics
import enum

PPTY_NAME_MAP = {
    "ProtStateA" : "ProtStateA",
    "ProtStateB" : "ProtStateA",
    "ProtStateC" : "ProtStateA",
    "RegTapA" : "RegTapA",
    "RegTapB" : "RegTapA",
    "RegTapC" : "RegTapA",
    "VLNA" : "VLNA",
    "VLNB" : "VLNA",
    "VLNC" : "VLNA",
    "KVAA" : "KVAA",
    "KVAB" : "KVAA",
    "KVAC" : "KVAA",
    "IA" : "IA",
    "IB" : "IA",
    "IC" : "IA",
}

class PROPERTY(enum.Enum):
    ProtStateA = {
        "type": "bool",
        "vector": True,
        "vector_list": ["ProtStateA", "ProtStateB", "ProtStateC"],
        "prefix": "switch",
        "suffix": "status",
        "unit": "",
        "tags" : [
            "phases",
            "federate"
            ],
    }
    KWTOT =  {
        "type": "complex",
        "vector": False,
        "isreal" : True,
        "pair" : "KVARTOT",
        "prefix": "pcc",
        "suffix": "pq",
        "unit": "kVA",
        "tags" : [
            "phases",
            "federate"
            ],
        }
    VLNA = {
        "type": "complex",
        "vector": True,
        "vector_list": ["VLNA", "VLNB", "VLNC"],
        "prefix": "ConnectivityNode",
        "suffix": "PNV",
        "unit": "V",
        "tags" : [
            "phases",
            "federate"
            ],
        }
    IA =  {
        "type": "complex",
        "vector": True,
        "vector_list": ["IA", "IB", "IC"],
        "prefix": "ACLineSegment",
        "suffix": "I",
        "unit": "A",
        "tags" : [
            "phases",
            "federate"
            ],
        } 
    RegTapA = {
        "mapped_object": "Regulator",
        "type": "integer",
        "vector": True,
        "vector_list": ["RegTapA", "RegTapB", "RegTapC"],
        "prefix": "RegulatingControl",
        "suffix": "pos",
        "unit": "pu",
        "tags" : [
            "phases",
            "federate"
        ],
    }
    CapStatus = {
        "mapped_object": "Capacitor",
        "type": "integer",
        "vector": False,
        "prefix": "ShuntCompensator",
        "suffix": "status",
        "unit": "",
        "tags" : [
            "phases",
            "federate"
        ],   
    }
    KVAA = {
        "type": "complex",
        "vector": True,
        "vector_list": ["KVAA", "KVAB", "KVAC"],
        "prefix": "EnergyConsumer",
        "suffix": "pq",
        "unit": "kVA",
        "tags" : [
            "phases",
            "federate"
        ],
    }

PUBLICATION_MAP = {
    "Source" : {
        PROPERTY.KWTOT.name : PROPERTY.KWTOT.value
    },
    "SpotLoad" : {
        PROPERTY.KVAA.name : PROPERTY.KVAA.value,
        PROPERTY.IA.name : PROPERTY.IA.value,
    },
    "DistributedLoad" : {
        PROPERTY.KVAA.name : PROPERTY.KVAA.value,
        PROPERTY.IA.name : PROPERTY.IA.value,
    },
    "Regulator" : {
        PROPERTY.RegTapA.name : PROPERTY.RegTapA.value,
    },
    "ShuntCapacitor" : {
        PROPERTY.CapStatus.name : PROPERTY.CapStatus.value,
    },
    "OverheadLineUnbalanced" : {
        PROPERTY.IA.name : PROPERTY.IA.value,
    },
    "OverheadByPhase": {
        PROPERTY.IA.name : PROPERTY.IA.value,
    },
    "OverheadLine": {
        PROPERTY.IA.name : PROPERTY.IA.value,
    },
    "Switch" : {
        PROPERTY.ProtStateA.name : PROPERTY.ProtStateA.value,
    }, 
    "Node" : {
        PROPERTY.VLNA.name : PROPERTY.VLNA.value
    },
}
CAPACITOR_STATES = {
    "Tripped" : 0,
    "Closed" : 1,
    "Connected" : 1,
}

SWITCH_STATES = {
    "Open" : 0,
    "Close" : 1,
}

class HELICS_MAPPING:

    def __init__(self, cympy, device, device_type, ppty, value, federate, pubInfo, node=None):
        self.cympy = cympy
        self.node = node
        self.cname = device_type
        self.ename = device.DeviceNumber

        self.pub = None
        self.obj = device
        self.ppty = ppty
        self.valuex = value
        self.pubInfo = pubInfo
        self.federate = federate

        found = False
        for PUBLICATION, PUBLICATION_PROPERTIES in PUBLICATION_MAP.items():
            #print(self.cname, PUBLICATION.name)
            if PUBLICATION == self.cname:
                for PPTY in PROPERTY:
                    if self.ppty in PUBLICATION_PROPERTIES:
                        if PPTY.name == self.ppty:
                            self.ppty_data = PPTY.value
                            found = True
                            break
            if found:
                break
        if not found:
            raise Exception(f"Unable to create a standardized publication for device {self.cname}/{self.ename}")

        return
    
    @property
    def dtype(self):
        return self.ppty_data['type']

    @property
    def pubname(self):
        if "is_global" not in self.pubInfo or not self.pubInfo["is_global"]:
            if self.node:
                return f"{self.ppty_data['prefix']}.{self.node}.{self.ppty_data['suffix']}"
            else:
                return f"{self.ppty_data['prefix']}.{self.ename}.{self.ppty_data['suffix']}"
        else:
            if self.node:
                return f"{self.federate}.{self.ppty_data['prefix']}.{self.node}.{self.ppty_data['suffix']}"
            else:
                return f"{self.federate}.{self.ppty_data['prefix']}.{self.ename}.{self.ppty_data['suffix']}"

    @property
    def tags(self): 
        tag_dict =  { "federate" : self.federate}
        tag_dict["phases"] = self.get_value('Phase')
        return tag_dict
    
    @property
    def units(self):
        return self.ppty_data['unit']

    @property
    def publication_type(self):
        value = self.value
        if isinstance(value, float):
            return helics.HELICS_DATA_TYPE_DOUBLE.name
        elif isinstance(value, str):
            return helics.HELICS_DATA_TYPE_STRING.name
        elif isinstance(value, bool):
            return helics.HELICS_DATA_TYPE_BOOLEAN.name
        elif isinstance(value, int):
            return helics.HELICS_DATA_TYPE_INT.name
        elif isinstance(value, complex):
            return helics.HELICS_DATA_TYPE_COMPLEX.name
        elif isinstance(value, list):
            if isinstance(value[0], complex):
                return helics.HELICS_DATA_TYPE_COMPLEX_VECTOR.name
            else:
                return helics.HELICS_DATA_TYPE_VECTOR.name
        else:
            raise Exception(f"Data type {type(value)} not supported")
        return

    @property
    def value(self):
        val = None
        if not self.ppty_data["vector"]:
            if "isreal" in self.ppty_data and self.ppty_data["isreal"]:
                real_part = self.get_value(self.ppty)
                if "pair" in self.ppty_data:
                    imag_part = self.get_value(self.ppty_data["pair"])
                val = float(real_part) + 1j * float(imag_part)              
            elif "isreal" in self.ppty_data and not  self.ppty_data["isreal"]:
                imag_part = self.get_value(self.ppty)
                if "pair" in self.ppty_data:
                    real_part = self.get_value(self.ppty_data["pair"])
                val = float(real_part) + 1j * float(imag_part)
            else:
                if self.cname in ["ShuntCapacitor", 'SeriesCapacitor']:  
                    val = CAPACITOR_STATES[self.get_value(self.ppty)]
        else:
            if "vector_list" in self.ppty_data:
                
                val = []
                for ppty in self.ppty_data["vector_list"]:
                    value = self.get_value(ppty)
                    if value:
                        if self.ppty_data["type"] == "complex":
                            val.append(complex(value))
                        elif self.ppty_data["type"] == "double":
                            val.append(float(value))
                        elif self.ppty_data["type"] == "integer":
                            val.append(int(float(value)))
                        elif self.ppty_data["type"] == "bool":
                            val.append(bool(value))
                        else:
                            val.append(value)
        return val

    def get_value(self, ppty):
        try:
            res = self.obj.GetValue(ppty)
        except:
            res = self.cympy.study.QueryInfoDevice(ppty, self.obj.DeviceNumber, self.obj.DeviceType)
        return res

    @property
    def isVector(self):
        return self.ppty_data['vector']

    @property
    def publish(self):
        
        return

    def __str__(self):
        return "<Publication tag: {}\n units: {},\n dtype: {},\n isVector: {},\n tags: {}\nat {}>\n".format(
            self.pubname,
            self.units,
            self.dtype,
            self.isVector,
            self.tags,
            hex(id(self))
        )

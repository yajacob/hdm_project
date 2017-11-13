import json

class DiagramScript:
    def __init__(self, hdm):
        self.result = "var config = "
        self.hdm_objective = hdm['hdm_objective'].replace("'", "\\'").replace('"', '\\"')
        self.hdm_criteria = hdm['hdm_criteria'].replace("'", "\\'").replace('"', '\\"')
        self.hdm_factors = hdm['hdm_factors'].replace("'", "\\'").replace('"', '\\"')
        self.model_keys = ['config', 'root', 'CR00']
        self.init_design()
        self.make_criteria()
        self.make_factors()
        self.make_model_keys()
        
    def init_design(self):
        self.result += """{
        container: '#DiagramHDM1',
        rootOrientation: 'NORTH',
        hideRootNode: true,
        levelSeparation: 30,
        siblingSeparation: 40,
        subTeeSeparation: 30,
        connectors: {
            type: 'curve'
        },
        node: {
            HTMLclass: 'nodeHDM'
        }
    },
    root = {},
    CR00 = {
        parent: root,
        text:{
            name: '%s'
        },
        stackChildren: false,
        HTMLid: "CR00"
    },\n""" % (self.hdm_objective)
    
    def make_criteria(self):
        #cdata = "Color, Memory, Delivery"
        #print("self.hdm_criteria:"+self.hdm_criteria)
        cdata = self.hdm_criteria.split(",")
        cr_result = ""
        for i in range(len(cdata)):
            key = "CR%d0" % (i+1)
            value = cdata[i].strip()
            self.model_keys.append(key)
        
            cr_result += """    %s = {
            parent: CR00,
            text:{
                name: '%s'
            },
            stackChildren: true,
            HTMLid: '%s'
        },\n""" % (key, value, key)
        self.result += cr_result

    def make_factors(self):
        #hdm_factors = "Pink, Blue, Yellow|16GB, 32GB, 64GB, 128GB|USPS, UPS, FedEx"
        #print("self.hdm_factors:"+self.hdm_factors)
        hdm_factors = self.hdm_factors.split("|")
        cr_result = ""
        for i in range(len(hdm_factors)):
            fdata = hdm_factors[i].strip()
            if len(fdata) < 1: continue
            
            fdata = hdm_factors[i].split(",")
            idx = 1 
            for j in range(len(fdata)):
                value = fdata[j].strip()
                if len(value) < 1: continue
                
                key = "CR%d%d" % (i+1, idx)
                parent = "CR%d0" % (i+1)
                self.model_keys.append(key)
                idx = idx + 1
            
                cr_result += """    %s = {
            parent: %s,
            text:{
                name: '%s'
            },
            HTMLid: '%s'
        },\n""" % (key, parent, value, key)

        self.result += cr_result

    def make_model_keys(self):
        mk_result = "    ALTERNATIVE = "
        mk_result += str(self.model_keys)
        mk_result = mk_result.replace("'", "") + ";"
        
        self.result += mk_result
    
    def __str__(self):
        return self.result
       

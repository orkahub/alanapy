####
## Fundamental libraries
####
import requests
import matplotlib.pyplot as plt
import datetime
from datetime import datetime
import json
import numpy as np
import pandas as pd
import os

####
## Classes & Functions
####
class AlanaPyHelper:
    """
    A helper class for interacting with the Alana API.

    Attributes:

        # Well-related attributes
        _wellmasterdict_all (tuple): A tuple containing two dictionaries for wellmaster data: (full wellmaster dictionary, simplified wellmaster dictionary).
        wellmasterdict (dict): A dictionary containing the simplified wellmaster data with well names as keys.
        wellmasterdict_full (dict): A dictionary containing the full wellmaster data with well IDs as keys.
        ids_wellnames (dict): A dictionary containing ids as keys and well names as values.
        
        # Field-related attributes
        _fieldmasterdict_all (tuple): A tuple containing three dictionaries for fieldmaster data: (full fieldmaster dictionary, simplified fieldmaster dictionary, inverted simplified fieldmaster dictionary).
        fieldmasterdict (dict): A dictionary containing the simplified fieldmaster data with field names as keys.
        fieldmasterdict_inv (dict): A dictionary containing ids and field names.
        
        # Formation-related attributes
        _formationmasterdict_all (tuple): A tuple containing two dictionaries for formationmaster data: (full formationmaster dictionary, simplified formationmaster dictionary).
        formationmasterdict (dict): A dictionary containing the simplified formationmaster data with formation names as keys.
        
        # FDP-related attributes
        _fdpmasterdict_all (tuple): A tuple containing two dictionaries for fdpmaster data: (full fdpmaster dictionary, simplified fdpmaster dictionary).
        fdpmasterdict (dict): A dictionary containing the simplified fdpmaster data.
        fdpmaster_full (dict): A dictionary containing the full fdpmaster data with FDP IDs as keys.
        fdpcasedict (dict): A dictionary containing fdpcase data with case IDs as keys.
        
        # DCA-related attributes
        dcamasterdict (dict): A dictionary containing dcamaster data with DCA IDs as keys.
        
        # VA-related attributes
        welltypemasterdict (dict): A dictionary containing welltypemaster data with well type names as keys.
        current_select_wells (None or list): A list containing selected well IDs for analysis, or None if not selected.
        current_selected_df_prod_inj (None or pandas.DataFrame): A DataFrame containing selected production and injection data for analysis, or None if not selected.
        dcacases (None or list): A list containing DCA case data, or None if not fetched.
        plt_layout (dict): A dictionary containing default parameters for plotting charts.
        bool_debug (bool): A boolean flag indicating whether debug mode is enabled (default: False).

        #
    """
    def re_init(self, token, root_url="http://127.0.0.1:8000"):
        self.root_url = root_url
        self.urls_suffix_dict = {
            "dcamaster": "/api/dca/dcamaster/",
            "fieldmaster": "/api/datasource/fieldmaster/",
            "wellmaster": "/api/datasource/wellmaster/",
            "formationmaster": "/api/datasource/formationmaster/",
            "fdpmaster": "/api/fdp/fdpmaster/",
            "fdpcase": "/api/fdp/fdpcase/",
                                                         
            "economicmaster": "/api/economics/economicmaster/",
            "economicforecastmaster": "/api/economics/economicforecastmaster/",
            "capexmaster": "/api/economics/capexmaster/",
            "opexmaster": "/api/economics/opexmaster/",
            "pricedeck": "/api/economics/pricedeck/",
            "abandonmentmaster": "/api/economics/abandonmentmaster/",
            "genericprodinjmaster": "/api/welltype/genericprodinjmaster/",
            "welltypemaster": '/api/welltype/welltypemaster/',
            "aimlmodel": '/api/aimlmodel/aimlmodel/'
        }
        self.api_mainitem_name_dict = {
            "dcamaster": "name",
            "fieldmaster": "field_name",
            "wellmaster": "well_name",
            "formationmaster": "formation_name",
            "fdpmaster": "name",
            "fdpcase": "name",
                                   
            "economicmaster": "name",
            "economicforecastmaster": "name",
            "capexmaster": "name",
            "opexmaster": "name",
            "pricedeck": "name",
            "abandonmentmaster": "name",
            "genericprodinjmaster": "name",
            "welltypemaster": "name",
            "aimlmodel": "name"
        }
        self.credentials = dict({"alana_token": None})
        #self.password = password  # self.credentials.alana_passwd
        #self.username = username  # self.credentials.alana_author
        try:
            self.credentials["alana_token"] = token
            self.header = {'Authorization': 'Token ' + self.credentials["alana_token"]}
            ## Well dicts        
            self._wellmasterdict_all = self._getGenericDict("wellmaster", fulldict=True)
            self.wellmasterdict = self._wellmasterdict_all[1]
            self.wellmasterdict_full = self._wellmasterdict_all[0]
            self.ids_wellnames = self._dictReversed(self._wellmasterdict_all[1])
            ## Field dicts
            self._fieldmasterdict_all = self._getGenericDict("fieldmaster", fulldict=True)
            self.fieldmasterdict = self._fieldmasterdict_all[1]
            self.fieldmasterdict_inv = self._fieldmasterdict_all[2]
            ## Formation dicts
            self._formationmasterdict_all = self._getGenericDict("formationmaster", fulldict=True)
            self.formationmasterdict = self._formationmasterdict_all[1]
            ## FDP
            self._fdpmasterdict_all = self._getGenericDict("fdpmaster", fulldict=True)
            self.fdpmasterdict = self._getGenericDict("fdpmaster")
            self.fdpmaster_full = self._fdpmasterdict_all[0]
            self.fdpcasedict = self._getGenericDict("fdpcase")
            ## DCA
            self.dcamasterdict = self._getGenericDict("dcamaster")
            #AIML
            self.aimlmasterdict = self._getGenericDict("aimlmodel")
            
            ## VA
            self.welltypemasterdict = self._getGenericDict('welltypemaster',fulldict=False)
            self.current_select_wells = None
            self.current_selected_df_prod_inj = None
            self.dcacases = None
            self.plt_layout = {
                "size": (15, 8),
                "label_x": "Date",
                "label_y": "Oil Production (stb/d)",
                "font_size": 15
            }
            self.bool_debug = False
            self.active_workspace = self.getActiveWorkspace()
            print(f"\nConnection stablished succesfully\n")
        except Exception as e:
            print("Error stablishing connection")
            if e.args[0] == "token":
                print(f"Please check your credentials or server connectivity\n\nIf the problem persists, please contact a developer for assistance\nError:{e}\n")
            else:
                print(e.value) #.format_exc()

    def getActiveWorkspace(self):
        url = self.root_url + "/api/general/active_workspace/"
        header = {'Authorization': 'Token ' + self.credentials["alana_token"],
                  "content-type": "application/json"}
        mydata = requests.get(url, headers=header)
        results = mydata.json()
        return results

    def _getCase(self, case_app, case_table, mastername_fk, master_id):
        """
        args(list_of_dicts, case_app, case_table)
        RETURN dict Response_api
        """
        url = self.root_url + "/api/" + case_app + "/" + case_table + "/"
        header = {'Authorization': 'Token ' + self.credentials["alana_token"],
                  "content-type": "application/json"}
        params = {
            mastername_fk: master_id
        }

        mydata = requests.get(url, headers=header, params=params)  # .json()
        if (mydata.status_code >= 200 and mydata.status_code < 300):
            pass
            #print("Success")
            #print(mydata.status_code)
        else:
            print("Error")
            print(mydata.status_code)
        results = mydata.json()
        return results

    def _getKeysDictList(self, val, dict_selected):
        """
        {
        "description": "Function that return a list of keys from a value in a given dictionary",
        "arguments" : {
            "value" : "str",
            "dictionary" : "dict"
            },
        "example": ""
        }
        """
        keys = []
        for key, value in dict_selected.items():
            if val == value:
                keys.append(key)
        if len(keys) > 0:
            return keys
        return "key doesn't exist in dictionary"

    def _getToken(self):
        """
        Internal Function
        """
        url = self.root_url + '/api-token-auth/'
        data = {
            'username': self.username,
            'password': self.password
        }
        header = {
            "content-type": "application/json"
        }
        
        mydata = requests.post(url, data=data)
        results = mydata.json()
        return results["token"]

    def _getGenericDict(self, itemname, fulldict=False, params={}):
        """
        }
        "description": "Construct a dictionary from the item provided, the boolean returns either the main itemname or the whole array",
        "arguments" : {
            "itemname" : "str",
            "bool_fulldict" : False
            },
        "example": ""
        }
        """
        url = self.root_url + self.urls_suffix_dict[itemname]

        header = self.header
        mydata = requests.get(url, headers=header, params=params)  # .json()
        try:
        #print(url)
            results = mydata.json()
            #print("results",results)
            df_results = pd.DataFrame(results)
        except :
            print(f"Issues with the followning api: {url}")
            results = None
        if fulldict:
            if not results:
                return results, {}, {}
            else:
                return results, dict(zip(df_results[self.api_mainitem_name_dict[itemname]], df_results['id'])), dict(
                    zip(df_results["id"], df_results[self.api_mainitem_name_dict[itemname]]))
        else:
            if not results:
                return {}
            else:
                return dict(zip(df_results[self.api_mainitem_name_dict[itemname]], df_results['id']))

    def _getMaster(self,master_app,master_table,master_fk: str=None, should_download=False):
        """
        }
        "description": "Construct a dictionary from the data of a master_app, master_table and a possible master:fk",
        "arguments" : {
            "master_app" : "str",
            "master_table" : "str",
            "master_fk" : "str",
            },
        "example": "",
        }
        """
        if master_fk is None:
            url = self.root_url + "/api/" + master_app + "/" + master_table + "/"
        else:
            url = self.root_url + "/api/" + master_app + "/" + master_table + "/" + master_fk + "/"
            if should_download:
                url = url + "download/"
        header = self.header
        mydata = requests.get(url, headers=header)  # .json()
        if should_download:
            # The URL should point to your custom action endpoint with the appropriate ID

            if mydata.status_code == 200:
                # Get the filename from the Content-Disposition header
                content_disposition = mydata.headers.get('Content-Disposition')
                if content_disposition:
                    filename = content_disposition.split('filename=')[-1]
                else:
                    filename = 'downloaded_file.ext'

                with open(filename, 'wb') as f:
                    results = mydata.content
            else:
                print(f"Failed to retrieve file. Status code: {mydata.status_code}")
        else:
            results = mydata.json()
        return results

    def _deleteMaster(self, master_app, master_table, master_fk):
        """
        }
        "description": "Delete data of a master_app, master_table and a masterfk",
        "arguments" : {
            "master_app" : "str",
            "master_table" : "str",
            "master_fk" : "int",
            },
        "example": ""
        }
        """
        url = self.root_url + "/api/" + master_app + "/" + master_table + "/" + str(master_fk) + "/"
        header = self.header
        mydata = requests.delete(url, headers=header)  # .json()
        mygeneric = Generic()
        bool_status = mygeneric.statusCodeCheck(mydata)
        if master_table == "dcamaster":
            self.dcamasterdict = self._getGenericDict(master_table)
        elif master_table == "fdpmaster":
            self.fdpmasterdict = self._getGenericDict(master_table)
        elif master_table == "wellmaster":
            self.wellmasterdict = self._getGenericDict(master_table)
        elif master_table == "fieldmaster":
            self.fieldmasterdict = self._getGenericDict(master_table)
        elif master_table == "formationmaster":
            self.formationmasterdict = self._getGenericDict(master_table)
        elif master_table == "economicmaster":
            self.economicmasterdict = self._getGenericDict(master_table)
        elif master_table == "economicforecastmaster":
            self.economicforecastmasterdict = self._getGenericDict(master_table)
        elif master_table == "capexmaster":
            self.capexmasterdict = self._getGenericDict(master_table)
        elif master_table == "opexmaster":
            self.opexmasterdict = self._getGenericDict(master_table)
        elif master_table == "pricedeck":
            self.pricedeckdict = self._getGenericDict(master_table)
        elif master_table == "abandonmentmaster":
            self.abandonmentmaster = self._getGenericDict(master_table)
        elif master_table == "genericprodinjmaster":
            self.genericprodinjmaster = self._getGenericDict(master_table)

        
        
        if(mydata.status_code == 204):
            print("Success")
        else:
            print(mydata.status_code)
            print("Error")
        return mydata
    
    def _createMaster(self, master_app, master_table, master_dict, files=None, json_dumps=True):
        """
        }
        "description": "Create master table given a master_app, master_table and a master_dict",
        "arguments" : {
            "master_app" : "str",
            "master_table" : "str",
            "master_dict" : "dict",
            },
        "example": ""
        }
        """
        mygeneric = Generic()
        header = {'Authorization': 'Token ' + self.credentials["alana_token"]}
        if json_dumps:
            master_dict = json.dumps(master_dict)
            header['"content-type"'] = "application/json"
        url = self.root_url + "/api/" + master_app + "/" + master_table + "/"

        mydata = requests.post(url, headers=header, data=master_dict, files=files)  # .json()
        bool_status = mygeneric.statusCodeCheck(mydata)
        if master_table == "dcamaster":
            self.dcamasterdict = self._getGenericDict(master_table)
        elif master_table == "fdpmaster":
            self.fdpmasterdict = self._getGenericDict(master_table)
        elif master_table == "wellmaster":
            self.wellmasterdict = self._getGenericDict(master_table)
        elif master_table == "fieldmaster":
            self.fieldmasterdict = self._getGenericDict(master_table)
        elif master_table == "formationmaster":
            self.formationmasterdict = self._getGenericDict(master_table)
        elif master_table == "economicmaster":
            self.economicmasterdict = self._getGenericDict(master_table)
        elif master_table == "economicforecastmaster":
            self.economicforecastmasterdict = self._getGenericDict(master_table)
        elif master_table == "capexmaster":
            self.capexmasterdict = self._getGenericDict(master_table)
        elif master_table == "opexmaster":
            self.opexmasterdict = self._getGenericDict(master_table)
        elif master_table == "pricedeck":
            self.pricedeckdict = self._getGenericDict(master_table)
        elif master_table == "abandonmentmaster":
            self.abandonmentmaster = self._getGenericDict(master_table)
        elif master_table == "genericprodinjmaster":
            self.genericprodinjmaster = self._getGenericDict(master_table)
        elif master_table == "aimlmaster":
            self.aimlmasterdict = self._getGenericDict(master_table)
        return mydata.json()

    def _createCases(self, list_of_dicts, case_app, case_table):
        """
        }
        "description": "Create cases from a list_of_dicts for a given case_app and a case_table",
        "arguments" : {
            "list_of_dicts" : [{dict_case_1},{dict_case_2}],
            "case_app" : "str",
            "case_table" : "dict",
            },
        "example": ""
        }
        """
        mygeneric = Generic()
        url = self.root_url + "/api/" + case_app + "/" + case_table + "/"
        header = {'Authorization': 'Token ' + self.credentials["alana_token"],
                  "content-type": "application/json"}
        data = {}
        data["instances"] = list_of_dicts
        data["has_many"] = True
        data = json.dumps(data)        
        mydata = requests.post(url, headers=header, data=data)  # .json()
        mygeneric.statusCodeCheck(mydata)
        results = mydata.json()
        return results

    def _createMasterCases(self, master_app, master_table, master_dict, list_of_dicts, case_app, case_table):
        """
        }
        "description": "Create a master of cases",
        "arguments" : {
            "master_app" : "str",
            "master_table"
            "list_of_dicts" : ["dict"],
            "case_app" : "str",
            "case_table" : "dict",
            },
        "example": ""
        }
        """
        response_master = self._createMaster(master_app, master_table, master_dict)
        id_master = response_master["id"]
        new_list = []
        for _dict in list_of_dicts:
            _dict[master_table+"_fk"] = id_master
            new_list.append(_dict)
        response_cases = self._createCases(new_list, case_app, case_table)
        return (response_master, response_cases)

    def _editMaster(self, master_app, master_table, master_dict, master_fk):
        """
         Function that update a Master
        args(master_app, master_table, master_dict)
        RETURN dict Response_api
        """
        master_dict = json.dumps(master_dict)
        url = self.root_url + "/api/" + master_app + "/" + master_table + "/" + str(master_fk) + "/"
        header = {'Authorization': 'Token ' + self.credentials["alana_token"],
                  "content-type": "application/json"}
        mydata = requests.put(url, headers=header, data=master_dict)  # .json()
        if mydata.status_code >= 200 and mydata.status_code < 300:
            print("Success")
            print(mydata.status_code)
        else:
            print("Error")
            print(mydata.status_code)
        results = mydata.json()
        print(mydata.status_code)
        return results

    def _fitForecastDCA(self, dates, rates, dca_template_fit_forecast):
        url = self.root_url + "/api/dca/fit_forecast/"
        dca_template_fit_forecast = json.dumps(dca_template_fit_forecast)
        header = {'Authorization': 'Token ' + self.credentials["alana_token"],
                  "content-type": "application/json"}
        mydata = requests.post(url, headers=header, data=dca_template_fit_forecast)  # .json()
        dca_forecast = mydata.json()
        # print("fit_forecast:",dca_forecast)
        return dca_forecast
    
    def _saveDCA(self, dcamaster_fk, well_fk, dca_forecast, x_selected, rates, dca_template_fit_forecast):
        dca_save_dict = dca_template_fit_forecast
        dca_save_dict['fit_type'] = 'AUTO'
        dca_save_dict['secondary_forecast_type'] = 'RATIO'
        dca_save_dict['water_forecast_type'] = 'RATIO'
        dca_save_dict['secondary_phase_ratio'] = 0.8
        dca_save_dict['water_phase_ratio'] = 0.8
        dca_save_dict['primary_plot_layout'] = None
        dca_save_dict['secondary_plot_data'] = None
        dca_save_dict['secondary_plot_layout'] = None
        dca_save_dict["oil_reserves"] = dca_forecast["primary_phase_reserves"]
        dca_save_dict["gas_reserves"] = dca_forecast["gas_reserves"]
        dca_save_dict["water_reserves"] = dca_forecast["water_reserves"]

        dca_save_dict['resources'] = None
        dca_save_dict['cumprod'] = None
        dca_save_dict['well_fk'] = well_fk
        dca_save_dict['dcamaster_fk'] = dcamaster_fk
        dca_save_dict["primary_phase_beta"] = dca_forecast["primary_phase_beta"]
        dca_save_dict["primary_phase_decline"] = dca_forecast["primary_phase_decline"]
        dca_save_dict["primary_phase_fit_rate"] = dca_template_fit_forecast["primary_phase_forecast_rate"]
        # dca_save_dict["primary_phase_forecast_rate"] = dca_forecast["primary_phase_forecast_rate"]
        # dca_save_dict["arps_type"] = dca_forecast["arps_type"]
        try:
            fit = dca_forecast["fit"]
            time_fit = dca_forecast["time_fit"]
        except:
            fit = None
            time_fit = None
        dca_save_dict["primary_plot_data"] = {
            'fit': fit,
            'time_fit': time_fit,
            'forecast': dca_forecast["forecast"],
            'time_forecast': dca_forecast["time_forecast"],
            'x_selected': x_selected,
            'y_selected': rates,
            'reinitialize_choice': 'NO',
            'fc_date_choice': 'DEFAULT',
            'fc_rate_choice': 'LASTVAL'
        }
        try:
            dca_save_dict = json.dumps(dca_save_dict)
        except:
            return dca_save_dict
        url = self.root_url + "/api/dca/dcacase/"
        header = {'Authorization': 'Token ' + self.credentials["alana_token"],
                  "content-type": "application/json"}
        mydata = requests.post(url, headers=header, data=dca_save_dict)  # .json()
        dca_save = mydata.json()
        return dca_save, dca_save_dict
    
    def _getKeyFromDict(self, val, dict_selected):
        """
        Function that obtains the key of a given dictionary based on the value
        args(str_value,dict_selected)
        Returns: str
        """
        for key, value in dict_selected.items():
            if val == value:
                return key
        return "key doesn't exist in dictionary"

    def _print(self,str_dbg_print):
        if self.bool_debug :
            print(f"Debug mode:\n{str_dbg_print}\n")
            
    def _dictReversed(self,dict_original):
        dict_reversed= {v: k for k, v in dict_original.items()}
        return dict_reversed
        
class Singleton:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.master = AlanaPyHelper()  # create and store parent instance
        return cls._instance

class Economics:
    def __init__(self):
        self.master = Singleton().master

    def runEconomics(self, params={}):
        """
        {
        "description":,
        "returns":,
        "example":,
        }
        """
        if len(params) == 0:
            return "Please provide the params dictionary, refer to the documentation of this function"

        url = self.master.root_url + "/api/economics/runeconomics/"
        header = self.master.header
        mydata = requests.get(url, headers=header, params=params)  # .json()
        results = mydata.json()
        return results

    def createEconomicForecastMaster(self, _dict: dict):
        """
        {
        "description":"Function that creates a Master for Economic Forecast",
        "arguments":{
                "name": "",
                "description": ""
            },
        "return":{
                "id": "",
                "name": "",
                "description": ""
            },
        "example":,
        }
        """
        dict_response_api = self.master._createMaster("economics", "economicforecastmaster", _dict)
        return dict_response_api

    def editEconomicForecastMaster(self, master_fk: int, dict_edit_master: dict):
        """
        {
        "description": "Function that update a Master for Economic Forecast",
        "arguments": [
            "master_fk",
            { "name": "",
            "description": ""}
            ],
        "return": {
                "id": "",
                "name": "",
                "description": ""
            },
        "example": ""
        }
        """
        dict_edit_master = self.master._editMaster("economics", "capexmaster", dict_edit_master,  str(master_fk))
        return dict_edit_master

    def getEconomicForecastMaster(self, master_fk: str):
        """
        Function that return the cases that match with the master_fk
        args(master_fk)
        RETURN dict_get_cases
        """
        dict_get_master = self.master._getMaster("economics", "economicforecastmaster", str(master_fk))
        print(dict_get_master)
        return dict_get_master

    def deleteEconomicForecastMaster(self, master_fk: str):
        """
        Function that delete the master that match with the master_fk
        args(master_fk)
        RETURN deleted_master
        """
        deleted_master = self.master._deleteMaster("economics", "economicforecastmaster", str(master_fk))
        return deleted_master
  
    def createEconomicForecastCases(self, list_of_dicts: list):
        """
        Function that creates a case sending the master_fk bind to a Master, sending a list
        list_of_dicts = [{
            "date": "2023-08-23",
            "oil": 399.700569476893,
            "wat": 800.299430523107,
            "gas": null,
            "wat_inj": null,
            "gas_inj": null,
            "steam_inj": null,
            "active_wells": null,
            "opex": null,
            "capex": null,
            "abandonment_cost": null,
            "total_cost_variable": null,
            "total_cost_fixed": null,
            "total_cost": null,
            "total_revenue": null,
            "cash_flow": null,
            "economicforecastmaster_fk": 4
        },
        {
            "date": "2023-07-01",
            "oil": 203.0,
            "wat": 397.0,
            "gas": null,
            "wat_inj": null,
            "gas_inj": null,
            "steam_inj": null,
            "active_wells": null,
            "opex": null,
            "capex": null,
            "abandonment_cost": null,
            "total_cost_variable": null,
            "total_cost_fixed": null,
            "total_cost": null,
            "total_revenue": null,
            "cash_flow": null,
            "economicforecastmaster_fk": 4
        }]

        RETURN Response_api
        """
        dict_response_api = self.master._createCases(list_of_dicts, "economics", "economicforecastcase")
        return dict_response_api

    def createEconomicForecastMasterCases(self, _dict: dict, list_of_dicts: list):
        """
            Please refer to the createEconomicMaster and createEconomicForecastCases for detailed example
        """
        tuple_response_api = self.master._createMasterCases("economics", "economicforecastmaster", _dict, list_of_dicts,
                                                            "economics", "economicforecastcase")
        print(tuple_response_api)
        return tuple_response_api

    def createEconomicScenario(self, _dict: dict):
        """
            createEconomicScenario
        """
        dict_response_api = self.master._createMaster("economics", "economicscenario", _dict)
        return dict_response_api

    def createEconomicScenarioCases(self, list_of_dicts: list):
        """
            createEconomicScenarioCases
        """
        dict_response_api = self.master._createCases(list_of_dicts, "economics", "economicscenariocase")
        return dict_response_api

    def createEconomicScenarioAndCases(self, _dict: dict, list_of_dicts: list):
        """
            Please refer to the createEconomicScenario and createEconomicScenarioCases for detailed example
        """
        tuple_response_api = self.master._createMasterCases("economics", "economicscenario", _dict, list_of_dicts,
                                                            "economics", "economicscenariocase")
        print(tuple_response_api)
        return tuple_response_api

    # def _createEconomicScenarioCase(self, dict_economicscenario : dict, lst_economicscenariocase: dict):
    #     """
    #     Function that takes the given dicts and create a scenario and a case
    #     dict_economicscenario = {
    #     "name": "Scenario_1",
    #     "description": deterministic scenario 1
    #     }
    #
    #     lst_economicscenariocase = [{
    #     "description": "",
    #     "capexmaster_fk": None,
    #     "forecastmaster_fk": None,
    #     "opexmaster_fk": None,
    #     "abandonmentmaster_fk": None
    #     },
    #     {
    #     "description": "",
    #     "capexmaster_fk": None,
    #     "forecastmaster_fk": None,
    #     "opexmaster_fk": None,
    #     "abandonmentmaster_fk": None
    #     }]
    #
    #     RETURN myscenariodata, mycasedata
    #     """
    #     scenario_url = Singleton().master.root_url + "/api/" + "economics" + "/" + "economicscenario" + "/"
    #     header = {'Authorization': 'Token ' + Singleton().master.credentials["alana_token"]}
    #     myscenariodata = requests.post(scenario_url, headers=header, data=dict_economicscenario)  # .json()
    #     scenario_results = myscenariodata.json()
    #     if(myscenariodata.status_code>=200 and myscenariodata.status_code<300):
    #         print("Success")
    #         print(myscenariodata.status_code)
    #     else:
    #         print(myscenariodata.status_code)
    #         print("Error in scenario")
    #     case_url = Singleton().master.root_url + "/api/" + "economics" + "/" + "economicscenariocase" + "/"
    #     mycasedata = requests.post(scenario_url, headers=header, data=lst_economicscenariocase)  # .json()
    #     if(mycasedata.status_code>=200 and mycasedata.status_code<300):
    #         print(mycasedata.status_code)
    #         print("Success")
    #     else:
    #         print(mycasedata.status_code)
    #         print("Error in case")
    #     case_results = mycasedata.json()
    #
    #     return scenario_results, case_results

    def createCapexMaster(self,  dict_capex : dict):
        """
        Function that creates capex master based on investment input with structure dict_capex
        dict_capex = {
            "name" : None,
            "description" : "_",
            "development_well" : 0,
            "development_well_vertical" : 0,
            "development_well_horizontal" : 0,
            "development_well_deviated" : 0,
            "development_g_a" : 0,
            "workover" : 0
        }
        args(dict_capex)
|
        RETURN dict Response_api
        """
        dict_response_api = self.master._createMaster("economics", "capexmaster", dict_capex)
        return dict_response_api

    def createCapexCases(self, list_of_dicts):
        """
        Function that uploads to the server a list of dicts from a data frame of investments along time
        list_of_dicts = [
        [
    {
        "date": "2017-01-01",
        "seismic_2D": 0.0,
        "seismic_3D": 0.0,
        "exploration_well": 0.0,
        "land_lease": 0.0,
        "appraisal_well": 0.0,
        "seismic_2D_optional": 0.0,
        "seismic_3D_optional": 0.0,
        "exploration_well_optional": 0.0,
        "land_lease_optional": 0.0,
        "appraisal_well_optional": 0.0,
        "exploration_g_a": 0.0,
        "total_facilities": 0.0,
        "studies": 0.0,
        "contingency": 0.0,
    },
        {
        "date": "2017-01-01",
        "seismic_2D": 0.0,
        "seismic_3D": 0.0,
        "exploration_well": 0.0,
        "land_lease": 0.0,
        "appraisal_well": 0.0,
        "seismic_2D_optional": 0.0,
        "seismic_3D_optional": 0.0,
        "exploration_well_optional": 0.0,
        "land_lease_optional": 0.0,
        "appraisal_well_optional": 0.0,
        "exploration_g_a": 0.0,
        "total_facilities": 0.0,
        "studies": 0.0,
        "contingency": 0.0,
    }
        ]
        list_of_dicts = pd.to_dict(df)
        args(list_of_dicts)
        RETURN dict Response_api
        """
        dict_response_api = self.master._createCases(list_of_dicts, "economics", "capexcase")
        return dict_response_api

    def createCapexMasterCases(self, dict_capex: dict, list_of_dicts: list):
        """
        Please refer to the createCapexMaster and createCapexCases for detailed example
        """
        tuple_response_api = self.master._createMasterCases("economics", "capexmaster", dict_capex, list_of_dicts,
                                                            "economics", "capexcase")
        print(tuple_response_api)
        return tuple_response_api

    def getCapexMaster(self, master_fk: str):
        """
        Function that return the cases that match with the master_fk
        args(master_fk)
        master_fk = Integer
        RETURN dict_get_cases
        """
        dict_get_master = self.master._getMaster("economics", "capexmaster", str(master_fk))
        print(dict_get_master)
        return dict_get_master

    def deleteCapexMaster(self, master_fk):
        """
        Function that delete the master that match with the master_fk
        args(master_fk)
        master_fk = Integer
        RETURN deleted_master
        """
        deleted_master = self.master._deleteMaster("economics", "capexmaster", str(master_fk))
        return deleted_master

    def editCapexMaster(self, master_fk: int, dict_edit_master: dict):
        """
        Function that updates a Master
        args(master_fk)
        master_fk = Integer
        RETURN dict_edit_master
        """
        dict_edit_master = self.master._editMaster("economics", "capexmaster", dict_edit_master,  str(master_fk))
        return dict_edit_master
    def createOpexMaster(self, dict_opex: dict):
        """
        Function that creates opex master based on investment input with structure dict_opex
        dict_opex = {
            "name": Provide_name,
            "description": "_",
            "variable_opex_oil": 0.0,
            "variable_opex_gas": 0.0,
            "variable_opex_fluid": 0.0,
            "variable_opex_water": 0.0,
            "variable_opex_1": 0.0,
            "variable_opex_2": 0.0,
            "variable_opex_3": 0.0
        }
        args(dict_opex)
        RETURN dict Response_api
        """
        dict_response_api = self.master._createMaster("economics", "opexmaster", dict_opex)
        return dict_response_api

    def createOpexCases(self, list_of_dicts):
        """
        Function that uploads to the server a list of dicts from a data frame of investments along time
        list_of_dicts = [
        {
        "date": "2018-01-01",
        "operating_g_a": 0.0,
        "fixed_opex": 0.0.06,
        "fixed_opex_1": 0.0,
        "fixed_opex_2": 0.0,
        "fixed_opex_3": 0.0,
        "workovers": 0.0,
        "transport_tariff": 0.0,
        "process_tariff": 0.0,
        "cost_share": 0.0,
        "tariff_revenue": 0.0,
        },
         {
        "date": "2018-01-01",
        "operating_g_a": 0.0,
        "fixed_opex": 0.0.06,
        "fixed_opex_1": 0.0,
        "fixed_opex_2": 0.0,
        "fixed_opex_3": 0.0,
        "workovers": 0.0,
        "transport_tariff": 0.0,
        "process_tariff": 0.0,
        "cost_share": 0.0,
        "tariff_revenue": 0.0,
        }
        ]
        args(list_of_dicts)
        RETURN dict Response_api
        """
        dict_response_api = self.master._createCases(list_of_dicts, "economics", "opexcase")
        return dict_response_api

    def createOpexMasterCases(self, dict_capex: dict, list_of_dicts: list):
        """
        Please refer to the createOpexMaster and createOpexCases for detailed example
        """
        tuple_response_api = self.master._createMasterCases("economics", "opexmaster", dict_capex, list_of_dicts,
                                                            "economics", "opexcase")
        return tuple_response_api

    def getOpexMaster(self, master_fk: str):
        """
        Function that return the cases that match with the master_fk
        args(master_fk)
        master_fk = Integer
        RETURN dict_get_cases
        """
        dict_get_master = self.master._getMaster("economics", "opexcases", str(master_fk))
        print(dict_get_master)
        return dict_get_master
    def deleteCapexMaster(self, master_fk):
        """
        Function that delete the master that match with the master_fk
        args(master_fk)
        master_fk = Integer
        RETURN deleted_master
        """
        deleted_master = self.master._deleteMaster("economics", "opexmaster", str(master_fk))
        return deleted_master
    def createPriceDeckMaster(self, dict_price: dict):
        """
        Function that creates price deck master based on investment input with structure dict_price
        dict_price = {
            "name": "general",
            "description": "EIA forecast"
        }
        args(dict_price)
        RETURN dict Response_api
        """
        dict_response_api = self.master._createMaster("economics", "pricedeck", dict_price)
        return dict_response_api

    def createPriceCases(self, list_of_dicts):
        """
        Function that uploads to the server a list of dicts from a data frame of investments along time
        list_of_dicts = [
        {
            "date": "2021-01-01",
            "oil": 0.0,
            "gas": 0.0,
            "condensate": 0.0,
            "ngl": 0.0,
        },
        {
            "date": "2021-07-07",
            "oil":  0.0,
            "gas":  0.0,
            "condensate":  0.0,
            "ngl": 0.0,
        }
        ]
            list_of_dicts = pd.to_dict(df)
            args(list_of_dicts)
            RETURN dict Response_api
            """
        dict_response_api = self.master._createCases(list_of_dicts, "economics", "pricecase")
        return dict_response_api

    def getPriceDeck(self, master_fk: str):
        """
        Function that return the cases that match with the master_fk
        args(master_fk)
        master_fk = Integer
        RETURN dict_get_cases
        """
        dict_get_master = self.master._getMaster("economics", "pricecase", str(master_fk))
        print(dict_get_master)
        return dict_get_master
    def deletePriceDeck(self, master_fk):
        """
        Function that delete the master that match with the master_fk
        args(master_fk)
        master_fk = Integer
        RETURN deleted_master
        """
        deleted_master = self.master._deleteMaster("economics", "pricedeck", str(master_fk))
        return deleted_master

    def createEconomicModelMaster(self, dict_economic: dict):
        """
        Function that creates economic modal master based on investment input with structure dict_economic
        dict_economic = {
            "name": Provided Name,
            "discount_rate_yearly": 0.0,
            "inflation_rate_yearly": 0.0,
            "BOE_factor": 0.0,
            "additional_financial_tax": 0.0,
            "depreciation_lifetime_months": 0.0,
            "POS": 0.0
        }
        args(dict_economic)
        RETURN dict Response_api
        """
        dict_response_api = self.master._createMaster("economics", "economicmaster", dict_economic)
        return dict_response_api

    def createEconomicCases(self, list_of_dicts):
        """
        Function that uploads to the server a list of dicts from a data frame of investments along time
        list_of_dicts = [
        {
            "date": "2021-01-01",
            "royalty_oil": 0.0 ,
            "royalty_gas": 0.0,
            "WI": 0.0,
            "inflation_rate": 0.0,
        },
        {
            "date": "2021-12-01",
            "royalty_oil": 0.0 ,
            "royalty_gas": 0.0,
            "WI": 0.0,
            "inflation_rate": 0.0,
        }
            ]

        list_of_dicts = pd.to_dict(df)
        args(list_of_dicts)
        RETURN dict Response_api
        """
        dict_response_api = self.master._createCases(list_of_dicts, "economics", "economiccase")
        return dict_response_api

    def getEconomicModelMaster(self, master_fk: str):
        """
        Function that return the cases that match with the master_fk
        args(master_fk)
        master_fk = Integer
        RETURN dict_get_cases
        """
        dict_get_master = self.master._getMaster("economics", "economiccase", str(master_fk))
        print(dict_get_master)
        return dict_get_master
    def deleteEconomicModelMaster(self, master_fk):
        """
        Function that delete the master that match with the master_fk
        args(master_fk)
        master_fk = Integer
        RETURN deleted_master
        """
        deleted_master = self.master._deleteMaster("economics", "economicmaster", str(master_fk))
        return deleted_master

    def createAbandonmentMaster(self, dict_abandonment: dict):
        """
        Function that creates abandonment master based on investment input with structure dict_abandonment
        dict_abandonment = {
            "name": "Provided Name",
            "abandonment_wells": null
            "abandonment_facilities": null
            "description": null
        }
        args(dict_abandonment)
        RETURN dict Response_api
        """
        dict_response_api = self._createMaster("economics", "abandonmentmaster", dict_abandonment)
        return dict_response_api

class FDP:
    def __init__(self):
        self.master = Singleton().master
        
    def createFDPMaster(self,fdp_master_dict):
        """
        {
        "description": "Create a Field Development Plan ",
        "arguments" : {
            "dict_main" : {
                "name": "str_fdp_name",
                "created_at": "YYYY-MM-DD",
                "updated_at": "YYYY-MM-DD",
                "description": "Empty",
                "start_date": "YYYY-MM-DD",
                "end_date": "YYYY-MM-DD",
                "scope": "PUBLIC"
                }
            },
        "return":{
                "id" : 1,
                "name" : "FDP A",
                "created_at": "YYYY-MM-DD"
            }
        }
        """
        dict_fdpmaster = self.master._createMaster("fdp", "fdpmaster", fdp_master_dict)
        return dict_fdpmaster
    
    def createFDPCase(self, case_app, case_table, list_of_dicts, str_fdp_name):
        """
        {
            "description": "Create a Field Development Plan ",
            "arguments" : {
                "dict_main" : {
                    "name": "str_fdp_name",
                    "created_at": "YYYY-MM-DD",
                    "updated_at": "YYYY-MM-DD",
                    "description": "Empty",
                    "start_date": "YYYY-MM-DD",
                    "end_date": "YYYY-MM-DD",
                    "scope": "PUBLIC"
                    }
                },
            "return":{
                "id":1,
                "name": "FDP Case A",
                "created_at": "YYYY-MM-DD"
            }
        }
        """
        df_temp = pd.DataFrame(list_of_dicts)
        df_temp["welltype_fk"] = ""
        df_temp["dcamaster_fk"] = ""       
        # fdpMaster
        try:
            df_temp["fdpmaster_fk"] = self.master.fdpmasterdict[str_fdp_name]
        except Exception as e:
            print(f"No such FDP Master\nError:{e}")
        # Case assignation    
        for index, row in df_temp.iterrows():
            if row['action_type'] == "WellType":
                df_temp.loc[index, 'welltype_fk'] = self.master.welltypemasterdict[row['action_name']]
                #row["welltype_fk"] = self.master.welltypemasterdict[row['action_name']]
            elif row['action_type'] == 'DCA':
                df_temp.loc[index, 'dcamaster_fk'] = self.master.dcamasterdict[row['action_name']]
                #row['dcamaster_fk'] = self.master.dcamasterdict[row['action_name']]
            elif row["action_type"] is None:
                print("No valid Type value for case")    
        dict_cases = df_temp.to_dict('records')
        self.master._print(f"dict_cases:{dict_cases}")
        dict_fdpcase= self.master._createCases(dict_cases,"fdp", "fdpcase")
        return dict_fdpcase
     
    def runFDP(self, str_fdp_name, preffix="FDP_"):
        """
        {
            "description": "Run FDP given by a FDP master and its cases",
            "arguments" : {
                "FDP_master_name" : "str_fdp_master",
                "Preffix" : "FDP_"
            },
            "return" : {
                "id": 1, 
                "name": "FDP_Case A",
                "created_at": "YYYY-MM-DD"
            }
        }
        """
        int_id_master = self.master.fdpmasterdict[str_fdp_name]
        url = self.master.root_url + "/api/" + "fdp/runfdp/"
        header = self.master.header
        params = {
            "fdpmaster_fk" : int_id_master ,
            "preffix" : preffix
        }
        mydata = requests.get(url, headers=header, params=params)  # .json()
        results = mydata.json()
        return results
        
    def createFDPMasterAndCases(self, _dict: dict, list_of_dicts: list):
        """
            Please refer to the createEconomicScenario and createEconomicScenarioCases for detailed example
        """
        tuple_response_api = self.master._createMasterCases("fdp", "fdpmaster", _dict, list_of_dicts, "fdp", "fdpcase")
        print(tuple_response_api)
        return tuple_response_api

    def getFDPCases(self, str_fdp_case: str):
        """
        {
            "description":"Function that return the fdp cases of a matching given case",
            "arguments":{
                "str_fdp_case" : "FDP_case_A"
            },
            "return":{
                "id": 1,
                "name": "FDP Case A",
                "created_at": "YYYY-MM-DD"
            }
        }
        """
        if str_fdp_case is None:
            print(f"Review arguments.")
        else:
            int_fdpcase_id = self.master.fdpcasedict[str_fdp_case]
            dict_get_cases = self.master._getMaster("fdp", "fdpcase", str(int_fdpcase_id))
            return dict_get_cases

    def createFDPDowtimeCases(self, _dict: dict, list_of_dicts: list):
        """
            Please refer to the createEconomicScenario and createEconomicScenarioCases for detailed example
        """
        tuple_response_api = self.master._createMasterCases("downtime", "downtimemaster", _dict, list_of_dicts, "downtime", "downtimecase")
        print(tuple_response_api)
        return tuple_response_api

    def getFDPDowtimeCases(self, master_fk: str):
        """
        {
            "description":"Function that return the cases that match with the master_fk",
            "arguments":{
                "master_fk" : int
            },
            "return":{
                "dict_response":{
                }
            },
            "example":,
        }
        """
        dict_get_cases = self.master._getMaster("fdp", "downtimecase", str(master_fk))
        print(dict_get_cases)
        return dict_get_cases

class Datasource:
    def __init__(self):
        self.master = Singleton().master

    def createWellMaster(self, well_master_dict: dict):
        """
        {
            "description": "Function that create Wells and returns well's information and status.",
            "arguments": {
                "dict_main": {
                    "well_name": "",
                    "spud_date": "YYYY-MM-DD",
                    "production_date": "YYYY-MM-DD",
                    "api_code": "int",
                    "latitude": "float",
                    "longitude": "float",
                    "utm_x": "float",
                    "utm_y": "float",
                    "comment": "",
                    "type": "",
                    "field": "str_field"
                }
            },
            "return": {
                "well_name": "YPF-1",
                "comment": "",
                "type": "EXPLORATION",
                "field": "Field A",
                "formation": "Formation A",
                "longitude": 123.456,
                "latitude": -123.456
            }
        }
        """
        well_master_dict["field_fk"] = self.master.fieldmasterdict[well_master_dict["field"]]
        well_master_dict["formation_fk"] = self.master.formationmasterdict[well_master_dict["formation"]]
        dict_wellmaster = self.master._createMaster("datasource", "wellmaster", well_master_dict)
        return dict_wellmaster

    def getWellMaster(self, str_well_name=None):
        """
        {
            "description":"Function that fetch wellmaster information of a given name or whole table and return a dict.",
            "arguments":
                {
                    "well_name" : "well_name"
                },
            "return": [
                {
                    "id" : "integer",
                    "well_name" : "well_A",
                    "comment": "",
                    "type": "EXPLORATION",
                    "field_fk": 1,
                    "formation": "Formation A",
                    "longitude": 123.456,
                    "latitude": -123.456
                }
            ]
        }
        """
        mygeneric = Generic()
        if str_well_name is None:
            dict_get_cases = self.master._getMaster("datasource", "wellmaster")
        else:
            int_well_id = self.master.wellmasterdict[str_well_name]
            dict_get_cases = self.master._getMaster("datasource", "wellmaster", str(int_well_id))
        dict_get_cases = mygeneric.fkChanger(dict_get_cases)
        return dict_get_cases

    def editWellMaster(self, str_well_name: str, dict_edit_master: dict):
        """
        {
            "description":"Function that update a well master record",
            "arguments":{
                "str_well_name" : "well_name",
                "dict_main" : {
                    "well_name": "well_name",
                    "spud_date": "YYYY-MM-DD",
                    "production_date": "YYYY-MM-DD",
                    "api_code": 12345,
                    "latitude": 12345.67,
                    "longitude": 76543.21,
                    "utm_x": 123.45,
                    "utm_y": 123.45,
                    "comment": "",
                    "type": "Producer",
                    "field": "str_field"
                }
            },
            "return":
                {
                    "id" : "integer",
                    "well_name" : "well_A",
                    "comment": "",
                    "type": "EXPLORATION",
                    "field": "Field A",
                    "formation": "Formation A",
                    "longitude": 123.456,
                    "latitude": -123.456
                }
            
        }
        """
        if (str_well_name in None) or (dict_edit_master is None):
            print(f"Please review the arguments.")
        else:
            int_well_id = self.master.wellmasterdict[str_well_name]
            dict_edit_master = self.master._editMaster("datasource", "wellmaster", dict_edit_master,  str(int_well_id))
            return dict_edit_master

    def deleteWellMaster(self, str_well_name:str):
        """
        {
            "description":"Function that delete the master that match with the master_fk",
            "arguments":{
                "well_name" : "Well_A"
            },
            "return": "StatusCode"
        }
        """
        if str_well_name is None:
            print(f"Well name missing.")
        else:
            int_well_id = self.master.wellmasterdict[str_well_name]
            deleted_master = self.master._deleteMaster("datasource", "wellmaster", str(int_well_id))
            return deleted_master

    def createFormationMaster(self, formation_master_dict: dict):
        """
        {
            "description": "Function that create a Formation in the database",
            "arguments" : {
                "dict_main":{
                    "formation_name": "Formation A",
                    "comment": ""
                }
            },
            "return":{
                "formation_name": "Formation A",
                "comment": ""
            }
        }
        """
        dict_wellmaster = self.master._createMaster("datasource", "formationmaster", formation_master_dict)
        return dict_wellmaster

    def getFormationMaster(self, str_formation_name=None):
        """
        {
            "description":"Function that fetch formation information of a given name or whole table and return a dict.",
            "arguments":{
                "str_formation_name" : "Formation_A"
            },
            "return": [
                {
                    "formation_name": "Formation A",
                    "comment": ""
                }
            ]
        }
        """
        if str_formation_name is None:
            dict_get_cases = self.master._getMaster("datasource", "formationmaster")
        else:
            int_formation_id = self.master.formationmasterdict[str_formation_name]
            dict_get_cases = self.master._getMaster("datasource", "formationmaster", str(int_formation_id))
        return dict_get_cases

    def editFormationMaster(self, str_formation_name: str, dict_formation_master: dict):
        """
        {
            "description":"Function that updates a formation master record",
            "arguments":{
                "str_formation_name" : "Formation_A",
                "dict_main":{
                    "formation_name":"Formation_A",
                    "comment":""
                }
            },
            "return":{
                "formation_name": "Formation A",
                "comment": ""
            }
        }
        """
        if (str_formation_name is None) or (dict_formation_master is None):
            print(f"Please review the arguments.")
        else:
            int_formation_id = self.master.formationmasterdict[str_formation_name]
            dict_edit_master = self.master._editMaster("datasource", "formationmaster", dict_formation_master,  str(int_formation_id))
            return dict_edit_master

    def deleteFormationMaster(self, str_formation_name:str):
        """
        {
			"description":"Function that delete the master that match with the master_fk",
			"arguments":{
                "str_formation_name": "Formation_A" 
            },
			"return": "StatusCode"
        }
        """
        if str_formation_name is None:
            print(f"Please review the arguments.")
        else:
            int_formation_id = self.master.fieldmasterdict[str_formation_name]
            deleted_master = self.master._deleteMaster("datasource", "formationmaster", str(int_formation_id))
            return deleted_master

    def createFieldMaster(self, field_master_dict: dict):
        """
        {
            "description": "Function that create Fields",
            "arguments" : {
                "field_name": "Field_A",
                "comment": "Comment",
                "Country": "Mexico",
                "Basin":"Basin_A",
                "Block":"Block_A"
                },
            "return":{
                "field_name": "Field_A",
                "comment": "Comment",
                "Country": "Country_A",
                "Basin":"Basin_A",
                "Block":"Block_A"
            }
        }
        """
        response_api = self.master._createMaster("datasource", "fieldmaster", field_master_dict)
        return response_api

    def getFieldMaster(self, str_field_name=None):
        """
        {
            "description": "Function that fetch field information of a given name or whole table and return a dict.",
            "arguments":{
                    "str_field_name" : "Field_A"
            },
            "return":[
                {
                    "field_name": "Field_A",
                    "comment": "Comment"
                }
            ]
        }
        """
        if str_field_name is None:
            dict_get_cases = self.master._getMaster("datasource", "fieldmaster")
        else:
            int_field_id = self.master.fieldmasterdict[str_field_name]
            dict_get_cases = self.master._getMaster("datasource", "fieldmaster", str(int_field_id))
        return dict_get_cases

    def editFieldMaster(self, str_field_name: str, dict_field_master: dict):
        """
        {
			"description":"Function that update a field master record",
			"arguments":{
                "str_field_name" : "Field_A", 
                "dict_main": {
                    "field_name": "Field_B",
                    "comment": "Comment",
                    "Country": "Country_B",
                    "Basin": "Basin_B",
                    "Block": "Block_B"
                }
            },
			"return": {
                "field_name": "Field_B",
                "comment": "Comment",
                "Country": "Country_B",
                "Basin": "Basin_B",
                "Block": "Block_B"
            }
        }
        """
        dict_edit_master = self.master._editMaster("datasource", "fieldmaster", dict_field_master,  str(master_fk))
        return dict_edit_master

    def deleteFieldMaster(self, str_field_name:str):
        """
        {
            "description": "Function that deletes a Field",
            "arguments" : {
                "str_field_name": "Field_A"
                },
            "return": "StatusCode"
        }
        """
        if str_field_name is None:
            print(f"Review arguments")
        else:
            int_field_id = self.master.fieldmasterdict[str_field_name]
            deleted_master = self.master._deleteMaster("datasource", "fieldmaster", str(int_field_id))
        return deleted_master

    def getFieldWellsDict(self):
        """
        {
            "description":"Preloaded dictionary of fields and its wells",
            "arguments":{
            },
            "return":{
                "Field_A":[
                    "Well A"
                ]
            }
        }
        """
        field_wells_dict = {}
        for field in list(self.master.fieldmasterdict.keys()):
            field_wells_dict[field] = self.master._getKeysDictList(field, self.getWellFieldDict())
        return field_wells_dict

    def getWellFieldDict(self):
        """
        {
            "description":"Preloaded dictionary of well names and its field",
            "arguments":{
            },
            "return":{
                "Well A" : "Field_A",
                "Well B" : "Field_B"
            }
        }
        """
        results = {}
        for welldict in self.master.wellmasterdict_full:
            results[welldict['well_name']] = self.master.fieldmasterdict_inv[welldict['field_fk']]
        return results
        
    def getWellDeviation(self,str_well_name = None):
        """
        {
            "description": "Function that fetch the well deviation data of a given well name",
            "arguments":{
                "str_well_name":"Well_A"
            },
            "return":[
                {
                    "id": 1,
                    "md": 0.0,
                    "tvd": 0.0,
                    "dispNs": 0.0,
                    "dispEw": 0.0
                }
            ]
        }
        """
        if str_well_name == None:
            print("Missing well name")
        else : 
            dict_welldeviations = self.master._getMaster("datasource", "welldeviation")
            df = pd.DataFrame(dict_welldeviations)
            int_well_id = self.master.wellmasterdict[str_well_name]
            df_final = df[df["well_fk"] == int_well_id]
            return df_final.to_dict(orient="records")
        
        def getWellIntervention(self,str_well_name = None):
            """
            {
                "description":" Function that fetch the well intervention data of a given well name",
                "arguments":{
                    "str_well_name":"Well_A"
                },
                "return":[
                    {
                        "id": 1,
                        "description": "description",
                        "intervention_type": "intervention type",
                        "purpose": "purpose"
                    }
                ]
            }
            """
            if str_well_name == None:
                print("Missing well name")
            else : 
                dict_wellinterventions = self.master._getMaster("datasource", "wellinterventions")
                df = pd.DataFrame(dict_wellinterventions)
                int_well_id = self.master.wellmasterdict[str_well_name]
                df_final = df[df["well_fk"] == int_well_id]
                return df_final.to_dict(orient="records")
            
    def getWellPressure(self,str_well_name = None):
        """
        {
            "description":"Function that fetch the well pressure data of a given well name",
            "arguments":{
                "str_well_name":"Well A"
            },
            "return":{
                "list_response":[
                    {
                    "id":1,
                    "pressure_depth": 12345.5,
                    "description":"description"
                    }
                ]
            }
        }
        """
        if str_well_name == None:
            print("Missing well name")
        else : 
            dict_welldeviations = self.master._getMaster("datasource", "wellpressure")
            df = pd.DataFrame(dict_welldeviations)
            int_well_id = self.master.wellmasterdict[str_well_name]
            df_final = df[df["well_fk"] == int_well_id]
            return df_final.to_dict(orient="records")
        
    def getWellStatus(self,str_well_name = None):
        """
        {
            "description":"Function that fetch the well status data of a given well name and if empty wellname all database",
            "arguments":{
                "str_well_name":"Well A"
            },
            "return":{
                "list_response":[
                    {
                    "id":1,
                    "status" : "Producing",
                    "reason" : "Producing reason",
                    "als": "ESP"                    
                    }
                ]
            }
        }
        """
        mygeneric = Generic()
        if str_well_name == None:
            dict_wellstatus = self.master._getMaster("datasource", "wellstatus")
            #return dict_wellstatus
        else : 
            dict_wellstatus = self.master._getMaster("datasource", "wellstatus")
            df = pd.DataFrame(dict_wellstatus)
            int_well_id = self.master.wellmasterdict[str_well_name]
            df_final = df[df["well_fk"] == int_well_id]
            dict_wellstatus = df_final.to_dict(orient="records")
            #return df_final.to_dict(orient="records")
        dict_final = mygeneric.fkChanger(dict_wellstatus)
        return dict_final
        
    def getWellCompletion(self,str_well_name = None):
        """
        {
            "description":"Function that fetch the well completion data of a given well name",
            "arguments":{
                "str_well_name":"Well A"
            },
            "return":{
                "list_response":[
                    {
                    "id":1,
                    "status" : "Producing",
                    "reason" : "Producing reason",
                    "als": "ESP"                    
                    }
                ]
            }
        }
        """
        mygeneric = Generic()
        if str_well_name == None:
            dict_wellstatus = self.master._getMaster("datasource", "wellcompletion")
            #return dict_wellstatus
        else : 
            dict_wellcompletion = self.master._getMaster("datasource", "wellcompletion")
            df = pd.DataFrame(dict_wellcompletion)
            int_well_id = self.master.wellmasterdict[str_well_name]
            df_final = df[df["well_fk"] == int_well_id]
            dict_wellstatus = df_final.to_dict(orient="records")
            #return df_final.to_dict(orient="records")
        dict_final = mygeneric.fkChanger(dict_wellstatus)
        return dict_final 

    def getMonthlyProduction(self, str_well_name: str):
        """
        {
            "description": "Function that fetch monthly production profile of a given well name",
            "arguments": "well_name",
            "return": [{
                "id": 1,
                "oil_rate": 12345.6,
                "gas_rate": 65432.1,
                "wat_rate": 12345.6,
                "oil_cum": 654321.0
            }],
            "example": "getMonthlyProduction('Well X')"
        }
        """
        mygeneric = Generic()
        int_well_id = self.master.wellmasterdict[str_well_name]
        monthly_volume = self.master._getCase("datasource", "wellmonthly", "well_fk", int_well_id)
        dict_final = mygeneric.fkChanger(monthly_volume["data"])
        return dict_final
    
    def getDailyProduction(self,str_well_name: str):
        """
        {
            "description": "Function that fetch daily production profile of a given well name",
            "arguments":{
                "str_well_name" : "Well A"
            },
            "return":[
                {
                    "id":1,
                    "oil_rate": 12345.6,
                    "gas_rate": 65432.1,
                    "wat_rate": 12345.6,
                    "oil_cum": 654321.0
                }
            ]            
        }
        """
        int_well_id = self.master.wellmasterdict[str_well_name]
        daily_volume = self.master._getCase("datasource", "welldaily", "well_fk", int_well_id)
        return daily_volume
    
    def getFieldMonthlyProduction(self,str_field_name: str):
        """
        {
            "description":"Function that fetch field monthly production profile of a given field name",
            "arguments":{
                "str_field_name" : "Field A"
            },
            "return":[
                {
                    "id":1,
                    "oil_rate": 12345.6,
                    "gas_rate": 65432.1,
                    "wat_rate": 12345.6,
                    "oil_cum": 654321.0
                }
            ]
        }
        """
        monthly_volume = self.master._getCase("datasource","fieldmonthly","fields[]", str_field_name)
        return monthly_volume
        
    def importDataSource(self, tablename, df_table, is_new_data=False):
        """
        {
            "description": "Function that uploads a csv with data",
            "arguments" : {
                "dict_main" : {
                    "tablename": "wellmaster",
                    "df_table": "df_table",
                    "is_new_date": "True"
                }
            },
            "return":{
                "keys":"items"
            }
        }
        """
        #test_file = open("/Users/alejandroprimeranavarro/Alana/jupyter_samples/DCA_Summary_sampledata.csv", "rb")
        df_table.to_csv("importDataSource_temp.csv", index=False)
        file = open("importDataSource_temp.csv", "rb")
        url = self.master.root_url +"/api/datasource/dataloader/import/"
        header = {'Authorization': 'Token ' + self.master.credentials["alana_token"]}
        data = {
            #"file_uploaded": file,
            "tablename": tablename,
            "is_new_data": is_new_data
        }
        print("uploaded:", {"file_uploaded": file})
        mydata = requests.post(url, headers=header, files={"file_uploaded": file}, data=data)
        print(mydata)
        file.close()
        os.remove("importDataSource_temp.csv")
        return mydata.json()

class Generic:
    def __init__(self):
        self.master = Singleton().master
        
    def lists_have_same_length(self, *lists):
        lengths = [len(lst) for lst in lists]
        return all(length == lengths[0] for length in lengths)
    
    def filterProductionData(self, dates, rates, months, delete_zeros):
        if len(rates) > months:
            dates = dates[-months:]
            rates = rates[-months:]
        if delete_zeros == 'YES':
            zero_indices = np.where(np.array(rates) != 0.0)
            dates = list(np.array(dates)[list(zero_indices[0])])
            rates = list(np.array(rates)[list(zero_indices[0])])
        return dates, rates
    
    def statusCodeCheck(self,response):
        status_messages = {
            100: "Continue",
            101: "Switching Protocols",
            102: "Processing",
            103: "Early Hints",
            200: "OK",
            201: "Created",
            202: "Accepted",
            203: "Non-Authoritative Information",
            204: "No Content",
            205: "Reset Content",
            206: "Partial Content",
            207: "Multi-Status",
            208: "Already Reported",
            226: "IM Used",
            300: "Multiple Choices",
            301: "Moved Permanently",
            302: "Found",
            303: "See Other",
            304: "Not Modified",
            305: "Use Proxy",
            307: "Temporary Redirect",
            308: "Permanent Redirect",
            400: "Bad Request",
            401: "Unauthorized",
            402: "Payment Required",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            406: "Not Acceptable",
            407: "Proxy Authentication Required",
            408: "Request Timeout",
            409: "Conflict",
            410: "Gone",
            411: "Length Required",
            412: "Precondition Failed",
            413: "Payload Too Large",
            414: "URI Too Long",
            415: "Unsupported Media Type",
            416: "Range Not Satisfiable",
            417: "Expectation Failed",
            418: "I'm a Teapot",
            421: "Misdirected Request",
            422: "Unprocessable Entity",
            423: "Locked",
            424: "Failed Dependency",
            425: "Too Early",
            426: "Upgrade Required",
            428: "Precondition Required",
            429: "Too Many Requests",
            431: "Request Header Fields Too Large",
            451: "Unavailable For Legal Reasons",
            500: "Internal Server Error",
            501: "Not Implemented",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout",
            505: "HTTP Version Not Supported",
            506: "Variant Also Negotiates",
            507: "Insufficient Storage",
            508: "Loop Detected",
            510: "Not Extended",
            511: "Network Authentication Required"
            # Add more status codes and messages as needed
        }
        print(f"Status : {response.status_code}, {status_messages[response.status_code]}\n")
        if (response.status_code >= 200) and (response.status_code < 300):
            return True
        else:
            return False

    def getKeyDict(self, val, dict_selected):
        """
        Function that obtains the key of a given dictionary based on the value
        args(str_value,dict_selected)

        Returns: str
        """
        for key, value in dict_selected.items():
            if val == value:
                return key
        return "key doesn't exist in dictionary"
        
    def cleanNaNNaT(self,df):
        """
        {
        "description": "Function that cleans NaN and NaT in a given DataFrame",
        "arguments" : { df }
        "example": "myapi.cleanNaNNaT(df)"
        }
        """
        df1 = df.replace(np.nan, None)
        df1.replace({pd.NaT: None},inplace=True)  
        new_dates = []
        for index, row in df1.iterrows():
            if row["start_date"] is None :
                new_dates.append(None)
            else :
                new_dates.append(row["start_date"].strftime('%Y-%m-%d')) 
        df1["start_date"] = new_dates
        new_dates = []
        for index, row in df1.iterrows():
            if row["end_date"] is None :
                new_dates.append(None)
            else :
                new_dates.append(row["end_date"].strftime('%Y-%m-%d')) 
        df1["end_date"] = new_dates
        new_dates = []
        for index, row in df1.iterrows():
            if row["start_production_date"] is None :
                new_dates.append(None)
            else :
                new_dates.append(row["start_production_date"].strftime('%Y-%m-%d')) 
        df1["start_production_date"] = new_dates
        return df1
        
    def fkChanger(self,dict_input):
        """
        Function that replaces and deletes the fk column with its equivalency.
        """
        dict_fks = {
            "well_fk":"well_name",
            "field_fk":"field_name",
            "formation_fk":"formation_name"
        }
        #print(f'dict_input: {dict_input}')
        mydatasource = DatasourceEDA() 
        df_dict = pd.DataFrame(dict_input)
        str_goal = [item for item in list(df_dict.columns) if "_fk" in item][0]
        #print(f'str_goal: {str_goal}')
        if str_goal == "well_fk":
            dict_replace = self.master.ids_wellnames
        elif str_goal == "field_fk":
            dict_replace = self.master.fieldmasterdict_inv
        elif str_goal == "formation_fk":
            dict_replace = mydatasource.invert_dict(self.master.formationmasterdict)
        df_dict[dict_fks[str_goal]] = df_dict[str_goal].replace(dict_replace)
        df_dict.drop(str_goal,axis=1,inplace=True)
        return df_dict.to_dict(orient="records")
    
    
class DCA:
    def __init__(self):
        self.master = Singleton().master
        
    def createDCAMaster(self, dca_master_dict):
        """
        {
            "description": "Function that creates master for DCA Data",
            "arguments" : {
                "dict_main":{
                    "name": "DCA A",
                    "dca_method": "ARPS",
                    "forecast_type": "DET",
                    "primary_fluid_phase": "OIL",
                    "dca_defaults": "False",
                    "dca_scope": "PUBLIC"
                }
            },
            "return":{
                "dict_response":{
                }
            }
        }
        """
        dca_master_dict["name"] = dca_master_dict["str_dca_name"]
        dict_dca_master = self.master._createMaster("dca", "dcamaster", dca_master_dict)
        return dict_dca_master
        
    def runDCA(self, dict_dca):
        """
        {
        "description": "Function that creates a DCA master and then the cases for multiple wells",
        "arguments":
            {
                "str_dca_name": "",
                "list_well_names": ["well 1", "well 2"],
                "date_primary_forecast": ["YYYY-MM-DD", "YYYY-MM-DD"],
                "str_arps": ["HYPE", "HYPE"],
                "str_date_prod": "monthly"
            },
        "example": ""
        }
        """
        mygeneric = Generic()
        list_check = mygeneric.lists_have_same_length(dict_dca["list_well_names"], dict_dca["date_primary_forecast"], dict_dca["str_arps"])
        if not list_check:
            return "All lists provided need to have the same size"
        url = self.master.root_url + "/api/dca/fit_forecast/"
        header = self.master.header
        mydata = requests.get(url, headers=header)
        dca_template_fit_forecast_base = mydata.json()
        wells_nofit = []
        wells_noprod = []
        print("DCA Master")
        dca_master = self.createDCAMaster(dict_dca)
        dcamaster_fk = dca_master['id']
        mydatasource = Datasource()
        list_well_ids = [item["id"] for item in mydatasource.getWellMaster() for well in dict_dca["list_well_names"] if item["well_name"] == well]
        count_time_to_fit = 60
        count_time_to_discard_well_if_zero_rates = 6
        if (dict_dca["str_date_prod"] == "daily") or (dict_dca["str_date_prod"] == "monthly"):
            count_time_to_fit = int(count_time_to_fit * 30.5)
            count_time_to_discard_well_if_zero_rates = int(count_time_to_discard_well_if_zero_rates * 30.5)
        else:
            print("No valid time")
        
        for n, well_fk in enumerate(dict_dca["list_well_names"]):
            if dict_dca["str_date_prod"] == "monthly":
                well_monthly_dict = {}
                well_monthly_dict['data'] = mydatasource.getMonthlyProduction(well_fk)["data"]
                dates = [x['date'] for x in well_monthly_dict['data']]
                dates = [datetime.strptime(x, "%Y-%m-%d") for x in dates]
                rates = [x["oil_rate"] for x in well_monthly_dict['data']]
                dates_or, rates_or = dates, rates
            elif dict_dca["str_date_prod"] == "daily":
                well_daily_dict = {}
                well_daily_dict['data'] = mydatasource.getDailyProduction(well_fk)["data"]
                dates = [x['date'] for x in well_daily_dict['data']]
                dates = [datetime.strptime(x, "%Y-%m-%d") for x in dates]
                rates = [x["oil_rate"] for x in well_daily_dict['data']]
                dates_or, rates_or = dates, rates
            else:
                print("Wrong date frequency")
                break
            dates, rates = mygeneric.filterProductionData(dates_or, rates_or, count_time_to_fit, 'YES')
            # print("rates_or: ", rates_or)
            # print(well_fk, sum(rates[-6:]), " all rates: "  , rates[-6:])
            if len(dates) <= 1:
                ##print(well_fk)
                wells_nofit.append(well_fk)
            elif sum(rates_or[-count_time_to_discard_well_if_zero_rates:]) <= 0:
                wells_noprod.append(well_fk)
            else:
                dca_template_fit_forecast = dca_template_fit_forecast_base
                dca_template_fit_forecast['arps_type'] = dict_dca["str_arps"][n]
                x_selected = [x.strftime('%Y-%m-%d') for x in dates]
                dca_template_fit_forecast['x_selected'] = x_selected
                dca_template_fit_forecast['y_selected'] = rates
                dca_template_fit_forecast['primary_phase_forecast_rate'] = rates_or[-1]
                dca_template_fit_forecast['forecast_months'] = 420.0
                dca_template_fit_forecast['primary_forecast_date'] = dict_dca["date_primary_forecast"][n]
                dca_template_fit_forecast['primary_forecast_last_date'] = x_selected[-1]
                dca_template_fit_forecast['primary_phase_abandonment'] = 0.0
                dca_template_fit_forecast['fit_dates'] = x_selected
                dca_template_fit_forecast['reinitialize_choice'] = 'NO'
                dca_template_fit_forecast['fc_date_choice'] = "DEFAULT"
                dca_template_fit_forecast['fc_rate_choice'] = "LASTVALFIT"
                #print("dca_template_fit_forecast: ",dca_template_fit_forecast)
                dca_forecast = self.master._fitForecastDCA(dates, rates, dca_template_fit_forecast)
                # print("dca_forecast: ",dca_forecast)
                # dca_forecast['primary_phase_forecast_rate'] = rates_or[-1]
                # dca_forecast['arps_type'] = dca_arps
                #print(f"_saveDCA:\n {dcamaster_fk}\n{list_well_ids[n]}\n{dca_forecast}\n{x_selected}\n{rates}\n{dca_template_fit_forecast}")
                self.master._saveDCA(dcamaster_fk, list_well_ids[n], dca_forecast, x_selected, rates, dca_template_fit_forecast)
        #print("Total analyzed wells: ", len(dict_dca["list_well_names"]))#, "\nWells with issues: ",
              #[self.master._getKeyFromDict(well, self.master.wellmasterdict) for well in wells_nofit], "\n Total with issues: ",
              #len(wells_nofit), [self.master._getKeyFromDict(well, self.master.wellmasterdict) for well in wells_noprod],
              #"\n Total with no Production in the last 6 months: ", len(wells_noprod))
        #print(f"Total analyzed wells: {len(dict_dca['list_well_names'])} \nWells with issues: {wells_nofit}")
        print(f"Total analyzed wells:\n{len(dict_dca['list_well_names'])} \nWells with DCA: \n{[x for x in dict_dca['list_well_names'] if x not in wells_nofit]}\nWells with issues: \n{wells_nofit}")

    def editDCAMaster(self, master_fk: int, dict_edit_master: dict):
        dict_edit_master = self.master._editMaster("dca", "dcamaster", dict_edit_master, str(master_fk))
        return dict_edit_master

    def getDCAMaster(self, master_fk: str):
        dict_get_master = self.master._getMaster("dca", "dcamaster", str(master_fk))
        return dict_get_master

    def deleteDCAMaster(self, master_fk: str):
        deleted_master = self.master._deleteMaster("dca", "dcamaster", str(master_fk))
        return deleted_master

    def createDCACases(self, list_of_dicts: list):
        dict_response_api = self.master._createCases(list_of_dicts, "dca", "dcacase")
        return dict_response_api

    def createDCAMasterCases(self, _dict: dict, list_of_dicts: list):
        tuple_response_api = self.master._createMasterCases("dca", "dcamaster", _dict, list_of_dicts, "dca", "dcacase")
        return tuple_response_api
        
class DatasourceEDA:
    def __init__(self):
        self.master = Singleton().master

    def runNearByWells(self, dict_input):
        """
        {
        "description": "Get Nearby wells given a well name and radius around it in metres"
        }
        "arguments" : {
            well_name: "",
            radius: float
            },
        "example": ""
        }
        """

        url = self.master.root_url + "/api/datasource/eda/nearbywells/"
        header = self.master.header
        mydata = requests.get(url, headers=header, params=dict_input)  # .json()
        results = mydata.json()
        return results
    
    def invert_dict(self,input_dict:dict):
        """
        {
        "description": "Function that inverts a dictionary, keys to values and viceversa."
        }
        "arguments" : {
            input_dict: {}
            }
        
        """
        inverted_dict = {value: key for key, value in input_dict.items()}
        return inverted_dict
        


class WellType:
    def __init__(self):
        self.master = Singleton().master

    def createWellType(self, welltype_master_dict):
        """
        {
        "description": "Function that creates master for DCA Data"
        }
        "arguments" : {
            "name": "",
            "dca_method": "ARPS",
            "forecast_type": "DET",
            "primary_fluid_phase": "OIL",
            "dca_defaults": "",
            "dca_scope": "PUBLIC"
            },
        "example": ""
        }

        """
        welltype_master_dict["name"] = welltype_master_dict["str_dca_name"]
        dict_welltype_master = self.master._createMaster("welltype", "welltypemaster", welltype_master_dict)
        return dict_welltype_master
        
    def runWellType(self, dict_welltype):
        """
        {
        "description": "Function that runs a welltype for a list of wells",
        "arguments":
            {
                "well_names[]": ["well 1", "well 2"],
                "date_col_name": "str_date",
                "rate_col_name": "str_col_name",
                "arps_type": "str_arps",
                "fit_type": "str_type",
                "skip_zeros": True,
                "use_daily": False
            },
        "example": "myapi.runWellType(dict_welltype = {
                "well_names[]": ["well 1"],
                "date_col_name": "date",
                "rate_col_name": "oil_rate",
                "arps_type": "HYPE",
                "fit_type": "daily",
                "skip_zeros": True,
                "use_daily": True
            })"
        }
        """
        mygeneric = Generic()
        url = self.master.root_url + "/api/welltype/welltype_calc/"
        dict_welltype = json.dumps(dict_welltype)
        header = {'Authorization': 'Token ' + self.master.credentials["alana_token"],
                  "content-type": "application/json"}
        mydata = requests.get(url, headers=header, data=dict_welltype)  # .json()
        bool_status = mygeneric.statusCodeCheck(mydata)
        if bool_status:
            dict_welltype_results = mydata.json()
            self.master._print(f"dict_welltype_results:{dict_welltype_results}")
            return dict_welltype_results
    
    def editWellTypeMaster(self, master_fk: int, dict_edit_master: dict):
        dict_edit_master = self.master._editMaster("welltype", "welltypemaster", dict_edit_master, str(master_fk))
        return dict_edit_master

    def getWellTypeMaster(self, master_fk: str):
        dict_get_master = self.master._getMaster("welltype", "welltypemaster", str(master_fk))
        return dict_get_master

    def deleteWellTypeMaster(self, master_fk: str):
        deleted_master = self.master._deleteMaster("welltype", "welltypemaster", str(master_fk))
        return deleted_master


class AIML:
    def __init__(self):
        self.master = Singleton().master
        self.datasource = "aiml"
        self.master_name = "aimlmodel"

    def createAIMLModel(self, _dict: dict, download=False):
        """
        {
            "description": "Function that create Wells and returns well's information and status.",
            "arguments": {
                "dict_main": {
                    "well_name": "",
                    "spud_date": "YYYY-MM-DD",
                    "production_date": "YYYY-MM-DD",
                    "api_code": "int",
                    "latitude": "float",
                    "longitude": "float",
                    "utm_x": "float",
                    "utm_y": "float",
                    "comment": "",
                    "type": "",
                    "field": "str_field"
                }
            },
            "return": {
                "well_name": "YPF-1",
                "comment": "",
                "type": "EXPLORATION",
                "field": "Field A",
                "formation": "Formation A",
                "longitude": 123.456,
                "latitude": -123.456
            }
        }
        """
        files = {
            "file": (_dict['file'], open(_dict['file'], mode='rb'))
        }
        results = self.master._createMaster(self.datasource, self.master_name, _dict, files, json_dumps=False)
        return results

    def getAIMLModel(self, str_master_name=None, should_download=False):
        """
        {
            "description":"Function that fetch wellmaster information of a given name or whole table and return a dict.",
            "arguments":
                {
                    "well_name" : "well_name"
                },
            "return": [
                {
                    "id" : "integer",
                    "well_name" : "well_A",
                    "comment": "",
                    "type": "EXPLORATION",
                    "field_fk": 1,
                    "formation": "Formation A",
                    "longitude": 123.456,
                    "latitude": -123.456
                }
            ]
        }
        """
        #mygeneric = Generic()
        if str_master_name is None:
            dict_get_masters = self.master._getMaster(self.datasource, self.master_name, should_download=should_download)
        else:
            dict_get_masters = self.master._getMaster(self.datasource, self.master_name, str_master_name, should_download=should_download)
        return dict_get_masters

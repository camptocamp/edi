from collections import OrderedDict

grammar = OrderedDict(
    {
        "Telheader_Quelle": {
            "type": "str",
            "length": 10,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": "get_source_q",
        },
        "Telheader_Ziel": {
            "type": "str",
            "length": 10,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": "get_destination_q",
        },
        "Telheader_TelSeq": {
            "type": "int",
            "length": 6,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": "get_sequence_number",
        },
        "Telheader_AnlZeit": {
            "type": "datetime",
            "length": 14,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": "get_current_datetime",
        },
        "Satzart": {
            "type": "str",
            "length": 9,
            "dp": False,
            "dict_key": False,
            "df_val": "AUSPQ0051",
            "df_func": False,
        },
        "IvAusp_UrAusId_Mand": {
            "type": "str",
            "length": 3,
            "dp": False,
            "dict_key": "RxAusp_AusId_Mand",
            "df_val": False,
            "df_func": False,
        },
        "IvAusp_UrAusId_AusNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": "RxAusp_AusId_AusNr",
            "df_val": False,
            "df_func": False,
        },
        "IvAusp_UrAusId_HostAusKz": {
            "type": "str",
            "length": 5,
            "dp": False,
            "dict_key": "RxAusp_AusId_HostAusKz",
            "df_val": False,
            "df_func": False,
        },
        "IvAusp_ExtRef": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": "RxAusp_ExtRef",
            "df_val": False,
            "df_func": False,
        },
        "IvAusp_HostPosNr": {
            "type": "int",
            "length": 6,
            "dp": False,
            "dict_key": "RxAusp_HostPosNr",
            "df_val": False,
            "df_func": False,
        },
        "IvAusp_MId_AId_Mand": {
            "type": "str",
            "length": 3,
            "dp": False,
            "dict_key": "RxAusp_MId_AId_Mand",
            "df_val": False,
            "df_func": False,
        },
        "IvAusp_MId_AId_ArtNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": "RxAusp_MId_AId_ArtNr",
            "df_val": False,
            "df_func": False,
        },
        "IvAusp_MId_AId_Var": {
            "type": "str",
            "length": 5,
            "dp": False,
            "dict_key": "RxAusp_MId_AId_Var",
            "df_val": False,
            "df_func": False,
        },
        "IvMatqk_HMATQ_HMatQ": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "IvAusp_LiefMngsWamas_Mng": {
            "type": "int",
            "length": 12,
            "dp": False,
            "dict_key": "BestMng",
            "df_val": False,
            "df_func": False,
        },
        "IvAusp_LiefMngsWamas_Gew": {
            "type": "int",
            "length": 12,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "IvArt_HOSTUNITS_HostEinh": {
            "type": "str",
            "length": 5,
            "dp": False,
            "dict_key": "HostEinheit",
            "df_val": False,
            "df_func": False,
        },
        "IvArt_Bestand_Einheit": {
            "type": "str",
            "length": 5,
            "dp": False,
            "dict_key": "HostEinheit",
            "df_val": False,
            "df_func": False,
        },
        "IvAusp_MId_Charge": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": "RxAusp_MId_Charge",
            "df_val": False,
            "df_func": False,
        },
        "IvAusp_Info": {
            "type": "str",
            "length": 40,
            "dp": False,
            "dict_key": "RxAusp_Info",
            "df_val": False,
            "df_func": False,
        },
        "IvAusp_MId_MHD": {
            "type": "date",
            "length": 8,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "LiefSNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
    }
)

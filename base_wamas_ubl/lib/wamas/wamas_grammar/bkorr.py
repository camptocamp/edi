from collections import OrderedDict

grammar = OrderedDict(
    {
        "Telheader_Quelle": {
            "type": "str",
            "length": 10,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": "get_source",
        },
        "Telheader_Ziel": {
            "type": "str",
            "length": 10,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": "get_destination",
        },
        "Telheader_TelSeq": {
            "type": "int",
            "length": 6,
            "dp": False,
            "df_val": False,
            "df_func": "get_sequence_number",
        },
        "Telheader_AnlZeit": {
            "type": "datetime",
            "length": 14,
            "dp": False,
            "df_val": False,
            "df_func": "get_current_datetime",
        },
        "Satzart": {
            "type": "str",
            "length": 9,
            "dp": False,
            "df_val": "BKORR0051",
            "df_func": False,
        },
        "Hostkorr_HostKorrKz": {
            "type": "str",
            "length": 5,
            "dp": False,
            "dict_key": False,
            "df_val": "HOST",
            "df_func": False,
        },
        "Invba_MId_AId_Mand": {
            "type": "str",
            "length": 3,
            "dp": False,
            "dict_key": False,
            "df_val": "000",
            "df_func": False,
        },
        "Invba_MId_AId_ArtNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Invba_MId_AId_Var": {
            "type": "str",
            "length": 5,
            "dp": False,
            "dict_key": False,
            "df_val": "00000",
            "df_func": False,
        },
        "Invba_MId_SerienNrGrp": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Invba_MId_ResNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Invba_MId_Charge": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Invba_MId_MHD": {
            "type": "date",
            "length": 8,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Invba_MId_WeNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Matqk_HMATQ_HMatQ": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Invba_DiffMngs_Mng": {
            "type": "float",
            "length": 12,
            "dp": 3,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Invba_DiffMngs_Gew": {
            "type": "float",
            "length": 12,
            "dp": 3,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Art_HOSTUNITS_HostEinh": {
            "type": "str",
            "length": 5,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Art_Bestand_Einheit": {
            "type": "str",
            "length": 5,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Invba_BuSchl": {
            "type": "str",
            "length": 10,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Bschl_HostBuschlPlus": {
            "type": "str",
            "length": 10,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Bschl_KOST_KostSte": {
            "type": "str",
            "length": 13,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Invba_InvbaId": {
            "type": "int",
            "length": 7,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Sign": {
            "type": "str",
            "length": 1,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
    }
)

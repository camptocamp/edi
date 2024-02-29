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
            "df_val": "LBABQ0052",
            "df_func": False,
        },
        "Lba_HOSTSTOCK_HostStockKz": {
            "type": "str",
            "length": 5,
            "dp": False,
            "dict_key": False,
            "df_val": "HOST",
            "df_func": False,
        },
        "Lba_LfdNummer": {
            "type": "int",
            "length": 4,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Lba_Mand": {
            "type": "str",
            "length": 3,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Lba_ArtNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Lba_Variante": {
            "type": "str",
            "length": 5,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Lba_HMatQ": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Lba_ResNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Lba_SNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Lba_Charge": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Lba_vonMHD": {
            "type": "date",
            "length": 8,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Lba_bisMHD": {
            "type": "date",
            "length": 8,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Lba_GrpChargeKz": {
            "type": "bool",
            "length": 1,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Lba_GrpWeNrKz": {
            "type": "bool",
            "length": 1,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Lba_GrpResNrKz": {
            "type": "bool",
            "length": 1,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Lba_GrpMHDKz": {
            "type": "bool",
            "length": 1,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Lba_GrpTeIdKz": {
            "type": "bool",
            "length": 1,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Lba_GrpSNrKz": {
            "type": "bool",
            "length": 1,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "Lba_WeNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
    }
)

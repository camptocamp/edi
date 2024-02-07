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
            "ubl_path": False,
            "df_val": False,
            "df_func": "get_sequence_number",
        },
        "Telheader_AnlZeit": {
            "type": "datetime",
            "length": 14,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": "get_current_datetime",
        },
        "Satzart": {
            "type": "str",
            "length": 9,
            "dp": False,
            "ubl_path": False,
            "df_val": "AUSP00054",
            "df_func": False,
        },
        "RxAusp_AusId_Mand": {
            "type": "str",
            "length": 3,
            "dp": False,
            "ubl_path": False,
            "df_val": "000",
            "df_func": False,
        },
        "RxAusp_AusId_AusNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "ubl_path": "DespatchAdvice.cbc:ID",
            "df_val": False,
            "df_func": False,
        },
        "RxAusp_AusId_HostAusKz": {
            "type": "str",
            "length": 5,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": "get_source",
        },
        "RxAusp_ExtRef": {
            "type": "str",
            "length": 20,
            "dp": False,
            "ubl_path": "DespatchAdvice.cac:DespatchLine.%s.cbc:ID",
            "df_val": False,
            "df_func": False,
        },
        "RxAusp_HostPosNr": {
            "type": "int",
            "length": 6,
            "dp": False,
            "ubl_path": "DespatchAdvice.cac:DespatchLine.%s.cac:OrderLineReference.cbc:LineID",
            "df_val": False,
            "df_func": False,
        },
        "RxAusp_MId_AId_Mand": {
            "type": "str",
            "length": 3,
            "dp": False,
            "ubl_path": False,
            "df_val": "000",
            "df_func": False,
        },
        "RxAusp_MId_AId_ArtNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "ubl_path": "DespatchAdvice.cac:DespatchLine.%s.cac:Item."
            "cac:SellersItemIdentification.cbc:ID",
            "df_val": False,
            "df_func": False,
        },
        "RxAusp_MId_AId_Var": {
            "type": "str",
            "length": 5,
            "dp": False,
            "ubl_path": False,
            "df_val": "00000",
            "df_func": False,
        },
        "RxAusp_MId_ResNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": False,
        },
        "Matqgs_Matqg1": {
            "type": "str",
            "length": 20,
            "dp": False,
            "ubl_path": False,
            "df_val": "DISPONIBLE",
            "df_func": False,
        },
        "Matqgs_Matqg2": {
            "type": "str",
            "length": 20,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": False,
        },
        "Matqgs_Matqg3": {
            "type": "str",
            "length": 20,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": False,
        },
        "RxAusp_GrundPreis": {
            "type": "float",
            "length": 14,
            "dp": 6,
            "ubl_path": False,
            "df_val": False,
            "df_func": False,
        },
        "RxAusp_LadenVerPreis": {
            "type": "float",
            "length": 14,
            "dp": 6,
            "ubl_path": False,
            "df_val": False,
            "df_func": False,
        },
        "RxAusp_LadenVerWhrCode": {
            "type": "str",
            "length": 3,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": False,
        },
        "BestMng": {
            "type": "float",
            "length": 12,
            "dp": 3,
            "ubl_path": "DespatchAdvice.cac:DespatchLine.%s."
            "cbc:DeliveredQuantity.#text",
            "df_val": False,
            "df_func": False,
        },
        "HostEinheit": {
            "type": "str",
            "length": 5,
            "dp": False,
            "ubl_path": "DespatchAdvice.cac:DespatchLine.%s."
            "cbc:DeliveredQuantity.@unitCode",
            "df_val": False,
            "df_func": False,
        },
        "RxAusp_WeiterPreis": {
            "type": "float",
            "length": 14,
            "dp": 6,
            "ubl_path": False,
            "df_val": False,
            "df_func": False,
        },
        "RxAusp_WeiterWhrCode": {
            "type": "str",
            "length": 3,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": False,
        },
        "RxAusp_AktionWpKz": {
            "type": "bool",
            "length": 1,
            "dp": False,
            "ubl_path": False,
            "df_val": "N",
            "df_func": False,
        },
        "RxAusp_AktionLvpKz": {
            "type": "bool",
            "length": 1,
            "dp": False,
            "ubl_path": False,
            "df_val": "N",
            "df_func": False,
        },
        "RxAusp_AktionNr": {
            "type": "str",
            "length": 10,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": False,
        },
        "RxAusp_VorVerNr": {
            "type": "str",
            "length": 10,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": False,
        },
        "RxAusp_Info": {
            "type": "str",
            "length": 40,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": False,
        },
        "RxAusp_HostBatch": {
            "type": "bool",
            "length": 1,
            "dp": False,
            "ubl_path": False,
            "df_val": "N",
            "df_func": False,
        },
        "RxAusp_BatchLagRf": {
            "type": "str",
            "length": 15,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": False,
        },
        "RxAusp_MId_SerienNrGrp": {
            "type": "str",
            "length": 20,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": False,
        },
        "RxAusp_MId_Charge": {
            "type": "str",
            "length": 20,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": False,
        },
        "RxAusp_RestHaltTaWa": {
            "type": "int",
            "length": 4,
            "dp": False,
            "ubl_path": False,
            "df_val": 0,
            "df_func": False,
        },
        "RxAusp_AscFifo": {
            "type": "bool",
            "length": 1,
            "dp": False,
            "ubl_path": False,
            "df_val": "N",
            "df_func": False,
        },
        "RxAusp_WATeSplittId": {
            "type": "str",
            "length": 10,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": False,
        },
    }
)

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
            "df_val": "WEAP00045",
            "df_func": False,
        },
        "RxWeap_WeaId_Mand": {
            "type": "str",
            "length": 3,
            "dp": False,
            "ubl_path": False,
            "df_val": "000",
            "df_func": False,
        },
        "RxWeap_WeaId_WeaNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "ubl_path": "DespatchAdvice.cbc:ID",
            "df_val": False,
            "df_func": False,
        },
        "RxWeap_WeaId_HostWeaKz": {
            "type": "str",
            "length": 5,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": "get_source",
        },
        "RxWeap_ExtRef": {
            "type": "str",
            "length": 20,
            "dp": False,
            "ubl_path": "DespatchAdvice.cac:OrderReference.cbc:ID",
            "df_val": False,
            "df_func": False,
        },
        "RxWeap_HostPosNr": {
            "type": "int",
            "length": 6,
            "dp": False,
            "ubl_path": "DespatchAdvice.cac:DespatchLine.%s.cbc:ID",
            "df_val": False,
            "df_func": "get_sequence_number",
        },
        "RxWeap_MId_AId_Mand": {
            "type": "str",
            "length": 3,
            "dp": False,
            "ubl_path": False,
            "df_val": "000",
            "df_func": False,
        },
        "RxWeap_MId_AId_ArtNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "ubl_path": "DespatchAdvice.cac:DespatchLine.%s.cac:Item."
            "cac:BuyersItemIdentification.cbc:ID",
            "df_val": False,
            "df_func": False,
        },
        "RxWeap_MId_AId_Var": {
            "type": "str",
            "length": 5,
            "dp": False,
            "ubl_path": False,
            "df_val": "00000",
            "df_func": False,
        },
        "RxWeap_MId_Charge": {
            "type": "str",
            "length": 20,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": False,
        },
        "RxWeap_MId_MHD": {
            "type": "date",
            "length": 8,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": False,
        },
        "RxWeap_MId_ResNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": False,
        },
        "RxWeap_MId_ThmKz": {
            "type": "bool",
            "length": 1,
            "dp": False,
            "ubl_path": False,
            "df_val": "N",
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
        "RxWeap_WeaPosTyp": {
            "type": "str",
            "length": 7,
            "dp": False,
            "ubl_path": False,
            "df_val": "NORMAL",
            "df_func": False,
        },
        "RxWeap_AvLiefTerm": {
            "type": "datetime",
            "length": 14,
            "dp": False,
            "ubl_path": "DespatchAdvice.cac:Shipment.cac:Delivery."
            "cac:EstimatedDeliveryPeriod.cbc:EndDate",
            "df_val": False,
            "df_func": False,
        },
        "RxWeap_AvLiefSNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": False,
        },
        "RxWeap_AvLiefSDatum": {
            "type": "datetime",
            "length": 14,
            "dp": False,
            "ubl_path": [
                "DespatchAdvice.cac:Shipment.cac:Delivery."
                "cac:EstimatedDeliveryPeriod.cbc:EndDate",
                "DespatchAdvice.cac:Shipment.cac:Delivery."
                "cac:EstimatedDeliveryPeriod.cbc:EndTime",
            ],
            "df_val": False,
            "df_func": False,
        },
        "RxWeap_LiefArtNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "ubl_path": "DespatchAdvice.cac:DespatchLine.%s."
            "cac:Item.cac:SellersItemIdentification.cbc:ID",
            "df_val": False,
            "df_func": False,
        },
        "RxWeap_SatzKzWeap": {
            "type": "str",
            "length": 1,
            "dp": False,
            "ubl_path": False,
            "df_val": "N",
            "df_func": False,
        },
        "RxWeap_PosEnde": {
            "type": "bool",
            "length": 1,
            "dp": False,
            "ubl_path": False,
            "df_val": "N",
            "df_func": False,
        },
        "RxWeap_RetTorKz": {
            "type": "str",
            "length": 3,
            "dp": False,
            "ubl_path": False,
            "df_val": "LG",
            "df_func": False,
        },
        "RxWeap_MId_SerienNrGrp": {
            "type": "str",
            "length": 20,
            "dp": False,
            "ubl_path": False,
            "df_val": False,
            "df_func": False,
        },
        "RxWeap_Info2Wamas": {
            "type": "str",
            "length": 77,
            "dp": False,
            "ubl_path": "DespatchAdvice.cbc:Note",
            "df_val": False,
            "df_func": False,
        },
    }
)

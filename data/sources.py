from pathlib import Path

from logindata import (
    destatis_login,
    destatis_password,
    regiostat_login,
    regiostat_password,
)


raw_dir = Path(__file__).resolve().parents[1] / "data" / "raw"

destatis_tablefile_url = "https://www-genesis.destatis.de/genesisWS/rest/2020/data/tablefile"
regiostat_url = "https://www-genesis.destatis.de/genesisWS/rest/2020/helloworld/logincheck"

destatis_sources = {
    "ewz" : {
        "name": "12411-0010: Einwohnerzahlen",
        "url": destatis_tablefile_url,
        "target_file": raw_dir / "destatis_12411-0010_Einwohnerzahlen.csv",
        "params": {
            "username": destatis_login,
            "password": destatis_password,
            "name": "12411-0010",
            "area": "all",
            "compress": "false",
            "transpose": "false",
            "startyear": "2009",
            "endyear": "2022",
            # "timeslices": "",
            # "regionalvariable": "",
            # "regionalkey": "",
            # "classifyingvariable1": "",
            # "classifyingkey1": "",
            # "classifyingvariable2": "",
            # "classifyingkey2": "",
            # "classifyingvariable3": "",
            # "classifyingkey3": "",
            # "job ": "false",
            # "stand ": "01.01.1970",
            # "language": "de"
        }
    },
    "geburten": {
        "name": "12612-0100: Geburten",
        "url": destatis_tablefile_url,
        "target_file": raw_dir / "destatis_12612-0100_Geburten.csv",
        "params": {
            "username": destatis_login,
            "password": destatis_password,
            "name": "12612-0100",
            "area": "all",
            "compress": "false",
            "transpose": "false",
            "startyear": "2009",
            "endyear": "2021",
            # "timeslices": "",
            # "regionalvariable": "",
            # "regionalkey": "",
            # "classifyingvariable1": "",
            # "classifyingkey1": "",
            # "classifyingvariable2": "",
            # "classifyingkey2": "",
            # "classifyingvariable3": "",
            # "classifyingkey3": "",
            # "job ": "false",
            # "stand ": "01.01.1970",
            # "language": "de"
        }
    },
    "eg_empfänger": {
        "name": "22922-0025: Elterngeldempfänger",
        "url": destatis_tablefile_url,
        "target_file": raw_dir / "destatis_22922-0025_Elterngeldempfangende.csv",
        "params": {
            "username": destatis_login,
            "password": destatis_password,
            "name": "22922-0025",
            "area": "all",
            "compress": "false",
            "transpose": "false",
            "startyear": "2009",
            "endyear": "2021",
            # "timeslices": "",
            # "regionalvariable": "",
            # "regionalkey": "",
            # "classifyingvariable1": "",
            # "classifyingkey1": "",
            # "classifyingvariable2": "",
            # "classifyingkey2": "",
            # "classifyingvariable3": "",
            # "classifyingkey3": "",
            # "job ": "false",
            # "stand ": "01.01.1970",
            # "language": "de"
        }
    },
    "eg_höhe": {
        "name": "2292-0118: durchschn. Höhe des Elterngelds",
        "url": destatis_tablefile_url,
        "target_file": raw_dir / "destatis_22922-0118_dschn_Höhe_EG.csv",
        "params": {
            "username": destatis_login,
            "password": destatis_password,
            "name": "22922-0118",
            "area": "all",
            "compress": "false",
            "transpose": "false",
            "startyear": "2017",
            "endyear": "2023",
            # "timeslices": "",
            # "regionalvariable": "",
            # "regionalkey": "",
            # "classifyingvariable1": "",
            # "classifyingkey1": "",
            # "classifyingvariable2": "",
            # "classifyingkey2": "",
            # "classifyingvariable3": "",
            # "classifyingkey3": "",
            # "job ": "false",
            # "stand ": "01.01.1970",
            # "language": "de"
        }
    },
    "eg_dauer": {
        "name": "2292-0125: durchschn. Bezugsdauer EG nach Kreisen",
        "url": destatis_tablefile_url,
        "target_file": raw_dir / "destatis_22922-0125_dschn_Dauer_EG.csv",
        "params": {
            "username": destatis_login,
            "password": destatis_password,
            "name": "22922-0125",
            "area": "all",
            "compress": "false",
            "transpose": "false",
            "startyear": "2016",
            # "endyear": "2023",
            # "timeslices": "",
            # "regionalvariable": "",
            # "regionalkey": "",
            # "classifyingvariable1": "",
            # "classifyingkey1": "",
            # "classifyingvariable2": "",
            # "classifyingkey2": "",
            # "classifyingvariable3": "",
            # "classifyingkey3": "",
            # "job ": "false",
            # "stand ": "01.01.1970",
            # "language": "de"
        }
    },
    "steuer": {
        "name": "Regionalstatistik 73111-01-01-4: Steuern",
        "url": regiostat_url,
        "target_file": raw_dir / "regionalstatistik 73111-01-01-4 - Steuern.csv",
        "params": {
            "username": regiostat_login,
            "password": regiostat_password,
            "term": "Abfall",
            "category": "all",
            "compress": "false",
            "transpose": "false",
            "startyear": "2016",
            # "endyear": "2023",
            # "timeslices": "",
            # "regionalvariable": "",
            # "regionalkey": "",
            # "classifyingvariable1": "",
            # "classifyingkey1": "",
            # "classifyingvariable2": "",
            # "classifyingkey2": "",
            # "classifyingvariable3": "",
            # "classifyingkey3": "",
            # "job ": "false",
            # "stand ": "01.01.1970",
            # "language": "de"
        },
    },
}

bkg_source = {
    "url": "https://daten.gdz.bkg.bund.de/produkte/vg/vg250-ew_ebenen_1231/2021/vg250-ew_12-31.utm32s.gpkg.ebenen.zip",
    "target_file": raw_dir / "vg250.zip",
    "extractable": "vg250_ew_ebenen_1231/DE_VG250.gpkg",
}

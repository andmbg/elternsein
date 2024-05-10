import requests
import logging
import chardet

from data.sources import destatis_sources, bkg_source


# set up logger, to be logged with the root logger in __init__.py:
logger = logging.getLogger(__name__)
logger.info("Starting new download run.")

#
# Destatis und Regionalstatistik:
#
for source in destatis_sources.values():
    logger.debug(f"Checking if {source['raw_file']} already exists.")
    if source["raw_file"].exists():
        logger.info("Raw data file already exists. Skipping.")
        next

    else:
        logger.debug(f"Downloading {source['name']}")
        logger.debug(f"Request: {requests.Request('GET', source['url'], params=source['params']).prepare().body}")

        response = requests.get(source["url"], params = source["params"])

        if response.status_code == 200:
            logger.debug("Request successful.")

            content = response.text
            # guess encoding:
            encoding = chardet.detect(response.content)["encoding"]
            logger.debug(f"Encoding of {source['name']} is {encoding}.")
            content_utf8 = response.content.decode(encoding).encode("utf-8")

            with open(source["raw_file"], "wb") as file:
                file.write(content_utf8)

            logger.debug(f"Wrote {len(content_utf8)} bytes to {source['raw_file']}.")

        else:
            logger.error("Request was unsuccessful. Wrong URL?")

#
# BKG (Geodaten):
#
if bkg_source["raw_file"].exists():
    logger.info(f"Raw data file {bkg_source['raw_file']} already exists. Skipping.")

else:

    response = requests.get(bkg_source["url"])

    if response.status_code == 200:
        logger.debug("Request successful.")

        content = response.content

        with open(bkg_source["raw_file"], "wb") as file:
            file.write(content)
        
        logger.debug(f"Wrote {len(content)} bytes to {bkg_source['raw_file']}.")

    else:
        logger.error("Request was unsuccessful. Wrong URL?")

import argparse
import logging
import subprocess
from pprint import pprint

import requests


class Vimeo:
    def __init__(
            self,
            video_id: str
    ):
        self.id = video_id

    @staticmethod
    def _request_jwt() -> str:
        logging.info("Requesting JWT...")

        jwt_api = 'https://vimeo.com/_rv/jwt'
        jwt_api_response = requests.post(
            url=jwt_api,
            headers={
                'X-Requested-With': 'XMLHttpRequest',
            }
        )

        assert (status := jwt_api_response.status_code) == 200, f"JWT API returned status code {status}"
        return jwt_api_response.json().get('token')

    def _request_config(
            self,
            token: str
    ) -> str:
        logging.info("Requesting config...")

        video_api = 'https://api.vimeo.com/videos/' + args.id
        video_api_response = requests.get(
            url=video_api,
            headers={
                'Authorization': 'jwt ' + token,
                'Accept': 'application/json',
            },
            params={
                'fields': 'config_url',
            }
        )

        assert (status := video_api_response.status_code) == 200, f"Video API returned status code {status}"
        return video_api_response.json().get('config_url')

    @staticmethod
    def _request_cdn(
            config_url: str
    ) -> str:
        logging.info("Requesting CDNs...")

        config_api_response = requests.get(
            url=config_url
        )

        assert (status := config_api_response.status_code) == 200, f"Config API returned status code {status}"

        files = config_api_response.json().get('request').get('files')
        hls_manifest = files.get('hls')
        cdn = hls_manifest.get('cdns').get(hls_manifest.get('default_cdn'))

        return cdn.get('url')

    def get_manifest_url(self):
        token = self._request_jwt()
        config = self._request_config(token)
        return self._request_cdn(config)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="Vimeo API downloader",
        description="Author: github.com/DevLARLEY"
    )
    parser.add_argument("--id", action="store")
    parser.add_argument(
        '--no-download',
        action="store_true",
        default=False,
        help="Don't download the manifest",
        required=False
    )
    args = parser.parse_args()

    logging.basicConfig(format='[%(levelname)s]: %(message)s', level=logging.INFO)

    if not args.id:
        logging.error("No id provided")
        parser.print_help()
        exit(-1)

    vimeo = Vimeo(
        video_id=args.id
    )

    logging.info(f"Manifest URL => {(manifest := vimeo.get_manifest_url())}")

    if not args.no_download:
        try:
            subprocess.run(
                [
                    "N_m3u8DL-RE",
                    manifest,
                    "-M",
                    "format=mkv",
                    "--no-log",
                ],
                shell=False
            )
        except FileNotFoundError:
            logging.error("N_m3u8DL-RE not found")

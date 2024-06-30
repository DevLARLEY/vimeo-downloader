import argparse
import logging

import requests

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", action="store")
    args = parser.parse_args()

    logging.basicConfig(format='[%(levelname)s]: %(message)s', level=logging.INFO)

    if not args.id:
        logging.error('No id provided')
        parser.print_help()
        exit(-1)

    jwt_api = 'https://vimeo.com/_rv/jwt'
    jwt_api_response = requests.post(
        url=jwt_api,
        headers={
            'X-Requested-With': 'XMLHttpRequest',
        }
    )
    assert (status := jwt_api_response.status_code) == 200, f"JWT API returned status code {status}"

    token = jwt_api_response.json().get('token')

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

    config_api = video_api_response.json().get('config_url')
    config_api_response = requests.get(
        url=config_api
    )
    assert (status := config_api_response.status_code) == 200, f"Config API returned status code {status}"

    files = config_api_response.json().get('request').get('files')

    manifest = files.get('hls')
    cdn = manifest.get('cdns').get(manifest.get('default_cdn'))

    logging.info(f'HLS Manifest URL => {cdn.get('url')}')

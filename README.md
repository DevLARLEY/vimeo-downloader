# vimeo-downloader
Creates an HLS(m3u8) Manifest from a vimeo video in the specified output path. HLS Manifests can be viewed using VLC and downloaded using N_m3u8DL-RE.

# vimeo_json.py
> [!IMPORTANT]  
> The input URL is not the video URL but rather the 'playlist.json'/'master.json' URL found in the Network Tab.

```
usage: vimeo_json.py [-h] [--url URL] [--output OUTPUT] [--no-download]

options:
  -h, --help       show this help message and exit
  --url URL
  --output OUTPUT
  --no-download    Don't download the manifest
```
> [!NOTE]  
> Downloading requires N_m3u8DL-RE and ffmpeg

# vimeo_api.py
> [!NOTE]  
> Input the video ID (e.g. 676247342) from the video URL.

> [!IMPORTANT]  
> Does not work on embedded videos.

```
usage: vimeo_api.py [-h] [--id ID]

options:
  -h, --help  show this help message and exit
  --id ID
```

# vimeo-downloader
Creates an HLS(m3u8) Manifest from a vimeo video in the specified output path. HLS Manifests can be viewed using VLC and downloaded using N_m3u8DL-RE.

# vimeo_json.py
> [!IMPORTANT]  
> The input URL is not the video URL but rather the 'playlist.json'/'master.json' URL found in the network tab.

```
usage: vimeo_json.py [-h] [--url URL] [--output OUTPUT]

options:
  -h, --help       show this help message and exit
  --url URL
  --output OUTPUT
```
Will output an HLS manifest file that can be played/converted locally.

# vimeo_api.py
> [!IMPORTANT]  
> Input the video ID (e.g. 676247342) from the video URL.

```
usage: test.py [-h] [--id ID]

options:
  -h, --help  show this help message and exit
  --id ID
```
Will output an HLS manifest file that can be played/converted online as its segments are relative to the URL.
For VLC: Media -> Open Network Stream... 

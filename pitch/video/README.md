# Captioned demo video (silent fallback)

`pitch/submission/NABD-demo-captioned.mp4`: 2 min 58 s, 1920×1080, 30 fps, burned-in captions that follow the v4 voiceover in `pitch/story.md`. It has a silent audio track, so it can be uploaded as it is, or a voiceover can be laid over it without re-encoding:

```bash
ffmpeg -i pitch/submission/NABD-demo-captioned.mp4 -i voiceover.m4a -map 0:v -map 1:a -c:v copy -c:a aac -shortest NABD-demo-voiced.mp4
```

Rebuild (needs the web page served locally, Playwright and Chrome):
```bash
python -m web.build && python -m http.server 8600 --directory web/dist &
cd pitch/video && mkdir -p shots frames seg && python capture.py && python endcard.py && python captions.py
# then encode each frame in frames/meta.json as a held still and join them (see the commit that added this folder)
```
Every number on screen comes from the live page, which is generated from `results/`.

# The Holy Quran — Local Qari Audio Test

## Your data path
The app is configured for:

D:\Web & AI\The Holy Quran App\QuranDownload

It automatically scans the Qari folders inside that directory.

## Current test
The page opens Chapter `001` by default and automatically finds every Qari folder that contains that chapter.

Your screenshot appears to show 19 Qari folders currently; the app does not hard-code the number. If 21 folders are present, it will use all 21.

## Run
1. Keep `server.py`, `index.html`, `app.js`, `style.css`, and `launch.bat` together.
2. Double-click `launch.bat`.
3. Open http://127.0.0.1:8787 in Chrome/Edge.
4. Select a chapter if desired.
5. Choose any Qari and play the chapter audio.

No external package is required. It uses Python's built-in HTTP server.

## Important
If your real folder path differs, edit the ROOT line at the top of `server.py`.

The server only exposes files underneath QuranDownload.

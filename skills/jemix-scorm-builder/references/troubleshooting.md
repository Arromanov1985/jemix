# JEMIX SCORM troubleshooting

## Blank gray preview

Likely cause: JavaScript did not initialize. A common cause is `fetch('lesson-data.json')` inside an LMS iframe.

Fix:
1. Embed the slide array directly in `app.js`.
2. Confirm `index.html` loads `styles.css` and `app.js`.
3. Add an on-screen JavaScript error fallback.
4. Test through a local HTTP server.

## Audio displays 0:00 / 0:00

Check:
1. The HTML audio source is `audio/slideNN.mp3`.
2. The ZIP contains the same exact path with `/`.
3. The file is a real MP3, not WAV with an MP3 extension.
4. The manifest lists the audio file.
5. The LMS is not serving an older cached package.

Signatures:
- MP3: `49 44 33` (`ID3`) or MPEG frame sync beginning with `FF`.
- WAV: `52 49 46 46` (`RIFF`) and `57 41 56 45` (`WAVE`).

## Broken images

Use identical paths in slide data and ZIP entries, for example `images/v2_08_case.png`.

Reject accidental paths such as:
- `content/images/images/...`
- `content/images/...`
- root-only filenames when the app requests `images/...`

## LMS reports missing files

Verify the files exist under the exact paths listed in `imsmanifest.xml`. Confirm the ZIP entry names rather than trusting the manifest alone.

## Screen-count mismatch

For approved lesson 1.1:
- 20 slide objects;
- 20 navigation items;
- progress out of 20;
- 20 MP3 files.

Reject the old 12-screen package for this workflow.

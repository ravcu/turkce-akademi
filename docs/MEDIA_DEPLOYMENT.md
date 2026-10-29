# Separate page and media delivery

The GitHub Pages site contains HTML, JavaScript and JSON. Binary images, audio,
video and fonts remain in this repository and are requested through
`raw.githubusercontent.com/ravcu/turkce-akademi/main/`.

`_config.yml` excludes media extensions from the default Jekyll/Pages build.
Do not add `.nojekyll`: this deployment uses Jekyll's exclusion rules.

`assets/js/media-loader.js` resolves existing local media addresses without
changing page navigation or dictionary/manifest JSON requests. This includes
dynamic images, `new Audio(...)`, media fetched as bytes, and generated thumbnails.
Static image addresses are prepared directly in HTML to avoid initial missing
image requests. The site URL and individual reader URLs stay the same.

## Adding or changing media

Upload the media to its existing repository folder. The media address follows
the main branch; GitHub's raw-content cache may take time to refresh. No media
copy is added to the Pages artifact. A Pages rebuild still checks out the
repository, so the checkout can remain slower than uploading the small artifact.

## Adding or regenerating a reader

Run `python tools/prepare-media-pages.py` after generating HTML. Check with
`python tools/prepare-media-pages.py --check`. It is safe to run repeatedly.
Commit the updated HTML together with any reader changes.

## Verification and rollback

Confirm the Pages artifact is below 1 GB, images render, dictionary JSON loads,
and audio playback/seek works. Media requests should go to raw.githubusercontent.com;
HTML and JSON requests should stay on the Pages site.

If rolling back, revert the HTML, media loader, and `_config.yml` in one commit.
Do not remove only the media loader while keeping media excluded.

The raw-file host is GitHub, not a dedicated media CDN. For higher traffic the
same resolver can be adapted to a separate media host after files are copied
and all paths are verified there.

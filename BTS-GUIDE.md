# Adding reels to the BTS page

The BTS ("Behind the Scenes") page shows Instagram reels listed in a Google Sheet. Once the sheet is connected (one-time setup, below), the owner only ever edits the sheet.

## Adding a reel (the owner, any time)

1. Open the reels sheet.
2. On the next empty row, paste the reel's link into the **url** column. (In Instagram: open the reel, tap the share arrow, then **Copy link**.)
3. Optionally type a short **caption** in the next column.
4. That's it. The page picks the change up within a few minutes. New reels go at the bottom of the sheet and appear first on the page.

Only **public** reels can be shown. To hide a reel, delete its row.

Optional third column, **thumbnail**: a link to a cover image (it must start with `https://`). Without it the reel shows a dark card with a play button.

## One-time setup

1. Create a Google Sheet with these headings in row 1: `url`, `caption`, `thumbnail`.
2. Add a few reel links underneath.
3. **File → Share → Publish to web.** Under "Link", choose the sheet tab and **Comma-separated values (.csv)**, then press **Publish** and copy the link. It looks like `https://docs.google.com/spreadsheets/d/e/.../pub?output=csv`.
4. In `build_pages.py` (or directly in `bts.html`), put that link in `BTS_SHEET_URL` / the `data-sheet` attribute on `#reel-grid`, then publish the site.

Publishing to the web shares the sheet's contents publicly, so keep only reel links and captions in it.

## If reels do not appear

- The page shows "New reels are on the way" when the sheet is empty, unreachable, or has no valid Instagram links.
- Links must look like `https://www.instagram.com/reel/XXXXXXXX/` (links from `/p/` posts work too).
- Browsers or extensions that block Instagram will block the player; each card also has a "Watch on Instagram" link.

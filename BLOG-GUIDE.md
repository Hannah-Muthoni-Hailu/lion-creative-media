# Writing Insights articles

Articles are written in **Pages CMS**, a simple editor that saves each article into this repository. A GitHub Action then rebuilds the site, the sitemap and `robots.txt` automatically. Nothing else needs doing; a new article is live a minute or two after saving.

## One-time setup (the site owner)
1. Go to https://app.pagescms.org and sign in with GitHub. Install the Pages CMS GitHub app on the `lion-creative-media` repository when asked.
2. For each writer: create a free GitHub account and add them as a collaborator on the repo (Settings > Collaborators). They then sign in to Pages CMS the same way and see the same screen.
3. In the repo, Settings > Actions > General > Workflow permissions: choose **Read and write permissions**. This lets the rebuild commit the finished pages.
4. Open `tools/build_site.py` and set `SITE_URL` (near the top) to the real public address, for example `https://www.lioncreativemedia.co.ke`. Do this again if a custom domain is connected later. It controls canonical links, social-share previews and the sitemap.
5. After the site is live, add it to **Google Search Console** and submit `sitemap.xml`.

## Writing an article
Open Pages CMS > **Insights articles** > **Add an entry**.

| Field | Notes |
| --- | --- |
| Article title | The headline readers see |
| Published | Leave **off** while drafting. Turn **on** to put it on the website |
| Publish date, Category, Author | Date also shows in the list and the sitemap |
| Short summary | Appears under the title and in the Insights list |
| Cover image + description | Upload a photo and describe it (this is the "alt text") |
| Which part to keep | Choose Upper for portraits so faces are not cropped |
| **SEO: focus keyword** | What someone would type into Google, e.g. `wedding photographer Nairobi` |
| **SEO: title** | Max 60 characters; blank = use the article title |
| **SEO: description** | 70 to 160 characters; this is the snippet shown on Google |
| Article | Use Heading 2 / Heading 3 for sub-headings; add a description to every image |

## SEO checks
Every rebuild checks each published article and lists problems as **warnings** in the repo's **Actions** tab (open the latest "Build site" run). They never stop the article going live. They flag: title over 60 characters, missing or badly sized description, missing cover or image descriptions, fewer than 300 words, no sub-headings, and a focus keyword missing from the title, description or first 100 words.

## What is generated for you
Each article gets its own page (`insights-<name>.html`) with a canonical link, social-share tags (WhatsApp, Facebook, X), Google "Article" structured data and a reading time. `sitemap.xml` and `robots.txt` are regenerated on every build.

## Working without the CMS
Articles are plain files in `content/posts/`. To publish from a computer instead: edit or add a `.md` file, run `pip install -r tools/requirements.txt` then `python3 tools/build_site.py`, and commit.

Note: six sample articles in `content/posts/` are saved as drafts (`published: false`). Open them in the CMS, write them up and switch **Published** on, or delete them.

# Website Guide

This guide explains how to test, build, and deploy the DeckSmith website.

## 1. Testing Locally

Since this is a static website (HTML/CSS), you don't need a complex build process.

### Option A: Python (Recommended)
If you have Python installed (which you do for DeckSmith), run this command from the root of the repository:

```bash
python -m http.server -d website
```

Then open your browser to `http://localhost:8000`.

### Option B: VS Code Live Server
1. Open the `website/index.html` file in VS Code.
2. Right-click and select "Open with Live Server" (if you have the extension installed).

## 2. Building

No build step is required! The website is pure HTML and CSS.

*Optional Optimization:*
If you want to minify the CSS for slightly faster load times, you can use an online tool or a CLI like `cssnano`, but it's not strictly necessary for this scale.

## 3. Deploying to GitHub Pages

The easiest way to deploy is using GitHub Actions to publish the `website` folder to the `gh-pages` branch.

### Step 1: Enable GitHub Pages
1. Go to your GitHub repository settings.
2. Navigate to **Pages**.
3. Under **Build and deployment**, select **Source** as **GitHub Actions**.

### Step 2: Create the Workflow
Create a file named `.github/workflows/deploy-site.yml` with the following content:

```yaml
name: Deploy Website

on:
  push:
    branches: ["main"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Pages
        uses: actions/configure-pages@v5
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: 'website'

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### Step 3: Push
Commit and push the workflow file. GitHub Actions will automatically deploy your website to `https://<username>.github.io/decksmith/`.

## SEO Checklist
- [x] Meta Description & Keywords
- [x] Open Graph Tags (Facebook/LinkedIn)
- [x] Twitter Card Tags
- [x] Canonical URLs
- [x] Sitemap (`sitemap.xml`)
- [x] Robots.txt
- [x] JSON-LD Structured Data
- [x] Alt text for images

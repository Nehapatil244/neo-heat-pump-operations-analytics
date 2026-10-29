# GitHub Publishing Guide (beginner, browser only)

You do **not** need to install Git or use the command line. Everything below happens in your web browser. It takes about 20 minutes.

**Before you start:**
- Unzip `neo-heat-pump-operations-analytics.zip` on your computer.
- Open the unzipped folder. You should see `README.md`, `excel`, `dashboard` and the other folders.
- Replace `[Your Name]`, `[GitHub URL]`, `[LinkedIn URL]` and `[Email]` in these files: `README.md`, `RESUME_AND_LINKEDIN.md`, `LICENSE` and the Excel `START HERE` sheet (cell C10). You can open the `.md` files in Notepad or TextEdit.

---

## Part A: publish the repository

### 1. Create a GitHub account (skip this if you have one)
1. Go to **https://github.com/signup**.
2. Enter your email, a password and a professional username (for example `firstname-lastname`). Recruiters will see this name.
3. Verify your email address.

### 2. Create a new repository
1. Once you are logged in, click the **+** in the top-right corner and choose **New repository**.
2. **Repository name:** `neo-heat-pump-operations-analytics`
3. **Description:** `Operations analytics case study: order fulfilment, delivery & installation KPIs, Excel + Streamlit dashboard (simulated data)`
4. Choose **Public**.
5. Leave **"Add a README file"**, **.gitignore** and **license** all **unticked**, because the project already has them.
6. Click **Create repository**.

### 3. Upload the files
1. On the new, empty repository page, click the link **"uploading an existing file"**.
2. Open your unzipped project folder. Select **everything inside it** (Ctrl+A on Windows, Cmd+A on Mac), *not* the folder itself.
3. Drag the selection into the browser upload area. GitHub keeps the sub-folders.
4. Wait until every file shows in the list. There are about 40 files.

> **Note on hidden items:** `.gitignore` and the `.streamlit` folder start with a dot, so your computer may hide them.
> - **Windows:** in File Explorer, choose View → Show → Hidden items.
> - **Mac:** press Cmd+Shift+. (full stop).
>
> If they still do not upload, the project works without them. `.streamlit` only sets the dashboard colours.

### 4. Commit the files
1. Scroll down to **Commit changes**.
2. In the first box, type: `Initial commit: operations analytics portfolio project`
3. Keep **"Commit directly to the main branch"** selected.
4. Click **Commit changes**.

### 5. Check the README
1. Click the repository name at the top. The README now displays below the file list.
2. Check that the dashboard picture appears near the top.

### 6. Check that the screenshots display
1. Scroll through the README. You should see the Excel dashboard and the Streamlit dashboard images.
2. Click **More screenshots** to expand the section and check the rest.
3. If an image shows a broken icon, open the `screenshots` folder on GitHub. Check that the file exists with exactly the same name (names are case-sensitive).

### 7. Check the links
1. Click a few links inside the README, for example **KPI Definitions**, **Data Quality Report** and the Excel file.
2. Each one should open the file.

### 8. Add topics (optional, helps discovery)
1. On the repository page, click the ⚙️ next to **About** on the right.
2. Add these topics: `operations-analytics`, `excel`, `kpi-dashboard`, `data-cleaning`, `streamlit`, `business-analysis`, `portfolio-project`.
3. Click **Save changes**.

### 9. Copy the repository URL
1. Copy the address from your browser bar. It looks like `https://github.com/<your-username>/neo-heat-pump-operations-analytics`.
2. Paste it everywhere `[GitHub URL]` appears (README, RESUME_AND_LINKEDIN.md, Case_Study.pdf note). Edit a file on GitHub by opening it and clicking the ✏️ pencil icon, then **Commit changes**.

### 10. Check that someone else can see it
1. Open a **private/incognito** browser window, where you are not logged in.
2. Paste the URL.
3. If you can see the README and the files, it is public. You can also send the link to a friend and ask them to open it.

---

## Part B (optional): publish the dashboard online, free

1. Go to **https://share.streamlit.io** and click **Continue with GitHub**. Authorise access.
2. Click **Create app**, then choose **Deploy a public app from GitHub**.
3. Fill in the fields:
   - **Repository:** `<your-username>/neo-heat-pump-operations-analytics`
   - **Branch:** `main`
   - **Main file path:** `dashboard/app.py`
4. *(Optional)* Choose a custom URL such as `neo-ops-dashboard`.
5. Click **Deploy**. The first start takes 2–5 minutes while it installs `dashboard/requirements.txt`.
6. Copy the app URL (`https://<name>.streamlit.app`) and add it to:
   - the README (section 14, add a line "Live demo: <URL>");
   - `RESUME_AND_LINKEDIN.md`.

**If deployment fails:**
1. Open **Manage app** at the bottom right and read the log.
2. The most common fix is choosing **Python 3.12 or 3.13** under *Advanced settings* when you create the app.
3. Free apps go to sleep after a few days without visitors. Anyone who opens the link can click "Yes, get this app back up" to wake it.

---

## Part C: things you must never upload
- Real customer names, phone numbers, addresses or invoices.
- Real company price lists, revenue or performance data, unless the company has given **written** permission.
- Passwords, API keys or a `.streamlit/secrets.toml` file. The included `.gitignore` already blocks this file.

This project contains none of these. Everything in it is synthetic.

---

## Optional: the command-line method
Only use this if you already have Git installed.
```bash
cd path/to/neo-heat-pump-operations-analytics        # go into the project folder
git init                                             # start version control here
git add .                                            # stage every file
git commit -m "Initial commit: operations analytics portfolio project"
git branch -M main                                   # name the branch 'main'
git remote add origin https://github.com/<your-username>/neo-heat-pump-operations-analytics.git
git push -u origin main                              # upload (GitHub will ask you to log in)
```

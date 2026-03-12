# Git Setup Instructions - Health Dashboards

## Step 1: Create Remote Repository on GitHub

1. **Go to GitHub:** https://github.com/new
2. **Create new repository:**
   - **Name:** `health-tracking` (or your preferred name)
   - **Description:** "Interactive health dashboards for tracking Anup & Deepali metrics (2011-2025)"
   - **Visibility:** Private (only you and Deepali can see)
   - **DO NOT** initialize with README/gitignore/license (we already have them)
   - **Click:** "Create repository"

3. **Copy the repository URL** (looks like: `https://github.com/username/health-tracking.git`)

## Step 2: Connect Local Repository to Remote

Run these commands in your terminal (from C:\Projects\health):

```bash
# Set the remote URL
git remote add origin https://github.com/YOUR_USERNAME/health-tracking.git

# Rename branch to main (GitHub default)
git branch -M main

# Push the code
git push -u origin main
```

**Note:** GitHub may ask you to authenticate. Use:
- **Username:** Your GitHub username
- **Password:** Your GitHub personal access token (create at https://github.com/settings/tokens)

## Step 3: Invite Deepali as Collaborator

1. **Go to repository settings:** https://github.com/YOUR_USERNAME/health-tracking/settings
2. **Click:** "Collaborators" (left sidebar)
3. **Click:** "Add people"
4. **Enter:** Deepali's GitHub username
5. **Click:** "Add"

## Step 4: Setup for Deepali

Deepali should:
1. **Install Git** (if not already installed): https://git-scm.com/downloads
2. **Configure Git:**
   ```bash
   git config --global user.name "Deepali Kamble"
   git config --global user.email "your-email@gmail.com"
   ```
3. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/health-tracking.git
   cd health-tracking
   ```
4. **Done!** Now she can open dashboards and make changes.

## Step 5: Using Git Together

### When Anup Makes Changes:
```bash
# From C:\Projects\health
git add .
git commit -m "Update Anup's Oct 2025 lab results"
git push origin main
```

### When Deepali Makes Changes:
```bash
# First, get latest changes
git pull origin main

# Make changes to dashboard files...

# Then push changes
git add .
git commit -m "Update Deepali's Mar 2026 lab results"
git push origin main
```

### When You Want to See Each Other's Changes:
```bash
git pull origin main
```

## Step 6: Making Dashboard Changes

### Example: Update Anup's Glucose Value

1. **Open:** `complete_health_trends.html` in text editor
2. **Find:** The data section (search for "data:")
3. **Locate:** Glucose values array: `[93, 95, 91, 97, 93, 94, 96, 95, 87]`
4. **Edit:** Change last value or add new value
5. **Save** the file
6. **Commit:**
   ```bash
   git add complete_health_trends.html
   git commit -m "Update Anup glucose: Oct 2025 = 87 mg/dL"
   git push origin main
   ```
7. **Tell Deepali** to pull: `git pull origin main`

## Alternative: GitHub Web UI (No Command Line)

If you prefer not to use terminal, you can edit directly on GitHub:

1. **Go to:** https://github.com/YOUR_USERNAME/health-tracking
2. **Click** on any `.html` file
3. **Click pencil icon** (Edit)
4. **Make changes** in the browser
5. **Scroll down** and click "Commit changes"
6. **Enter message** and "Commit"

**Note:** Changes made in GitHub web UI will need to be pulled locally:
```bash
git pull origin main
```

## Troubleshooting

### "Permission denied" when pushing?
- Check that you invited Deepali as collaborator
- Verify GitHub personal access token has correct permissions

### "Merge conflict" when pulling?
This happens when both people edited the same file. To fix:
```bash
# See what's conflicted
git status

# Open the conflicted file, find lines marked with <<<<< and >>>>>
# Manually choose which changes to keep
# Then:
git add .
git commit -m "Resolve merge conflict"
git push origin main
```

### Don't see changes Deepali made?
```bash
git pull origin main
```

## Tips for Success

1. **Pull before you work:**
   ```bash
   git pull origin main
   ```

2. **Push when done:**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```

3. **Commit messages should be descriptive:**
   - ✓ "Update Deepali glucose to 95 mg/dL (Mar 2026 labs)"
   - ✗ "fixed stuff"

4. **Never commit PDFs or sensitive files** (they're in .gitignore)

5. **Check status before pushing:**
   ```bash
   git status
   ```

## File Access URLs

After pushing to GitHub, you can access dashboards at:
- Main comparison: `https://github.com/YOUR_USERNAME/health-tracking/blob/main/anup_deepali_2011_2025_comparison.html`
- Anup's dashboard: `https://github.com/YOUR_USERNAME/health-tracking/blob/main/complete_health_trends.html`
- Deepali's dashboard: `https://github.com/YOUR_USERNAME/health-tracking/blob/main/deepali_health_trends.html`

**To view as interactive HTML** (instead of raw code):
- Use: https://htmlpreview.github.io/?github.com/YOUR_USERNAME/health-tracking/blob/main/anup_deepali_2011_2025_comparison.html

---

**Questions?** GitHub has great documentation at https://docs.github.com/en/get-started

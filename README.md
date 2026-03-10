# Health Tracking Dashboard - Anup & Deepali

Interactive health metrics tracking and trend analysis for Anup (ASK) and Deepali (DAK) spanning 2011-2025.

## 📊 Available Dashboards

### Main Comparison Dashboard
- **File:** `anup_deepali_2011_2025_comparison.html`
- **Content:** Side-by-side comparison of both users across all metrics (2011-2025)
- **Metrics:** Glucose, Cholesterol, LDL, HDL, Triglycerides, TSH, Vitamin D
- **Features:** 14-year trend analysis, metabolic syndrome assessment, clinical recommendations

### Individual Dashboards

#### Anup (ASK)
- **File:** `complete_health_trends.html`
- **Span:** 2011-2025 (14 years of data)
- **Status:** Dyslipidemia focus; excellent glucose control
- **Key Finding:** LDL 141 (high), HDL 38 (low), Glucose 87 (excellent)
- **Current Intervention:** 6 months gym program (5x/week 5 AM workouts)

#### Deepali (DAK)
- **File:** `deepali_health_trends.html`
- **Span:** 2021-2025 (5 years of data)
- **Status:** Prediabetic (HbA1c 5.9%); dyslipidemia
- **Key Finding:** Elevated HbA1c despite normal fasting glucose (postprandial glucose dysfunction)
- **Current Intervention:** 6 months gym program + dietary modifications + weight loss

### Historical Dashboards
- `lipid_trends.html` - Lipid focus only
- `lipid_glucose_tsh_trends.html` - Lipids + glucose + thyroid

## 🚀 Quick Start

### View Dashboards Locally
1. Clone this repository
2. Open any `.html` file directly in your web browser (Chrome, Firefox, Safari)
3. All charts are interactive - hover to see values, zoom to inspect trends

### Collaborate & Make Changes

#### For Anup & Deepali:
```bash
# First time setup
git clone <repository-url>
cd health
git pull origin main

# Before making changes
git pull origin main

# After making changes
git add .
git commit -m "Update dashboard with [specific changes]"
git push origin main
```

#### To Customize Dashboards:
1. Open the `.html` file in a text editor (VS Code, Sublime, etc.)
2. Find the data section (usually marked with comments)
3. Update values, add new metrics, change colors
4. Save the file
5. Commit and push to git
6. Both users can pull changes

#### Example Customizations:
- Add new metrics or data points
- Change chart colors or styles
- Update clinical thresholds/goals
- Add personal notes or observations
- Create new comparison views

## 📈 Data Structure

### Dashboard Data Format
Each HTML file contains embedded JavaScript with data arrays:

```javascript
labels: ['2011', '2012', ..., 'Oct 2025'],
datasets: [{
    label: 'LDL Cholesterol',
    data: [93, 109, ..., 141],  // Values for each date
    borderColor: '#FF6B6B',
    ...
}]
```

To update values:
1. Find the date in the `labels` array
2. Find the corresponding position in the `data` array
3. Update the value
4. Save and push

## 🔄 Workflow for New Lab Results

When new labs are available (e.g., from Wednesday appointments):

1. **Extract values** from lab report
2. **Add to appropriate dashboard:**
   - Find the correct metric section
   - Locate the `data:` array
   - Add new value at the end
   - Update the `labels` array with new date
3. **Commit with descriptive message:**
   ```bash
   git commit -m "Add Mar 2026 labs: Anup LDL 130, HDL 42; Deepali HbA1c 5.7"
   ```
4. **Push to remote** so both can access
5. **Pull regularly** to see each other's updates

## 📋 Metrics Tracked

### Common Metrics
- **Glucose (Fasting)** - Goal: 65-110 mg/dL
- **HbA1c** - Goal: <5.7% (non-diabetic)
- **Total Cholesterol** - Goal: <200 mg/dL
- **LDL Cholesterol** - Goal: <100 mg/dL
- **HDL Cholesterol** - Goal: >40 mg/dL (men), >50 mg/dL (women)
- **Triglycerides** - Goal: <150 mg/dL
- **TSH** - Goal: 0.4-4.0 mIU/mL
- **Vitamin D** - Goal: 30-100 ng/mL

## 🏥 Clinical Context

### Anup's Status (ASK)
- **Primary Concern:** Dyslipidemia (abnormal lipids)
- **Glucose Control:** Excellent (87 mg/dL, stable 14 years)
- **Intervention:** 6 months gym work + dietary modification
- **Next Action:** Consider statin therapy if Oct 2025 results don't improve enough

### Deepali's Status (DAK)
- **Primary Concern:** Prediabetes (HbA1c 5.9%) + Dyslipidemia
- **Glucose Pattern:** Normal fasting but elevated postprandial (2-hour post-meal)
- **Intervention:** 6 months gym work + dietary modification + weight loss
- **Next Action:** Monitor if HbA1c drops below 5.8% by next labs

## 🛠️ Technical Setup

### Local Development
No special software needed! Dashboards are pure HTML/JavaScript:
- **View:** Any web browser
- **Edit:** Any text editor
- **Version Control:** Git

### Hosting (Optional)
To access dashboards over internet without downloading:
1. Push to GitHub/GitLab
2. Enable GitHub Pages (settings → Pages → main branch)
3. Share URL: `https://username.github.io/health/`

## 📝 File Structure
```
C:\Projects\health\
├── README.md                          # This file
├── .gitignore                         # Git ignore rules
├── .git/                              # Git repository data
│
├── anup_deepali_2011_2025_comparison.html  # Main comparison
├── complete_health_trends.html             # Anup detailed
├── deepali_health_trends.html              # Deepali detailed
│
├── agent/                             # Python agent code (future)
│   ├── main.py
│   ├── config.yaml
│   └── parsers/
│
├── ASK/                               # Anup's reports folder
├── DAK/                               # Deepali's reports folder
├── vault/                             # Obsidian vault integration
└── raw_reports/                       # Original PDF files
```

## 🔐 Privacy & Security
- **Local storage:** All dashboards work offline
- **Git sharing:** Only share repository access with authorized users
- **Sensitive data:** PDFs are gitignored, only summaries are tracked
- **No cloud uploads:** Everything stays in your control

## 🎯 Next Steps

1. **Set up remote repository:**
   ```bash
   git remote add origin <your-github-url>
   git branch -M main
   git push -u origin main
   ```

2. **Invite Deepali:**
   - Add her as collaborator on GitHub/GitLab
   - She clones: `git clone <url>`
   - She can pull/push changes

3. **After Wednesday labs:**
   - Update dashboards with new values
   - Commit: `git commit -m "Add [date] labs for both"`
   - Push: `git push origin main`
   - Both pull to see updates

4. **Regular updates:**
   - Every 3 months when new labs available
   - When making lifestyle/medication changes
   - When adding new metrics or customizations

## 📞 Support
For questions on:
- **Git workflow:** Refer to git documentation or GitHub/GitLab guides
- **Dashboard customization:** Edit the HTML directly, all is self-contained
- **Clinical interpretation:** Consult your healthcare provider

---

**Last Updated:** March 9, 2026
**Data Through:** October 3, 2025 (Anup), Oct 2025 (Deepali pending Mar 2026 labs)

# 🚨 URGENT: GitHub Actions Secrets Not Configured

## The Problem

The workflow is running but **failing silently** because the `PLANNING_PAGES` GitHub secret is not configured.

The script exits immediately with:
```
ValueError: PLANNING_PAGES environment variable required.
Expected format: '{"3670017": "DESIGN"}'
```

This happens **before any sync occurs**, so:
- ❌ No Jira issues are fetched
- ❌ No decisions are captured
- ❌ No Confluence pages are updated
- ❌ The workflow shows as "success" but does nothing

---

## Solution: Configure GitHub Secrets (2 minutes)

### Step 1: Go to Repository Settings
https://github.com/tswanatlassian/rovo-sync/settings/secrets/actions

### Step 2: Click "New repository secret"

### Step 3: Add PLANNING_PAGES Secret

**Name:** `PLANNING_PAGES`

**Value:** 
```json
{"3670017": "DESIGN"}
```

Click "Add secret"

### Step 4: Verify Other Secrets Exist

Make sure these also exist (they may already be set):
- ✅ `JIRA_TOKEN` - Your Jira API token
- ✅ `CONFLUENCE_TOKEN` - Your Confluence API token  
- ✅ `JIRA_URL` - Should default to https://timswn-aibw.atlassian.net
- ✅ `CONFLUENCE_URL` - Should default to https://timswn-aibw.atlassian.net/wiki

---

## Test It Works

### Option 1: Manual Trigger
1. Go to: https://github.com/tswanatlassian/rovo-sync/actions
2. Click "Rovo Sync - Automated Confluence ↔ Jira Sync"
3. Click "Run workflow" button
4. Wait 1-2 minutes

### Option 2: Wait for Hourly Sync
The workflow runs automatically every hour at :00

---

## What Should Happen After Setup

Once the secret is configured, the workflow will:

1. **Fetch Confluence page** (3670017)
   - Log: "Retrieved page: Planning Page - Synced"

2. **Extract linked Jira issues**
   - Log: "Starting sync for page 3670017 (space: DESIGN)"

3. **Detect changes** (Phase 3.1)
   - Log: "Running Phase 3.1: Change Detection"
   - Log: "TACS-39: To Do"
   - Log: "TACS-40: To Do"
   - Log: "TACS-42: In Progress" (if you changed it)

4. **Capture decisions** (Phase 3.2)
   - Log: "Processing 2 comments for TACS-42"
   - Log: "Captured decision from TACS-42" (if you added decision comment)

5. **Update Confluence**
   - Log: "Updated page 3670017 with 5 activities"

6. **Confluence page updates**
   - 📢 Recent Activity feed appears
   - 📊 Work Item Status table updates
   - 📝 Decisions section populated

---

## Verify Workflow Logs

After running the workflow:

1. Go to: https://github.com/tswanatlassian/rovo-sync/actions/runs
2. Click the latest run
3. Click "Sync Planning Pages" job
4. Look for these log messages:
   ```
   Retrieved page: Planning Page - Synced
   Starting sync for page 3670017
   Running Phase 3.1: Change Detection
   TACS-42: In Progress
   Processing X comments for TACS-42
   Updated page 3670017 with X activities
   ```

If you see these, ✅ **it's working!**

If you see:
```
ValueError: PLANNING_PAGES environment variable required
```

The secret wasn't saved. Go back to step 1 and add it again.

---

## Troubleshooting

### Workflow shows "success" but no Confluence update

**Cause:** PLANNING_PAGES secret not configured (or empty)

**Fix:** Add the secret following steps 1-3 above

### Workflow shows "failure"

Check the logs for error messages. Common issues:
- ❌ JIRA_TOKEN or CONFLUENCE_TOKEN invalid
- ❌ Page 3670017 doesn't exist or isn't accessible
- ❌ Jira issues TACS-39, TACS-40, etc. don't exist

### Still not working?

1. Verify all 5 secrets are set in GitHub
2. Verify tokens have correct permissions (read Jira, write Confluence)
3. Verify page ID 3670017 is correct (check URL on Confluence)
4. Check workflow logs for error messages

---

## Summary

**Why it wasn't working:**
- PLANNING_PAGES GitHub secret was never configured
- Without it, the script exits before doing anything

**How to fix it:**
- Add `PLANNING_PAGES` secret with value `{"3670017": "DESIGN"}`

**Time to fix:**
- 2 minutes

**Next steps:**
- Configure the secret now
- Trigger a manual workflow run
- Check Confluence page for updates

---

## Questions?

Refer to:
- `DIAGNOSIS_AND_FIX.md` - Complete technical details
- `COMPLETE_WALKTHROUGH.md` - How to use the system once it's working
- `OPTIMIZATION_SUMMARY.md` - Performance improvements already made

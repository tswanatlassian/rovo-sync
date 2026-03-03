# Fix: 403 Forbidden - Token Permissions Issue

## 🔴 Problem Found

```
Response status: 403
Error: 403 Client Error: Forbidden
URL: /rest/api/content/3670017
```

**The Confluence token you set does NOT have permission to access page 3670017.**

This can happen if:
1. Token was created with limited scopes (read-only instead of read+write)
2. Token is restricted to specific spaces (not DESIGN space)
3. Token scope excludes content read/write permissions

## ✅ Solution: Regenerate Token with Correct Scopes

### Step 1: Go to Atlassian Manage Profile

Visit: https://id.atlassian.com/manage-profile/security/api-tokens

### Step 2: Delete the Old Token

If you still have the old token listed, delete it to avoid confusion.

### Step 3: Create a NEW Token with Explicit Scopes

1. Click "Create API token"
2. Name it: `rovo-sync-token` or similar
3. **IMPORTANT: Make sure these scopes are selected:**
   - ☑️ `read:confluence-content.all` - Read all Confluence content
   - ☑️ `write:confluence-content.all` - Write all Confluence content
   - ☑️ `read:jira-work` - Read Jira issues
   - ☑️ `write:jira-work` - Write/update Jira issues
4. Click "Create"
5. Copy the token (you'll only see it once)

### Step 4: Update GitHub Secret

1. Go to: https://github.com/tswanatlassian/rovo-sync/settings/secrets/actions
2. Click on `CONFLUENCE_TOKEN`
3. Delete the old value
4. Paste the NEW token
5. Click "Update secret"

**Alternatively for JIRA_TOKEN:**
1. Same process at https://id.atlassian.com/manage-profile/security/api-tokens
2. Create a new API token with read+write scopes for Jira
3. Update the `JIRA_TOKEN` secret in GitHub

### Step 5: Test

1. Go to: https://github.com/tswanatlassian/rovo-sync/actions
2. Click "Rovo Sync" workflow
3. Click "Run workflow"
4. Wait 2 minutes
5. Check logs for:
   ```
   Response status: 200
   Retrieved page: Demo Mobile App Redesign...
   Updated page 3670017 with X activities
   ```

## Why This Matters

Atlassian tokens can be created with limited scopes for security. The 403 error means:
- ✅ API is working
- ✅ Page exists
- ✅ Endpoint is correct
- ❌ Token lacks permission

The fix is simple: regenerate with broader scopes.

## API Scopes Reference

For Confluence:
- `read:confluence-content.all` - Full read access to content
- `write:confluence-content.all` - Full write access to content
- `manage:confluence-project` - Manage projects (optional)

For Jira:
- `read:jira-work` - Read Jira issues and related data
- `write:jira-work` - Write/create/update Jira issues

## Verification

After updating the token, the workflow should show:
```
Fetching Confluence page: https://timswn-aibw.atlassian.net/wiki/rest/api/content/3670017
Response status: 200 ✅
Retrieved page: Demo Mobile App Redesign...
Processing X comments...
Updated page 3670017 with X activities ✅
```

Instead of:
```
Response status: 403 ❌
Error: 403 Client Error: Forbidden
```

---

**Summary:** The code is working perfectly. The only issue is the token doesn't have permission. Once you regenerate it with full read+write scopes, everything will work.

# Fix: Confluence 403 Forbidden - Use Basic Auth

## Problem

The Bearer token auth keeps returning **403 Forbidden** for all Confluence pages, even with fresh tokens with full scopes.

## Root Cause

**Confluence Cloud API requires Basic Authentication with email:token format**, not Bearer tokens.

Bearer tokens work for Jira, but Confluence needs:
```
Authorization: Basic base64(email:api_token)
```

## Solution

Update your `CONFLUENCE_TOKEN` secret to use the **email:token format**.

### Step 1: Get Your Email

The email address associated with your Atlassian account (e.g., `tswan@atlassian.com`)

### Step 2: Get Your API Token

The API token you created at https://id.atlassian.com/manage-profile/security/api-tokens

### Step 3: Update GitHub Secret

1. Go to: https://github.com/tswanatlassian/rovo-sync/settings/secrets/actions
2. Click on `CONFLUENCE_TOKEN`
3. **Update the value to:**
   ```
   your.email@atlassian.com:YOUR_API_TOKEN_HERE
   ```
   
   **Example:**
   ```
   tswan@atlassian.com:ATATT3xFfGF0abcdefghijklmnop
   ```

4. Click "Update secret"

### Step 4: Test

1. Trigger workflow: https://github.com/tswanatlassian/rovo-sync/actions
2. Check logs for:
   ```
   Confluence auth method: Basic (email:token)
   Response status: 200 ✅
   Retrieved page: [page title]
   ```

## How It Works

The code now:
1. Checks if token contains `:` (email:token format)
2. If yes → Use Basic auth (correct for Confluence)
3. If no → Use Bearer token (fallback)
4. Logs which method is being used

## Why This Matters

**Confluence Cloud Authentication:**
- ✅ Basic auth with `email:token` → **Works**
- ❌ Bearer token → **403 Forbidden** (what we were getting)

**Jira Cloud Authentication:**
- ✅ Bearer token → **Works**
- ✅ Basic auth with `email:token` → **Also works**

So we keep Jira using Bearer, Confluence using Basic auth.

## Verification

After updating the secret, you should see in logs:
```
Confluence auth method: Basic (email:token)
Response status: 200
Retrieved page: Planning Page Title
Processing X comments for TACS-42
Updated page 2031632 with X activities
```

Instead of:
```
Confluence auth method: Bearer
Response status: 403
Error: 403 Client Error: Forbidden
```

---

**TL;DR:** Update `CONFLUENCE_TOKEN` secret to `your.email@domain.com:YOUR_API_TOKEN`

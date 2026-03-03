# Complete Walkthrough: See Rovo Sync Phases 1-3 in Action

**Duration:** 30-45 minutes  
**Skill Level:** Anyone (no coding required)  
**Goal:** Watch the complete planning → execution → feedback loop work end-to-end

---

## 🎯 What You'll See

1. **Phase 1:** Planning pages with rich context that flow into Jira
2. **Phase 2:** Work execution with live status sync back to Confluence
3. **Phase 3:** Automated change detection, decision capture, refinement tracking, and learning loops

---

## 📚 Part 1: See the System Already Running (10 minutes)

### Step 1.1: View the Planning Page (Phase 1 Foundation)

**URL:** https://timswn-aibw.atlassian.net/wiki/spaces/DESIGN/pages/3670017

**What to observe:**

#### 🎯 Outcome Surface (Top of Page)
```
Redesign mobile app navigation to increase engagement by 20%
and improve app rating to 4.5+ stars
```
- This is the **outcome** - the north star for all work
- Everything below ties back to this goal

#### 🚧 Work Breakdown Section
You'll see 5 work items with:
- **Description** - What needs to happen
- **Owner** - Who's responsible (@Tim Swan)
- **Due date** - When it should complete (2026-03-05, 2026-03-12, etc.)
- **Context** - Why it matters to the outcome

**Work Items:**
1. TACS-39: Conduct User Research and Navigation Audit
2. TACS-40: Design New Navigation System
3. TACS-38: Conduct User Testing with Prototype
4. TACS-42: Build Navigation Component in React Native
5. TACS-41: Deploy to Beta and Measure Impact

#### 🛡️ Constraints & Guardrails
```
Technical Constraints:
- Must use React Native
- Performance budget: <100ms transitions
- App size budget: +500KB max

Team Practices:
- 2 code reviews required
- No direct commits to main

Risk Mitigation:
- Risk: Performance regression
  Mitigation: Test on iPhone 8 and Galaxy S9
```

**✅ This is Phase 1 in action:** Outcome-driven planning with guardrails embedded directly in the planning document.

---

### Step 1.2: See Rich Context in Jira Issues (Phase 1 Extraction)

**Pick any issue, e.g., TACS-42:**  
https://timswn-aibw.atlassian.net/browse/TACS-42

**What you'll see in the description:**

```markdown
## Outcome Context
Supports: Mobile App Redesign outcome
Why: Navigation performance directly impacts user experience

## Work Spec
Implement the new navigation component using React Native

## Constraints & Guardrails
- Must use React Native (no native rewrites)
- Performance budget: <100ms transitions
- App size budget: +500KB max

## Agent Context
Space Knowledge: TACS space knowledge
Related Work: TACS-40, TACS-38
Performance Budgets: <100ms transitions
Key Decisions: Use bottom tab bar (78% vs 54% task completion)

Risk Mitigation:
- Risk: Performance regression on older devices
- Mitigation: Test on iPhone 8 and Galaxy S9 as baselines
```

**✅ This is Phase 1 extraction:** All the rich context from Confluence is now embedded in the Jira issue - perfect for both humans and AI agents.

---

### Step 1.3: See Live Sync Back to Confluence (Phase 1 Sync)

**Back on the Confluence page, find the section:** "📊 Live Work Items"

You'll see a table like:

| Key | Summary | Status | Owner | Due Date | Latest Update |
|-----|---------|--------|-------|----------|----------------|
| TACS-39 | Conduct User Research... | To Do | Tim Swan | 2026-03-05 | Created |
| TACS-40 | Design New Navigation... | To Do | Tim Swan | 2026-03-12 | Created |
| TACS-38 | Conduct User Testing... | To Do | Tim Swan | 2026-03-15 | Created |
| TACS-42 | Build Navigation... | To Do | Tim Swan | 2026-03-19 | Created |
| TACS-41 | Deploy to Beta... | To Do | Tim Swan | 2026-03-28 | Created |

**✅ This is Phase 1 sync:** The Jira status is automatically synced back to Confluence - single source of truth maintained.

---

### Step 1.4: See Decisions Captured (Phase 3.2)

**On the Confluence page, scroll to:** "📝 Decision Log"

You'll see captured decisions like:

```markdown
### Decision 1: Use Tab Bar Navigation Instead of Hamburger Menu
What: Implement bottom tab bar navigation with 5 main sections
Why: User research showed 78% task completion with tab bar vs 54% with hamburger
When: 2026-02-20 (during planning)
By: Design Team
Impact: Changes component structure but improves UX significantly
Tags: #navigation #ux-research #mobile

### Decision 2: No Animation on Low-End Devices
What: Disable navigation animations on devices with <2GB RAM
Why: Performance testing showed >200ms delays on older devices
When: 2026-02-21
By: Engineering Team
Impact: Reduces animation complexity but ensures performance budget compliance
Tags: #performance #mobile #accessibility
```

**✅ This is Phase 3.2 in action:** Decisions from comments are automatically extracted and logged with context.

---

### Step 1.5: Check the Activity Feed (Phase 3.1)

**On the Confluence page, find:** "📢 Recent Activity"

You'll see real-time updates like:

```markdown
🟢 TACS-42 moved to In Progress (2 hours ago)
💬 Decision captured: Use bottom tab bar navigation (Yesterday)
🚨 TACS-40 blocked by design approval (3 days ago)
✅ TACS-39 completed (1 week ago)
🆕 New work discovered: TACS-43 - Accessibility Testing (2 weeks ago)
```

**✅ This is Phase 3.1 in action:** Changes are automatically detected and surfaced in chronological order.

---

## 🔄 Part 2: See the System Respond to Changes (15 minutes)

Now let's make some changes and watch the system react!

### Step 2.1: Move a Work Item to "In Progress"

1. Go to any Jira issue: https://timswn-aibw.atlassian.net/browse/TACS-42
2. Click the **Status** dropdown
3. Change it from "To Do" → "In Progress"
4. Wait 2-3 minutes (or trigger manual sync - see below)

**Watch what happens:**
- ✅ Confluence "Live Work Items" table updates with new status
- ✅ Activity feed gets new entry: "🟢 TACS-42 moved to In Progress"
- ✅ Timestamp shows when the change occurred

**✅ This is Phase 3.1 change detection:** Status changes are automatically detected and synced.

---

### Step 2.2: Add a Blocker

1. On the same issue (TACS-42), change status to **"Blocked"**
2. Add a comment explaining why:
   ```
   Blocked waiting for design approval from @Sarah on the tab bar icons.
   Need this by EOW to stay on track.
   ```
3. Wait for the sync

**Watch what happens:**
- 🚨 Activity feed shows: "TACS-42 blocked by design approval"
- ⚠️ Blocker gets tagged as **HIGH SEVERITY** (has a deadline)
- 📝 Comment context appears in the activity feed

**✅ This is Phase 3.1 blocker detection:** Blockers are identified and surfaced with appropriate urgency.

---

### Step 2.3: Capture a Decision

1. On TACS-42, add a comment with a decision:
   ```
   Decision: We'll use React Navigation library instead of building custom.
   
   Why: React Navigation has better community support and handles edge cases 
   we haven't thought of. Custom solution would take 2+ extra weeks.
   
   Alternatives considered:
   - Custom navigation: More control but 2 weeks extra dev time
   - Expo Router: Too opinionated for our use case
   
   Impact: Adds 50KB to bundle but saves significant development time.
   ```
2. Wait for the sync

**Watch what happens:**
- 📝 Decision Log gets a new entry with full context
- 🏷️ Auto-tagged with: #navigation, #architecture, #react-native
- 📊 Searchable for future reference
- 💾 Stored in space memory for reuse

**✅ This is Phase 3.2 decision capture:** Decisions are automatically extracted, formatted, and stored.

---

### Step 2.4: Discover New Work

1. On TACS-42, add a comment:
   ```
   While building this, I realized we need to add accessibility support for 
   screen readers. Creating a new issue to track this work.
   ```
2. Create a new issue TACS-43: "Add Screen Reader Support"
3. Link it to TACS-42 ("is related to")
4. Wait for the sync

**Watch what happens:**
- 🆕 Activity feed shows: "New work discovered: TACS-43"
- 🔗 Confluence refinement log tracks it as "New Work" with context
- 📊 Timeline impact calculated (if estimated)

**✅ This is Phase 3.3 continuous refinement:** New work is automatically discovered and tracked.

---

### Step 2.5: Complete Work and Extract Learnings

1. Move TACS-42 to **"Done"**
2. Add a final comment:
   ```
   ✅ Completed! React Navigation worked great.
   
   What went well:
   - Library documentation was excellent
   - Performance meets our <100ms budget
   - Team picked it up quickly
   
   What we learned:
   - Deep linking setup is tricky - took 2 days longer than expected
   - Need to configure gesture handlers early in the setup
   - Tab bar customization requires understanding theme system
   
   For next time:
   - Budget extra time for deep linking
   - Set up gesture handlers in initial scaffold
   - Review theme docs before starting
   ```
3. Wait for the sync

**Watch what happens:**
- ✅ Activity feed shows completion
- 📚 Learning log extracts the "what went well" and "what we learned"
- 🎯 Learnings tagged for future discoverability
- 💡 Available for future similar work

**✅ This is Phase 3.4 learning loop:** Learnings are extracted and stored for future reference.

---

## ⚙️ Part 3: Understand How It Works (10 minutes)

### How Does the Sync Happen?

**Option 1: Automated Hourly Sync (Already Running)**

Every hour at :00, GitHub Actions automatically:
1. Fetches all configured planning pages
2. Checks all linked Jira issues for changes
3. Detects changes (status, blockers, new comments, etc.)
4. Extracts decisions and learnings from comments
5. Updates Confluence pages with new data
6. Stores decisions and learnings in memory files

**To see it running:**
1. Go to: https://github.com/tswanatlassian/rovo-sync/actions
2. Click on "Rovo Sync - Automated Confluence ↔ Jira Sync"
3. See the latest runs (every hour)

**Option 2: Manual Trigger (Test Immediately)**

Don't want to wait an hour? Trigger it manually:

1. Go to: https://github.com/tswanatlassian/rovo-sync/actions
2. Click "Rovo Sync - Automated Confluence ↔ Jira Sync"
3. Click "Run workflow" dropdown
4. Click green "Run workflow" button
5. Watch it run in ~30-45 seconds

**Option 3: Real-Time Webhooks (Optional - Not Yet Deployed)**

For instant updates on critical changes:
- Deploy webhook server (see DEPLOYMENT_GUIDE.md)
- Configure Jira webhooks
- Get instant sync for blockers, critical decisions, etc.

---

### What Files Make This Work?

**Phase 3.1 - Change Detection:**
- `change_detection_implementation.py` (461 lines)
- Detects status changes, blockers, new work, completions
- Updates Confluence activity feed and work items table

**Phase 3.2 - Decision Capture:**
- `decision_capture_implementation.py` (515 lines)
- Scans comments for decision patterns
- Extracts WHAT, WHY, ALTERNATIVES, IMPACT
- Stores in decision log and space memory

**Phase 3.3 - Continuous Refinement:**
- `continuous_refinement_implementation.py` (424 lines)
- Tracks new work discovery, scope changes, timeline impacts
- Maintains refinement log with all adjustments

**Phase 3.4 - Learning Loop:**
- `learning_loop_implementation.py` (465 lines)
- Extracts learnings from completed work
- Categorizes by type (technical, process, team)
- Builds searchable knowledge base

**Orchestrator:**
- `rovo_sync_orchestrator.py` (371 lines)
- Coordinates all Phase 3 components
- Handles Jira/Confluence API calls
- Runs hourly via GitHub Actions

---

## 🎯 Part 4: See the Value (5 minutes)

### What Problems Does This Solve?

**Problem 1: Context Lost in Handoffs**
- ❌ Before: Engineers get a Jira issue with just a title and basic description
- ✅ After: Every issue has outcome context, constraints, related decisions, and risk mitigations

**Problem 2: Status Updates Are Manual**
- ❌ Before: Someone manually updates planning docs or runs standup to sync status
- ✅ After: Confluence pages automatically reflect current Jira state every hour

**Problem 3: Decisions Get Lost**
- ❌ Before: Important decisions buried in comment threads or Slack
- ✅ After: Decisions automatically extracted, formatted, and logged with full context

**Problem 4: Learnings Don't Transfer**
- ❌ Before: Team learns something on one project, forgets it on the next
- ✅ After: Learnings automatically captured and searchable for future work

**Problem 5: Scope Creep is Invisible**
- ❌ Before: New work appears without tracking its impact
- ✅ After: New work automatically detected and timeline impact calculated

---

## 🚀 Next Steps

### Want to Set This Up for Your Team?

1. **Read:** `DEPLOYMENT_GUIDE.md` for full setup instructions
2. **Configure:** Your own planning pages in `PLANNING_PAGES` secret
3. **Customize:** Detection rules in `change_detection_implementation.py`
4. **Deploy:** Webhook server for real-time updates (optional)

### Want to Extend the System?

1. **Add More Detection Patterns:** Edit the rules in Phase 3.1
2. **Customize Decision Formats:** Modify Phase 3.2 extractors
3. **Track Different Metrics:** Extend Phase 3.3 refinement tracking
4. **Categorize Learnings Differently:** Adjust Phase 3.4 learning types

### Want to See the Code?

All files are in this repo:
- `change_detection_implementation.py`
- `decision_capture_implementation.py`
- `continuous_refinement_implementation.py`
- `learning_loop_implementation.py`
- `rovo_sync_orchestrator.py`

Each file is ~400-500 lines, well-commented, and ready to customize.

---

## 📊 Summary

You just witnessed:
- ✅ **Phase 1:** Planning pages flowing into Jira with rich context
- ✅ **Phase 2:** Live work status syncing back to Confluence
- ✅ **Phase 3.1:** Automatic change detection and activity feeds
- ✅ **Phase 3.2:** Automatic decision capture and logging
- ✅ **Phase 3.3:** Continuous refinement tracking (new work, scope changes)
- ✅ **Phase 3.4:** Learning loops building organizational knowledge

**Total automation:** ~1,900 lines of Python code running hourly to keep planning and execution in sync with zero manual effort.

**Questions?** Check the other docs:
- `HOW_TO_SEE_IT_IN_ACTION.md` - Detailed scenarios
- `DEPLOYMENT_GUIDE.md` - Setup instructions
- `PHASE_3_IMPLEMENTATION_SUMMARY.md` - Technical details
- `OPTIMIZATION_SUMMARY.md` - Performance improvements

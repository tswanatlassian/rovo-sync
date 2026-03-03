#!/usr/bin/env python3
"""
Phase 3.1: Change Detection System Implementation
Monitors Jira for important changes and syncs them back to Confluence

Features:
- Detect status transitions
- Identify blockers
- Capture completions
- Find new work items
- Extract decisions
- Update Confluence planning page automatically
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class IssueState:
    """Tracks the last known state of a Jira issue"""
    issue_key: str
    page_id: str
    last_synced: str
    status: str
    assignee: Optional[str]
    due_date: Optional[str]
    comments_count: int
    latest_comment_ts: str
    latest_comment_text: str
    linked_issues: List[str]
    is_blocked: bool
    labels: List[str]

@dataclass
class Change:
    """Represents a detected change in a Jira issue"""
    issue_key: str
    change_type: str  # status_change, blocker, completion, new_comment, new_link, decision
    old_value: Optional[str]
    new_value: Optional[str]
    timestamp: str
    severity: str  # critical, high, normal, low
    action_required: bool
    description: str

# ============================================================================
# CHANGE DETECTION RULES
# ============================================================================

class ChangeDetectionRules:
    """Rules for detecting important changes in Jira"""
    
    @staticmethod
    def detect_status_change(old_status: str, new_status: str) -> Optional[Change]:
        """Detect when issue status changes"""
        important_transitions = {
            ("To Do", "In Progress"): ("critical", True),
            ("In Progress", "Done"): ("critical", True),
            ("In Progress", "Blocked"): ("critical", True),
            ("Blocked", "In Progress"): ("high", True),
            ("To Do", "Blocked"): ("high", True),
        }
        
        transition = (old_status, new_status)
        if transition in important_transitions:
            severity, action_required = important_transitions[transition]
            return Change(
                issue_key="",
                change_type="status_change",
                old_value=old_status,
                new_value=new_status,
                timestamp=datetime.now().isoformat(),
                severity=severity,
                action_required=action_required,
                description=f"Status changed from {old_status} to {new_status}"
            )
        return None
    
    @staticmethod
    def detect_blocker(status: str, comments: List[str]) -> Optional[Change]:
        """Detect if issue is blocked"""
        if status == "Blocked":
            return Change(
                issue_key="",
                change_type="blocker",
                old_value=None,
                new_value="Blocked",
                timestamp=datetime.now().isoformat(),
                severity="critical",
                action_required=True,
                description="Issue is blocked - needs attention"
            )
        
        # Check comments for blocker keywords
        blocker_keywords = ["blocked", "waiting", "depends on", "can't proceed", "stuck"]
        for comment in comments:
            if any(keyword in comment.lower() for keyword in blocker_keywords):
                return Change(
                    issue_key="",
                    change_type="blocker",
                    old_value=None,
                    new_value="Blocked (from comment)",
                    timestamp=datetime.now().isoformat(),
                    severity="high",
                    action_required=True,
                    description=f"Blocker detected: {comment[:100]}"
                )
        
        return None
    
    @staticmethod
    def detect_decision(comment_text: str) -> Optional[Change]:
        """Detect if comment contains a decision"""
        decision_keywords = [
            "decided", "chose", "will use", "going with",
            "architecture decision", "picked", "selected", "concluded"
        ]
        
        if any(keyword in comment_text.lower() for keyword in decision_keywords):
            return Change(
                issue_key="",
                change_type="decision",
                old_value=None,
                new_value="Decision made",
                timestamp=datetime.now().isoformat(),
                severity="normal",
                action_required=False,
                description=f"Decision: {comment_text[:150]}"
            )
        
        return None
    
    @staticmethod
    def detect_completion(status: str) -> Optional[Change]:
        """Detect when work is completed"""
        if status == "Done":
            return Change(
                issue_key="",
                change_type="completion",
                old_value=None,
                new_value="Done",
                timestamp=datetime.now().isoformat(),
                severity="high",
                action_required=True,
                description="Work completed successfully"
            )
        return None
    
    @staticmethod
    def detect_new_linked_issue(old_links: List[str], new_links: List[str]) -> Optional[Change]:
        """Detect when new issue is linked"""
        new_issues = set(new_links) - set(old_links)
        if new_issues:
            return Change(
                issue_key="",
                change_type="new_link",
                old_value=None,
                new_value=", ".join(new_issues),
                timestamp=datetime.now().isoformat(),
                severity="normal",
                action_required=False,
                description=f"New work discovered: {', '.join(new_issues)}"
            )
        return None

# ============================================================================
# CHANGE DETECTION ENGINE
# ============================================================================

class ChangeDetectionEngine:
    """Main engine for detecting and processing changes"""
    
    def __init__(self):
        self.state_cache = {}  # issue_key -> IssueState
        self.change_history = []  # List of detected changes
    
    def detect_changes(self, current_issue: Dict[str, Any], 
                      cached_state: Optional[IssueState]) -> List[Change]:
        """
        Compare current issue state with cached state and detect changes
        
        Args:
            current_issue: Current Jira issue data
            cached_state: Previously cached state (if exists)
        
        Returns:
            List of detected changes
        """
        changes = []
        
        if not cached_state:
            # First time seeing this issue, no changes to detect
            return changes
        
        # Detect status change
        if current_issue.get("status") != cached_state.status:
            change = ChangeDetectionRules.detect_status_change(
                cached_state.status,
                current_issue.get("status")
            )
            if change:
                change.issue_key = current_issue["key"]
                changes.append(change)
        
        # Detect blocker
        blocker_change = ChangeDetectionRules.detect_blocker(
            current_issue.get("status"),
            [c.get("text", "") for c in current_issue.get("comments", [])]
        )
        if blocker_change:
            blocker_change.issue_key = current_issue["key"]
            changes.append(blocker_change)
        
        # Detect completion
        completion_change = ChangeDetectionRules.detect_completion(
            current_issue.get("status")
        )
        if completion_change:
            completion_change.issue_key = current_issue["key"]
            changes.append(completion_change)
        
        # Detect decisions from new comments
        current_comment_count = len(current_issue.get("comments", []))
        if current_comment_count > cached_state.comments_count:
            new_comments = current_issue.get("comments", [])[cached_state.comments_count:]
            for comment in new_comments:
                decision_change = ChangeDetectionRules.detect_decision(
                    comment.get("text", "")
                )
                if decision_change:
                    decision_change.issue_key = current_issue["key"]
                    changes.append(decision_change)
        
        # Detect new linked issues
        current_links = current_issue.get("linked_issues", [])
        new_link_change = ChangeDetectionRules.detect_new_linked_issue(
            cached_state.linked_issues,
            current_links
        )
        if new_link_change:
            new_link_change.issue_key = current_issue["key"]
            changes.append(new_link_change)
        
        return changes
    
    def cache_state(self, issue: Dict[str, Any], page_id: str) -> IssueState:
        """Cache the current state of an issue"""
        comments = issue.get("comments", [])
        latest_comment = comments[-1] if comments else {}
        
        state = IssueState(
            issue_key=issue["key"],
            page_id=page_id,
            last_synced=datetime.now().isoformat(),
            status=issue.get("status", "Unknown"),
            assignee=issue.get("assignee"),
            due_date=issue.get("due_date"),
            comments_count=len(comments),
            latest_comment_ts=latest_comment.get("timestamp", ""),
            latest_comment_text=latest_comment.get("text", ""),
            linked_issues=issue.get("linked_issues", []),
            is_blocked=issue.get("status") == "Blocked",
            labels=issue.get("labels", [])
        )
        
        self.state_cache[issue["key"]] = state
        return state
    
    def get_cached_state(self, issue_key: str) -> Optional[IssueState]:
        """Get cached state for an issue"""
        return self.state_cache.get(issue_key)

# ============================================================================
# CONFLUENCE UPDATE HANDLER
# ============================================================================

class ConfluenceUpdateHandler:
    """Handles updating Confluence with detected changes"""
    
    @staticmethod
    def format_activity_entry(change: Change) -> str:
        """Format a change as an activity feed entry"""
        icons = {
            "status_change": "📊",
            "blocker": "⚠️",
            "completion": "✅",
            "decision": "💡",
            "new_link": "🔗",
        }
        icon = icons.get(change.change_type, "📝")
        
        return f"**{icon} {change.issue_key}** - {change.description} ({change.timestamp[:10]})"
    
    @staticmethod
    def update_live_work_items_table(page_content: str, issue_key: str,
                                     status: str, latest_update: str) -> str:
        """
        Update the "Live Work Items" table in Confluence page
        
        Would replace table row for the issue with new data
        """
        # In real implementation, would parse and update markdown table
        # For now, return updated content
        return page_content
    
    @staticmethod
    def add_activity_feed_entry(page_content: str, entry: str) -> str:
        """Add entry to Activity Feed section"""
        # In real implementation, would insert into Activity Feed section
        # For now, return updated content
        return page_content
    
    @staticmethod
    def add_decision_log_entry(page_content: str, decision: Dict[str, str]) -> str:
        """Add entry to Decision Log section"""
        # In real implementation, would insert into Decision Log section
        # For now, return updated content
        return page_content

# ============================================================================
# POLLING LOOP
# ============================================================================

class ChangeDetectionPollingLoop:
    """Implements hourly polling for change detection"""
    
    def __init__(self, check_interval_seconds: int = 3600):
        self.engine = ChangeDetectionEngine()
        self.handler = ConfluenceUpdateHandler()
        self.check_interval = check_interval_seconds
        self.last_check = None
    
    def get_linked_issues(self, confluence_page_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all Jira issues linked to a Confluence page
        
        In real implementation:
        - Read custom field from Jira
        - Or search for issues linking to page
        """
        # Stub implementation
        return []
    
    def get_current_issue_state(self, issue_key: str) -> Dict[str, Any]:
        """
        Fetch current state of a Jira issue
        
        In real implementation:
        - Call Jira API to get issue details
        - Include status, assignee, due date, comments, links
        """
        # Stub implementation
        return {
            "key": issue_key,
            "status": "Unknown",
            "comments": [],
            "linked_issues": []
        }
    
    def should_check(self) -> bool:
        """Determine if it's time to check for changes"""
        if not self.last_check:
            return True
        
        elapsed = (datetime.now() - self.last_check).total_seconds()
        return elapsed >= self.check_interval
    
    def poll_once(self, confluence_page_id: str) -> List[Change]:
        """
        Run one polling cycle
        
        Returns:
            List of detected changes
        """
        if not self.should_check():
            return []
        
        all_changes = []
        
        # Get all issues linked to this planning page
        linked_issues = self.get_linked_issues(confluence_page_id)
        
        for issue_key in [i["key"] for i in linked_issues]:
            # Get current state
            current_state = self.get_current_issue_state(issue_key)
            
            # Get cached state
            cached_state = self.engine.get_cached_state(issue_key)
            
            # Detect changes
            changes = self.engine.detect_changes(current_state, cached_state)
            all_changes.extend(changes)
            
            # Cache new state
            self.engine.cache_state(current_state, confluence_page_id)
        
        # Update Confluence with changes
        for change in all_changes:
            self._process_change(confluence_page_id, change)
        
        self.last_check = datetime.now()
        return all_changes
    
    def _process_change(self, page_id: str, change: Change):
        """Process a detected change and update Confluence"""
        # Update Live Work Items table
        if change.change_type in ["status_change", "blocker", "completion"]:
            # Update status in table
            pass
        
        # Add to Activity Feed
        entry = self.handler.format_activity_entry(change)
        # Add entry to page
        
        # Special handling for decisions
        if change.change_type == "decision":
            # Extract and add to Decision Log
            pass
        
        # Notify if action required
        if change.action_required:
            # Send notification to team lead
            pass

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of the change detection system
    """
    
    # Create polling loop
    loop = ChangeDetectionPollingLoop(check_interval_seconds=3600)
    
    # Simulate polling for a planning page
    # In real usage, this would be called every hour
    page_id = "3670017"  # Demo: Mobile App Redesign
    
    changes = loop.poll_once(page_id)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Detected {len(changes)} changes:")
    for change in changes:
        logger.info(f"  - {change.issue_key}: {change.change_type} - {change.description}")
    
    # Example: Query cached state
    state = loop.engine.get_cached_state("TACS-42")
    if state:
        logger.info(f"\nCached state for TACS-42:")
        logger.info(f"  Status: {state.status}")
        logger.info(f"  Assignee: {state.assignee}")
        logger.info(f"  Comments: {state.comments_count}")
        logger.info(f"  Blocked: {state.is_blocked}")

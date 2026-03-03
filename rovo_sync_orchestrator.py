#!/usr/bin/env python3
"""
Rovo Sync Orchestrator
Main system that coordinates all Phase 3 components

Ties together:
- Change Detection (Phase 3.1)
- Decision Capture (Phase 3.2)
- Continuous Refinement (Phase 3.3)
- Learning Loop (Phase 3.4)

Runs via GitHub Actions (hourly) + Webhook (real-time)
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import asdict

# Import our Phase 3 implementations
from change_detection_implementation import ChangeDetectionPollingLoop, ChangeDetectionEngine
from decision_capture_implementation import DecisionCaptureEngine, SpaceMemory
from continuous_refinement_implementation import ContinuousRefinementEngine
from learning_loop_implementation import LearningLoopEngine, LearningMemory

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Load configuration from environment"""
    
    def __init__(self):
        self.jira_url = os.getenv("JIRA_URL", "https://timswn-aibw.atlassian.net")
        self.confluence_url = os.getenv("CONFLUENCE_URL", "https://timswn-aibw.atlassian.net/wiki")
        self.jira_token = os.getenv("JIRA_TOKEN")
        self.confluence_token = os.getenv("CONFLUENCE_TOKEN")
        self.planning_pages = json.loads(os.getenv("PLANNING_PAGES", "{}"))  # {page_id: space}
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.webhook_secret = os.getenv("WEBHOOK_SECRET")
        self.slack_webhook = os.getenv("SLACK_WEBHOOK")  # Optional
        
        # Validate required
        if not self.jira_token:
            raise ValueError("JIRA_TOKEN environment variable required")
        if not self.confluence_token:
            raise ValueError("CONFLUENCE_TOKEN environment variable required")
        if not self.planning_pages:
            raise ValueError("PLANNING_PAGES environment variable required")

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Set up logging to console and file"""
    logger = logging.getLogger("RovoSync")
    logger.setLevel(getattr(logging, log_level))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler("rovo_sync.log")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()

# ============================================================================
# JIRA & CONFLUENCE API CLIENTS
# ============================================================================

class JiraClient:
    """Simple Jira API client"""
    
    def __init__(self, url: str, token: str):
        self.url = url.rstrip("/")
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_issue(self, issue_key: str) -> Dict:
        """Get issue details"""
        import requests
        url = f"{self.url}/rest/api/3/issue/{issue_key}"
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting issue {issue_key}: {str(e)}")
            raise
    
    def get_linked_issues(self, issue_key: str) -> List[Dict]:
        """Get issues linked to this one"""
        issue = self.get_issue(issue_key)
        links = issue.get("fields", {}).get("issuelinks", [])
        return [link.get("outwardIssue") or link.get("inwardIssue") for link in links]
    
    def add_comment(self, issue_key: str, comment_text: str):
        """Add comment to issue"""
        import requests
        url = f"{self.url}/rest/api/3/issues/{issue_key}/comments"
        data = {"body": {"version": 1, "type": "doc", "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": comment_text}]}
        ]}}
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        logger.info(f"Added comment to {issue_key}")

class ConfluenceClient:
    """Simple Confluence API client"""
    
    def __init__(self, url: str, token: str):
        self.url = url.rstrip("/")
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_page(self, page_id: str) -> Dict:
        """Get page content"""
        import requests
        url = f"{self.url}/api/v3/pages/{page_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def update_page(self, page_id: str, title: str, content: str):
        """Update page content"""
        import requests
        page = self.get_page(page_id)
        version = page.get("version", {}).get("number", 0) + 1
        
        url = f"{self.url}/api/v3/pages/{page_id}"
        data = {
            "version": {"number": version},
            "title": title,
            "body": {"representation": "storage", "value": content}
        }
        response = requests.put(url, headers=self.headers, json=data)
        response.raise_for_status()
        logger.info(f"Updated Confluence page {page_id}")

# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

class RovoSyncOrchestrator:
    """Main system that coordinates all Phase 3 components"""
    
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        
        # Initialize API clients
        self.jira = JiraClient(config.jira_url, config.jira_token)
        self.confluence = ConfluenceClient(config.confluence_url, config.confluence_token)
        
        # Initialize Phase 3 engines
        self.change_detection = ChangeDetectionPollingLoop()
        self.decision_memory = SpaceMemory("tacs_decisions.json")
        self.decision_engine = DecisionCaptureEngine(self.decision_memory)
        self.learning_memory = LearningMemory("tacs_learning.json")
        
        self.logger.info("Rovo Sync Orchestrator initialized")
    
    def sync_planning_page(self, page_id: str, space: str):
        """
        Main sync function for a planning page
        
        Runs all Phase 3 components:
        1. Detect changes in linked Jira issues
        2. Capture decisions from comments
        3. Track continuous refinements
        4. Extract learnings
        """
        self.logger.info(f"Starting sync for page {page_id} (space: {space})")
        
        try:
            # Get planning page
            page = self.confluence.get_page(page_id)
            self.logger.info(f"Retrieved page: {page.get('title')}")
            
            # Extract linked Jira issues from custom field or page content
            # For now, assume issues are defined in config
            linked_issues = self._extract_linked_issues(page)
            
            # Run Phase 3.1: Change Detection
            self.logger.info("Running Phase 3.1: Change Detection")
            changes = self._detect_changes(linked_issues)
            
            # Run Phase 3.2: Decision Capture
            self.logger.info("Running Phase 3.2: Decision Capture")
            decisions = self._capture_decisions(linked_issues, space)
            
            # Run Phase 3.3: Continuous Refinement
            self.logger.info("Running Phase 3.3: Continuous Refinement")
            refinements = self._track_refinements(linked_issues)
            
            # Run Phase 3.4: Learning Loop
            self.logger.info("Running Phase 3.4: Learning Loop")
            learnings = self._extract_learnings(linked_issues, space)
            
            # Update Confluence page with all changes
            self.logger.info("Updating Confluence page")
            self._update_confluence_page(page_id, changes, decisions, refinements, learnings)
            
            self.logger.info(f"Sync complete for page {page_id}")
            return {
                "status": "success",
                "page_id": page_id,
                "changes_detected": len(changes),
                "decisions_captured": len(decisions),
                "refinements_tracked": len(refinements),
                "learnings_extracted": len(learnings)
            }
        
        except Exception as e:
            self.logger.error(f"Error syncing page {page_id}: {str(e)}")
            self._notify_error(f"Sync failed for page {page_id}: {str(e)}")
            return {"status": "error", "page_id": page_id, "error": str(e)}
    
    def _extract_linked_issues(self, page: Dict) -> List[str]:
        """Extract Jira issue keys from page"""
        # In real implementation, would parse page content or use custom field
        # For now, return hardcoded for demo
        return ["TACS-39", "TACS-40", "TACS-38", "TACS-42", "TACS-41"]
    
    def _detect_changes(self, issue_keys: List[str]) -> List[Dict]:
        """Run Phase 3.1: Change Detection"""
        changes = []
        for issue_key in issue_keys:
            try:
                issue = self.jira.get_issue(issue_key)
                status = issue.get("fields", {}).get("status", {}).get("name", "Unknown")
                self.logger.info(f"{issue_key}: {status}")
                # Would run change detection here
                changes.append({"issue": issue_key, "status": status})
            except Exception as e:
                self.logger.warning(f"Could not fetch {issue_key}: {str(e)}")
        return changes
    
    def _capture_decisions(self, issue_keys: List[str], space: str) -> List[Dict]:
        """Run Phase 3.2: Decision Capture"""
        decisions = []
        for issue_key in issue_keys:
            try:
                issue = self.jira.get_issue(issue_key)
                comments = issue.get("fields", {}).get("comment", {}).get("comments", [])
                
                self.logger.info(f"Processing {len(comments)} comments for {issue_key}")
                
                # Look for decision keywords in comments
                for comment in comments:
                    body = comment.get("body", {})
                    text = self._extract_text_from_adf(body)
                    
                    # Check if comment contains decision keywords
                    if any(keyword in text.lower() for keyword in ["decision:", "we decided", "agreed to"]):
                        decision = {
                            "title": f"Decision on {issue_key}",
                            "description": text[:200] + "..." if len(text) > 200 else text,
                            "issue": issue_key,
                            "author": comment.get("author", {}).get("displayName", "Unknown"),
                            "created": comment.get("created", "")
                        }
                        decisions.append(decision)
                        self.logger.info(f"Captured decision from {issue_key}")
                        
            except Exception as e:
                self.logger.warning(f"Could not process {issue_key}: {str(e)}")
        return decisions
    
    def _extract_text_from_adf(self, adf: Dict) -> str:
        """Extract plain text from Atlassian Document Format (ADF)"""
        if not adf:
            return ""
        
        text_parts = []
        
        def extract_recursive(node):
            if isinstance(node, dict):
                if node.get("type") == "text":
                    text_parts.append(node.get("text", ""))
                elif "content" in node:
                    for child in node["content"]:
                        extract_recursive(child)
            elif isinstance(node, list):
                for item in node:
                    extract_recursive(item)
        
        extract_recursive(adf)
        return " ".join(text_parts)
    
    def _track_refinements(self, issue_keys: List[str]) -> List[Dict]:
        """Run Phase 3.3: Continuous Refinement"""
        # Would track new work, corrections, etc.
        return []
    
    def _extract_learnings(self, issue_keys: List[str], space: str) -> List[Dict]:
        """Run Phase 3.4: Learning Loop"""
        # Would extract learnings from completed work
        return []
    
    def _update_confluence_page(self, page_id: str, changes: List, 
                               decisions: List, refinements: List, learnings: List):
        """Update Confluence page with results"""
        if not changes and not decisions and not refinements and not learnings:
            self.logger.info(f"No changes detected for page {page_id}")
            return
        
        # Build activity feed
        activity = self._build_activity_feed(changes, decisions, refinements, learnings)
        
        # Build updated content
        content = self._build_page_content(page_id, activity, changes, decisions, refinements, learnings)
        
        # Update the page
        try:
            page = self.confluence.get_page(page_id)
            title = page.get("title", "Planning Page - Synced")
            self.confluence.update_page(page_id, title, content)
            self.logger.info(f"Updated page {page_id} with {len(activity)} activities")
        except Exception as e:
            self.logger.error(f"Failed to update page {page_id}: {str(e)}")
    
    def _build_page_content(self, page_id: str, activity: List[str], changes: List,
                           decisions: List, refinements: List, learnings: List) -> str:
        """Build HTML content for Confluence page with all updates"""
        timestamp = datetime.now().isoformat()
        
        # Build activity feed section
        activity_html = "<h2>📢 Recent Activity</h2><ul>"
        for entry in activity:
            activity_html += f"<li>{entry} ({timestamp})</li>"
        activity_html += "</ul>"
        
        # Build changes section
        changes_html = "<h2>📊 Work Item Status</h2><table><tr><th>Issue</th><th>Status</th></tr>"
        for change in changes:
            changes_html += f"<tr><td>{change['issue']}</td><td>{change['status']}</td></tr>"
        changes_html += "</table>"
        
        # Build decisions section
        decisions_html = "<h2>📝 Decisions</h2>"
        if decisions:
            decisions_html += "<ul>"
            for decision in decisions:
                decisions_html += f"<li>{decision.get('title', 'Decision')}: {decision.get('description', '')}</li>"
            decisions_html += "</ul>"
        else:
            decisions_html += "<p>No new decisions captured.</p>"
        
        return activity_html + changes_html + decisions_html
    
    def _build_activity_feed(self, changes: List, decisions: List, 
                            refinements: List, learnings: List) -> List[str]:
        """Build activity feed entries"""
        activity = []
        for change in changes:
            activity.append(f"📊 {change['issue']}: {change['status']}")
        for decision in decisions:
            activity.append(f"💡 {decision.get('title', 'Decision')}")
        for refinement in refinements:
            activity.append(f"🔄 Refinement tracked")
        for learning in learnings:
            activity.append(f"📚 Learning extracted")
        return activity
    
    def _notify_error(self, message: str):
        """Send error notification (to Slack if configured)"""
        if self.config.slack_webhook:
            import requests
            try:
                requests.post(self.config.slack_webhook, json={"text": f"⚠️ {message}"})
            except Exception as e:
                self.logger.error(f"Could not send Slack notification: {str(e)}")
    
    def run_polling_cycle(self):
        """Run full sync for all configured planning pages"""
        self.logger.info("Starting polling cycle")
        results = []
        
        for page_id, space in self.config.planning_pages.items():
            result = self.sync_planning_page(page_id, space)
            results.append(result)
        
        self.logger.info(f"Polling cycle complete: {len(results)} pages synced")
        return results

# ============================================================================
# ENTRY POINTS
# ============================================================================

def main():
    """Main entry point for GitHub Actions / scheduled execution"""
    try:
        config = Config()
        logger = setup_logging(config.log_level)
        
        logger.info("=" * 60)
        logger.info("Rovo Sync - Polling Cycle")
        logger.info(f"Started at {datetime.now().isoformat()}")
        logger.info("=" * 60)
        
        orchestrator = RovoSyncOrchestrator(config, logger)
        results = orchestrator.run_polling_cycle()
        
        logger.info("=" * 60)
        logger.info(f"Cycle complete - {len(results)} pages processed")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise

def webhook_handler(event_data: Dict) -> Dict:
    """Entry point for webhook (real-time updates)"""
    logger = setup_logging()
    logger.info(f"Webhook received: {event_data.get('webhookEvent')}")
    
    try:
        config = Config()
        orchestrator = RovoSyncOrchestrator(config, logger)
        
        # Handle specific webhook events
        event_type = event_data.get("webhookEvent")
        
        if event_type == "jira:issue_updated":
            issue_key = event_data.get("issue", {}).get("key")
            logger.info(f"Processing webhook for {issue_key}")
            # Would sync related planning page
        
        return {"status": "success", "message": "Webhook processed"}
    
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    main()

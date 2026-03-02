#!/usr/bin/env python3
"""
Phase 3.3: Continuous Plan Refinement Implementation
Enable teams to iterate on plans as execution unfolds

Features:
- Detect new work discovered during execution
- Capture course corrections
- Handle blocker resolution
- Support scope changes
- Track priority shifts
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class RefinementEntry:
    """Represents a plan refinement"""
    entry_id: str
    page_id: str
    refinement_type: str  # new_work, course_correction, blocker_resolved, scope_change, priority_shift
    title: str
    description: str
    related_issue: str
    impact: str  # How this affects timeline/scope
    timestamp: str
    in_scope: Optional[bool] = None  # For new work decisions
    timeline_impact_days: Optional[int] = None

# ============================================================================
# REFINEMENT DETECTION
# ============================================================================

class RefinementDetector:
    """Detects different types of plan refinements"""
    
    @staticmethod
    def detect_new_work(linked_issues_before: List[str], 
                       linked_issues_after: List[str]) -> List[str]:
        """Detect newly linked issues (new work discovered)"""
        return list(set(linked_issues_after) - set(linked_issues_before))
    
    @staticmethod
    def detect_course_correction(estimated_days: int, 
                                actual_days: int, 
                                progress_percent: int) -> Optional[Dict]:
        """
        Detect if work is taking longer than estimated
        
        Returns correction info if detected
        """
        if actual_days > estimated_days * 1.2:  # 20% over
            remaining_days = estimated_days - actual_days
            if remaining_days < 0:
                return {
                    "overrun_days": abs(remaining_days),
                    "progress_percent": progress_percent,
                    "original_estimate": estimated_days,
                    "actual_so_far": actual_days
                }
        
        return None
    
    @staticmethod
    def detect_blocker_resolution(was_blocked: bool, 
                                 now_blocked: bool,
                                 blocking_issue: Optional[str] = None) -> bool:
        """Detect when a blocker is resolved"""
        return was_blocked and not now_blocked

# ============================================================================
# REFINEMENT PROCESSOR
# ============================================================================

class RefinementProcessor:
    """Process refinements and update planning page"""
    
    @staticmethod
    def process_new_work(new_issue_key: str, discovered_during: str) -> RefinementEntry:
        """
        Process discovery of new work
        
        Args:
            new_issue_key: Jira issue key of new work
            discovered_during: Which issue this was discovered during
        
        Returns:
            RefinementEntry for new work
        """
        entry_id = f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return RefinementEntry(
            entry_id=entry_id,
            page_id="",  # To be filled by caller
            refinement_type="new_work",
            title=f"New Work: {new_issue_key}",
            description=f"Work discovered during {discovered_during} implementation",
            related_issue=new_issue_key,
            impact="Impact TBD - needs estimation",
            timestamp=datetime.now().isoformat(),
            in_scope=None  # Team to decide
        )
    
    @staticmethod
    def process_course_correction(issue_key: str, 
                                 correction_info: Dict) -> RefinementEntry:
        """Process course correction for overrunning work"""
        overrun_days = correction_info.get("overrun_days", 0)
        
        entry_id = f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return RefinementEntry(
            entry_id=entry_id,
            page_id="",
            refinement_type="course_correction",
            title=f"Course Correction: {issue_key}",
            description=f"{issue_key} is taking longer than estimated. " \
                       f"Originally 3 days, now at {correction_info['actual_so_far']} days " \
                       f"with {correction_info['progress_percent']}% complete.",
            related_issue=issue_key,
            impact=f"Timeline extends by {overrun_days} days",
            timestamp=datetime.now().isoformat(),
            timeline_impact_days=overrun_days
        )
    
    @staticmethod
    def process_blocker_resolution(issue_key: str, 
                                  was_blocked_by: str) -> RefinementEntry:
        """Process resolution of a blocker"""
        entry_id = f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return RefinementEntry(
            entry_id=entry_id,
            page_id="",
            refinement_type="blocker_resolved",
            title=f"Blocker Resolved: {issue_key}",
            description=f"{issue_key} was blocked by {was_blocked_by}. " \
                       f"Blocker now resolved - work can proceed.",
            related_issue=issue_key,
            impact="Unblocks downstream work",
            timestamp=datetime.now().isoformat()
        )
    
    @staticmethod
    def process_scope_change(issue_key: str, scope_change_desc: str, 
                            timeline_impact_days: int) -> RefinementEntry:
        """Process scope change in work item"""
        entry_id = f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return RefinementEntry(
            entry_id=entry_id,
            page_id="",
            refinement_type="scope_change",
            title=f"Scope Change: {issue_key}",
            description=scope_change_desc,
            related_issue=issue_key,
            impact=f"Timeline changes by {timeline_impact_days} days",
            timestamp=datetime.now().isoformat(),
            timeline_impact_days=timeline_impact_days
        )
    
    @staticmethod
    def process_priority_shift(changes: Dict[str, int]) -> RefinementEntry:
        """
        Process priority shifts across multiple items
        
        Args:
            changes: Dict of {issue_key: new_priority}
        
        Returns:
            RefinementEntry for priority shift
        """
        entry_id = f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        issue_list = ", ".join(changes.keys())
        
        return RefinementEntry(
            entry_id=entry_id,
            page_id="",
            refinement_type="priority_shift",
            title="Priority Reordering",
            description=f"Based on new information, priorities adjusted for: {issue_list}",
            related_issue="",
            impact="Execution sequence changed",
            timestamp=datetime.now().isoformat()
        )

# ============================================================================
# REFINEMENT LOG
# ============================================================================

class RefinementLog:
    """Maintains log of all refinements to a planning page"""
    
    def __init__(self, page_id: str):
        self.page_id = page_id
        self.entries: List[RefinementEntry] = []
    
    def add_refinement(self, entry: RefinementEntry):
        """Add refinement entry to log"""
        entry.page_id = self.page_id
        self.entries.append(entry)
    
    def get_refinements_by_type(self, refinement_type: str) -> List[RefinementEntry]:
        """Get refinements of a specific type"""
        return [e for e in self.entries if e.refinement_type == refinement_type]
    
    def get_timeline_impact(self) -> int:
        """Calculate total timeline impact from all refinements"""
        total_impact = 0
        for entry in self.entries:
            if entry.timeline_impact_days:
                total_impact += entry.timeline_impact_days
        return total_impact
    
    def get_new_work_in_scope(self) -> List[str]:
        """Get new work items added to scope"""
        new_work = self.get_refinements_by_type("new_work")
        in_scope = [e.related_issue for e in new_work if e.in_scope]
        return in_scope
    
    def to_markdown(self) -> str:
        """Format refinement log as Confluence markdown"""
        markdown = "## 🔄 Refinements & Iterations\n\n"
        
        if not self.entries:
            markdown += "*No refinements yet*\n"
            return markdown
        
        # Group by type
        by_type = {}
        for entry in self.entries:
            if entry.refinement_type not in by_type:
                by_type[entry.refinement_type] = []
            by_type[entry.refinement_type].append(entry)
        
        # Format each type
        type_labels = {
            "new_work": "📝 New Work Discovered",
            "course_correction": "🔄 Course Corrections",
            "blocker_resolved": "✅ Blockers Resolved",
            "scope_change": "📊 Scope Changes",
            "priority_shift": "⬆️ Priority Shifts"
        }
        
        for ref_type, label in type_labels.items():
            if ref_type in by_type:
                markdown += f"### {label}\n"
                for entry in by_type[ref_type]:
                    markdown += f"- **{entry.related_issue or 'General'}**: " \
                               f"{entry.description} " \
                               f"({entry.timestamp[:10]})\n"
                markdown += "\n"
        
        # Summary
        total_days = self.get_timeline_impact()
        if total_days != 0:
            markdown += f"**Timeline Impact:** +{total_days} days\n"
        
        return markdown

# ============================================================================
# PLANNING PAGE UPDATER
# ============================================================================

class PlanningPageUpdater:
    """Updates Confluence planning page with refinements"""
    
    @staticmethod
    def add_new_work_item(page_content: str, new_work_key: str, 
                         description: str) -> str:
        """Add new work item to Work Breakdown section"""
        # In real implementation, would parse markdown and insert
        # For now, return with notation
        return page_content
    
    @staticmethod
    def update_timeline(page_content: str, old_date: str, 
                       new_date: str) -> str:
        """Update timeline due date"""
        # In real implementation, would update date fields
        return page_content
    
    @staticmethod
    def add_refinement_section(page_content: str, 
                             refinement_log: RefinementLog) -> str:
        """Add/update refinement section with log"""
        refinement_markdown = refinement_log.to_markdown()
        
        # In real implementation, would find and replace section
        # For now, return with notation
        return page_content

# ============================================================================
# CONTINUOUS REFINEMENT ENGINE
# ============================================================================

class ContinuousRefinementEngine:
    """Main engine for continuous plan refinement"""
    
    def __init__(self, page_id: str):
        self.page_id = page_id
        self.log = RefinementLog(page_id)
        self.detector = RefinementDetector()
        self.processor = RefinementProcessor()
    
    def handle_new_work_discovery(self, new_issue_key: str, 
                                 discovered_during: str) -> RefinementEntry:
        """Handle discovery of new work"""
        entry = self.processor.process_new_work(new_issue_key, discovered_during)
        self.log.add_refinement(entry)
        return entry
    
    def handle_course_correction(self, issue_key: str, 
                                estimated_days: int,
                                actual_days: int,
                                progress_percent: int) -> Optional[RefinementEntry]:
        """Handle course correction for overrunning work"""
        correction = self.detector.detect_course_correction(
            estimated_days, actual_days, progress_percent
        )
        
        if correction:
            entry = self.processor.process_course_correction(issue_key, correction)
            self.log.add_refinement(entry)
            return entry
        
        return None
    
    def handle_blocker_resolution(self, issue_key: str, 
                                 was_blocked_by: str) -> RefinementEntry:
        """Handle resolution of blocker"""
        entry = self.processor.process_blocker_resolution(issue_key, was_blocked_by)
        self.log.add_refinement(entry)
        return entry
    
    def handle_scope_change(self, issue_key: str, 
                           description: str,
                           timeline_impact_days: int) -> RefinementEntry:
        """Handle scope change"""
        entry = self.processor.process_scope_change(
            issue_key, description, timeline_impact_days
        )
        self.log.add_refinement(entry)
        return entry
    
    def decide_new_work_scope(self, new_issue_key: str, in_scope: bool):
        """Decide if new work is in scope"""
        new_work_entries = self.log.get_refinements_by_type("new_work")
        for entry in new_work_entries:
            if entry.related_issue == new_issue_key:
                entry.in_scope = in_scope
                break
    
    def get_current_timeline_impact(self) -> int:
        """Get total timeline impact from refinements"""
        return self.log.get_timeline_impact()

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """Example usage of continuous refinement system"""
    
    # Create engine for demo page
    engine = ContinuousRefinementEngine(page_id="3670017")
    
    # Scenario 1: New work discovered
    print("=== New Work Discovery ===")
    new_work = engine.handle_new_work_discovery(
        new_issue_key="TACS-43",
        discovered_during="TACS-42"
    )
    print(f"New work: {new_work.title}")
    print(f"Description: {new_work.description}\n")
    
    # Team decides scope
    engine.decide_new_work_scope("TACS-43", in_scope=True)
    
    # Scenario 2: Course correction
    print("=== Course Correction ===")
    correction = engine.handle_course_correction(
        issue_key="TACS-42",
        estimated_days=3,
        actual_days=2,
        progress_percent=30
    )
    if correction:
        print(f"Correction: {correction.title}")
        print(f"Impact: {correction.impact}\n")
    
    # Scenario 3: Blocker resolution
    print("=== Blocker Resolution ===")
    resolved = engine.handle_blocker_resolution(
        issue_key="TACS-42",
        was_blocked_by="TACS-40"
    )
    print(f"Resolved: {resolved.title}")
    print(f"Impact: {resolved.impact}\n")
    
    # Scenario 4: Scope change
    print("=== Scope Change ===")
    scope = engine.handle_scope_change(
        issue_key="TACS-40",
        description="Reduced from 5 to 3 tab sections based on user feedback",
        timeline_impact_days=-1
    )
    print(f"Change: {scope.title}")
    print(f"Impact: {scope.impact}\n")
    
    # Summary
    print("=== Refinement Summary ===")
    print(f"Total timeline impact: {engine.get_current_timeline_impact()} days")
    print(f"New work in scope: {engine.log.get_new_work_in_scope()}")
    print("\nRefinement Log:")
    print(engine.log.to_markdown())

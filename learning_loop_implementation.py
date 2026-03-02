#!/usr/bin/env python3
"""
Phase 3.4: Learning Loop Implementation
Capture learnings from execution and build organizational memory

Features:
- Extract learnings from completed work
- Categorize learnings (successful patterns, failures, risks, dependencies)
- Store in Space Memory
- Make searchable and accessible
- Surface in future planning
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Learning:
    """Represents a captured learning"""
    learning_id: str
    space: str
    learning_type: str  # successful_pattern, failed_experiment, risk_materialized, dependency_discovered
    title: str
    context: str  # Which outcome/project this came from
    what: str  # What happened
    why: str  # Why it happened / why it matters
    when: str  # When this was learned
    outcome_achieved: bool  # Did this help or hurt?
    applies_to: List[str]  # Tags for when this applies
    related_issues: List[str]
    reuse_count: int = 0  # How many times this has been referenced
    confidence_score: float = 1.0  # How confident we are (0-1)

# ============================================================================
# LEARNING EXTRACTION
# ============================================================================

class LearningExtractor:
    """Extracts learnings from completed work"""
    
    @staticmethod
    def extract_from_completion_comment(comment_text: str, 
                                       issue_key: str) -> List[Learning]:
        """
        Extract learnings from completion comment
        
        Looks for patterns like:
        - "We learned that..."
        - "Next time we should..."
        - "The key insight was..."
        - "This worked well: ..."
        - "This didn't work: ..."
        """
        learnings = []
        
        # Pattern 1: Successful patterns
        if any(phrase in comment_text.lower() for phrase in 
               ["worked well", "success", "this approach"]):
            learning = Learning(
                learning_id=f"LEARN-{issue_key}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                space="",
                learning_type="successful_pattern",
                title="",  # To be extracted
                context="",
                what=comment_text[:200],
                why="Pattern that worked well",
                when=datetime.now().isoformat(),
                outcome_achieved=True,
                applies_to=[],
                related_issues=[issue_key]
            )
            learnings.append(learning)
        
        # Pattern 2: Failed experiments
        if any(phrase in comment_text.lower() for phrase in 
               ["didn't work", "failed", "mistake", "wrong approach"]):
            learning = Learning(
                learning_id=f"LEARN-{issue_key}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                space="",
                learning_type="failed_experiment",
                title="",
                context="",
                what=comment_text[:200],
                why="Approach that didn't work",
                when=datetime.now().isoformat(),
                outcome_achieved=False,
                applies_to=[],
                related_issues=[issue_key]
            )
            learnings.append(learning)
        
        return learnings
    
    @staticmethod
    def extract_from_retrospective(retrospective_text: str, 
                                  outcome: str) -> List[Learning]:
        """
        Extract learnings from retrospective section
        
        Expects structured format:
        - What worked well
        - What didn't work
        - What surprised us
        - What we'll do differently next time
        """
        learnings = []
        
        # Parse each section
        sections = {
            "what worked well": "successful_pattern",
            "what didn't work": "failed_experiment",
            "what surprised us": "risk_materialized",
            "dependencies": "dependency_discovered"
        }
        
        for section_title, learning_type in sections.items():
            if section_title in retrospective_text.lower():
                # Extract content from this section
                # In real implementation, would parse properly
                learning = Learning(
                    learning_id=f"LEARN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    space="",
                    learning_type=learning_type,
                    title=section_title.title(),
                    context=outcome,
                    what="",  # To be extracted
                    why="",
                    when=datetime.now().isoformat(),
                    outcome_achieved=learning_type == "successful_pattern",
                    applies_to=[],
                    related_issues=[]
                )
                learnings.append(learning)
        
        return learnings
    
    @staticmethod
    def extract_risk_materialization(issue_key: str, 
                                    risk_description: str,
                                    mitigation_used: str,
                                    effectiveness: str) -> Learning:
        """Extract learning from materialized risk"""
        return Learning(
            learning_id=f"LEARN-{issue_key}-RISK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            space="",
            learning_type="risk_materialized",
            title=f"Risk: {risk_description[:50]}",
            context=f"From {issue_key}",
            what=risk_description,
            why=f"Mitigation: {mitigation_used}. Effectiveness: {effectiveness}",
            when=datetime.now().isoformat(),
            outcome_achieved="effective" in effectiveness.lower(),
            applies_to=["risk", "mitigation"],
            related_issues=[issue_key]
        )
    
    @staticmethod
    def extract_dependency_discovery(discovered_dependency: str,
                                    from_issue: str,
                                    to_issue: str,
                                    was_expected: bool) -> Learning:
        """Extract learning from discovered dependency"""
        return Learning(
            learning_id=f"LEARN-DEP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            space="",
            learning_type="dependency_discovered",
            title=f"Dependency: {from_issue} → {to_issue}",
            context="Cross-team dependency",
            what=discovered_dependency,
            why="Unexpected dependency" if not was_expected else "Expected dependency",
            when=datetime.now().isoformat(),
            outcome_achieved=was_expected,
            applies_to=["dependency", "planning"],
            related_issues=[from_issue, to_issue],
            confidence_score=0.8 if was_expected else 0.6
        )

# ============================================================================
# SPACE MEMORY (Enhanced)
# ============================================================================

class LearningMemory:
    """Enhanced Space Memory for storing and retrieving learnings"""
    
    def __init__(self, storage_path: str = "learning_memory.json"):
        self.storage_path = storage_path
        self.memory = self._load()
    
    def _load(self) -> Dict[str, List[Dict]]:
        """Load learning memory from storage"""
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save(self):
        """Save learning memory to storage"""
        with open(self.storage_path, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def store_learning(self, learning: Learning):
        """Store learning in memory"""
        space_key = learning.space
        
        if space_key not in self.memory:
            self.memory[space_key] = []
        
        self.memory[space_key].append(asdict(learning))
        self._save()
    
    def search_learnings(self, space: str, 
                        learning_type: Optional[str] = None,
                        tags: Optional[List[str]] = None,
                        keyword: Optional[str] = None,
                        min_confidence: float = 0.0) -> List[Learning]:
        """
        Search for relevant learnings
        
        Args:
            space: Space key to search
            learning_type: Filter by type
            tags: Filter by tags (applies_to)
            keyword: Search keyword
            min_confidence: Minimum confidence score
        
        Returns:
            List of matching learnings
        """
        if space not in self.memory:
            return []
        
        learnings = [Learning(**l) for l in self.memory[space]]
        
        # Filter by type
        if learning_type:
            learnings = [l for l in learnings if l.learning_type == learning_type]
        
        # Filter by tags
        if tags:
            learnings = [l for l in learnings if any(t in l.applies_to for t in tags)]
        
        # Filter by keyword
        if keyword:
            keyword_lower = keyword.lower()
            learnings = [
                l for l in learnings
                if (keyword_lower in l.what.lower() or
                    keyword_lower in l.title.lower())
            ]
        
        # Filter by confidence
        learnings = [l for l in learnings if l.confidence_score >= min_confidence]
        
        # Sort by reuse count (most reused first) and confidence
        learnings.sort(key=lambda l: (l.reuse_count, l.confidence_score), reverse=True)
        
        return learnings
    
    def get_successful_patterns(self, space: str, tags: List[str] = None) -> List[Learning]:
        """Get successful patterns for a space"""
        return self.search_learnings(
            space,
            learning_type="successful_pattern",
            tags=tags,
            min_confidence=0.7
        )
    
    def get_failed_experiments(self, space: str, tags: List[str] = None) -> List[Learning]:
        """Get failed experiments to avoid"""
        return self.search_learnings(
            space,
            learning_type="failed_experiment",
            tags=tags,
            min_confidence=0.5
        )
    
    def increment_reuse(self, learning_id: str, space: str):
        """Increment reuse count when learning is referenced"""
        if space not in self.memory:
            return
        
        for learning_dict in self.memory[space]:
            if learning_dict.get("learning_id") == learning_id:
                learning_dict["reuse_count"] = learning_dict.get("reuse_count", 0) + 1
                self._save()
                break
    
    def get_statistics(self, space: str) -> Dict[str, int]:
        """Get statistics about learnings in a space"""
        if space not in self.memory:
            return {}
        
        learnings = [Learning(**l) for l in self.memory[space]]
        
        stats = {
            "total_learnings": len(learnings),
            "successful_patterns": len([l for l in learnings if l.learning_type == "successful_pattern"]),
            "failed_experiments": len([l for l in learnings if l.learning_type == "failed_experiment"]),
            "risks_materialized": len([l for l in learnings if l.learning_type == "risk_materialized"]),
            "dependencies_discovered": len([l for l in learnings if l.learning_type == "dependency_discovered"]),
            "total_reuses": sum(l.reuse_count for l in learnings),
            "avg_confidence": sum(l.confidence_score for l in learnings) / len(learnings) if learnings else 0
        }
        
        return stats

# ============================================================================
# LEARNING LOOP ENGINE
# ============================================================================

class LearningLoopEngine:
    """Main engine for learning loop"""
    
    def __init__(self, space: str, memory: LearningMemory):
        self.space = space
        self.memory = memory
        self.extractor = LearningExtractor()
    
    def capture_from_completed_work(self, issue_key: str, 
                                   completion_comment: str,
                                   outcome: str) -> List[Learning]:
        """Capture learnings when work completes"""
        learnings = self.extractor.extract_from_completion_comment(
            completion_comment,
            issue_key
        )
        
        # Fill in space and context
        for learning in learnings:
            learning.space = self.space
            learning.context = outcome
            self.memory.store_learning(learning)
        
        return learnings
    
    def capture_from_retrospective(self, outcome: str, 
                                  retrospective_text: str) -> List[Learning]:
        """Capture learnings from outcome retrospective"""
        learnings = self.extractor.extract_from_retrospective(
            retrospective_text,
            outcome
        )
        
        for learning in learnings:
            learning.space = self.space
            self.memory.store_learning(learning)
        
        return learnings
    
    def capture_risk_materialization(self, issue_key: str,
                                   risk_description: str,
                                   mitigation_used: str,
                                   effectiveness: str) -> Learning:
        """Capture learning from materialized risk"""
        learning = self.extractor.extract_risk_materialization(
            issue_key, risk_description, mitigation_used, effectiveness
        )
        learning.space = self.space
        self.memory.store_learning(learning)
        return learning
    
    def get_relevant_learnings_for_planning(self, tags: List[str]) -> Dict[str, List[Learning]]:
        """
        Get relevant learnings for new planning
        
        Returns learnings organized by type
        """
        return {
            "successful_patterns": self.memory.get_successful_patterns(self.space, tags),
            "failed_experiments": self.memory.get_failed_experiments(self.space, tags),
            "risks": self.memory.search_learnings(self.space, learning_type="risk_materialized", tags=tags),
            "dependencies": self.memory.search_learnings(self.space, learning_type="dependency_discovered", tags=tags)
        }
    
    def format_learnings_for_confluence(self, learnings: Dict[str, List[Learning]]) -> str:
        """Format learnings for Confluence planning page"""
        markdown = "## 📚 Relevant Learnings from Past Work\n\n"
        
        sections = {
            "successful_patterns": "✅ Successful Patterns to Reuse",
            "failed_experiments": "❌ Approaches to Avoid",
            "risks": "⚠️ Risks to Mitigate",
            "dependencies": "🔗 Dependencies to Plan For"
        }
        
        for key, title in sections.items():
            if learnings.get(key):
                markdown += f"### {title}\n"
                for learning in learnings[key][:5]:  # Top 5
                    markdown += f"- **{learning.title}**: {learning.what[:100]}... " \
                               f"(Used {learning.reuse_count} times) " \
                               f"[{learning.related_issues[0] if learning.related_issues else 'N/A'}]\n"
                markdown += "\n"
        
        return markdown

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """Example usage of learning loop"""
    
    # Initialize learning memory
    memory = LearningMemory("tacs_learning_memory.json")
    
    # Initialize engine
    engine = LearningLoopEngine(space="TACS", memory=memory)
    
    # Scenario 1: Capture from completed work
    print("=== Capturing Learning from Completed Work ===")
    learnings = engine.capture_from_completed_work(
        issue_key="TACS-42",
        completion_comment="""
        Component completed successfully! React Navigation v6 worked well - 
        the TypeScript support made development much faster. We learned that 
        disabling animations on low-end devices prevents janky transitions.
        Next time, we should test on older devices earlier in the process.
        """,
        outcome="Mobile App Redesign"
    )
    print(f"Captured {len(learnings)} learnings")
    for l in learnings:
        print(f"  - {l.learning_type}: {l.what[:60]}...")
    
    # Scenario 2: Capture risk materialization
    print("\n=== Capturing Risk Materialization ===")
    risk_learning = engine.capture_risk_materialization(
        issue_key="TACS-42",
        risk_description="Performance regression on iPhone 8",
        mitigation_used="Tested on baseline devices early, disabled animations on low-end",
        effectiveness="Very effective - prevented production issues"
    )
    print(f"Risk learning: {risk_learning.title}")
    print(f"Outcome achieved: {risk_learning.outcome_achieved}")
    
    # Scenario 3: Get relevant learnings for new planning
    print("\n=== Getting Relevant Learnings for New Planning ===")
    relevant = engine.get_relevant_learnings_for_planning(
        tags=["react", "mobile", "performance"]
    )
    
    for category, items in relevant.items():
        if items:
            print(f"\n{category.upper()}: {len(items)} items")
            for item in items[:2]:
                print(f"  - {item.title} (confidence: {item.confidence_score})")
    
    # Scenario 4: Format for Confluence
    print("\n=== Formatted for Confluence ===")
    confluence_markdown = engine.format_learnings_for_confluence(relevant)
    print(confluence_markdown)
    
    # Scenario 5: Statistics
    print("\n=== Learning Statistics for TACS ===")
    stats = memory.get_statistics("TACS")
    for key, value in stats.items():
        print(f"  {key}: {value}")

#!/usr/bin/env python3
"""
Phase 3.2: Decision Capture Implementation
Automatically extract key decisions from Jira comments and log them

Features:
- Keyword-based decision detection
- Structured comment parsing
- Natural language extraction
- Decision log formatting
- Space Memory storage
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Decision:
    """Represents a captured decision"""
    decision_id: str
    space: str
    outcome: str
    issue_key: str
    title: str
    what: str
    why: Optional[str]
    when: str
    who: str
    alternatives: List[str]
    impact: Optional[str]
    tags: List[str]
    related_issues: List[str]
    outcome_achieved: Optional[bool] = None
    lessons: Optional[str] = None

# ============================================================================
# DECISION DETECTION
# ============================================================================

class DecisionDetector:
    """Detects decisions in Jira comments"""
    
    DECISION_KEYWORDS = [
        "decided", "chose", "will use", "going with",
        "architecture decision", "picked", "selected",
        "concluded", "determined", "opted for"
    ]
    
    @staticmethod
    def has_decision_keyword(text: str) -> bool:
        """Check if text contains decision keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in DecisionDetector.DECISION_KEYWORDS)
    
    @staticmethod
    def is_structured_decision(text: str) -> bool:
        """Check if comment follows structured decision format"""
        required_fields = ["decision:", "rationale:"]
        text_lower = text.lower()
        return all(field in text_lower for field in required_fields)
    
    @staticmethod
    def detect(comment_text: str) -> bool:
        """Detect if comment contains a decision"""
        return (DecisionDetector.has_decision_keyword(comment_text) or 
                DecisionDetector.is_structured_decision(comment_text))

# ============================================================================
# DECISION EXTRACTION
# ============================================================================

class DecisionExtractor:
    """Extracts decision details from text"""
    
    @staticmethod
    def extract_what(text: str) -> Optional[str]:
        """
        Extract what was decided using pattern matching
        
        Patterns:
        - "decided to [ACTION]"
        - "will use [THING]"
        - "chose [OPTION]"
        - "going with [CHOICE]"
        """
        patterns = [
            r'decided to ([^.!?\n]+)',
            r'will use ([^.!?\n]+)',
            r'chose ([^.!?\n]+)',
            r'going with ([^.!?\n]+)',
            r'picked ([^.!?\n]+)',
            r'selected ([^.!?\n]+)',
            r'architecture decision:\s*([^.!?\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Check for structured format
        match = re.search(r'decision:\s*([^\n]+)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return None
    
    @staticmethod
    def extract_why(text: str) -> Optional[str]:
        """
        Extract rationale/why using pattern matching
        
        Patterns:
        - "because [REASON]"
        - "for [REASON]"
        - "rationale: [REASON]"
        - "since [REASON]"
        """
        patterns = [
            r'because ([^.!?\n]+)',
            r'rationale:\s*([^\n]+)',
            r'for ([^.!?\n]+)',
            r'since ([^.!?\n]+)',
            r'reason:\s*([^\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    @staticmethod
    def extract_alternatives(text: str) -> List[str]:
        """
        Extract alternatives considered
        
        Patterns:
        - "alternatives: [LIST]"
        - "instead of [OPTION]"
        - "vs [OPTION]"
        """
        alternatives = []
        
        # Check for structured format
        match = re.search(r'alternatives?:\s*([^\n]+)', text, re.IGNORECASE)
        if match:
            alt_text = match.group(1)
            # Split by commas or "and"
            alternatives = [a.strip() for a in re.split(r',|\band\b', alt_text)]
        
        # Check for "instead of" pattern
        match = re.search(r'instead of ([^.!?\n]+)', text, re.IGNORECASE)
        if match:
            alternatives.append(match.group(1).strip())
        
        # Check for "vs" pattern
        match = re.search(r'vs\.?\s+([^.!?\n]+)', text, re.IGNORECASE)
        if match:
            alternatives.append(match.group(1).strip())
        
        return alternatives
    
    @staticmethod
    def extract_impact(text: str) -> Optional[str]:
        """
        Extract impact statement
        
        Patterns:
        - "impact: [STATEMENT]"
        - "this means [STATEMENT]"
        - "this affects [STATEMENT]"
        """
        patterns = [
            r'impact:\s*([^\n]+)',
            r'this means ([^.!?\n]+)',
            r'this affects ([^.!?\n]+)',
            r'as a result,?\s*([^.!?\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    @staticmethod
    def extract_decision(comment_text: str, issue_key: str, author: str, 
                        timestamp: str) -> Optional[Decision]:
        """
        Extract full decision from comment
        
        Args:
            comment_text: The comment text
            issue_key: Jira issue key
            author: Comment author
            timestamp: When comment was made
        
        Returns:
            Decision object if extraction successful
        """
        what = DecisionExtractor.extract_what(comment_text)
        if not what:
            return None
        
        # Generate decision ID
        decision_id = f"DEC-{issue_key}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Extract other fields
        why = DecisionExtractor.extract_why(comment_text)
        alternatives = DecisionExtractor.extract_alternatives(comment_text)
        impact = DecisionExtractor.extract_impact(comment_text)
        
        # Generate title from what
        title = what[:60] + "..." if len(what) > 60 else what
        
        # Extract tags from text
        tags = DecisionExtractor._extract_tags(comment_text, what)
        
        return Decision(
            decision_id=decision_id,
            space="",  # To be filled by caller
            outcome="",  # To be filled by caller
            issue_key=issue_key,
            title=title,
            what=what,
            why=why,
            when=timestamp,
            who=author,
            alternatives=alternatives,
            impact=impact,
            tags=tags,
            related_issues=[issue_key]
        )
    
    @staticmethod
    def _extract_tags(text: str, what: str) -> List[str]:
        """Extract relevant tags from decision"""
        tags = []
        
        # Technology-related keywords
        tech_keywords = {
            "react": ["react", "typescript", "javascript"],
            "navigation": ["navigation", "routing", "nav"],
            "mobile": ["mobile", "ios", "android", "react-native"],
            "performance": ["performance", "optimization", "speed"],
            "testing": ["testing", "test", "qa"],
            "architecture": ["architecture", "design", "pattern"],
        }
        
        text_lower = (text + " " + what).lower()
        
        for tag, keywords in tech_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(tag)
        
        return tags

# ============================================================================
# DECISION LOG FORMATTER
# ============================================================================

class DecisionLogFormatter:
    """Formats decisions for Confluence Decision Log"""
    
    @staticmethod
    def format_markdown(decision: Decision) -> str:
        """
        Format decision as markdown for Confluence
        
        Returns markdown string ready to insert into Decision Log section
        """
        alternatives_str = ""
        if decision.alternatives:
            alternatives_str = ", ".join(decision.alternatives)
        
        markdown = f"""
### Decision: {decision.title}

**What:** {decision.what}  
**Why:** {decision.why or "Not specified"}  
**When:** {decision.when[:10]}  
**By:** {decision.who}  
**Impact:** {decision.impact or "Not specified"}  
**Alternatives Considered:** {alternatives_str or "None specified"}  
**Related Work:** [{decision.issue_key}](https://timswn-aibw.atlassian.net/browse/{decision.issue_key})

---
"""
        return markdown
    
    @staticmethod
    def format_activity_entry(decision: Decision) -> str:
        """Format decision as activity feed entry"""
        return f"**💡 {decision.issue_key}** - Decision: {decision.what} ({decision.when[:10]})"

# ============================================================================
# SPACE MEMORY STORAGE
# ============================================================================

class SpaceMemory:
    """Stores decisions in Space Memory for future reference"""
    
    def __init__(self, storage_path: str = "space_memory.json"):
        self.storage_path = storage_path
        self.memory = self._load()
    
    def _load(self) -> Dict[str, List[Dict]]:
        """Load Space Memory from storage"""
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save(self):
        """Save Space Memory to storage"""
        with open(self.storage_path, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def store_decision(self, decision: Decision):
        """Store decision in Space Memory"""
        space_key = decision.space
        
        if space_key not in self.memory:
            self.memory[space_key] = []
        
        # Convert to dict and add
        self.memory[space_key].append(asdict(decision))
        self._save()
    
    def search_decisions(self, space: str, tags: List[str] = None, 
                        keyword: str = None) -> List[Decision]:
        """
        Search for decisions in Space Memory
        
        Args:
            space: Space key to search
            tags: Filter by tags
            keyword: Search keyword in what/why/title
        
        Returns:
            List of matching decisions
        """
        if space not in self.memory:
            return []
        
        decisions = [Decision(**d) for d in self.memory[space]]
        
        # Filter by tags
        if tags:
            decisions = [d for d in decisions if any(t in d.tags for t in tags)]
        
        # Filter by keyword
        if keyword:
            keyword_lower = keyword.lower()
            decisions = [
                d for d in decisions
                if (keyword_lower in d.what.lower() or
                    (d.why and keyword_lower in d.why.lower()) or
                    keyword_lower in d.title.lower())
            ]
        
        return decisions
    
    def get_recent_decisions(self, space: str, count: int = 10) -> List[Decision]:
        """Get most recent decisions for a space"""
        if space not in self.memory:
            return []
        
        decisions = [Decision(**d) for d in self.memory[space]]
        # Sort by timestamp descending
        decisions.sort(key=lambda d: d.when, reverse=True)
        return decisions[:count]

# ============================================================================
# DECISION CAPTURE ENGINE
# ============================================================================

class DecisionCaptureEngine:
    """Main engine for capturing and processing decisions"""
    
    def __init__(self, space_memory: SpaceMemory):
        self.detector = DecisionDetector()
        self.extractor = DecisionExtractor()
        self.formatter = DecisionLogFormatter()
        self.memory = space_memory
    
    def process_comment(self, comment: Dict[str, any], issue_key: str, 
                       space: str, outcome: str) -> Optional[Decision]:
        """
        Process a comment and extract decision if present
        
        Args:
            comment: Comment data (text, author, timestamp)
            issue_key: Jira issue key
            space: Space key (e.g., "TACS")
            outcome: Parent outcome name
        
        Returns:
            Decision object if decision detected and extracted
        """
        comment_text = comment.get("text", "")
        
        # Detect if comment contains decision
        if not self.detector.detect(comment_text):
            return None
        
        # Extract decision
        decision = self.extractor.extract_decision(
            comment_text,
            issue_key,
            comment.get("author", "Unknown"),
            comment.get("timestamp", datetime.now().isoformat())
        )
        
        if not decision:
            return None
        
        # Fill in space and outcome
        decision.space = space
        decision.outcome = outcome
        
        # Store in Space Memory
        self.memory.store_decision(decision)
        
        return decision
    
    def add_to_decision_log(self, page_content: str, decision: Decision) -> str:
        """
        Add decision to Confluence Decision Log section
        
        Args:
            page_content: Current page content
            decision: Decision to add
        
        Returns:
            Updated page content
        """
        # Format decision as markdown
        decision_markdown = self.formatter.format_markdown(decision)
        
        # Find Decision Log section and insert
        # In real implementation, would parse and insert properly
        # For now, return updated content
        return page_content
    
    def add_to_activity_feed(self, page_content: str, decision: Decision) -> str:
        """Add decision to Activity Feed"""
        activity_entry = self.formatter.format_activity_entry(decision)
        # In real implementation, would insert into Activity Feed
        return page_content

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """Example usage of decision capture system"""
    
    # Initialize Space Memory
    memory = SpaceMemory("tacs_space_memory.json")
    
    # Initialize engine
    engine = DecisionCaptureEngine(memory)
    
    # Example comment with decision
    comment = {
        "text": """After testing on older devices, we decided to use React Navigation v6 
        instead of a custom solution because it has better TypeScript support and 
        active maintenance. Alternatives we considered were React Router and building 
        our own navigation. This means faster development and better maintainability.""",
        "author": "Tim Swan",
        "timestamp": "2026-02-26T14:30:00Z"
    }
    
    # Process comment
    decision = engine.process_comment(
        comment,
        issue_key="TACS-42",
        space="TACS",
        outcome="Mobile App Redesign"
    )
    
    if decision:
        print("Decision captured!")
        print(f"  ID: {decision.decision_id}")
        print(f"  What: {decision.what}")
        print(f"  Why: {decision.why}")
        print(f"  Alternatives: {decision.alternatives}")
        print(f"  Impact: {decision.impact}")
        print(f"  Tags: {decision.tags}")
        print("\nFormatted for Confluence:")
        print(engine.formatter.format_markdown(decision))
    
    # Search for related decisions
    print("\nSearching for React-related decisions:")
    react_decisions = memory.search_decisions("TACS", tags=["react"])
    for d in react_decisions:
        print(f"  - {d.title}")
    
    # Get recent decisions
    print("\nRecent decisions:")
    recent = memory.get_recent_decisions("TACS", count=5)
    for d in recent:
        print(f"  - [{d.when[:10]}] {d.title}")

#!/usr/bin/env python3
"""
Brodie GEO Scoring Engine
Evidence-based scoring with configurable weighting profiles.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class ScoringMode(Enum):
    STANDARD = "standard"
    TECHNICAL_REMEDIATION = "technical"
    CONTENT_OPTIMIZATION = "content"
    LOCAL_BUSINESS = "local"

@dataclass
class DimensionScore:
    """Score for a single scoring dimension."""
    name: str
    score: float  # 0-100
    confidence: float  # 0-1
    weight: float  # 0-1
    supporting_findings: List[str] = field(default_factory=list)
    affected_pages: List[str] = field(default_factory=list)
    recommended_fixes: List[str] = field(default_factory=list)

@dataclass
class GEOScore:
    """Complete GEO audit score."""
    overall_score: float
    overall_confidence: float
    blockers_count: int
    fast_wins_count: int
    strategic_opportunities_count: int
    dimensions: Dict[str, DimensionScore]
    mode: ScoringMode

class BrodieScoringEngine:
    """
    Evidence-based scoring engine with configurable weighting profiles.
    """
    
    # Weighting profiles for different modes
    WEIGHTS = {
        ScoringMode.STANDARD: {
            "technical_foundation": 0.20,
            "ai_accessibility": 0.20,
            "content_quality": 0.20,
            "citability": 0.20,
            "structured_identity": 0.10,
            "platform_readiness": 0.10,
        },
        ScoringMode.TECHNICAL_REMEDIATION: {
            "technical_foundation": 0.25,
            "ai_accessibility": 0.15,
            "content_quality": 0.15,
            "citability": 0.15,
            "structured_identity": 0.15,
            "platform_readiness": 0.15,
        },
        ScoringMode.CONTENT_OPTIMIZATION: {
            "technical_foundation": 0.15,
            "ai_accessibility": 0.20,
            "content_quality": 0.25,
            "citability": 0.25,
            "structured_identity": 0.05,
            "platform_readiness": 0.10,
        },
        ScoringMode.LOCAL_BUSINESS: {
            "technical_foundation": 0.15,
            "ai_accessibility": 0.20,
            "content_quality": 0.20,
            "citability": 0.15,
            "structured_identity": 0.20,
            "platform_readiness": 0.10,
        },
    }
    
    def __init__(self, mode: ScoringMode = ScoringMode.STANDARD):
        self.mode = mode
        self.weights = self.WEIGHTS[mode]
    
    def calculate_overall_score(self, dimensions: Dict[str, DimensionScore]) -> GEOScore:
        """
        Calculate overall score from dimension scores.
        
        Each dimension score is weighted by its profile weight.
        Overall confidence is the average of dimension confidences.
        """
        weighted_sum = 0.0
        confidence_sum = 0.0
        
        blockers = 0
        fast_wins = 0
        strategic = 0
        
        for dim_name, dim_score in dimensions.items():
            weight = self.weights.get(dim_name, 0.0)
            weighted_sum += dim_score.score * weight
            confidence_sum += dim_score.confidence
            
            # Categorize recommendations
            for fix in dim_score.recommended_fixes:
                if "critical" in fix.lower() or "blocker" in fix.lower():
                    blockers += 1
                elif "fast" in fix.lower() or "quick" in fix.lower():
                    fast_wins += 1
                else:
                    strategic += 1
        
        overall_score = weighted_sum
        overall_confidence = confidence_sum / len(dimensions) if dimensions else 0.0
        
        return GEOScore(
            overall_score=round(overall_score, 1),
            overall_confidence=round(overall_confidence, 2),
            blockers_count=blockers,
            fast_wins_count=fast_wins,
            strategic_opportunities_count=strategic,
            dimensions=dimensions,
            mode=self.mode
        )
    
    def score_technical_foundation(self, findings: List[dict]) -> DimensionScore:
        """
        Score technical foundation.
        
        Measures: crawlability, indexability, canonicalization, redirects,
        render parity, metadata quality, internal link health, page health.
        """
        # Analyze findings
        score = 100.0
        confidence = 1.0
        supporting = []
        fixes = []
        pages = []
        
        for finding in findings:
            severity = finding.get("severity", "info")
            category = finding.get("category", "")
            
            if severity == "critical":
                score -= 15
                confidence -= 0.1
            elif severity == "warning":
                score -= 5
                confidence -= 0.05
            
            supporting.append(finding.get("message", ""))
            if finding.get("page"):
                pages.append(finding["page"])
            if finding.get("fix"):
                fixes.append(finding["fix"])
        
        # Ensure bounds
        score = max(0, min(100, score))
        confidence = max(0, min(1, confidence))
        
        return DimensionScore(
            name="Technical Foundation",
            score=score,
            confidence=confidence,
            weight=self.weights["technical_foundation"],
            supporting_findings=supporting,
            affected_pages=list(set(pages)),
            recommended_fixes=fixes
        )
    
    def score_ai_accessibility(self, findings: List[dict]) -> DimensionScore:
        """
        Score AI accessibility.
        
        Measures: robots behavior, llms.txt presence/quality,
        key content discoverability, answer content reachability.
        """
        score = 100.0
        confidence = 1.0
        supporting = []
        fixes = []
        pages = []
        
        for finding in findings:
            severity = finding.get("severity", "info")
            
            if severity == "critical":
                score -= 20
                confidence -= 0.15
            elif severity == "warning":
                score -= 8
                confidence -= 0.08
            
            supporting.append(finding.get("message", ""))
            if finding.get("page"):
                pages.append(finding["page"])
            if finding.get("fix"):
                fixes.append(finding["fix"])
        
        score = max(0, min(100, score))
        confidence = max(0, min(1, confidence))
        
        return DimensionScore(
            name="AI Accessibility",
            score=score,
            confidence=confidence,
            weight=self.weights["ai_accessibility"],
            supporting_findings=supporting,
            affected_pages=list(set(pages)),
            recommended_fixes=fixes
        )
    
    def score_content_quality(self, findings: List[dict]) -> DimensionScore:
        """
        Score content quality.
        
        Measures: answer-first structure, heading clarity, useful definitions,
        FAQ patterns, tables/lists, freshness, author signals, citations.
        """
        score = 100.0
        confidence = 1.0
        supporting = []
        fixes = []
        pages = []
        
        for finding in findings:
            severity = finding.get("severity", "info")
            
            if severity == "critical":
                score -= 12
                confidence -= 0.08
            elif severity == "warning":
                score -= 4
                confidence -= 0.04
            
            supporting.append(finding.get("message", ""))
            if finding.get("page"):
                pages.append(finding["page"])
            if finding.get("fix"):
                fixes.append(finding["fix"])
        
        score = max(0, min(100, score))
        confidence = max(0, min(1, confidence))
        
        return DimensionScore(
            name="Content Quality",
            score=score,
            confidence=confidence,
            weight=self.weights["content_quality"],
            supporting_findings=supporting,
            affected_pages=list(set(pages)),
            recommended_fixes=fixes
        )
    
    def score_citability(self, findings: List[dict]) -> DimensionScore:
        """
        Score citability.
        
        Measures: passage strength, self-containment, claim specificity,
        entity density, heading support, citation cues, context independence.
        """
        score = 100.0
        confidence = 1.0
        supporting = []
        fixes = []
        pages = []
        
        for finding in findings:
            severity = finding.get("severity", "info")
            
            if severity == "critical":
                score -= 15
                confidence -= 0.1
            elif severity == "warning":
                score -= 6
                confidence -= 0.05
            
            supporting.append(finding.get("message", ""))
            if finding.get("page"):
                pages.append(finding["page"])
            if finding.get("fix"):
                fixes.append(finding["fix"])
        
        score = max(0, min(100, score))
        confidence = max(0, min(1, confidence))
        
        return DimensionScore(
            name="Citability",
            score=score,
            confidence=confidence,
            weight=self.weights["citability"],
            supporting_findings=supporting,
            affected_pages=list(set(pages)),
            recommended_fixes=fixes
        )
    
    def score_structured_identity(self, findings: List[dict]) -> DimensionScore:
        """
        Score structured identity.
        
        Measures: schema quality, entity consistency, sameAs coverage,
        clear communication of who/what/entity connections.
        """
        score = 100.0
        confidence = 1.0
        supporting = []
        fixes = []
        pages = []
        
        for finding in findings:
            severity = finding.get("severity", "info")
            
            if severity == "critical":
                score -= 10
                confidence -= 0.08
            elif severity == "warning":
                score -= 4
                confidence -= 0.03
            
            supporting.append(finding.get("message", ""))
            if finding.get("page"):
                pages.append(finding["page"])
            if finding.get("fix"):
                fixes.append(finding["fix"])
        
        score = max(0, min(100, score))
        confidence = max(0, min(1, confidence))
        
        return DimensionScore(
            name="Structured Identity",
            score=score,
            confidence=confidence,
            weight=self.weights["structured_identity"],
            supporting_findings=supporting,
            affected_pages=list(set(pages)),
            recommended_fixes=fixes
        )
    
    def score_platform_readiness(self, findings: List[dict]) -> DimensionScore:
        """
        Score platform readiness.
        
        Measures: Google AI Overviews, search enhancements, Perplexity retrieval,
        ChatGPT retrieval, Claude summarization readiness.
        """
        score = 100.0
        confidence = 1.0
        supporting = []
        fixes = []
        pages = []
        
        for finding in findings:
            severity = finding.get("severity", "info")
            
            if severity == "critical":
                score -= 12
                confidence -= 0.1
            elif severity == "warning":
                score -= 4
                confidence -= 0.04
            
            supporting.append(finding.get("message", ""))
            if finding.get("page"):
                pages.append(finding["page"])
            if finding.get("fix"):
                fixes.append(finding["fix"])
        
        score = max(0, min(100, score))
        confidence = max(0, min(1, confidence))
        
        return DimensionScore(
            name="Platform Readiness",
            score=score,
            confidence=confidence,
            weight=self.weights["platform_readiness"],
            supporting_findings=supporting,
            affected_pages=list(set(pages)),
            recommended_fixes=fixes
        )


def example_usage():
    """Example of how to use the scoring engine."""
    # Create engine with standard mode
    engine = BrodieScoringEngine(mode=ScoringMode.STANDARD)
    
    # Example findings from analyzers
    technical_findings = [
        {"severity": "warning", "message": "Missing X-Frame-Options header", "page": "/", "fix": "Add X-Frame-Options: DENY"},
        {"severity": "info", "message": "HTTPS with HSTS enabled", "page": "/"},
    ]
    
    ai_findings = [
        {"severity": "critical", "message": "SPA with minimal SSR content", "page": "/", "fix": "Implement SSR or pre-rendering"},
        {"severity": "warning", "message": "No llms.txt file detected", "page": "/", "fix": "Create llms.txt"},
    ]
    
    # Score each dimension
    dimensions = {
        "technical_foundation": engine.score_technical_foundation(technical_findings),
        "ai_accessibility": engine.score_ai_accessibility(ai_findings),
        "content_quality": engine.score_content_quality([]),
        "citability": engine.score_citability([]),
        "structured_identity": engine.score_structured_identity([]),
        "platform_readiness": engine.score_platform_readiness([]),
    }
    
    # Calculate overall score
    result = engine.calculate_overall_score(dimensions)
    
    return result


if __name__ == "__main__":
    result = example_usage()
    print(f"Overall Score: {result.overall_score}")
    print(f"Confidence: {result.overall_confidence}")
    print(f"Blockers: {result.blockers_count}")
    print(f"Fast Wins: {result.fast_wins_count}")
    print(f"Strategic: {result.strategic_opportunities_count}")

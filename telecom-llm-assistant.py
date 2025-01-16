import os
from typing import Dict, Optional, List, Tuple, Set
import requests
from dataclasses import dataclass
import json
from enum import Enum
import re
from collections import defaultdict

class QueryType(Enum):
    PROCEDURE = "procedure"
    ARCHITECTURE = "architecture"
    PROTOCOL = "protocol"
    INTERFACE = "interface"
    SECURITY = "security"
    PERFORMANCE = "performance"
    QOS = "qos"
    RELIABILITY = "reliability"
    DEPLOYMENT = "deployment"
    INTERWORKING = "interworking"
    MIGRATION = "migration"
    TROUBLESHOOTING = "troubleshooting"
    COMPLIANCE = "compliance"
    FEATURE = "feature"
    GENERAL = "general"

@dataclass
class QueryClassification:
    primary_type: QueryType
    secondary_types: Set[QueryType]
    confidence_score: float
    keywords_matched: Dict[str, List[str]]

class TelecomPromptGenerator:
    """Enhanced prompt generator with comprehensive query classification"""
    
    # Keyword mappings for query classification
    QUERY_KEYWORDS = {
        QueryType.PROCEDURE: {
            'high_priority': ['procedure', 'process', 'flow', 'step', 'sequence', 'operation'],
            'medium_priority': ['how to', 'when', 'trigger', 'initiate', 'handle'],
            'low_priority': ['do', 'perform', 'execute']
        },
        QueryType.ARCHITECTURE: {
            'high_priority': ['architecture', 'structure', 'framework', 'design', 'topology'],
            'medium_priority': ['component', 'element', 'node', 'entity', 'function'],
            'low_priority': ['system', 'network', 'setup']
        },
        QueryType.PROTOCOL: {
            'high_priority': ['protocol', 'signaling', 'message', 'packet', 'format'],
            'medium_priority': ['header', 'payload', 'encoding', 'decoding', 'stack'],
            'low_priority': ['communicate', 'exchange', 'transfer']
        },
        QueryType.INTERFACE: {
            'high_priority': ['interface', 'reference point', 'connection', 'link'],
            'medium_priority': ['between', 'connects to', 'interconnection'],
            'low_priority': ['connect', 'communicate']
        },
        QueryType.SECURITY: {
            'high_priority': ['security', 'authentication', 'encryption', 'integrity', 'privacy'],
            'medium_priority': ['protect', 'secure', 'cipher', 'key', 'credential'],
            'low_priority': ['safe', 'guard', 'threat']
        },
        QueryType.PERFORMANCE: {
            'high_priority': ['performance', 'throughput', 'latency', 'bandwidth', 'capacity'],
            'medium_priority': ['speed', 'efficiency', 'optimization', 'metric'],
            'low_priority': ['fast', 'slow', 'measure']
        },
        QueryType.QOS: {
            'high_priority': ['qos', 'quality of service', 'priority', 'class', 'bearer'],
            'medium_priority': ['traffic', 'flow', 'guarantee', 'requirement'],
            'low_priority': ['quality', 'service']
        },
        QueryType.RELIABILITY: {
            'high_priority': ['reliability', 'availability', 'redundancy', 'resilience'],
            'medium_priority': ['failover', 'backup', 'recovery', 'robust'],
            'low_priority': ['stable', 'reliable', 'maintain']
        },
        QueryType.DEPLOYMENT: {
            'high_priority': ['deployment', 'installation', 'configuration', 'setup'],
            'medium_priority': ['implement', 'roll out', 'provision', 'integrate'],
            'low_priority': ['deploy', 'install', 'configure']
        },
        QueryType.INTERWORKING: {
            'high_priority': ['interworking', 'interoperability', 'compatibility', 'integration'],
            'medium_priority': ['interact', 'work together', 'coordinate'],
            'low_priority': ['between', 'with']
        },
        QueryType.MIGRATION: {
            'high_priority': ['migration', 'upgrade', 'transition', 'evolution'],
            'medium_priority': ['move to', 'change', 'transform'],
            'low_priority': ['new', 'old', 'legacy']
        },
        QueryType.TROUBLESHOOTING: {
            'high_priority': ['troubleshoot', 'debug', 'diagnose', 'problem', 'issue'],
            'medium_priority': ['error', 'fault', 'failure', 'fix'],
            'low_priority': ['wrong', 'fail', 'break']
        },
        QueryType.COMPLIANCE: {
            'high_priority': ['compliance', 'standard', 'regulation', 'requirement'],
            'medium_priority': ['conform', 'adhere', 'follow', 'meet'],
            'low_priority': ['rule', 'guideline', 'specification']
        },
        QueryType.FEATURE: {
            'high_priority': ['feature', 'capability', 'functionality', 'service'],
            'medium_priority': ['support', 'provide', 'enable', 'offer'],
            'low_priority': ['can', 'able', 'function']
        }
    }

    # Specialized contexts for different query types
    SPECIALIZED_CONTEXTS = {
        QueryType.PROCEDURE: """
        For procedure-related queries:
        - Provide a clear step-by-step breakdown
        - Include sequence diagrams if relevant
        - List all involved network elements
        - Detail message flows and parameters
        - Specify preconditions and postconditions
        - Highlight potential error scenarios
        - Reference relevant 3GPP specifications (TS documents)
        """,
        
        QueryType.ARCHITECTURE: """
        For architecture-related queries:
        - Describe overall architecture structure
        - Detail component roles and responsibilities
        - Explain interfaces and reference points
        - Discuss deployment considerations
        - Include scalability aspects
        - Mention virtualization options
        - Reference relevant 3GPP specifications
        """,
        
        QueryType.PROTOCOL: """
        For protocol-related queries:
        - Explain protocol stack placement
        - Detail message formats and fields
        - Describe state machines
        - List supported procedures
        - Include protocol parameters
        - Discuss protocol extensions
        - Reference relevant 3GPP specifications
        """,
        
        QueryType.INTERFACE: """
        For interface-related queries:
        - Define connected network elements
        - List supported protocols
        - Detail interface requirements
        - Explain message flows
        - Describe interface configuration
        - Include performance aspects
        - Reference relevant 3GPP specifications
        """,
        
        QueryType.SECURITY: """
        For security-related queries:
        - Explain security mechanisms
        - Detail key management
        - Describe authentication flows
        - List security features
        - Include threat mitigations
        - Discuss privacy aspects
        - Reference relevant 3GPP specifications
        """,
        
        QueryType.PERFORMANCE: """
        For performance-related queries:
        - List key performance indicators
        - Provide measurement methods
        - Include benchmark data
        - Detail optimization options
        - Discuss scaling factors
        - Explain monitoring approaches
        - Reference relevant 3GPP specifications
        """,
        
        QueryType.QOS: """
        For QoS-related queries:
        - Define QoS parameters
        - Explain QoS flows
        - Detail QoS handling
        - List QoS classes
        - Include mapping rules
        - Discuss enforcement methods
        - Reference relevant 3GPP specifications
        """,
        
        QueryType.RELIABILITY: """
        For reliability-related queries:
        - Explain redundancy mechanisms
        - Detail failover procedures
        - Describe recovery methods
        - List availability features
        - Include monitoring aspects
        - Discuss SLA considerations
        - Reference relevant 3GPP specifications
        """,
        
        QueryType.DEPLOYMENT: """
        For deployment-related queries:
        - Provide deployment options
        - List prerequisites
        - Detail configuration steps
        - Include best practices
        - Discuss scaling aspects
        - Explain maintenance procedures
        - Reference relevant 3GPP specifications
        """,
        
        QueryType.INTERWORKING: """
        For interworking-related queries:
        - Explain interworking mechanisms
        - Detail protocol conversions
        - List supported features
        - Include limitations
        - Discuss compatibility aspects
        - Describe roaming scenarios
        - Reference relevant 3GPP specifications
        """,
        
        QueryType.MIGRATION: """
        For migration-related queries:
        - Provide migration paths
        - Detail upgrade steps
        - List compatibility issues
        - Include rollback procedures
        - Discuss impact analysis
        - Explain testing approaches
        - Reference relevant 3GPP specifications
        """,
        
        QueryType.TROUBLESHOOTING: """
        For troubleshooting-related queries:
        - List common issues
        - Provide diagnostic steps
        - Detail resolution procedures
        - Include logging aspects
        - Discuss prevention methods
        - Explain monitoring tools
        - Reference relevant 3GPP specifications
        """,
        
        QueryType.COMPLIANCE: """
        For compliance-related queries:
        - List applicable standards
        - Detail requirements
        - Explain conformance testing
        - Include certification aspects
        - Discuss validation methods
        - Provide compliance checklist
        - Reference relevant 3GPP specifications
        """,
        
        QueryType.FEATURE: """
        For feature-related queries:
        - Explain feature capabilities
        - Detail configuration options
        - List dependencies
        - Include limitations
        - Discuss use cases
        - Provide implementation guidance
        - Reference relevant 3GPP specifications
        """
    }

    def _calculate_keyword_matches(self, query: str) -> Dict[QueryType, Dict[str, List[str]]]:
        """
        Calculate keyword matches for each query type with priority levels
        """
        query_lower = query.lower()
        matches = defaultdict(lambda: defaultdict(list))
        
        for query_type, priority_keywords in self.QUERY_KEYWORDS.items():
            for priority, keywords in priority_keywords.items():
                for keyword in keywords:
                    if keyword in query_lower:
                        matches[query_type][priority].append(keyword)
        
        return matches

    def _calculate_confidence_score(self, matches: Dict[str, List[str]]) -> float:
        """
        Calculate confidence score based on keyword matches and priorities
        """
        score = 0
        weights = {
            'high_priority': 1.0,
            'medium_priority': 0.6,
            'low_priority': 0.3
        }
        
        for priority, keywords in matches.items():
            score += len(keywords) * weights[priority]
        
        return min(score, 1.0)

    def _classify_query(self, query: str) -> QueryClassification:
        """
        Enhanced query classification with multiple types and confidence scoring
        """
        keyword_matches = self._calculate_keyword_matches(query)
        
        # Calculate confidence scores for each type
        type_scores = {}
        for query_type, matches in keyword_matches.items():
            confidence = self._calculate_confidence_score(matches)
            if confidence > 0:
                type_scores[query_type] = confidence
        
        # If no matches found, return GENERAL type
        if not type_scores:
            return QueryClassification(
                primary_type=QueryType.GENERAL,
                secondary_types=set(),
                confidence_score=0.0,
                keywords_matched={}
            )
        
        # Get primary and secondary types
        sorted_types = sorted(type_scores.items(), key=lambda x: x[1], reverse=True)
        primary_type = sorted_types[0][0]
        
        # Get secondary types with confidence > 0.3
        secondary_types = {
            query_type for query_type, score in sorted_types[1:]
            if score > 0.3
        }
        
        return QueryClassification(
            primary_type=primary_type,
            secondary_types=secondary_types,
            confidence_score=sorted_types[0][1],
            keywords_matched={str(k): dict(v) for k, v in keyword_matches.items() if v}
        )

    def generate_prompt(self, user_query: str) -> str:
        """
        Generate comprehensive prompt based on query classification
        """
        classification = self._classify_query(user_query)
        
        # Get primary context
        primary_context = self.SPECIALIZED_CONTEXTS.get(
            classification.primary_type,
            "Provide a clear, technical response with relevant 3GPP specification references."
        )
        
        # Add secondary contexts if any
        secondary_contexts = []
        for secondary_type in classification.secondary_types:
            if secondary_type in self.SPECIALIZED_CONTEXTS:
                context_lines = self.SPECIALIZED_CONTEXTS[secondary_type].split('\n')
                # Take only the first few lines to keep it concise
                secondary_contexts.extend(context_lines[1:4])
        
        # Combine contexts
        combined_context = f"""
        Primary Focus - {classification.primary_type.value}:
        {primary_context}
        
        {'Additional Considerations:' if secondary_contexts else ''}
        {chr(10).join(secondary_contexts)}
        
        Query Classification Confidence: {classification.confidence_score:.2f}
        
        User Query: {user_query}
        
        Response Guidelines:
        1. Start with a clear overview
        2. Focus on {classification.primary_type.value}-related aspects
        3. Include relevant 3GPP specification references
        4. Provide practical examples where applicable
        5. Consider interdependencies with {', '.join(t.value for t in classification.secondary_types) if classification.secondary_types else 'other aspects'}
        6. Conclude with key takeaways and considerations
        """
        
        return combined_context

# [Previous LLMProvider and derived classes remain the same]
[rest of the code remains the same as in the previous version]

def main():
    # Initialize providers [same as before]
    
    # Example queries demonstrating different query types
    example_queries = [
        "Explain the 5G NR handover procedure including preparation and execution phases",
        "How does 5G Core network architecture support network slicing?",
        "What security mechanisms are used in 5G NAS protocol?",
        "Describe QoS flow handling and mapping in 5G system",
        "How to troubleshoot 5G registration failures?",
        "What are the interworking procedures between 5G and 4G networks?",
        "Explain 5G network deployment options and migration strategies",
        "Detail the compliance requirements for 5G NR base stations",
    ]
    
    # Create assistant
    assistant = TelecomAssistant(
        primary_provider=openai_provider,
        backup_providers=[anthropic_provider, google_provider, mistral_provider]
    )
    
    # Process queries with detailed classification
    for query in example_queries:
        print(f"\nQuery: {query}")
        classification = assistant.prompt_generator._classify_query(query)
        print(f"Primary Type: {classification.primary_type.value}")
        print(f"Secondary Types: {[t.value for t in classification.secondary_types]}")
        print(f"Confidence Score: {classification.confidence_score:.2f}")
        print(f"Keywords Matched: {json.dumps(classification.keywords_matched, indent=2)}")
        
        response = assistant.process_query(query)
        print(f"Response: {response}\n")
        print("-" * 80)

if __name__ == "__main__":
    main()

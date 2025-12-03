"""
Research Tasks for Study Assistant CrewAI integration.
Defines tasks for the Research Agent.
"""

from crewai import Task
from typing import Dict, Any


class ResearchTasks:
    """Research task definitions for CrewAI workflow."""
    
    @staticmethod
    def analyze_document_task(agent, document_content: str, rag_context: str = "") -> Task:
        """
        Create a task for document analysis.
        
        Args:
            agent: The research agent to perform the task
            document_content: The document content to analyze
            rag_context: Additional RAG context
            
        Returns:
            CrewAI Task for document analysis
        """
        return Task(
            description=f"""
            Analyze the following study document and extract key educational insights:
            
            DOCUMENT CONTENT:
            {document_content[:2000]}{"..." if len(document_content) > 2000 else ""}
            
            ADDITIONAL CONTEXT:
            {rag_context[:1000]}{"..." if len(rag_context) > 1000 else ""}
            
            Your analysis should identify:
            1. Main topics and themes
            2. Key concepts and definitions
            3. Important facts and relationships
            4. Learning objectives and educational goals
            5. Difficulty level and prerequisites
            6. Areas suitable for different types of study materials
            
            Provide a comprehensive research analysis that will guide content generation.
            """,
            agent=agent,
            expected_output="A detailed research analysis containing main topics, key concepts, learning objectives, difficulty assessment, and recommendations for study material creation."
        )
    
    @staticmethod
    def concept_extraction_task(agent, research_analysis: str) -> Task:
        """
        Create a task for extracting key concepts from research analysis.
        
        Args:
            agent: The research agent to perform the task
            research_analysis: Previous research analysis
            
        Returns:
            CrewAI Task for concept extraction
        """
        return Task(
            description=f"""
            Based on the research analysis, extract and prioritize key concepts for study material creation:
            
            RESEARCH ANALYSIS:
            {research_analysis}
            
            Extract:
            1. Top 10 most important concepts
            2. Hierarchical relationship between concepts
            3. Difficulty level for each concept
            4. Prerequisites for understanding each concept
            5. Recommended study material types for each concept
            
            Prioritize concepts by importance and learning value.
            """,
            agent=agent,
            expected_output="A prioritized list of key concepts with difficulty levels, relationships, and recommendations for study material formats."
        )
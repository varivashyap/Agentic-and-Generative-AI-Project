"""
Research Agent for Study Assistant CrewAI integration.
Specializes in analyzing documents and extracting key information.
"""

import logging
from typing import Dict, Any, Optional
from crewai import Agent
from langchain.llms.base import LLM

from ...generation.llm_client import LLMClient
from ...config import get_config

logger = logging.getLogger(__name__)


class CustomLlamaLLM(LLM):
    """Custom LangChain LLM wrapper for our existing LLMClient."""
    
    client: Any = None
    config: Any = None
    
    def __init__(self, llm_client: LLMClient):
        super().__init__()
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, 'client', llm_client)
        object.__setattr__(self, 'config', get_config())
    
    def _call(self, prompt: str, stop: Optional[list] = None) -> str:
        """Call the LLM with a prompt."""
        try:
            # Use summary max tokens as a reasonable default
            max_tokens = getattr(self.config.generation, 'summary_max_tokens', 600)
            temperature = getattr(self.config.generation, 'summary_temperature', 0.1)
            
            response = self.client.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.strip()
        except Exception as e:
            logger.error(f"Error in LLM call: {e}")
            return f"Error: {str(e)}"
    
    @property
    def _llm_type(self) -> str:
        return "custom_llama"


class ResearchAgent:
    """
    Research Agent for analyzing study documents and extracting key concepts.
    
    This agent specializes in:
    - Document analysis and comprehension
    - Key concept identification
    - Topic structure understanding
    - Knowledge extraction from RAG context
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize the Research Agent.
        
        Args:
            llm_client: Optional LLMClient instance. If None, creates a new one.
        """
        self.config = get_config()
        self.llm_client = llm_client or LLMClient()
        self.custom_llm = CustomLlamaLLM(self.llm_client)
        
        # Create the CrewAI agent
        self.agent = Agent(
            role='Research Analyst',
            goal='Analyze study documents and extract key educational concepts, topics, and learning objectives',
            backstory="""You are an expert research analyst with deep expertise in educational content analysis.
            Your primary focus is understanding complex academic material and identifying the most important
            concepts that students need to learn. You excel at breaking down complex topics into digestible
            components and understanding relationships between different concepts.""",
            verbose=True,
            allow_delegation=False,
            llm=self.custom_llm
        )
    
    def analyze_document_context(self, document_text: str, rag_context: str = "") -> Dict[str, Any]:
        """
        Analyze document and RAG context to extract key research insights.
        
        Args:
            document_text: The main document text to analyze
            rag_context: Additional context from RAG retrieval
            
        Returns:
            Dictionary containing research insights and key concepts
        """
        analysis_prompt = f"""
        As a research analyst, analyze the following study material and provide a comprehensive analysis:
        
        DOCUMENT TEXT:
        {document_text}
        
        ADDITIONAL CONTEXT:
        {rag_context}
        
        Please provide:
        1. Main topics and themes
        2. Key concepts and definitions
        3. Important facts and figures
        4. Learning objectives
        5. Difficulty level assessment
        6. Prerequisites or background knowledge needed
        7. Relationships between concepts
        
        Format your response as a structured analysis that will help other agents create effective study materials.
        """
        
        try:
            response = self.llm_client.generate(
                prompt=analysis_prompt,
                max_tokens=self.config.llm.max_tokens,
                temperature=0.3  # Lower temperature for more focused analysis
            )
            
            return {
                "status": "success",
                "analysis": response,
                "key_concepts": self._extract_key_concepts(response),
                "topics": self._extract_topics(response),
                "difficulty_level": self._assess_difficulty(response)
            }
        except Exception as e:
            logger.error(f"Error in document analysis: {e}")
            return {
                "status": "error",
                "error": str(e),
                "analysis": "",
                "key_concepts": [],
                "topics": [],
                "difficulty_level": "unknown"
            }
    
    def _extract_key_concepts(self, analysis: str) -> list:
        """Extract key concepts from the analysis."""
        # Simple extraction - could be enhanced with NLP
        concepts = []
        lines = analysis.split('\n')
        for line in lines:
            if 'concept' in line.lower() or 'definition' in line.lower():
                concepts.append(line.strip())
        return concepts[:10]  # Limit to top 10
    
    def _extract_topics(self, analysis: str) -> list:
        """Extract main topics from the analysis."""
        topics = []
        lines = analysis.split('\n')
        for line in lines:
            if 'topic' in line.lower() or 'theme' in line.lower():
                topics.append(line.strip())
        return topics[:5]  # Limit to top 5
    
    def _assess_difficulty(self, analysis: str) -> str:
        """Assess the difficulty level from the analysis."""
        analysis_lower = analysis.lower()
        if 'advanced' in analysis_lower or 'complex' in analysis_lower:
            return "advanced"
        elif 'intermediate' in analysis_lower:
            return "intermediate"
        elif 'basic' in analysis_lower or 'beginner' in analysis_lower:
            return "beginner"
        else:
            return "intermediate"  # Default
"""
StudyAssistantOrchestrator - Main CrewAI integration for Study Assistant.
Orchestrates multi-agent workflows for enhanced study material generation.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from .crews.study_material_crew import StudyMaterialCrew
from ..generation.llm_client import LLMClient
from ..config import get_config

logger = logging.getLogger(__name__)


class StudyAssistantOrchestrator:
    """
    Main orchestrator for CrewAI-enhanced study material generation.
    
    Integrates with existing Study Assistant pipeline to provide multi-agent
    collaborative content generation capabilities.
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None, config_path: Optional[str] = None):
        """
        Initialize the StudyAssistantOrchestrator.
        
        Args:
            llm_client: Optional LLM client instance
            config_path: Optional path to configuration file
        """
        # Load configuration
        if config_path:
            from ..config import Config
            self.config = Config(config_path)
        else:
            self.config = get_config()
        
        # Initialize LLM client
        self.llm_client = llm_client or LLMClient()
        
        # Initialize CrewAI components
        self.study_crew = StudyMaterialCrew(self.llm_client)
        
        # CrewAI settings
        self.crewai_enabled = self.config.crewai.enabled if hasattr(self.config, 'crewai') else True
        self.default_workflow = getattr(self.config.crewai, 'default_workflow', 'comprehensive') if hasattr(self.config, 'crewai') else 'comprehensive'
        self.enable_quality_review = getattr(self.config.crewai, 'enable_quality_review', True) if hasattr(self.config, 'crewai') else True
        
        logger.info(f"StudyAssistantOrchestrator initialized (CrewAI enabled: {self.crewai_enabled})")
    
    def generate_study_materials(
        self, 
        document_content: str, 
        rag_context: str = "",
        content_types: List[str] = None,
        workflow_type: str = "comprehensive",
        enable_quality_review: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Generate study materials using CrewAI multi-agent workflow.
        
        Args:
            document_content: The main document content to process
            rag_context: Additional context from RAG retrieval
            content_types: Types of content to generate (["summaries", "flashcards", "quiz"])
            workflow_type: Type of workflow ("comprehensive", "focused", "summaries", "flashcards", "quiz")
            enable_quality_review: Whether to include quality review (None = use config default)
            
        Returns:
            Dictionary containing generated study materials and metadata
        """
        if not self.crewai_enabled:
            logger.warning("CrewAI is disabled. Use regular pipeline instead.")
            return {
                "status": "disabled",
                "message": "CrewAI orchestration is disabled in configuration",
                "suggestion": "Use regular Study Assistant pipeline or enable CrewAI in config"
            }
        
        # Set defaults
        if content_types is None:
            content_types = ["summaries", "flashcards", "quiz"]
        
        if enable_quality_review is None:
            enable_quality_review = self.enable_quality_review
        
        try:
            logger.info(f"Starting CrewAI workflow: {workflow_type}")
            logger.info(f"Content types: {content_types}")
            logger.info(f"Quality review: {enable_quality_review}")
            
            # Choose workflow based on type
            if workflow_type == "comprehensive" or workflow_type == "focused":
                result = self.study_crew.generate_comprehensive_study_materials(
                    document_content=document_content,
                    rag_context=rag_context,
                    content_types=content_types,
                    enable_quality_review=enable_quality_review
                )
            
            elif workflow_type == "summaries":
                result = self.study_crew.generate_summaries_with_review(
                    document_content=document_content,
                    rag_context=rag_context
                )
            
            elif workflow_type == "flashcards":
                result = self.study_crew.generate_flashcards_with_review(
                    document_content=document_content,
                    rag_context=rag_context
                )
            
            elif workflow_type == "quiz":
                result = self.study_crew.generate_quiz_with_review(
                    document_content=document_content,
                    rag_context=rag_context
                )
            
            else:
                raise ValueError(f"Unknown workflow type: {workflow_type}")
            
            # Add orchestrator metadata
            result["orchestrator_metadata"] = {
                "crewai_version": "0.74.0",
                "workflow_type": workflow_type,
                "content_types_requested": content_types,
                "quality_review_enabled": enable_quality_review,
                "model_used": self.llm_client.model_name if hasattr(self.llm_client, 'model_name') else "unknown"
            }
            
            logger.info("CrewAI workflow completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in CrewAI orchestration: {e}")
            return {
                "status": "error",
                "error": str(e),
                "workflow_type": workflow_type,
                "fallback_suggestion": "Consider using regular pipeline as fallback"
            }
    
    def generate_enhanced_summaries(self, document_content: str, rag_context: str = "") -> Dict[str, Any]:
        """
        Generate enhanced summaries with multi-agent collaboration.
        
        Args:
            document_content: Document content to summarize
            rag_context: Additional RAG context
            
        Returns:
            Enhanced summaries with research insights and quality review
        """
        return self.generate_study_materials(
            document_content=document_content,
            rag_context=rag_context,
            content_types=["summaries"],
            workflow_type="summaries",
            enable_quality_review=True
        )
    
    def generate_enhanced_flashcards(self, document_content: str, rag_context: str = "") -> Dict[str, Any]:
        """
        Generate enhanced flashcards with multi-agent collaboration.
        
        Args:
            document_content: Document content for flashcard creation
            rag_context: Additional RAG context
            
        Returns:
            Enhanced flashcards with research insights and quality review
        """
        return self.generate_study_materials(
            document_content=document_content,
            rag_context=rag_context,
            content_types=["flashcards"],
            workflow_type="flashcards",
            enable_quality_review=True
        )
    
    def generate_enhanced_quiz(self, document_content: str, rag_context: str = "") -> Dict[str, Any]:
        """
        Generate enhanced quiz questions with multi-agent collaboration.
        
        Args:
            document_content: Document content for quiz creation
            rag_context: Additional RAG context
            
        Returns:
            Enhanced quiz questions with research insights and quality review
        """
        return self.generate_study_materials(
            document_content=document_content,
            rag_context=rag_context,
            content_types=["quiz"],
            workflow_type="quiz",
            enable_quality_review=True
        )
    
    def generate_complete_study_package(
        self, 
        document_content: str, 
        rag_context: str = "",
        custom_content_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete study package with all material types.
        
        Args:
            document_content: Document content to process
            rag_context: Additional RAG context
            custom_content_types: Custom list of content types to generate
            
        Returns:
            Complete study package with all materials and comprehensive review
        """
        content_types = custom_content_types or ["summaries", "flashcards", "quiz"]
        
        return self.generate_study_materials(
            document_content=document_content,
            rag_context=rag_context,
            content_types=content_types,
            workflow_type="comprehensive",
            enable_quality_review=True
        )
    
    def is_available(self) -> bool:
        """
        Check if CrewAI orchestration is available and properly configured.
        
        Returns:
            Boolean indicating availability status
        """
        try:
            return (
                self.crewai_enabled and 
                self.llm_client is not None and 
                self.study_crew is not None
            )
        except Exception:
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status and configuration of the orchestrator.
        
        Returns:
            Status information dictionary
        """
        return {
            "crewai_enabled": self.crewai_enabled,
            "orchestrator_ready": self.is_available(),
            "default_workflow": self.default_workflow,
            "quality_review_enabled": self.enable_quality_review,
            "llm_model": getattr(self.llm_client, 'model_name', 'unknown'),
            "agents_available": {
                "research_agent": self.study_crew.research_agent is not None,
                "content_generator": self.study_crew.content_generator is not None,
                "quality_reviewer": self.study_crew.quality_reviewer is not None
            }
        }
    
    def get_supported_workflows(self) -> List[str]:
        """
        Get list of supported workflow types.
        
        Returns:
            List of supported workflow type strings
        """
        return [
            "comprehensive",    # All materials with quality review
            "focused",          # Selected materials with quality review  
            "summaries",        # Summaries only with review
            "flashcards",       # Flashcards only with review
            "quiz"              # Quiz only with review
        ]
    
    def get_supported_content_types(self) -> List[str]:
        """
        Get list of supported content types.
        
        Returns:
            List of supported content type strings
        """
        return ["summaries", "flashcards", "quiz"]
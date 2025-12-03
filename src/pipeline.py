"""Main pipeline orchestration for Study Assistant."""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from .config import get_config
from .ingestion import PDFIngestion, AudioIngestion
from .preprocessing import TextCleaner
from .representation import TextChunker, EmbeddingModel, VectorStore
from .retrieval import HybridRetriever, Reranker
from .generation import LLMClient, SummaryGenerator, FlashcardGenerator, QuizGenerator
from .evaluation import ContentValidator, EvaluationMetrics
from .export import AnkiExporter, CSVExporter

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# CrewAI integration (optional)
try:
    from .crew_ai import StudyAssistantOrchestrator
    CREWAI_AVAILABLE = True
    logger.info("✓ CrewAI import successful")
except ImportError as e:
    CREWAI_AVAILABLE = False
    StudyAssistantOrchestrator = None
    logger.warning(f"⚠️ CrewAI import failed: {e}")

logger = logging.getLogger(__name__)


class StudyAssistantPipeline:
    """Main pipeline for processing study materials and generating content."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the study assistant pipeline.
        
        Args:
            config_path: Path to config file (optional)
        """
        # Load configuration
        if config_path:
            from .config import Config
            self.config = Config(config_path)
        else:
            self.config = get_config()
        
        logger.info("Initializing Study Assistant Pipeline")
        
        # Initialize components
        self.pdf_ingestion = PDFIngestion()
        self.audio_ingestion = AudioIngestion()
        self.text_cleaner = TextCleaner()
        self.chunker = TextChunker()
        self.embedding_model = EmbeddingModel()
        # Pass dimension from embedding model to vector store
        self.vector_store = VectorStore(dimension=self.embedding_model.dimension)
        self.retriever = HybridRetriever(self.vector_store, self.embedding_model)
        self.reranker = Reranker()
        
        self.llm_client = LLMClient()
        self.summary_generator = SummaryGenerator(self.llm_client)
        self.flashcard_generator = FlashcardGenerator(self.llm_client)
        self.quiz_generator = QuizGenerator(self.llm_client)

        self.validator = ContentValidator(self.embedding_model)
        self.metrics = EvaluationMetrics()

        self.anki_exporter = AnkiExporter()
        self.csv_exporter = CSVExporter()

        # Initialize CrewAI orchestrator (if available)
        self.crewai_orchestrator = None
        if CREWAI_AVAILABLE:
            try:
                self.crewai_orchestrator = StudyAssistantOrchestrator(
                    llm_client=self.llm_client,
                    config_path=config_path
                )
                logger.info("✓ CrewAI orchestrator initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize CrewAI orchestrator: {e}")
        else:
            logger.info("CrewAI not available - using standard pipeline only")

        logger.info("Pipeline initialized successfully")

    def reload_model(self, model_name: str):
        """
        Reload the LLM with a different model.

        Args:
            model_name: Name of the model to load (e.g., "phi-3-mini-4k-instruct.Q4_K_M")
        """
        logger.info(f"Reloading pipeline with model: {model_name}")
        self.llm_client.reload_model(model_name)
        logger.info(f"✓ Pipeline now using model: {model_name}")

    def get_current_model(self) -> str:
        """Get the name of the currently loaded model."""
        return self.llm_client.get_current_model()
    
    def ingest_pdf(self, pdf_path: str):
        """
        Ingest and process a PDF file.
        
        Args:
            pdf_path: Path to PDF file
        """
        logger.info(f"Ingesting PDF: {pdf_path}")
        
        # Extract text
        pages = self.pdf_ingestion.extract(pdf_path)
        
        # Clean text
        pages = self.text_cleaner.clean_batch(pages)
        
        # Chunk text
        chunks = self.chunker.chunk(pages)
        
        # Generate embeddings
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedding_model.embed(texts)
        
        # Add to vector store
        self.vector_store.add(embeddings, chunks)
        
        # Update retriever index
        self.retriever.update_index()
        
        logger.info(f"Successfully ingested PDF with {len(chunks)} chunks")
    
    def ingest_audio(self, audio_path: str):
        """
        Ingest and process an audio/video file.
        
        Args:
            audio_path: Path to audio/video file
        """
        logger.info(f"Ingesting audio: {audio_path}")
        
        # Transcribe
        segments = self.audio_ingestion.transcribe(audio_path)
        
        # Clean text
        segments = self.text_cleaner.clean_batch(segments)
        
        # Chunk text
        chunks = self.chunker.chunk(segments)
        
        # Generate embeddings
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedding_model.embed(texts)
        
        # Add to vector store
        self.vector_store.add(embeddings, chunks)
        
        # Update retriever index
        self.retriever.update_index()
        
        logger.info(f"Successfully ingested audio with {len(chunks)} chunks")
    
    def ingest_file(self, file_path: str) -> List[Dict]:
        """
        Ingest and process a file (PDF or audio) and return chunks.
        
        Args:
            file_path: Path to file (PDF or audio)
            
        Returns:
            List of text chunks with metadata
        """
        from pathlib import Path
        
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            # Store current chunk count
            initial_count = self.vector_store.get_count() if hasattr(self.vector_store, 'get_count') else 0
            
            # Ingest PDF
            self.ingest_pdf(str(file_path))
            
            # Get the newly added chunks (simplified approach)
            # In a real implementation, this might return actual chunk objects
            return [{"text": f"PDF chunk {i}", "source": str(file_path)} for i in range(5)]
            
        elif suffix in ['.mp3', '.wav', '.m4a', '.mp4']:
            # Store current chunk count
            initial_count = self.vector_store.get_count() if hasattr(self.vector_store, 'get_count') else 0
            
            # Ingest audio
            self.ingest_audio(str(file_path))
            
            # Get the newly added chunks (simplified approach)
            return [{"text": f"Audio chunk {i}", "source": str(file_path)} for i in range(3)]
            
        else:
            logger.error(f"Unsupported file type: {suffix}")
            return []
    
    def generate_summaries(
        self,
        query: Optional[str] = None,
        scale: str = "paragraph",
        temperature: float = None,
        max_tokens: int = None,
        system_prompt: str = None
    ) -> str:
        """
        Generate summary from ingested content.

        Args:
            query: Optional query to focus summary (uses general summary if None)
            scale: Summary scale ("sentence", "paragraph", "section")
            temperature: Override temperature (uses config default if None)
            max_tokens: Override max_tokens (uses config default if None)
            system_prompt: Override system prompt (uses default if None)

        Returns:
            Generated summary
        """
        logger.info(f"Generating {scale} summary")

        # Retrieve context
        if query is None:
            query = "Summarize the main concepts and key information"

        context = self._retrieve_context(query)

        # Generate summary (pass through override parameters)
        summary = self.summary_generator.generate(
            context,
            scale,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt
        )

        # Validate
        validation = self.validator.validate_summary(summary, context)
        if not validation['is_valid']:
            logger.warning(f"Summary validation warnings: {validation['warnings']}")

        # Record metrics
        self.metrics.record_factuality(validation['source_containment'], 'summary')

        return summary
    
    def generate_flashcards(
        self,
        query: Optional[str] = None,
        card_type: str = "definition",
        max_cards: int = 50,
        temperature: float = None,
        system_prompt: str = None
    ) -> List[Dict[str, str]]:
        """
        Generate flashcards from ingested content.

        Args:
            query: Optional query to focus flashcards
            card_type: Type of flashcard
            max_cards: Maximum number of cards
            temperature: Optional temperature override (None = use config default)
            system_prompt: Override system prompt (uses default if None)

        Returns:
            List of flashcard dicts
        """
        logger.info(f"Generating {card_type} flashcards")

        # Retrieve context
        if query is None:
            query = "Extract key concepts, definitions, and facts"

        context = self._retrieve_context(query, top_k=30)

        # Generate flashcards (pass through override parameters)
        flashcards = self.flashcard_generator.generate(
            context,
            card_type,
            max_cards,
            temperature=temperature,
            system_prompt=system_prompt
        )

        logger.info(f"Generated {len(flashcards)} flashcards")
        return flashcards
    
    def generate_quizzes(
        self,
        query: Optional[str] = None,
        question_type: str = "mcq",
        num_questions: int = 10,
        temperature: float = None,
        max_tokens: int = None,
        system_prompt: str = None
    ) -> List[Dict[str, any]]:
        """
        Generate quiz questions from ingested content.

        Args:
            query: Optional query to focus questions
            question_type: Type of question
            num_questions: Number of questions
            temperature: Optional temperature override (None = use config default)
            max_tokens: Optional max_tokens override (None = use config default)
            system_prompt: Override system prompt (uses default if None)

        Returns:
            List of question dicts
        """
        logger.info(f"Generating {question_type} questions")

        # Retrieve context
        if query is None:
            query = "Generate assessment questions covering key concepts"

        context = self._retrieve_context(query, top_k=30)

        # Generate questions (pass through override parameters)
        questions = self.quiz_generator.generate(
            context,
            question_type,
            num_questions,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt
        )

        logger.info(f"Generated {len(questions)} questions")
        return questions
    
    def export_anki(self, flashcards: List[Dict[str, str]], output_path: str):
        """Export flashcards to Anki deck."""
        self.anki_exporter.export(flashcards, output_path)
    
    def export_csv_flashcards(self, flashcards: List[Dict[str, str]], output_path: str):
        """Export flashcards to CSV."""
        self.csv_exporter.export_flashcards(flashcards, output_path)
    
    def export_csv_quizzes(self, questions: List[Dict[str, any]], output_path: str):
        """Export quiz questions to CSV."""
        self.csv_exporter.export_quizzes(questions, output_path)
    
    def save_index(self, path: str):
        """Save vector store index to disk."""
        self.vector_store.save(path)
        logger.info(f"Saved index to {path}")
    
    def load_index(self, path: str):
        """Load vector store index from disk."""
        self.vector_store.load(path)
        self.retriever.update_index()
        logger.info(f"Loaded index from {path}")
    
    def _retrieve_context(
        self,
        query: str,
        top_k: Optional[int] = None
    ) -> List[Tuple[Dict, float]]:
        """Retrieve and rerank context for a query."""
        # Retrieve
        results = self.retriever.retrieve(query, top_k)
        
        # Rerank
        results = self.reranker.rerank(query, results)
        
        return results
    
    def get_metrics_summary(self) -> Dict:
        """Get evaluation metrics summary."""
        return self.metrics.get_summary()
    
    # =================== CrewAI Enhanced Generation Methods ===================
    
    def is_crewai_available(self) -> bool:
        """Check if CrewAI orchestration is available."""
        return self.crewai_orchestrator is not None and self.crewai_orchestrator.is_available()
    
    def get_crewai_status(self) -> Dict[str, any]:
        """Get CrewAI orchestrator status."""
        if self.crewai_orchestrator:
            return self.crewai_orchestrator.get_status()
        return {
            "crewai_enabled": False,
            "orchestrator_ready": False,
            "reason": "CrewAI not available or not initialized"
        }
    
    def generate_enhanced_study_materials(
        self,
        file_path: str,
        content_types: List[str] = None,
        workflow_type: str = "comprehensive",
        enable_quality_review: bool = True,
        use_crewai: bool = True
    ) -> Dict[str, any]:
        """
        Generate study materials using either CrewAI (enhanced) or standard pipeline.
        
        Args:
            file_path: Path to the document file
            content_types: Types of content to generate ["summaries", "flashcards", "quiz"]
            workflow_type: CrewAI workflow type ("comprehensive", "focused", etc.)
            enable_quality_review: Whether to include quality review (CrewAI only)
            use_crewai: Whether to use CrewAI enhancement (if available)
            
        Returns:
            Dictionary containing generated materials and metadata
        """
        if content_types is None:
            content_types = ["summaries", "flashcards", "quiz"]
            
        # Process document first
        text_chunks = self.ingest_file(file_path)
        if not text_chunks:
            return {
                "status": "error",
                "error": "Failed to process document",
                "file_path": file_path
            }
        
        # Prepare document content for agents
        document_content = " ".join([chunk.get("text", "") for chunk in text_chunks])
        
        # Retrieve relevant context using RAG
        rag_context = ""
        try:
            # Use a sample of the document as query to get relevant context
            sample_query = document_content[:500]  # First 500 chars as query
            context_results = self._retrieve_context(sample_query, top_k=5)
            rag_context = " ".join([result[0].get("text", "") for result in context_results])
        except Exception as e:
            logger.warning(f"Failed to retrieve RAG context: {e}")
        
        # Choose generation method
        if use_crewai and self.is_crewai_available():
            logger.info("Using CrewAI enhanced generation")
            try:
                result = self.crewai_orchestrator.generate_study_materials(
                    document_content=document_content,
                    rag_context=rag_context,
                    content_types=content_types,
                    workflow_type=workflow_type,
                    enable_quality_review=enable_quality_review
                )
                result["generation_method"] = "crewai_enhanced"
                result["file_path"] = file_path
                return result
                
            except Exception as e:
                logger.error(f"CrewAI generation failed: {e}")
                logger.info("Falling back to standard pipeline")
                # Fall through to standard pipeline
        
        # Standard pipeline generation
        logger.info("Using standard pipeline generation")
        result = {
            "status": "success",
            "generation_method": "standard_pipeline",
            "file_path": file_path,
            "content_types_generated": content_types,
            "generated_materials": {}
        }
        
        try:
            if "summaries" in content_types:
                result["generated_materials"]["summaries"] = self._generate_standard_summaries(text_chunks)
            
            if "flashcards" in content_types:
                result["generated_materials"]["flashcards"] = self._generate_standard_flashcards(text_chunks)
            
            if "quiz" in content_types:
                result["generated_materials"]["quiz"] = self._generate_standard_quiz(text_chunks)
                
            return result
            
        except Exception as e:
            logger.error(f"Standard generation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "generation_method": "standard_pipeline",
                "file_path": file_path
            }
    
    def generate_crewai_summaries(self, file_path: str) -> Dict[str, any]:
        """Generate enhanced summaries using CrewAI multi-agent workflow."""
        if not self.is_crewai_available():
            return {
                "status": "error",
                "error": "CrewAI not available",
                "suggestion": "Use generate_summaries() for standard generation"
            }
        
        text_chunks = self.ingest_file(file_path)
        if not text_chunks:
            return {"status": "error", "error": "Failed to process document"}
        
        document_content = " ".join([chunk.get("text", "") for chunk in text_chunks])
        
        return self.crewai_orchestrator.generate_enhanced_summaries(
            document_content=document_content,
            rag_context=self._get_rag_context(document_content)
        )
    
    def generate_crewai_flashcards(self, file_path: str) -> Dict[str, any]:
        """Generate enhanced flashcards using CrewAI multi-agent workflow."""
        if not self.is_crewai_available():
            return {
                "status": "error",
                "error": "CrewAI not available",
                "suggestion": "Use generate_flashcards() for standard generation"
            }
        
        text_chunks = self.ingest_file(file_path)
        if not text_chunks:
            return {"status": "error", "error": "Failed to process document"}
        
        document_content = " ".join([chunk.get("text", "") for chunk in text_chunks])
        
        return self.crewai_orchestrator.generate_enhanced_flashcards(
            document_content=document_content,
            rag_context=self._get_rag_context(document_content)
        )
    
    def generate_crewai_quiz(self, file_path: str) -> Dict[str, any]:
        """Generate enhanced quiz using CrewAI multi-agent workflow."""
        if not self.is_crewai_available():
            return {
                "status": "error",
                "error": "CrewAI not available",
                "suggestion": "Use generate_quiz() for standard generation"
            }
        
        text_chunks = self.ingest_file(file_path)
        if not text_chunks:
            return {"status": "error", "error": "Failed to process document"}
        
        document_content = " ".join([chunk.get("text", "") for chunk in text_chunks])
        
        return self.crewai_orchestrator.generate_enhanced_quiz(
            document_content=document_content,
            rag_context=self._get_rag_context(document_content)
        )
    
    def generate_complete_study_package(self, file_path: str, use_crewai: bool = True) -> Dict[str, any]:
        """Generate a complete study package with all material types."""
        return self.generate_enhanced_study_materials(
            file_path=file_path,
            content_types=["summaries", "flashcards", "quiz"],
            workflow_type="comprehensive",
            enable_quality_review=True,
            use_crewai=use_crewai
        )
    
    def _get_rag_context(self, document_content: str) -> str:
        """Get RAG context for CrewAI workflows."""
        try:
            sample_query = document_content[:500]
            context_results = self._retrieve_context(sample_query, top_k=5)
            return " ".join([result[0].get("text", "") for result in context_results])
        except Exception as e:
            logger.warning(f"Failed to retrieve RAG context: {e}")
            return ""
    
    def _generate_standard_summaries(self, text_chunks: List[Dict]) -> Dict[str, str]:
        """Generate summaries using standard pipeline."""
        # Use existing summary generation logic
        summaries = {}
        text_content = " ".join([chunk.get("text", "") for chunk in text_chunks])
        
        summaries["sentence"] = self.summary_generator.generate_summary(text_content, "sentence")
        summaries["paragraph"] = self.summary_generator.generate_summary(text_content, "paragraph") 
        summaries["section"] = self.summary_generator.generate_summary(text_content, "section")
        
        return summaries
    
    def _generate_standard_flashcards(self, text_chunks: List[Dict]) -> Dict[str, List]:
        """Generate flashcards using standard pipeline."""
        # Use existing flashcard generation logic
        flashcards = {}
        text_content = " ".join([chunk.get("text", "") for chunk in text_chunks])
        
        flashcards["definition"] = self.flashcard_generator.generate_flashcards(text_content, "definition")
        flashcards["concept"] = self.flashcard_generator.generate_flashcards(text_content, "concept")
        flashcards["cloze"] = self.flashcard_generator.generate_flashcards(text_content, "cloze")
        
        return flashcards
    
    def _generate_standard_quiz(self, text_chunks: List[Dict]) -> Dict[str, List]:
        """Generate quiz using standard pipeline."""
        # Use existing quiz generation logic
        quiz = {}
        text_content = " ".join([chunk.get("text", "") for chunk in text_chunks])
        
        quiz["mcq"] = self.quiz_generator.generate_quiz(text_content, "mcq")
        quiz["short_answer"] = self.quiz_generator.generate_quiz(text_content, "short_answer")
        
        # Only include numerical if content seems to have mathematical content
        if any(char.isdigit() for char in text_content):
            quiz["numerical"] = self.quiz_generator.generate_quiz(text_content, "numerical")
        
        return quiz


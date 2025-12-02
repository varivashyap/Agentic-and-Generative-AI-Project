"""
User settings manager for dynamic hyperparameter configuration.
Allows users to override default config.yaml values without modifying the file.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class UserSettings:
    """User-configurable hyperparameters with defaults from config.yaml."""
    
    # LLM Generation Settings
    temperature: float = 0.2  # Creativity (0.0 = deterministic, 1.0 = creative)
    max_tokens: int = 512  # Maximum response length
    top_p: float = 0.9  # Nucleus sampling (0.0-1.0)
    
    # Summary Settings
    summary_temperature: float = 0.1  # Lower = more factual
    summary_max_tokens: int = 600
    summary_scale: str = "paragraph"  # sentence, paragraph, section
    
    # Flashcard Settings
    flashcard_temperature: float = 0.25
    flashcard_max_tokens: int = 1500
    flashcard_max_cards: int = 20
    
    # Quiz Settings
    quiz_temperature: float = 0.2
    quiz_max_tokens: int = 1500
    quiz_num_questions: int = 10
    
    # Chatbot Settings
    chatbot_temperature: float = 0.7  # Higher for conversational
    chatbot_max_tokens: int = 300
    chatbot_max_history: int = 5
    
    # Retrieval Settings
    retrieval_top_k: int = 20  # Number of chunks to retrieve
    reranker_top_m: int = 6  # Final chunks after reranking
    
    # Advanced Settings (for power users)
    chunk_size_tokens: int = 300
    chunk_overlap_tokens: int = 60
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSettings':
        """Create from dictionary, ignoring unknown keys."""
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)


class SettingsManager:
    """Manage user settings with persistence and defaults from config.yaml."""
    
    def __init__(self, cache_dir: str = "data/cache"):
        """Initialize settings manager."""
        self.cache_dir = Path(cache_dir)
        self.settings_file = self.cache_dir / "user_settings.json"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load default settings from config.yaml
        self.default_settings = self._load_defaults_from_config()
        
        # Load user settings (if any)
        self.user_settings: Dict[str, UserSettings] = {}
        self._load_user_settings()
    
    def _load_defaults_from_config(self) -> UserSettings:
        """Load default values from config.yaml."""
        try:
            from src.config import get_config
            config = get_config()
            
            return UserSettings(
                # LLM defaults
                temperature=0.2,
                max_tokens=512,
                top_p=0.9,
                
                # Summary defaults
                summary_temperature=config.generation.summary_temperature,
                summary_max_tokens=config.generation.summary_max_tokens,
                summary_scale="paragraph",
                
                # Flashcard defaults
                flashcard_temperature=config.generation.flashcard_temperature,
                flashcard_max_tokens=config.generation.flashcard_max_tokens,
                flashcard_max_cards=20,
                
                # Quiz defaults
                quiz_temperature=config.generation.quiz_temperature,
                quiz_max_tokens=config.generation.quiz_max_tokens,
                quiz_num_questions=10,
                
                # Chatbot defaults
                chatbot_temperature=0.7,
                chatbot_max_tokens=300,
                chatbot_max_history=5,
                
                # Retrieval defaults
                retrieval_top_k=config.retrieval.top_k,
                reranker_top_m=config.retrieval.top_m,
                
                # Chunking defaults
                chunk_size_tokens=config.chunking.chunk_size_tokens,
                chunk_overlap_tokens=config.chunking.overlap_tokens,
            )
        except Exception as e:
            logger.warning(f"Failed to load config.yaml defaults: {e}")
            return UserSettings()  # Use dataclass defaults
    
    def _load_user_settings(self):
        """Load user settings from disk."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    for user_id, settings_dict in data.items():
                        self.user_settings[user_id] = UserSettings.from_dict(settings_dict)
                logger.info(f"Loaded settings for {len(self.user_settings)} users")
            except Exception as e:
                logger.error(f"Failed to load user settings: {e}")

    def _save_user_settings(self):
        """Save user settings to disk."""
        try:
            data = {
                user_id: settings.to_dict()
                for user_id, settings in self.user_settings.items()
            }
            with open(self.settings_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug("Saved user settings to disk")
        except Exception as e:
            logger.error(f"Failed to save user settings: {e}")

    def get_settings(self, user_id: str = "default") -> UserSettings:
        """
        Get settings for a user. Returns default if user hasn't customized.

        Args:
            user_id: User identifier

        Returns:
            UserSettings object (either custom or default)
        """
        if user_id in self.user_settings:
            logger.debug(f"Using custom settings for user {user_id}")
            return self.user_settings[user_id]
        else:
            logger.debug(f"Using default settings for user {user_id}")
            return self.default_settings

    def update_settings(
        self,
        user_id: str,
        settings_update: Dict[str, Any]
    ) -> UserSettings:
        """
        Update settings for a user. Only updates provided fields.

        Args:
            user_id: User identifier
            settings_update: Dictionary of settings to update

        Returns:
            Updated UserSettings object
        """
        # Get current settings (or default)
        current = self.get_settings(user_id)

        # Create updated settings
        current_dict = current.to_dict()
        current_dict.update(settings_update)
        updated = UserSettings.from_dict(current_dict)

        # Save to user settings
        self.user_settings[user_id] = updated
        self._save_user_settings()

        logger.info(f"Updated settings for user {user_id}: {list(settings_update.keys())}")
        return updated

    def reset_settings(self, user_id: str) -> UserSettings:
        """
        Reset user settings to defaults.

        Args:
            user_id: User identifier

        Returns:
            Default UserSettings object
        """
        if user_id in self.user_settings:
            del self.user_settings[user_id]
            self._save_user_settings()
            logger.info(f"Reset settings for user {user_id} to defaults")
        return self.default_settings

    def has_custom_settings(self, user_id: str) -> bool:
        """Check if user has customized settings."""
        return user_id in self.user_settings

    def get_settings_schema(self) -> Dict[str, Any]:
        """
        Get schema describing all available settings.
        Used by frontend to build settings UI.
        """
        return {
            "llm": {
                "temperature": {
                    "type": "float",
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "default": self.default_settings.temperature,
                    "description": "Creativity level (0=deterministic, 1=creative)"
                },
                "max_tokens": {
                    "type": "int",
                    "min": 100,
                    "max": 2000,
                    "step": 50,
                    "default": self.default_settings.max_tokens,
                    "description": "Maximum response length"
                },
                "top_p": {
                    "type": "float",
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "default": self.default_settings.top_p,
                    "description": "Nucleus sampling threshold"
                }
            },
            "summary": {
                "temperature": {
                    "type": "float",
                    "min": 0.0,
                    "max": 0.5,
                    "step": 0.05,
                    "default": self.default_settings.summary_temperature,
                    "description": "Summary creativity (lower=more factual)"
                },
                "max_tokens": {
                    "type": "int",
                    "min": 200,
                    "max": 1000,
                    "step": 50,
                    "default": self.default_settings.summary_max_tokens,
                    "description": "Summary length"
                }
            },
            "flashcard": {
                "temperature": {
                    "type": "float",
                    "min": 0.0,
                    "max": 0.5,
                    "step": 0.05,
                    "default": self.default_settings.flashcard_temperature,
                    "description": "Flashcard creativity"
                },
                "max_cards": {
                    "type": "int",
                    "min": 5,
                    "max": 50,
                    "step": 5,
                    "default": self.default_settings.flashcard_max_cards,
                    "description": "Maximum flashcards to generate"
                }
            },
            "quiz": {
                "temperature": {
                    "type": "float",
                    "min": 0.0,
                    "max": 0.5,
                    "step": 0.05,
                    "default": self.default_settings.quiz_temperature,
                    "description": "Quiz creativity"
                },
                "num_questions": {
                    "type": "int",
                    "min": 5,
                    "max": 20,
                    "step": 5,
                    "default": self.default_settings.quiz_num_questions,
                    "description": "Number of questions"
                }
            },
            "chatbot": {
                "temperature": {
                    "type": "float",
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "default": self.default_settings.chatbot_temperature,
                    "description": "Chatbot creativity (higher=more conversational)"
                },
                "max_tokens": {
                    "type": "int",
                    "min": 100,
                    "max": 500,
                    "step": 50,
                    "default": self.default_settings.chatbot_max_tokens,
                    "description": "Response length"
                }
            },
            "retrieval": {
                "top_k": {
                    "type": "int",
                    "min": 5,
                    "max": 50,
                    "step": 5,
                    "default": self.default_settings.retrieval_top_k,
                    "description": "Number of chunks to retrieve"
                },
                "top_m": {
                    "type": "int",
                    "min": 2,
                    "max": 10,
                    "step": 1,
                    "default": self.default_settings.reranker_top_m,
                    "description": "Final chunks after reranking"
                }
            }
        }


# Global settings manager instance
_settings_manager: Optional[SettingsManager] = None


def get_settings_manager() -> SettingsManager:
    """Get global settings manager instance."""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager


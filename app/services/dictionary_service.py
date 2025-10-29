import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from app.schemas.schemas import WordDefinition, DictionaryResponse
from app.repositories.paragraph_repository import ParagraphRepository


logger = logging.getLogger(__name__)


class DictionaryService:
    """Service layer for dictionary and word analysis operations."""
    
    def __init__(self):
        self.repository = ParagraphRepository()
    
    async def analyze_word_frequency_with_definitions(
        self,
        db: AsyncSession,
        dictionary_api_url: str,
        word_limit: int = 10,
        timeout: float = 10.0
    ) -> DictionaryResponse:
        """
        Analyze word frequency and fetch definitions for top words.
        
        Args:
            db: Database session
            dictionary_api_url: Base URL for dictionary API
            word_limit: Number of top words to analyze
            timeout: Timeout for dictionary API calls
            
        Returns:
            DictionaryResponse with words, frequencies, and definitions
        """
        logger.info("Starting word frequency analysis with definitions")
        
        # Check if there are any paragraphs
        total_paragraphs = await self.repository.count(db)
        if total_paragraphs == 0:
            logger.info("No paragraphs found in database")
            return DictionaryResponse(
                words=[],
                total_paragraphs_analyzed=0,
                message="No paragraphs available for analysis"
            )
        
        # Get word frequency analysis
        try:
            word_frequencies = await self.repository.analyze_word_frequency(db, word_limit)
            logger.info(f"Found {len(word_frequencies)} frequent words")
            
        except Exception as e:
            logger.error(f"Error analyzing word frequencies: {e}")
            raise
        
        if not word_frequencies:
            logger.info("No frequent words found after analysis")
            return DictionaryResponse(
                words=[],
                total_paragraphs_analyzed=total_paragraphs,
                message="No frequent words found in stored paragraphs"
            )
        
        # Fetch definitions for each word
        word_definitions = []
        
        for word, frequency in word_frequencies:
            try:
                logger.info(f"Fetching definition for word: {word} (frequency: {frequency})")
                
                word_data = await self._fetch_word_definition(word, dictionary_api_url, timeout)
                
                if word_data:
                    definition_info = self._extract_definition_info(word_data)
                    
                    word_def = WordDefinition(
                        word=word,
                        frequency=frequency,
                        definition=definition_info["definition"],
                        pronunciation=definition_info["pronunciation"],
                        part_of_speech=definition_info["part_of_speech"]
                    )
                else:
                    # Create entry without definition if API fails
                    word_def = WordDefinition(
                        word=word,
                        frequency=frequency,
                        definition=None,
                        pronunciation=None,
                        part_of_speech=None
                    )
                
                word_definitions.append(word_def)
                
            except Exception as e:
                logger.warning(f"Error processing word '{word}': {e}")
                # Include word without definition if there's an error
                word_definitions.append(WordDefinition(
                    word=word,
                    frequency=frequency,
                    definition=None,
                    pronunciation=None,
                    part_of_speech=None
                ))
        
        logger.info(f"Successfully processed {len(word_definitions)} words")
        
        return DictionaryResponse(
            words=word_definitions,
            total_paragraphs_analyzed=total_paragraphs,
            message=f"Top {len(word_definitions)} most frequent words with definitions"
        )
    
    async def _fetch_word_definition(
        self, 
        word: str, 
        api_url: str, 
        timeout: float
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch word definition from dictionary API.
        
        Args:
            word: The word to get definition for
            api_url: Base URL for dictionary API
            timeout: Request timeout
            
        Returns:
            Dictionary containing word definition data or None if not found
        """
        try:
            timeout_config = httpx.Timeout(timeout)
            
            async with httpx.AsyncClient(timeout=timeout_config) as client:
                response = await client.get(f"{api_url}/{word}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data and isinstance(data, list) and len(data) > 0:
                        return data[0]  # Return first definition entry
                elif response.status_code == 404:
                    logger.info(f"No definition found for word: {word}")
                    return None
                else:
                    logger.warning(f"Dictionary API returned status {response.status_code} for word: {word}")
                    return None
                    
        except httpx.TimeoutException:
            logger.warning(f"Timeout while fetching definition for word: {word}")
            return None
        except Exception as e:
            logger.warning(f"Error fetching definition for word '{word}': {e}")
            return None
    
    def _extract_definition_info(self, word_data: Dict[str, Any]) -> Dict[str, Optional[str]]:
        """
        Extract definition, pronunciation, and part of speech from API response.
        
        Args:
            word_data: Raw dictionary API response data
            
        Returns:
            Dictionary with extracted information
        """
        result = {
            "definition": None,
            "pronunciation": None,
            "part_of_speech": None
        }
        
        try:
            # Extract phonetic pronunciation
            if "phonetics" in word_data and word_data["phonetics"]:
                for phonetic in word_data["phonetics"]:
                    if phonetic.get("text"):
                        result["pronunciation"] = phonetic["text"]
                        break
            
            # Extract definition and part of speech from meanings
            if "meanings" in word_data and word_data["meanings"]:
                first_meaning = word_data["meanings"][0]
                
                # Get part of speech
                result["part_of_speech"] = first_meaning.get("partOfSpeech")
                
                # Get first definition
                definitions = first_meaning.get("definitions", [])
                if definitions and len(definitions) > 0:
                    result["definition"] = definitions[0].get("definition")
        
        except Exception as e:
            logger.warning(f"Error extracting definition info: {e}")
        
        return result
import re
from typing import List, Optional, Tuple, Dict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func, desc, or_, select
from app.database.database import Paragraph
from app.schemas.schemas import ParagraphCreate
from app.repositories.paragraph_repository_interface import ParagraphRepositoryInterface


# Common English stop words to exclude from frequency analysis
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
    'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
    'above', 'below', 'between', 'among', 'under', 'over', 'is', 'are', 'was', 'were',
    'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'should', 'could', 'can', 'may', 'might', 'must', 'shall', 'i', 'you', 'he', 'she',
    'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her',
    'its', 'our', 'their', 'this', 'that', 'these', 'those', 'am', 'not', 'no', 'yes'
}


class ParagraphRepository(ParagraphRepositoryInterface):
    """Repository for paragraph data access operations."""
    
    async def create(self, db: AsyncSession, paragraph: ParagraphCreate) -> Paragraph:
        """Create a new paragraph in the database."""
        db_paragraph = Paragraph(text=paragraph.text)
        db.add(db_paragraph)
        await db.commit()
        await db.refresh(db_paragraph)
        return db_paragraph
    
    
    async def count(self, db: AsyncSession) -> int:
        """Get total count of paragraphs in database."""
        result = await db.execute(select(func.count(Paragraph.id)))
        return result.scalar()
    
    async def search_by_text(self, db: AsyncSession, words: List[str], operator: str = "or") -> List[Paragraph]:
        """
        Search paragraphs using PostgreSQL full-text search or simple text search for tests.
        
        Args:
            db: Database session
            words: List of words to search for
            operator: 'and' or 'or' for combining search terms
            
        Returns:
            List of matching paragraphs ordered by relevance
        """
        import os
        
        if not words:
            return []
        
        # Clean and prepare search terms
        clean_words = [re.sub(r'[^\w\s]', '', word.strip().lower()) for word in words if word.strip()]
        if not clean_words:
            return []

        # PostgreSQL full-text search - Fixed implementation
        if operator == "and":
                # For AND operation, create separate plainto_tsquery for each word and combine with AND
                tsquery_parts = [f"plainto_tsquery('english', '{word}')" for word in clean_words]
                tsquery_condition = " AND ".join([f"search_vector @@ {part}" for part in tsquery_parts])
                
                sql_query = f"""
                    SELECT id, text, created_at,
                           ts_rank(search_vector, {tsquery_parts[0]}) as rank
                    FROM paragraphs 
                    WHERE {tsquery_condition}
                    ORDER BY rank DESC, created_at DESC
                """
                result = await db.execute(text(sql_query))
                rows = result.fetchall()
                
                # Convert to Paragraph objects
                paragraphs = []
                if rows:  # Check if rows is not None or empty
                    for row in rows:
                        paragraph = Paragraph()
                        paragraph.id = row.id
                        paragraph.text = row.text
                        paragraph.created_at = row.created_at
                        paragraphs.append(paragraph)
                
                return paragraphs
                
        else:  # OR operation
            # For OR operation, create separate conditions for each word and combine with UNION
            union_queries = []
            for i, word in enumerate(clean_words):
                union_queries.append(f"""
                    SELECT id, text, created_at,
                           ts_rank(search_vector, plainto_tsquery('english', :word{i})) as rank
                    FROM paragraphs 
                    WHERE search_vector @@ plainto_tsquery('english', :word{i})
                """)
            
            # Combine with UNION and remove duplicates, then order by rank
            sql_query = f"""
                SELECT DISTINCT id, text, created_at, MAX(rank) as max_rank
                FROM ({' UNION ALL '.join(union_queries)}) combined
                GROUP BY id, text, created_at
                ORDER BY max_rank DESC, created_at DESC
            """
            
            # Create parameters dict
            params = {f"word{i}": word for i, word in enumerate(clean_words)}
            result = await db.execute(text(sql_query), params)
        
            rows = result.fetchall()
            
            # Convert to Paragraph objects
            paragraphs = []
            if rows and hasattr(rows, '__iter__'):  # Check if rows is not None, empty, or a coroutine
                for row in rows:
                    paragraph = Paragraph()
                    paragraph.id = row.id
                    paragraph.text = row.text
                    paragraph.created_at = row.created_at
                    paragraphs.append(paragraph)
                
            return paragraphs
    

    async def analyze_word_frequency(self, db: AsyncSession, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Analyze all paragraphs to find the most frequent words.
        
        Args:
            db: Database session
            limit: Number of top words to return
            
        Returns:
            List of tuples (word, frequency) for top words
        """
        # Get all paragraph texts
        result = await db.execute(select(Paragraph.text))
        paragraphs = result.fetchall()
        
        if not paragraphs:
            return []
        
        # Count word frequencies
        word_count: Dict[str, int] = {}
        
        for (text,) in paragraphs:
            # Convert to lowercase and extract words
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            
            for word in words:
                # Skip stop words and very short words
                if word not in STOP_WORDS and len(word) >= 3:
                    word_count[word] = word_count.get(word, 0) + 1
        
        # Sort by frequency and return top results
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return sorted_words[:limit]
import re
from typing import Dict, List, Any

class TextParser:
    """Utility for parsing text content"""
    
    @staticmethod
    def extract_sections(text: str, section_headers: List[str]) -> Dict[str, str]:
        """Extract sections from text content
        
        Args:
            text: Text content
            section_headers: List of section headers to extract
            
        Returns:
            Dictionary mapping section names to section content
        """
        sections = {}
        
        # Convert text to lowercase for case-insensitive matching
        lower_text = text.lower()
        
        for i, header in enumerate(section_headers):
            # Look for current header in text
            lower_header = header.lower()
            header_pos = lower_text.find(lower_header)
            
            if header_pos == -1:
                # Header not found
                continue
            
            # Find start of content (after header)
            start_pos = header_pos + len(lower_header)
            
            # Find next header position
            next_pos = len(text)
            for next_header in section_headers:
                if next_header.lower() == lower_header:
                    continue  # Skip current header
                
                next_header_pos = lower_text.find(next_header.lower(), start_pos)
                if next_header_pos != -1 and next_header_pos < next_pos:
                    next_pos = next_header_pos
            
            # Extract section content
            section_content = text[start_pos:next_pos].strip()
            sections[header] = section_content
        
        return sections
    
    @staticmethod
    def extract_list_items(text: str) -> List[str]:
        """Extract list items from text
        
        Args:
            text: Text content with list items
            
        Returns:
            List of extracted items
        """
        items = []
        
        # Try different list formats
        patterns = [
            r'(?:^|\n)[\s]*[•\*\-]\s*(.*?)(?=(?:^|\n)[\s]*[•\*\-]|$)',  # Bullet points
            r'(?:^|\n)[\s]*\d+[\.\)]\s*(.*?)(?=(?:^|\n)[\s]*\d+[\.\)]|$)',  # Numbered items
            r'(?:^|\n)(.*?)(?:(?:^|\n)|$)'  # Plain lines
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            if matches:
                items = [item.strip() for item in matches if item.strip()]
                break
        
        # If still no items found, try comma-separated list
        if not items and ',' in text:
            items = [item.strip() for item in text.split(',') if item.strip()]
        
        return items
    
    @staticmethod
    def extract_key_value_pairs(text: str) -> Dict[str, str]:
        """Extract key-value pairs from text
        
        Args:
            text: Text content with key-value pairs
            
        Returns:
            Dictionary of key-value pairs
        """
        pairs = {}
        
        # Look for patterns like "Key: Value" or "Key - Value"
        patterns = [
            r'([\w\s]+):\s*(.*?)(?=(?:[\w\s]+:)|$)',  # Key: Value
            r'([\w\s]+)-\s*(.*?)(?=(?:[\w\s]+-)|$)',  # Key - Value
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            if matches:
                for key, value in matches:
                    key = key.strip()
                    value = value.strip()
                    if key and value:
                        pairs[key] = value
        
        return pairs 
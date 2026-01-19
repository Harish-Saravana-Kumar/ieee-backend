from importlib.metadata import PackageNotFoundError
import os
import re
import torch
import logging
import docx
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model = SentenceTransformer('all-MiniLM-L6-v2')  # Light, fast BERT model

def extract_text_from_docx(file_path):
    try:
        document = docx.Document(file_path)
        full_text = []
        for para in document.paragraphs:
            full_text.append(para.text)
        return "\n".join(full_text)
    except PackageNotFoundError:
        logger.error("The uploaded file is not a valid .docx file.")
        raise ValueError("The uploaded file is not a valid .docx file. Please upload a proper Word document.")
    except Exception as e:
        logger.error(f"Failed to extract text: {e}")
        raise ValueError(f"Error reading document: {str(e)}")

def split_into_sentences(text: str) -> List[str]:
    # Basic sentence splitting (you can improve with SpaCy/NLTK)
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]

def extract_references(text: str) -> List[str]:
    # Extract references block based on "References" section
    if "references" not in text.lower():
        return []
    refs = text.lower().split("references")[-1]
    return split_into_sentences(refs)

def check_citations(text: str, references: List[str]) -> Dict[str, bool]:
    citation_pattern = r"\[(\d+)\]"
    found = re.findall(citation_pattern, text)
    ref_map = {str(i+1): ref for i, ref in enumerate(references)}
    citation_check = {}
    for c in found:
        citation_check[f"[{c}]"] = c in ref_map
    return citation_check

def compute_semantic_similarity(sentences: List[str], threshold: float = 0.85) -> List[Dict]:
    embeddings = model.encode(sentences, convert_to_tensor=True)
    sims = cosine_similarity(embeddings.cpu(), embeddings.cpu())
    
    flagged = []
    for i in range(len(sentences)):
        for j in range(i+1, len(sentences)):
            if sims[i][j] > threshold:
                flagged.append({
                    "sentence_1": sentences[i],
                    "sentence_2": sentences[j],
                    "similarity": float(sims[i][j]),
                    "index_1": i,
                    "index_2": j
                })
    return flagged

def calculate_word_count(text: str) -> int:
    """Calculate total word count in the document"""
    return len(text.split())

def detect_repetitive_content(sentences: List[str]) -> Dict:
    """Detect patterns of repetitive content"""
    word_frequency = {}
    for sentence in sentences:
        words = sentence.lower().split()
        for word in words:
            if len(word) > 4:  # Only count significant words
                word_frequency[word] = word_frequency.get(word, 0) + 1
    
    # Find overly repeated words
    total_words = sum(word_frequency.values())
    repetitive_words = {word: count for word, count in word_frequency.items() 
                        if count > 10 and count / total_words > 0.02}
    
    return {
        "repetitive_words": repetitive_words,
        "unique_word_count": len(word_frequency),
        "total_word_count": total_words
    }

def generate_insights(text: str, sentences: List[str], similar_pairs: List[Dict], 
                      citations: Dict, references: List[str]) -> List[str]:
    """Generate actionable insights for real-world scenarios"""
    insights = []
    
    # Insight 1: Citation analysis
    if citations:
        valid_citations = sum(1 for v in citations.values() if v)
        invalid_citations = len(citations) - valid_citations
        if invalid_citations > 0:
            insights.append(f"⚠ Citation Issue: {invalid_citations} citation(s) found without corresponding references. Ensure all citations are properly referenced.")
        else:
            insights.append(f"✓ All {len(citations)} citations are properly referenced.")
    else:
        if len(references) > 0:
            insights.append("⚠ References exist but no citations found in text. Ensure proper citation placement.")
        else:
            insights.append("ℹ No citations or references found. Consider adding references to support your claims.")
    
    # Insight 2: Document structure
    word_count = calculate_word_count(text)
    total_sentences = len(sentences)
    avg_sentence_length = word_count / total_sentences if total_sentences > 0 else 0
    
    if avg_sentence_length > 30:
        insights.append(f"ℹ Average sentence length is {avg_sentence_length:.1f} words. Consider breaking down complex sentences for better readability.")
    elif avg_sentence_length < 10:
        insights.append(f"ℹ Average sentence length is {avg_sentence_length:.1f} words. Consider developing ideas more fully.")
    else:
        insights.append(f"✓ Good sentence structure with average length of {avg_sentence_length:.1f} words.")
    
    # Insight 3: Content analysis
    repetitive_data = detect_repetitive_content(sentences)
    if repetitive_data['repetitive_words']:
        top_repeated = sorted(repetitive_data['repetitive_words'].items(), 
                            key=lambda x: x[1], reverse=True)[:3]
        repeated_terms = ", ".join([f"'{word}' ({count}x)" for word, count in top_repeated])
        insights.append(f"⚠ Repetitive terminology detected: {repeated_terms}. Consider using synonyms for variety.")
    
    # Insight 4: Vocabulary richness
    vocabulary_ratio = repetitive_data['unique_word_count'] / repetitive_data['total_word_count'] if repetitive_data['total_word_count'] > 0 else 0
    if vocabulary_ratio < 0.3:
        insights.append(f"⚠ Limited vocabulary diversity ({vocabulary_ratio:.1%}). Enhance text with more varied terminology.")
    elif vocabulary_ratio > 0.5:
        insights.append(f"✓ Good vocabulary diversity ({vocabulary_ratio:.1%}). Effective use of varied terminology.")
    
    # Insight 5: Document completeness
    has_intro = any('introduction' in s.lower() or 'abstract' in s.lower() for s in sentences[:5])
    has_conclusion = any('conclusion' in s.lower() or 'summary' in s.lower() for s in sentences[-5:])
    
    if has_intro:
        insights.append("✓ Clear introduction/abstract detected.")
    else:
        insights.append("ℹ Consider adding a clear introduction or abstract section.")
    
    if has_conclusion:
        insights.append("✓ Clear conclusion/summary detected.")
    else:
        insights.append("ℹ Consider adding a concluding section to summarize findings.")
    
    # Insight 6: Word count assessment
    if word_count < 500:
        insights.append(f"ℹ Document is brief ({word_count} words). Consider expanding key sections.")
    elif word_count > 5000:
        insights.append(f"✓ Comprehensive document ({word_count:,} words).")
    else:
        insights.append(f"✓ Well-sized document ({word_count:,} words).")
    
    return insights

def analyze_plagiarism(docx_path: str, threshold: float = 0.85) -> Dict:
    try:
        logger.info("Extracting text...")
        text = extract_text_from_docx(docx_path)
        sentences = split_into_sentences(text)
        references = extract_references(text)
        citations = check_citations(text, references)
        
        # Skip internal similarity check - focus on document quality metrics
        total_sentences = len(sentences)
        word_count = calculate_word_count(text)
        
        # Generate insights without similarity data
        insights = generate_insights(text, sentences, [], citations, references)
        
        # Calculate quality score (0-100)
        quality_score = 0
        
        # Citation quality (40 points max)
        citation_issues = sum(1 for v in citations.values() if not v)
        if len(citations) > 0:
            citation_accuracy = (sum(1 for v in citations.values() if v) / len(citations)) * 40
            quality_score += citation_accuracy
        elif len(references) == 0:
            quality_score += 20  # Partial credit if no citations/refs needed
        
        # Document structure (20 points max)
        has_intro = any('introduction' in s.lower() or 'abstract' in s.lower() for s in sentences[:5])
        has_conclusion = any('conclusion' in s.lower() or 'summary' in s.lower() for s in sentences[-5:])
        if has_intro:
            quality_score += 10
        if has_conclusion:
            quality_score += 10
        
        # Vocabulary richness (20 points max)
        repetitive_data = detect_repetitive_content(sentences)
        vocabulary_ratio = repetitive_data['unique_word_count'] / repetitive_data['total_word_count'] if repetitive_data['total_word_count'] > 0 else 0
        quality_score += min(vocabulary_ratio * 40, 20)  # Scale 0-0.5 ratio to 0-20 points
        
        # Sentence structure (10 points max)
        avg_sentence_length = word_count / total_sentences if total_sentences > 0 else 0
        if 10 <= avg_sentence_length <= 30:
            quality_score += 10
        elif 8 <= avg_sentence_length <= 35:
            quality_score += 5
        
        # Word count appropriateness (10 points max)
        if 500 <= word_count <= 10000:
            quality_score += 10
        elif 300 <= word_count < 500 or 10000 < word_count <= 15000:
            quality_score += 5
        
        # Round to integer
        quality_score = round(quality_score)
        
        # Determine overall assessment based on quality score
        if quality_score >= 85:
            overall_status = "EXCELLENT"
            status_message = f"Outstanding academic quality ({quality_score}/100)"
        elif quality_score >= 70:
            overall_status = "GOOD"
            status_message = f"Good quality with room for improvement ({quality_score}/100)"
        elif quality_score >= 50:
            overall_status = "NEEDS_IMPROVEMENT"
            status_message = f"Needs improvement in multiple areas ({quality_score}/100)"
        else:
            overall_status = "POOR"
            status_message = f"Significant quality issues detected ({quality_score}/100)"

        return {
            "overall_status": overall_status,
            "status_message": status_message,
            "quality_score": quality_score,
            "total_sentences": total_sentences,
            "word_count": word_count,
            "citation_validation": citations,
            "insights": insights,
            "statistics": {
                "unique_citations": len(citations),
                "valid_citations": sum(1 for v in citations.values() if v),
                "total_references": len(references),
                "citation_issues": citation_issues
            }
        }

    except Exception as e:
        logger.error(f"Plagiarism analysis failed: {e}")
        raise RuntimeError("Plagiarism analysis failed.")


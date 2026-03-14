import requests
import fitz  # PyMuPDF
from semanticscholar import SemanticScholar
import json
import logging
import itertools
import time

# Configure tool-level logging for ADK observability
logger = logging.getLogger(__name__)

def search_arxiv(query: str, limit: int = 3) -> str:
    """
    Searches arXiv for papers matching a query using the arXiv API.
    
    Args:
        query: The search query (e.g., a topic or keyword).
        limit: The maximum number of papers to return.
    
    Returns:
        A JSON string summarizing the search results, or an error message.
    """
    logger.info(f"Searching arXiv for: '{query}' (limit={limit})")
    try:
        # arXiv API endpoint
        base_url = "http://export.arxiv.org/api/query"
        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': limit,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        # Parse XML response
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)
        
        # Define namespaces
        ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom'
        }
        
        entries = root.findall('atom:entry', ns)
        
        if not entries:
            logger.warning(f"No papers found for query: '{query}'")
            return json.dumps({"error": "No papers found for the query."})
        
        logger.info(f"Found {len(entries)} papers.")
        
        papers_summary = []
        for entry in entries[:limit]:
            title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
            summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
            published = entry.find('atom:published', ns).text[:4]  # Year only
            link = entry.find('atom:id', ns).text
            
            # Get authors
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns).text
                authors.append(name)
            
            papers_summary.append({
                "title": title,
                "authors": authors,
                "year": published,
                "venue": "arXiv",
                "url": link,
                "abstract": summary[:500]  # Truncate long abstracts
            })
        
        return json.dumps(papers_summary, indent=2)
    
    except Exception as e:
        logger.error(f"arXiv search error: {e}")
        return json.dumps({"error": f"An error occurred while searching arXiv: {e}"})


# TODO: This method doesnt work; rate limits + pagination fuccc up the results
# def search_semantic_scholar(query: str, limit: int = 3) -> str:
#     """
#     Searches Semantic Scholar for papers matching a query and returns a summary.
    
#     Args:
#         query: The search query (e.g., a topic or keyword).
#         limit: The maximum number of papers to return.
    
#     Returns:
#         A JSON string summarizing the search results, or an error message.
#     """
#     logger.info(f"Searching Semantic Scholar for: '{query}' (limit={limit})")
#     try:
#         ss = SemanticScholar()
#         fields = ['title', 'url', 'abstract', 'authors', 'year', 'venue']
        
#         # CRITICAL: Convert to list immediately to prevent automatic pagination
#         # The semanticscholar library returns a PaginatedResults object that
#         # automatically fetches more pages when iterated, causing rate limits
#         results_iter = ss.search_paper(query, limit=limit, fields=fields)
#         results = list(itertools.islice(results_iter, limit))
        
#         if not results or len(results) == 0:
#             logger.warning(f"No papers found for query: '{query}'")
#             return json.dumps({"error": "No papers found for the query."})

#         logger.info(f"Found {len(results)} papers.")

#         # Format the results into a clear, summarized list
#         papers_summary = []
#         for paper in results:
#             # Paper objects use attribute access, not dictionary .get()
#             authors_list = []
#             if hasattr(paper, 'authors') and paper.authors:
#                 authors_list = [author.name if hasattr(author, 'name') else str(author) for author in paper.authors]
            
#             papers_summary.append({
#                 "title": paper.title if hasattr(paper, 'title') else None,
#                 "authors": authors_list,
#                 "year": paper.year if hasattr(paper, 'year') else None,
#                 "venue": paper.venue if hasattr(paper, 'venue') else None,
#                 "url": paper.url if hasattr(paper, 'url') else None,
#                 "abstract": paper.abstract if hasattr(paper, 'abstract') else None
#             })
        
#         return json.dumps(papers_summary, indent=2)

#     except Exception as e:
#         logger.error(f"Semantic Scholar error: {e}")
#         # If Semantic Scholar fails, try arXiv as fallback
#         logger.info("Falling back to arXiv search...")
#         return search_arxiv(query, limit)

def get_pdf_text_from_url(url: str, page_limit: int = 2) -> str:
    """
    Downloads a PDF from a URL and extracts text from the first few pages.
    
    Args:
        url: The direct URL to a PDF file.
        page_limit: The maximum number of pages to extract text from.
    
    Returns:
        A JSON string containing the extracted text, or an error message.
    """
    if not url or not url.lower().endswith('.pdf'):
        return json.dumps({"error": "Invalid URL. The URL must be a direct link to a .pdf file."})

    logger.info(f"Downloading PDF from URL: {url}")
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        logger.info("PDF downloaded successfully.")

        # Open the PDF from the content stream
        pdf_document = fitz.open(stream=response.content, filetype="pdf")
        total_pages = len(pdf_document)
        pages_to_extract = min(page_limit, total_pages)

        extracted_text = ""
        for page_num in range(pages_to_extract):
            page = pdf_document[page_num]
            extracted_text += page.get_text()

        pdf_document.close()

        if not extracted_text.strip():
            return json.dumps({"error": "No text could be extracted from the PDF."})

        return json.dumps({
            # cannot return the full text; will hog up the context window
            "text": extracted_text[:5000],  # Limit to first 5000 characters
            "pages_extracted": pages_to_extract,
            "total_pages": total_pages
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"An error occurred while reading PDF: {e}"})

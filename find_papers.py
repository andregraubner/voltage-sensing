import requests
import time
from urllib.parse import quote_plus

def search_papers(batch_size=100, max_results=None):
    """
    Search for papers containing the keyword in title or abstract.
    
    Args:
        keyword (str): Search term
        batch_size (int): Number of results per request (default: 100, max: 100)
        max_results (int): Maximum total results to return (default: None, meaning all available)
    """
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    batch_size = min(batch_size, 100)  # API limit is 100 per request
    total_fetched = 0
    
    try:
        while True:
            # Check if we've reached the maximum requested results
            if max_results and total_fetched >= max_results:
                break
                
            # Calculate how many results to fetch in this batch
            current_limit = batch_size
            if max_results:
                current_limit = min(batch_size, max_results - total_fetched)
            
            # URL encode the keyword and create query parameters
            params = {
                'query': 'voltage + protein + "electrophysiology"',
                'limit': current_limit,
                'offset': total_fetched,
                'fields': 'title,abstract,url',
                #'fieldsOfStudy': 'Biology'
            }
            
            # Make API request with appropriate delay to respect rate limits
            time.sleep(10)  # Rate limiting: 1 second between requests
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            search_data = response.json()
            
            # Extract papers from response
            papers = search_data.get('data', [])
            total = search_data.get('total', 0)
            
            if not papers:  # No more results
                break
                
            # Update the count of fetched papers
            total_fetched += len(papers)
            
            print(f"Fetched batch of {len(papers)} papers (Total: {total_fetched}/{total})")
            
            yield papers
            
            # If we've fetched all available papers, stop
            if total_fetched >= total:
                break
                
    except requests.exceptions.RequestException as e:
        print(f"Error searching papers: {e}")
        return

def process_papers(save_path, max_results=None):
    """
    Download paper data and write to file
    """

    for batch in search_papers(max_results=max_results):
        
        with open(save_path, "a") as f:
            papers = [f"{paper.get('title')}\n" for paper in batch]
            f.writelines(papers)

# Example usage
if __name__ == "__main__":
    papers = process_papers("mutagenesis.txt", max_results=1000)
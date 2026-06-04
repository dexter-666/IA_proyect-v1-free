"""youtube_video.py — Clean YouTube video launching action."""
import webbrowser
import urllib.parse

def youtube_video(parameters: dict, response=None, player=None) -> str:
    """Search for and play a YouTube video in the default browser."""
    query = parameters.get("query", "").strip()
    if not query:
        return "Please specify what you would like to play on YouTube, sir."
        
    try:
        encoded_query = urllib.parse.quote(query)
        # Directly launch search results or use auto-play URL
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        
        webbrowser.open(url)
        msg = f"Playing YouTube search for '{query}' in your browser."
        if player:
            player.write_log(f"📺 {msg}")
        return msg
    except Exception as e:
        return f"Failed to play YouTube video: {e}"

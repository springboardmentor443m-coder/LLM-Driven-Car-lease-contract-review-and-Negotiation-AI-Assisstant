export async function runFullAnalysis(text) {
  try {
    const response = await fetch("http://localhost:8000/llm/full-analysis", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API Error: ${response.statusText} - ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Full Analysis Failed:", error);
    // Provide more helpful error messages
    if (error.message.includes("Failed to fetch") || error.message.includes("NetworkError")) {
      return { 
        error: "Cannot connect to backend server. Please ensure the backend is running on http://localhost:8000" 
      };
    }
    return { error: error.message };
  }
}

export async function sendChatMessage(history, message) {
  try {
    const response = await fetch("http://localhost:8000/llm/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ history, message }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Chat API Error: ${response.statusText} - ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Chat Message Failed:", error);
    // Provide more helpful error messages
    if (error.message.includes("Failed to fetch") || error.message.includes("NetworkError")) {
      return { 
        error: "Cannot connect to backend server. Please ensure the backend is running on http://localhost:8000" 
      };
    }
    return { error: error.message };
  }
}
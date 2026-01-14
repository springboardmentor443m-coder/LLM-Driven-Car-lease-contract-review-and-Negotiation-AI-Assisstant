export async function uploadFile(file) {
  try {
    const fd = new FormData();
    fd.append("file", file); // Ensure your backend expects the key "file"

    const res = await fetch("http://localhost:8000/ocr/upload", {
      method: "POST",
      body: fd,
      // Note: Do NOT set 'Content-Type': 'multipart/form-data' manually here.
      // The browser sets it automatically with the correct boundary for FormData.
    });

    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`OCR Upload Failed: ${res.statusText} - ${errorText}`);
    }

    return await res.json();
  } catch (error) {
    console.error("OCR API Error:", error);
    // Provide more helpful error messages
    if (error.message.includes("Failed to fetch") || error.message.includes("NetworkError")) {
      return { 
        error: "Cannot connect to backend server. Please ensure the backend is running on http://localhost:8000" 
      };
    }
    return { error: error.message };
  }
}
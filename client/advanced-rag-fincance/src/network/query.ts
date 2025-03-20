export async function query(data: {
  query_id: string;
  query: string;
  conversation_id: string;
  document_id: string;
  file_name: string;
  user_id?: string;
}) {
  try {
    const response = await fetch(`http://127.0.0.1:5000/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      // Try to get more detailed error information
      const errorText = await response.text();
      throw new Error(
        `Server error (${response.status}): ${errorText || response.statusText}`
      );
    }

    return response.json();
  } catch (error) {
    console.error("Query request failed:", error);
    throw error; // Re-throw for the mutation error handler
  }
}

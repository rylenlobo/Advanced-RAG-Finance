export const cancelDocumentProcessing = async (
  documentId: string
): Promise<void> => {
  const response = await fetch(
    `http://127.0.0.1:5000/cancel-processing/${documentId}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      }
    }
  );

  if (!response.ok) {
    throw new Error(
      "An unexpected error occurred while trying to cancel the document processing"
    );
  }
};

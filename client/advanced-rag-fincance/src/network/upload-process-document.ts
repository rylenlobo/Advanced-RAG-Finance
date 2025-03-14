export const uploadProcessDocument = async (formData: FormData) => {
  const response = await fetch("http://127.0.0.1:5000/upload", {
    method: "POST",
    body: formData
  });

  if (!response.ok) {
    throw new Error(
      "An unexpected error occured while processing the document"
    );
  }
};

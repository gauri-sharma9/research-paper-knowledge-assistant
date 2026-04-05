import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function uploadPDFs(files, onProgress) {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }
  const response = await axios.post(`${BASE_URL}/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded * 100) / e.total));
      }
    },
  });
  return response.data;
}

export async function queryQuestion(question) {
  const response = await axios.post(`${BASE_URL}/query`, { question });
  return response.data;
}

export async function resetIndex() {
  const response = await axios.delete(`${BASE_URL}/reset`);
  return response.data;
}

export async function checkHealth() {
  const response = await axios.get(`${BASE_URL}/health`);
  return response.data;
}

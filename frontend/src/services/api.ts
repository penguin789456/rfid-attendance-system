import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail || "發生未知錯誤";
    console.error("API Error:", message);
    return Promise.reject(error);
  },
);

export default api;

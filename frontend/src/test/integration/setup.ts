const API_URL = import.meta.env.VITE_API_URL;

if (!API_URL) {
  console.warn(
    'VITE_API_URL not set — skipping integration tests.\n' +
    'Set VITE_API_URL to the running API (e.g. http://localhost:8000) to run them.',
  );
}

export { API_URL };

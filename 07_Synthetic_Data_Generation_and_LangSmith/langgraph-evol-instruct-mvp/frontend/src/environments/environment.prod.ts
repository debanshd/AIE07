// Production environment configuration
// This will be used when building for production

export const environment = {
  production: true,
  apiUrl: 'https://langgraph-evol-instruct-backend-new.fly.dev'
};

// Function to get API URL dynamically (for backward compatibility)
export function getApiUrl(): string {
  return environment.apiUrl;
} 
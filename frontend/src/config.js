let configCache = null;
let configPromise = null;

// Default API base (fallback)
const DEFAULT_API_BASE = 'https://password-tracker-backend-681629792414.us-central1.run.app';

// Initialize config on module load with immediate fallback
function initializeConfig() {
  if (configPromise) {
    console.log('📦 Config promise already exists, returning cached promise');
    return configPromise;
  }
  
  console.log('📦 Starting config initialization...');
  
  configPromise = (async () => {
    try {
      console.log('📦 Attempting to fetch /config.json');
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout
      
      // Add cache-buster to ensure fresh config.json
      const timestamp = Date.now();
      const res = await fetch(`/config.json?t=${timestamp}`, { 
        cache: 'no-store',
        signal: controller.signal 
      });
      
      clearTimeout(timeoutId);
      
      if (!res.ok) {
        console.warn(`📦 config.json returned status ${res.status}`);
        throw new Error(`HTTP ${res.status}`);
      }
      
      configCache = await res.json();
      console.log('✅ Config loaded from config.json:', configCache);
      return configCache;
    } catch (e) {
      console.warn('⚠️ Failed to load config.json:', e.message);
      console.log('📦 Using fallback API base:', DEFAULT_API_BASE);
      
      // Fallback to env var or Cloud Run backend
      configCache = {
        apiBase: process.env.REACT_APP_API_URL || DEFAULT_API_BASE,
      };
      return configCache;
    }
  })();
  
  return configPromise;
}

// Pre-initialize config immediately on module load
// This starts the fetch as soon as this module is imported
console.log('📦 [config.js] Module loaded, pre-initializing config');
initializeConfig();

export async function getRuntimeConfig() {
  // Always wait for initialization to complete
  console.log('📦 getRuntimeConfig() called');
  return await initializeConfig();
}

export async function getApiBase() {
  console.log('📦 getApiBase() called');
  const cfg = await getRuntimeConfig();
  
  if (!cfg || !cfg.apiBase) {
    console.warn('⚠️ API base not configured, using default:', DEFAULT_API_BASE);
    return DEFAULT_API_BASE;
  }
  
  console.log('✅ API base ready:', cfg.apiBase);
  return cfg.apiBase;
}




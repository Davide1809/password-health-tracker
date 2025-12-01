# First-Load Login Failure Troubleshooting Guide

## Issue
When accessing the app for the first time and attempting to sign in, users receive:
```
Login failed. Please check your credentials.
```

After refreshing the page, login works correctly.

## Root Cause (Fixed)
A race condition in the config initialization process:
1. The app didn't properly wait for the `config.json` to load
2. The login request would use an undefined API base URL
3. After refresh, config was cached, so login worked

## Fix Applied
- Changed config system to use promise caching
- Config promise is reused across all calls
- Ensures sequential, non-parallel initialization
- Prevents race conditions

## Verification Steps

### 1. Open Browser Developer Console (F12)
The app now includes detailed logging. Look for these messages in order:

```
✓ Config loaded from config.json: {apiBase: "https://..."}
App: Starting config initialization...
App: Config loaded successfully: {apiBase: "https://..."}
Login: Getting API base...
✓ Using API base: https://password-tracker-backend-681629792414.us-central1.run.app
Login: Sending login request to: https://password-tracker-backend-681629792414.us-central1.run.app/api/auth/login
Login: Success, received token
```

### 2. If Login Still Fails
Check the console for these error messages:

**Network Error:**
```
Network error. Please check your internet connection and try again.
```
→ Solution: Check your internet connection, ensure backend service is running

**Configuration Error:**
```
Configuration error. Please refresh the page and try again.
⚠ Failed to load config.json, using fallback: ...
```
→ Solution: This is expected if config.json can't be found; app uses fallback URL

**Backend Connection Error:**
```
{AxiosError} Error: connect ECONNREFUSED 127.0.0.1:5000
```
→ Solution: Ensure the backend is running on the configured URL

**Invalid Credentials:**
```
{status: 401, data: {error: "Invalid email or password"}}
```
→ Solution: Check email and password are correct, ensure user account exists

### 3. Test the Fix

**Local Development:**
```bash
# Terminal 1: Start backend
cd backend
python app.py

# Terminal 2: Start frontend
cd frontend
npm start

# Open http://localhost:3000
# Open DevTools (F12)
# Try logging in - check console logs in order
# Monitor Network tab to see config.json and /api/auth/login requests
```

**Cloud Deployment:**
```bash
# Check the application logs:
git push origin main  # Triggers GitHub Actions

# View logs:
# GitHub Actions: https://github.com/Davide1809/password-health-tracker/actions
# Cloud Run Backend: https://console.cloud.google.com/run
# Cloud Run Frontend: https://console.cloud.google.com/run
```

## Console Logging Map

| Log Message | Meaning |
|------------|---------|
| `✓ Config loaded from config.json` | Config.json was successfully fetched |
| `⚠ Failed to load config.json, using fallback` | Config.json not found, using default URL |
| `App: Starting config initialization` | App is waiting for config |
| `App: Config loaded successfully` | Config ready, app can render |
| `Login: Getting API base` | Login form submitted, retrieving API URL |
| `✓ Using API base: https://...` | API URL found, sending request |
| `Login: Success, received token` | Login successful! |

## If Still Having Issues

### Try these steps:

1. **Hard refresh the page:**
   - Mac: Cmd + Shift + R
   - Windows: Ctrl + Shift + R
   - Or clear browser cache for localhost/your domain

2. **Check Network Tab (DevTools):**
   - Look for `config.json` request - should return 200 status
   - Look for `/api/auth/login` request - check status and response
   - If 404, backend may not be running

3. **Test backend directly:**
   ```bash
   curl -X POST http://localhost:5000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"your@email.com","password":"yourpassword"}'
   ```

4. **Check environment variables:**
   - Frontend needs `/config.json` or `REACT_APP_API_URL` env var
   - Backend needs `MONGO_URI`, `JWT_SECRET_KEY`, `CREDENTIAL_ENCRYPTION_KEY`

5. **Restart services:**
   - Kill frontend: Ctrl+C in terminal
   - Kill backend: Ctrl+C in terminal
   - Start both fresh

## Related Files

- `/frontend/src/config.js` - Config loading logic
- `/frontend/src/App.js` - App initialization
- `/frontend/src/pages/Login.js` - Login form and submission
- `/public/config.json` - Runtime configuration file

## Recent Fixes (Dec 1, 2025)

1. **Promise caching** - Config promise is reused, preventing parallel fetches
2. **Better logging** - Console messages trace the entire flow
3. **Timeout protection** - Login requests have 10-second timeout
4. **Improved error handling** - Specific error messages for different failure modes

## Expected Behavior After Fix

✅ First login attempt should work without refreshing  
✅ Console should show all debug logs in order  
✅ Network tab should show single config.json request  
✅ Backend receives login request with correct API URL  

## Questions?

If login still fails:
1. Check browser console (F12 → Console tab)
2. Check Network tab to see which requests are failing
3. Verify backend is running and accessible
4. Try hard refresh (Cmd+Shift+R or Ctrl+Shift+R)
5. Check that config.json exists in `/public/config.json`

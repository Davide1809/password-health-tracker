import React, { useState, useEffect, useCallback } from 'react';
import { LogIn, UserPlus, XCircle, CheckCircle, Eye, EyeOff, Clipboard, PlusCircle, Trash2, Key, Zap } from 'lucide-react';

// === CRITICAL: LIVE CLOUD RUN SERVICE URL ===
const API_BASE_URL = 'https://password-backend-749522457256.us-central1.run.app'; 

// Object defining password security requirements and their regex patterns
const passwordRequirements = [
  { key: 'length', text: 'At least 8 characters', regex: /.{8,}/ },
  { key: 'uppercase', text: 'At least one uppercase letter (A-Z)', regex: /[A-Z]/ },
  { key: 'lowercase', text: 'At least one lowercase letter (a-z)', regex: /[a-z]/ },
  { key: 'number', text: 'At least one number (0-9)', regex: /[0-9]/ },
  { key: 'symbol', text: 'At least one symbol (!@#$%)', regex: /[!@#$%^&*]/ },
];

// Email validation function (UPDATED REGEX for standard email formats)
const isEmailValid = (email) => {
  // Relaxed regex to allow for standard TLDs like .com, .it, .co
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/; 
  return emailRegex.test(email);
};

// --- API Fetch Wrapper (CRITICAL: Adds Authorization Header) ---
const protectedFetch = async (url, options = {}) => {
    const token = localStorage.getItem('jwtToken');
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    // CRITICAL FIX: Only add Authorization header if token exists
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    // Exponential Backoff implementation (Max 3 retries)
    for (let i = 0; i < 3; i++) {
        try {
            const response = await fetch(url, { ...options, headers });
            return response;
        } catch (error) {
            if (i < 2) {
                // Wait 2^i * 100ms before retrying
                await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 100));
            } else {
                throw error; // Re-throw error on final attempt
            }
        }
    }
    // Should be unreachable, but here for robustness
    throw new Error("Failed to fetch after multiple retries.");
};


// --- Utility Components ---

// Component for displaying password requirements status
const PasswordRequirements = ({ password }) => {
  const validationState = passwordRequirements.map(req => ({
    ...req,
    isMet: req.regex.test(password),
  }));

  return (
    <div className="mt-4 p-4 bg-gray-900 rounded-xl text-xs space-y-1 shadow-inner">
      <h3 className="font-semibold text-sm text-yellow-300 mb-2">Security Requirements:</h3>
      {validationState.map(req => (
        <p key={req.key} className={`flex items-center transition-colors ${req.isMet ? 'text-green-400' : 'text-red-400'}`}>
          {req.isMet ? <CheckCircle size={14} className="mr-2" /> : <XCircle size={14} className="mr-2" />}
          {req.text}
        </p>
      ))}
    </div>
  );
};

// Helper for copying text to clipboard (using document.execCommand for cross-browser compatibility in iframes)
const copyToClipboard = (text) => {
    try {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed'; 
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        return true;
    } catch (err) {
        console.error('Failed to copy text: ', err);
        return false;
    }
};

// --- Custom UI Components ---

const Header = ({ userEmail, onLogout, isAuthenticated }) => (
    <header className="fixed top-0 left-0 right-0 bg-gray-900 border-b border-indigo-700/50 shadow-lg z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex justify-between items-center">
            <div className="flex items-center">
                <Zap className="h-7 w-7 text-yellow-400 mr-2" />
                <span className="text-xl font-bold text-white tracking-wider">VaultGuard</span>
            </div>
            {isAuthenticated && (
                <div className="flex items-center space-x-4">
                    <span className="text-sm text-gray-400 hidden sm:inline">{userEmail}</span>
                    <button
                        onClick={onLogout}
                        className="flex items-center py-2 px-4 rounded-full text-xs font-semibold text-white bg-red-600 hover:bg-red-700 transition duration-150 shadow-md"
                    >
                        <LogIn className="mr-1 h-4 w-4" />
                        Log Out
                    </button>
                </div>
            )}
        </div>
    </header>
);


// --- Form Components ---

// Main Signup Form Component (Story 1)
const SignupForm = ({ onAuthSuccess, onSwitchMode }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const [reqsMet, setReqsMet] = useState({});

  useEffect(() => {
    const newState = {};
    passwordRequirements.forEach(req => {
      newState[req.key] = req.regex.test(password);
    });
    setReqsMet(newState);
  }, [password]);

  const isValidEmail = isEmailValid(email);
  const isPasswordStrong = Object.values(reqsMet).every(Boolean);
  const isSubmitEnabled = isValidEmail && isPasswordStrong && !isLoading;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!isSubmitEnabled) {
      setError("Please meet all validation requirements.");
      return;
    }

    setIsLoading(true);

    try {
      const response = await protectedFetch(`${API_BASE_URL}/api/signup`, {
        method: 'POST',
        body: JSON.stringify({ email, password }),
        headers: {
            // Token not needed for signup
        }
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('jwtToken', data.token); // Store token on success
        onAuthSuccess(data.email, 'signup');
      } else {
        setError(data.message || 'Error during registration.');
      }
    } catch (err) {
      console.error('Network or fetch error:', err);
      setError('Connection error. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 p-8 md:p-12 rounded-3xl shadow-2xl w-full max-w-md border-t-8 border-indigo-500 transform transition-all hover:shadow-indigo-500/30">
      <h2 className="text-3xl font-extrabold text-white flex items-center mb-6">
        <UserPlus className="mr-3 text-indigo-400" size={30} />
        Create an Account
      </h2>
      
      {error && (
        <div className="p-3 mb-4 text-sm text-red-300 bg-red-800/50 rounded-lg border border-red-700" role="alert">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-300">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={`mt-1 block w-full px-4 py-3 border rounded-lg shadow-inner text-gray-900 bg-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 sm:text-sm 
              ${email === '' ? 'border-gray-500' : isValidEmail ? 'border-green-500' : 'border-red-500'}`}
            placeholder="user@example.com"
            disabled={isLoading}
          />
          {email !== '' && !isValidEmail && (
            <p className="mt-1 text-xs text-red-400">Please enter a valid email.</p>
          )}
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-300">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="new-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={`mt-1 block w-full px-4 py-3 border rounded-lg shadow-inner text-gray-900 bg-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 sm:text-sm 
              ${password === '' ? 'border-gray-500' : isPasswordStrong ? 'border-green-500' : 'border-red-500'}`}
            placeholder="Create a strong password"
            disabled={isLoading}
          />
          
          <PasswordRequirements password={password} />
        </div>

        <button
          type="submit"
          disabled={!isSubmitEnabled}
          className={`w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-lg text-base font-semibold text-white 
            ${isSubmitEnabled
              ? 'bg-indigo-600 hover:bg-indigo-700 transition duration-150 transform hover:scale-[1.01] focus:ring-4 focus:ring-indigo-500/50'
              : 'bg-indigo-400 cursor-not-allowed opacity-70'}`}
        >
          {isLoading ? 'Signing Up...' : 'Sign Up'}
        </button>
      </form>

      <div className="mt-8 text-center">
        <p className="text-sm text-gray-400">
          Already have an account?{' '}
          <button
            onClick={() => onSwitchMode('login')}
            className="font-semibold text-yellow-400 hover:text-yellow-300 transition duration-150"
            disabled={isLoading}
          >
            Log in here
          </button>
        </p>
      </div>
    </div>
  );
};

// Main Login Form Component
const LoginForm = ({ onAuthSuccess, onSwitchMode }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const response = await protectedFetch(`${API_BASE_URL}/api/login`, {
        method: 'POST',
        body: JSON.stringify({ email, password }),
        headers: {
            // Token not needed for login
        }
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('jwtToken', data.token); // Store token on success
        onAuthSuccess(data.email, 'login');
      } else {
        setError(data.message || 'Invalid credentials.');
      }
    } catch (err) {
      setError('Connection error. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 p-8 md:p-12 rounded-3xl shadow-2xl w-full max-w-md border-t-8 border-indigo-500 transform transition-all hover:shadow-indigo-500/30">
      <h2 className="text-3xl font-extrabold text-white flex items-center mb-6">
        <LogIn className="mr-3 text-indigo-400" size={30} />
        Access the Vault
      </h2>
      
      {error && (
        <div className="p-3 mb-4 text-sm text-red-300 bg-red-800/50 rounded-lg border border-red-700" role="alert">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-300">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 block w-full px-4 py-3 border border-gray-500 rounded-lg shadow-inner text-gray-900 bg-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 sm:text-sm"
            placeholder="user@example.com"
            disabled={isLoading}
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-300">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 block w-full px-4 py-3 border border-gray-500 rounded-lg shadow-inner text-gray-900 bg-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 sm:text-sm"
            placeholder="Enter your password"
            disabled={isLoading}
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-lg text-base font-semibold text-white bg-indigo-600 hover:bg-indigo-700 transition duration-150 transform hover:scale-[1.01] focus:ring-4 focus:ring-indigo-500/50"
        >
          {isLoading ? 'Logging In...' : 'Log In'}
        </button>
      </form>

      <div className="mt-8 text-center">
        <p className="text-sm text-gray-400">
          Don't have an account?{' '}
          <button
            onClick={() => onSwitchMode('signup')}
            className="font-semibold text-yellow-400 hover:text-yellow-300 transition duration-150"
            disabled={isLoading}
          >
            Sign up here
          </button>
        </p>
      </div>
    </div>
  );
};

// Password Analysis Component (Story 2)
const PasswordAnalyzer = ({ onBackToDashboard }) => {
    const [password, setPassword] = useState('');
    const [analysisResult, setAnalysisResult] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    // This runs the analysis whenever the password changes
    const analyzePassword = useCallback(async (pwd) => {
        if (pwd.length === 0) {
             setAnalysisResult(null);
             setError(null);
             return;
        }

        setIsLoading(true);
        setError(null);
        setAnalysisResult(null);

        try {
            const response = await protectedFetch(`${API_BASE_URL}/api/analyze`, {
                method: 'POST',
                body: JSON.stringify({ password: pwd }),
            });

            const data = await response.json();

            if (response.ok) {
                setAnalysisResult(data);
            } else {
                setError(data.message || 'Error during analysis.');
            }
        } catch (err) {
            setError('Connection error to the analysis service.');
        } finally {
            setIsLoading(false);
        }
    }, []);
    
    useEffect(() => {
        // Ensure API_BASE_URL is not empty before attempting analysis
        if (API_BASE_URL.startsWith('http')) {
            analyzePassword(password);
        } else if (password.length > 0) {
            setError('API Base URL is not configured. Cannot connect to backend.');
            setIsLoading(false);
        } else {
            setError(null);
        }
    }, [password, analyzePassword]);


    const scoreColors = ['text-red-500', 'text-orange-500', 'text-yellow-500', 'text-lime-500', 'text-green-500'];
    const scoreDescriptions = ['Too Weak', 'Weak', 'Acceptable', 'Good', 'Excellent'];
    // Simplified time descriptions for display
    const timeDescriptions = ['< 1 Second', 'Seconds', 'Hours', 'Days', 'Months', 'Years', 'Centuries', 'Millennia'];

    const getScoreDisplay = (score) => ({
        text: scoreDescriptions[score] || 'Unknown',
        color: scoreColors[score] || 'text-gray-400'
    });
    
    // Convert crack time estimate to a more user-friendly string
    const getCrackTimeDisplay = (timeText) => {
        if (!timeText) return 'N/A';
        // Mock mapping based on zxcvbn common outputs
        if (timeText.includes('instant')) return timeDescriptions[0];
        if (timeText.includes('second')) return timeDescriptions[1];
        if (timeText.includes('hour')) return timeDescriptions[2];
        if (timeText.includes('day')) return timeDescriptions[3];
        if (timeText.includes('month')) return timeDescriptions[4];
        if (timeText.includes('year')) return timeDescriptions[5];
        if (timeText.includes('centuries')) return timeDescriptions[6];
        return timeText;
    }


    return (
        <div className="bg-gray-800 p-8 md:p-12 rounded-3xl shadow-2xl w-full max-w-lg border-t-8 border-indigo-500">
            <h2 className="text-3xl font-extrabold text-white mb-6 flex items-center">
                <Zap className="mr-3 text-yellow-400" size={30} />
                Password Security Analysis
            </h2>
            
            <button 
                onClick={onBackToDashboard} 
                className="mb-6 text-sm font-medium text-indigo-400 hover:text-indigo-300 transition flex items-center"
            >
                &larr; Back to Dashboard
            </button>

            <div className="mb-6">
                <label htmlFor="password-analyze" className="block text-sm font-medium text-gray-300 mb-2">
                    Enter Password to Analyze
                </label>
                <input
                    id="password-analyze"
                    name="password-analyze"
                    type="text"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="mt-1 block w-full px-4 py-3 border border-gray-500 rounded-lg shadow-inner text-gray-900 bg-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 sm:text-sm"
                    placeholder="Type a password here..."
                    disabled={isLoading}
                />
            </div>
            
            {error && (
                <div className="p-3 mb-4 text-sm text-red-300 bg-red-800/50 rounded-lg border border-red-700" role="alert">
                    {error}
                </div>
            )}

            {isLoading && password.length > 0 && (
                 <div className="text-indigo-400">Analyzing...</div>
            )}
            
            {analysisResult && (
                <div className="mt-6 p-6 bg-gray-700 rounded-xl shadow-inner border border-gray-600">
                    <h3 className="text-xl font-semibold text-white mb-3">Analysis Results</h3>
                    
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-gray-600 pb-2 mb-2">
                        <span className="text-gray-400 font-medium">Security Score:</span>
                        <span className={`text-2xl font-bold ${getScoreDisplay(analysisResult.score).color} sm:mt-0 mt-1`}>
                            {getScoreDisplay(analysisResult.score).text}
                        </span>
                    </div>

                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-gray-600 pb-2 mb-2">
                        <span className="text-gray-400 font-medium">Estimated Crack Time:</span>
                        <span className="text-lg font-medium text-gray-300 sm:mt-0 mt-1">
                            {getCrackTimeDisplay(analysisResult.crack_time_display)}
                        </span>
                    </div>

                    {analysisResult.feedback && analysisResult.feedback.warning && (
                        <div className="mt-4 p-3 bg-red-900/50 text-red-300 rounded-lg">
                            <p className="font-semibold mb-1">Warning:</p>
                            <p className="text-sm">{analysisResult.feedback.warning}</p>
                        </div>
                    )}

                    {analysisResult.feedback && analysisResult.feedback.suggestions && analysisResult.feedback.suggestions.length > 0 && (
                        <div className="mt-4">
                            <p className="font-semibold text-gray-300 mb-2">Suggestions:</p>
                            <ul className="list-disc list-inside text-sm text-gray-400 space-y-1">
                                {analysisResult.feedback.suggestions.map((suggestion, index) => (
                                    <li key={index}>{suggestion}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}
            
            {!analysisResult && !isLoading && password.length > 0 && (
                 <div className="text-gray-400 mt-6">Type a password to see the security analysis.</div>
            )}
        </div>
    );
};

// Component for adding a new password entry (Part of Story 3)
const AddPasswordForm = ({ onPasswordAdded }) => {
    const [siteName, setSiteName] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    const isFormValid = siteName.trim() !== '' && username.trim() !== '' && password.trim() !== '';

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(false);

        if (!isFormValid) {
            setError("All fields are required.");
            return;
        }
        
        setIsLoading(true);

        try {
            const response = await protectedFetch(`${API_BASE_URL}/api/passwords`, {
                method: 'POST',
                body: JSON.stringify({ site_name: siteName, username, password }),
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess(true);
                // Reset form and call parent callback to refresh list
                setSiteName('');
                setUsername('');
                setPassword('');
                onPasswordAdded(); 
            } else {
                setError(data.message || 'Password saving failed.');
            }
        } catch (err) {
            setError('Connection error. Please try again later.');
        } finally {
            setIsLoading(false);
            // Hide success message after a few seconds
            setTimeout(() => setSuccess(false), 3000);
        }
    };

    return (
        <div className="bg-gray-700 p-6 rounded-xl shadow-xl border border-indigo-600/50 mb-8">
            <h3 className="text-2xl font-bold text-white mb-4 flex items-center">
                <PlusCircle className="mr-2 h-6 w-6 text-yellow-400" />
                Add New Secure Credential
            </h3>

            {success && (
                <div className="p-3 mb-4 text-sm text-green-300 bg-green-900/50 rounded-lg">
                    ✅ Password successfully saved!
                </div>
            )}
            {error && (
                <div className="p-3 mb-4 text-sm text-red-300 bg-red-800/50 rounded-lg">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label htmlFor="site-name" className="block text-sm font-medium text-gray-300">Site / Service Name</label>
                    <input
                        id="site-name"
                        type="text"
                        required
                        value={siteName}
                        onChange={(e) => setSiteName(e.target.value)}
                        className="mt-1 block w-full px-4 py-2 border border-gray-500 rounded-lg text-gray-900 bg-gray-200"
                        placeholder="E.g., Google, Amazon, Bank"
                        disabled={isLoading}
                    />
                </div>
                <div>
                    <label htmlFor="username" className="block text-sm font-medium text-gray-300">Username / Email</label>
                    <input
                        id="username"
                        type="text"
                        required
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="mt-1 block w-full px-4 py-2 border border-gray-500 rounded-lg text-gray-900 bg-gray-200"
                        placeholder="Your username or email"
                        disabled={isLoading}
                    />
                </div>
                <div>
                    <label htmlFor="password-to-save" className="block text-sm font-medium text-gray-300">Password</label>
                    <input
                        id="password-to-save"
                        type="password"
                        required
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="mt-1 block w-full px-4 py-2 border border-gray-500 rounded-lg text-gray-900 bg-gray-200"
                        placeholder="The password you want to save"
                        disabled={isLoading}
                    />
                </div>
                <button
                    type="submit"
                    disabled={isLoading || !isFormValid}
                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-xl shadow-md text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 transition duration-150 disabled:bg-indigo-400"
                >
                    {isLoading ? 'Saving...' : 'Save Password Securely'}
                </button>
            </form>
        </div>
    );
};

// Component for a single password item
const PasswordItem = ({ entry }) => {
    const [showPassword, setShowPassword] = useState(false);
    const [copyStatus, setCopyStatus] = useState(null);

    const handleCopy = (text) => {
        if (copyToClipboard(text)) {
            setCopyStatus('Copied!');
            setTimeout(() => setCopyStatus(null), 1500);
        } else {
            setCopyStatus('Copy failed.');
            setTimeout(() => setCopyStatus(null), 1500);
        }
    };

    // Helper to format creation date
    const formatDate = (isoString) => {
        const date = new Date(isoString);
        return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    };

    return (
        <div className="bg-gray-800 p-4 rounded-xl shadow-md border-l-4 border-yellow-500 hover:bg-gray-700 transition duration-100 ease-in-out">
            <div className="flex justify-between items-start mb-2">
                <h4 className="text-xl font-semibold text-indigo-300">{entry.site_name}</h4>
                <div className="text-sm text-gray-400 flex items-center">
                    <Key className="inline h-4 w-4 mr-1 text-yellow-500"/> Saved on: {formatDate(entry.created_at)}
                </div>
            </div>

            <p className="text-gray-300 mb-2">
                <span className="font-medium text-gray-400">Username: </span>
                {entry.username}
                <button
                    onClick={() => handleCopy(entry.username)}
                    className="ml-2 p-1 text-gray-400 hover:text-yellow-400 transition"
                    title="Copy Username"
                >
                    <Clipboard size={14} />
                </button>
            </p>

            <div className="flex items-center justify-between mt-3 bg-gray-900 p-3 rounded-lg border border-gray-700">
                <span className="font-medium text-gray-400 mr-4">Password:</span>
                <div className="flex-grow font-mono text-white truncate mr-4">
                    {showPassword ? entry.password : '••••••••••••••••'}
                </div>
                <div className="flex space-x-2">
                    {/* Copy Button */}
                    <button
                        onClick={() => handleCopy(entry.password)}
                        className={`p-1 rounded-full transition ${copyStatus === 'Copied!' ? 'bg-green-600 text-white' : 'bg-indigo-600 text-white hover:bg-indigo-700'}`}
                        title={copyStatus || "Copy Password"}
                        disabled={copyStatus === 'Copied!'}
                    >
                        {copyStatus === 'Copied!' ? <CheckCircle size={18} /> : <Clipboard size={18} />}
                    </button>
                    {/* Show/Hide Button */}
                    <button
                        onClick={() => setShowPassword(!showPassword)}
                        className="p-1 bg-gray-600 text-white rounded-full hover:bg-gray-500 transition"
                        title={showPassword ? "Hide Password" : "Show Password"}
                    >
                        {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                </div>
            </div>
        </div>
    );
};

// Component for listing all stored passwords (Part of Story 3)
const PasswordList = ({ onRefresh, passwords, isLoading, error }) => {
    return (
        <div className="mt-10">
            <div className="flex justify-between items-center mb-4 pb-2 border-b border-gray-700">
                <h3 className="text-2xl font-bold text-white flex items-center">
                    <Key className="mr-3 h-6 w-6 text-yellow-400" />
                    Your Saved Credentials ({passwords.length})
                </h3>
                <button
                    onClick={onRefresh}
                    disabled={isLoading}
                    className="flex items-center py-2 px-4 text-sm font-medium text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 transition shadow-md disabled:bg-indigo-400"
                >
                    {isLoading ? 'Loading...' : 'Refresh List'}
                </button>
            </div>

            {error && (
                <div className="p-4 mb-4 text-sm text-red-300 bg-red-800/50 rounded-lg border border-red-700">
                    Error loading passwords: {error}
                </div>
            )}

            {passwords.length === 0 && !isLoading && (
                <div className="p-8 text-center text-gray-400 border border-dashed border-gray-600 rounded-xl mt-4">
                    You haven't saved any passwords yet. Use the form above to add your first secure credential!
                </div>
            )}

            <div className="space-y-4">
                {passwords.map(p => (
                    <PasswordItem key={p.id} entry={p} />
                ))}
            </div>
        </div>
    );
};


// Dashboard Component
const Dashboard = ({ userEmail, onAnalyzeClick }) => {
  const [dashboardMessage, setDashboardMessage] = useState(null);
  const [isLoadingStatus, setIsLoadingStatus] = useState(true);
  
  // State for Story 3: Password Management
  const [passwords, setPasswords] = useState([]);
  const [isLoadingPasswords, setIsLoadingPasswords] = useState(false);
  const [passwordError, setPasswordError] = useState(null);

  // Function to fetch the protected message
  const fetchDashboardStatus = async () => {
    try {
      // Use protectedFetch to send JWT token
      const response = await protectedFetch(`${API_BASE_URL}/api/dashboard`, { method: 'GET' });
      const data = await response.json();

      if (response.ok) {
        setDashboardMessage(data.message);
      } else {
        setDashboardMessage(data.message || 'Error retrieving data (Unauthorized).');
      }
    } catch (error) {
      setDashboardMessage('Backend Connection Error. Check API_BASE_URL configuration.');
    } finally {
      setIsLoadingStatus(false);
    }
  };
  
  // Function to fetch the list of passwords
  const fetchPasswords = useCallback(async () => {
      if (!API_BASE_URL.startsWith('http')) {
        setPasswordError('API Base URL is not configured. Cannot connect to backend.');
        setPasswords([]);
        return;
      }
      
      setIsLoadingPasswords(true);
      setPasswordError(null);
      try {
          // Use protectedFetch to send JWT token
          const response = await protectedFetch(`${API_BASE_URL}/api/passwords`, { method: 'GET' });
          const data = await response.json();

          if (response.ok) {
              setPasswords(data);
          } else {
              setPasswordError(data.message || 'Password retrieval failed (Unauthorized).');
          }
      } catch (error) {
          setPasswordError('Connection error while fetching passwords.');
      } finally {
          setIsLoadingPasswords(false);
      }
  }, []);

  // Run initial data fetch
  useEffect(() => {
    fetchDashboardStatus();
    fetchPasswords();
  }, [fetchPasswords]);
  
  const handlePasswordAdded = () => {
      // Refresh the list immediately after a successful add
      fetchPasswords();
  }

  return (
    <div className="bg-gray-900 p-8 md:p-12 rounded-2xl shadow-2xl w-full max-w-4xl mt-16 border border-indigo-700/50">
      <h1 className="text-4xl font-extrabold text-white mb-2">
        Main Dashboard
      </h1>
      <p className="text-xl text-indigo-400 mb-6 border-b border-gray-700 pb-4">
        <span className="font-semibold">Welcome, {userEmail}!</span>
      </p>

      {/* Auth Status Section */}
      <div className="bg-gray-800 p-4 rounded-lg mb-8 border border-gray-700 shadow-inner">
        <h3 className="text-lg font-semibold text-gray-300 mb-2">Authentication Status (Backend)</h3>
        {isLoadingStatus ? (
          <p className="text-gray-400">Loading protected message...</p>
        ) : (
          <p className={`${dashboardMessage && dashboardMessage.includes('Unauthorized') || dashboardMessage.includes('Error') ? 'text-red-400' : 'text-green-300'}`}>
            {dashboardMessage}
          </p>
        )}
      </div>

      {/* Add Password Form */}
      <AddPasswordForm onPasswordAdded={handlePasswordAdded} />

      {/* Password List */}
      <PasswordList 
        passwords={passwords} 
        onRefresh={fetchPasswords} 
        isLoading={isLoadingPasswords} 
        error={passwordError}
      />
      
      {/* Global Actions Section */}
      <div className="flex justify-center mt-10 pt-4 border-t border-gray-700">
        <button
          onClick={onAnalyzeClick}
          className="flex items-center justify-center py-3 px-8 rounded-xl text-base font-semibold text-white bg-blue-600 hover:bg-blue-700 transition duration-150 shadow-lg transform hover:scale-[1.01]"
        >
          <Zap className="mr-2 h-5 w-5" />
          Analyze New Password
        </button>
      </div>
    </div>
  );
};


// Application Root Component
export default function App() {
  // Mode: 'login', 'signup', 'dashboard', 'analyze'
  const [mode, setMode] = useState('login'); 
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userEmail, setUserEmail] = useState(''); 
  const [lastAction, setLastAction] = useState(null); 

  // Effect to check local storage for existing token on load
  useEffect(() => {
    const storedToken = localStorage.getItem('jwtToken');
    const storedEmail = localStorage.getItem('userEmail');
    
    if (storedToken && storedEmail) {
      // If a token exists, assume the user is still authenticated 
      // (a quick check is made when loading the dashboard)
      setUserEmail(storedEmail);
      setIsAuthenticated(true);
      setMode('dashboard');
    } else {
      setMode('login');
    }
  }, []);

  const handleAuthSuccess = (email, action) => {
    localStorage.setItem('userEmail', email); // Store email alongside token
    setUserEmail(email);
    setIsAuthenticated(true);
    setLastAction(action);
    setMode('dashboard'); 
  };

  const handleLogout = async () => {
    try {
      // Clear token from local storage immediately
      localStorage.removeItem('jwtToken');
      localStorage.removeItem('userEmail');
      
      // Attempt to log out on the backend (using the now-cleared token, which is okay)
      await protectedFetch(`${API_BASE_URL}/api/logout`, { method: 'POST' });
    } catch (error) {
      console.error('Error during backend logout:', error);
    }
    // Force frontend logout regardless of backend success/failure
    setUserEmail('');
    setIsAuthenticated(false);
    setMode('login'); 
    setLastAction(null);
  };
  
  const handleAnalyzeClick = () => {
    setMode('analyze');
  };

  const handleBackToDashboard = () => {
      setMode('dashboard');
  };

  const renderContent = () => {
    if (!isAuthenticated) {
      if (mode === 'signup') {
        return <SignupForm onAuthSuccess={handleAuthSuccess} onSwitchMode={setMode} />;
      }
      return <LoginForm onAuthSuccess={handleAuthSuccess} onSwitchMode={setMode} />;
    }
    
    // Authenticated content
    switch (mode) {
        case 'analyze':
            return (
                <PasswordAnalyzer 
                    onBackToDashboard={handleBackToDashboard}
                />
            );
        case 'dashboard':
        default:
            return (
                <Dashboard 
                    userEmail={userEmail} 
                    lastAction={lastAction}
                    onAnalyzeClick={handleAnalyzeClick}
                />
            );
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col items-center pt-20 pb-10 font-sans">
      <Header 
        userEmail={userEmail} 
        onLogout={handleLogout} 
        isAuthenticated={isAuthenticated} 
      />
      <div className="flex-grow flex items-center justify-center w-full max-w-7xl px-4 sm:px-6 lg:px-8">
        {renderContent()}
      </div>
    </div>
  );
}
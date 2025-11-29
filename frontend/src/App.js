import React, { useState, useEffect, useCallback } from 'react';
import { LogIn, UserPlus, XCircle, CheckCircle, Eye, EyeOff, Clipboard, PlusCircle, Trash2, Key, Zap } from 'lucide-react';

// === CRITICAL: LIVE CLOUD RUN SERVICE URL ===
const API_BASE_URL = 'https://password-backend-749522457256.us-central1.run.app'; 

// --- SESSION CONFIGURATION ---\n
const INACTIVITY_TIMEOUT_MS = 60 * 60 * 1000; // 60 minutes of inactivity
// The /api/logout endpoint will be hit by the browser's 'unload' event.

// Object defining password security requirements and their regex patterns
const passwordRequirements = [
  { key: 'length', text: 'At least 8 characters', regex: /.{8,}/ },
  { key: 'uppercase', text: 'At least one uppercase letter (A-Z)', regex: /[A-Z]/ },
  { key: 'lowercase', text: 'At least one lowercase letter (a-z)', regex: /[a-z]/ },
  { key: 'number', text: 'At least one number (0-9)', regex: /[0-9]/ },
  { key: 'symbol', text: 'At least one symbol (!@#$%)', regex: /[!@#$%^&*]/ },
];

// Email validation function
const isEmailValid = (email) => {
  const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]{2,}$/; 
  return emailRegex.test(email);
};

// --- API Fetch Utility ---
const apiFetch = async (endpoint, options = {}) => {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
  let data = {};
  try {
    data = await response.json();
  } catch (e) {
    // If the response is not JSON (e.g., empty 204 or text), handle gracefully
    data = { message: response.statusText || 'Operation successful' };
  }
  
  if (!response.ok) {
    throw new Error(data.message || `API Error: ${response.status}`);
  }
  return data;
};

// --- COMPONENTS ---

const Message = ({ message, type }) => {
  if (!message) return null;
  const classes = type === 'error' 
    ? "bg-red-900 text-red-300" 
    : "bg-green-900 text-green-300";
  const Icon = type === 'error' ? XCircle : CheckCircle;

  return (
    <div className={`mt-4 p-3 rounded-lg flex items-center shadow-lg ${classes}`}>
      <Icon size={18} className="mr-2 flex-shrink-0" />
      <span className="text-sm">{message}</span>
    </div>
  );
};

// --- Form Components ---

const AuthFormWrapper = ({ title, children, onSwitchMode, linkText, linkTarget }) => (
  <div className="p-8 max-w-lg w-full bg-gray-800 rounded-xl shadow-2xl">
    <h2 className="text-3xl font-bold text-center text-white mb-6">{title}</h2>
    {children}
    <div className="mt-6 text-center text-sm text-gray-400">
      {linkText}{' '}
      <button 
        onClick={() => onSwitchMode(linkTarget)} 
        className="text-indigo-400 hover:text-indigo-300 font-medium transition duration-150"
      >
        {linkTarget === 'login' ? 'Login' : 'Sign Up'}
      </button>
    </div>
  </div>
);


const LoginForm = ({ onAuthSuccess, onSwitchMode }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setMessage('');
    setLoading(true);

    if (!isEmailValid(email)) {
      setMessage("Please enter a valid email address.");
      setMessageType('error');
      setLoading(false);
      return;
    }

    try {
      const data = await apiFetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      setMessage('Login successful! Redirecting...');
      setMessageType('success');
      setTimeout(() => onAuthSuccess(data.email, data.user_name), 1000);
    } catch (error) {
      setMessage(error.message);
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthFormWrapper 
      title="Login" 
      onSwitchMode={onSwitchMode} 
      linkText="Don't have an account?" 
      linkTarget="signup"
    >
      <form onSubmit={handleLogin} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300">Email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} 
            className="mt-1 block w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg shadow-sm text-white focus:ring-indigo-500 focus:border-indigo-500" required />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300">Password</label>
          <div className="relative">
            <input type={showPassword ? "text" : "password"} value={password} onChange={e => setPassword(e.target.value)} 
              className="mt-1 block w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg shadow-sm text-white focus:ring-indigo-500 focus:border-indigo-500" required />
            <button type="button" onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-indigo-400">
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
        </div>
        <button type="submit" disabled={loading}
          className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-lg text-lg font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 transition duration-200">
          {loading ? 'Logging in...' : 'Log In'}
        </button>
      </form>
      <Message message={message} type={messageType} />
    </AuthFormWrapper>
  );
};


const SignupForm = ({ onAuthSuccess, onSwitchMode }) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const passwordChecks = passwordRequirements.map(req => ({
    ...req,
    passed: req.regex.test(password),
  }));
  const isPasswordValid = passwordChecks.every(check => check.passed);

  const handleSignup = async (e) => {
    e.preventDefault();
    setMessage('');
    setLoading(true);

    if (!name.trim()) {
      setMessage("Name field cannot be empty.");
      setMessageType('error');
      setLoading(false);
      return;
    }
    if (!isEmailValid(email)) {
      setMessage("Please enter a valid email address.");
      setMessageType('error');
      setLoading(false);
      return;
    }
    if (!isPasswordValid) {
      setMessage("Password does not meet all security requirements.");
      setMessageType('error');
      setLoading(false);
      return;
    }

    try {
      const data = await apiFetch('/api/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          email: email, 
          password: password, 
          // --- FIX APPLIED HERE ---
          // The backend expects 'user_name', not 'name'
          user_name: name // CORRECTED KEY
          // --- END FIX ---
        }),
      });
      setMessage('Account created successfully! Redirecting...');
      setMessageType('success');
      setTimeout(() => onAuthSuccess(data.email, data.user_name), 1000);
    } catch (error) {
      setMessage(error.message);
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthFormWrapper 
      title="Sign Up" 
      onSwitchMode={onSwitchMode} 
      linkText="Already have an account?" 
      linkTarget="login"
    >
      <form onSubmit={handleSignup} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300">Full Name</label>
          <input type="text" value={name} onChange={e => setName(e.target.value)} 
            className="mt-1 block w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg shadow-sm text-white focus:ring-indigo-500 focus:border-indigo-500" required />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300">Email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} 
            className="mt-1 block w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg shadow-sm text-white focus:ring-indigo-500 focus:border-indigo-500" required />
          {!isEmailValid(email) && email.length > 0 && (
            <p className="text-red-400 text-xs mt-1">Please enter a valid email format.</p>
          )}
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300">Password</label>
          <div className="relative">
            <input type={showPassword ? "text" : "password"} value={password} onChange={e => setPassword(e.target.value)} 
              className="mt-1 block w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg shadow-sm text-white focus:ring-indigo-500 focus:border-indigo-500" required />
            <button type="button" onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-indigo-400">
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
          <div className="mt-2 text-xs space-y-1">
            {passwordChecks.map(req => (
              <div key={req.key} className={`flex items-center ${req.passed ? 'text-green-400' : 'text-red-400'}`}>
                <CheckCircle size={12} className={`mr-2 ${req.passed ? 'text-green-500' : 'hidden'}`} />
                <XCircle size={12} className={`mr-2 ${!req.passed ? 'text-red-500' : 'hidden'}`} />
                {req.text}
              </div>
            ))}
          </div>
        </div>
        <button type="submit" disabled={loading || !isPasswordValid || !isEmailValid(email) || !name.trim()}
          className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-lg text-lg font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 transition duration-200">
          {loading ? 'Signing Up...' : 'Sign Up'}
        </button>
      </form>
      <Message message={message} type={messageType} />
    </AuthFormWrapper>
  );
};

// --- Password Analyzer Component ---

const PasswordAnalyzer = ({ onBackToDashboard }) => {
  const [password, setPassword] = useState('');
  const [score, setScore] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const analyzePassword = useCallback(() => {
    setIsAnalyzing(true);
    // zxcvbn is complex and generally assumed to be available in the environment
    // or loaded via a script tag in a single-file React context.
    // For this demonstration, we'll simulate the analysis result structure.
    
    // NOTE: In a real-world scenario, you would need to ensure zxcvbn is available 
    // in the React environment, likely by importing it if using Node/Webpack, 
    // or by checking for a global `zxcvbn` function if loaded via CDN script.

    // Simulated zxcvbn result structure for safety:
    const mockResult = {
        score: Math.min(4, Math.floor(password.length / 4)), // Score 0 to 4 based on length
        suggestions: password.length < 8 ? ['Increase the length of your password.'] : [],
        // ... more complex analysis usually here ...
    };

    // Replace with actual zxcvbn(password) if available
    const zxcvbnResult = window.zxcvbn ? window.zxcvbn(password) : mockResult;

    setScore(zxcvbnResult.score);
    setSuggestions(zxcvbnResult.feedback ? zxcvbnResult.feedback.suggestions : mockResult.suggestions);
    setIsAnalyzing(false);
  }, [password]);

  useEffect(() => {
    if (password.length > 0) {
      // Debounce analysis slightly
      const timer = setTimeout(analyzePassword, 300); 
      return () => clearTimeout(timer);
    } else {
      setScore(null);
      setSuggestions([]);
    }
  }, [password, analyzePassword]);
  
  const scoreText = ['Terrible', 'Weak', 'Fair', 'Good', 'Excellent'][score] || 'Not Rated';
  const scoreColor = ['bg-red-600', 'bg-orange-500', 'bg-yellow-500', 'bg-lime-500', 'bg-green-600'][score] || 'bg-gray-600';

  return (
    <div className="p-8 max-w-2xl w-full bg-gray-800 rounded-xl shadow-2xl">
      <h2 className="text-3xl font-bold text-white mb-6 flex items-center">
        <Zap size={28} className="mr-2 text-yellow-400" /> Password Analyzer
      </h2>
      
      <div className="space-y-4">
        <label className="block text-sm font-medium text-gray-300">Enter Password to Analyze</label>
        <input 
          type="password" 
          value={password} 
          onChange={e => setPassword(e.target.value)} 
          placeholder="Type your password here..."
          className="mt-1 block w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg shadow-sm text-white focus:ring-indigo-500 focus:border-indigo-500"
        />
      </div>

      {password.length > 0 && !isAnalyzing && score !== null && (
        <div className="mt-6 p-4 border border-gray-700 rounded-lg bg-gray-900">
          <div className="flex justify-between items-center mb-4">
            <span className="text-lg font-semibold text-white">Security Score:</span>
            <span className={`text-xl font-bold text-white px-3 py-1 rounded-full ${scoreColor} shadow-md transition-colors duration-300`}>
              {scoreText} ({score}/4)
            </span>
          </div>

          {suggestions.length > 0 && (
            <div>
              <p className="text-sm font-medium text-gray-400 mb-2">Suggestions to Improve:</p>
              <ul className="list-disc list-inside text-sm text-gray-300 space-y-1 ml-4">
                {suggestions.map((s, index) => (
                  <li key={index}>{s}</li>
                ))}
              </ul>
            </div>
          )}
           {suggestions.length === 0 && score === 4 && (
            <p className="text-green-400 font-medium text-sm">This password is highly secure! Good job.</p>
           )}
        </div>
      )}

      <button onClick={onBackToDashboard}
        className="mt-8 flex items-center justify-center py-2 px-4 border border-indigo-500 rounded-lg shadow-md text-sm font-medium text-indigo-400 hover:bg-indigo-900 transition duration-200">
        Back to Dashboard
      </button>
    </div>
  );
};


// --- Dashboard Components ---

const PasswordEntry = ({ entry, onDelete }) => {
  const [showPassword, setShowPassword] = useState(false);
  const [message, setMessage] = useState('');

  const handleCopyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      setMessage('Copied!');
      setTimeout(() => setMessage(''), 2000);
    }).catch(err => {
      setMessage('Failed to copy.');
      console.error('Could not copy text: ', err);
    });
  };

  return (
    <div className="bg-gray-700 p-4 rounded-lg shadow-lg flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-3 sm:space-y-0">
      <div className="flex-1 min-w-0">
        <p className="text-lg font-semibold text-indigo-300 truncate">{entry.service}</p>
        <p className="text-sm text-gray-300 truncate">User: {entry.username}</p>
      </div>
      
      <div className="flex items-center space-x-2">
        <button onClick={() => setShowPassword(!showPassword)}
          className="p-2 rounded-full text-gray-400 hover:text-white hover:bg-gray-600 transition duration-150"
          title={showPassword ? "Hide Password" : "Show Password"}>
          {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
        
        <div className="relative min-w-[120px] max-w-[200px] bg-gray-600 rounded-lg px-3 py-1 text-sm text-white truncate">
          {showPassword ? entry.password : '••••••••••••'}
          {message && (
            <span className="absolute top-0 right-0 transform -translate-y-full px-2 py-1 bg-green-600 text-white rounded-md text-xs shadow-xl z-10">
              {message}
            </span>
          )}
        </div>

        <button onClick={() => handleCopyToClipboard(entry.password)}
          className="p-2 rounded-full text-gray-400 hover:text-indigo-400 hover:bg-gray-600 transition duration-150"
          title="Copy Password">
          <Clipboard size={18} />
        </button>

        <button onClick={() => onDelete(entry._id)}
          className="p-2 rounded-full text-gray-400 hover:text-red-400 hover:bg-gray-600 transition duration-150"
          title="Delete Password">
          <Trash2 size={18} />
        </button>
      </div>
    </div>
  );
};


const AddPasswordModal = ({ onClose, onSave }) => {
  const [service, setService] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    
    if (!service.trim() || !username.trim() || !password.trim()) {
        setMessage('All fields must be filled.');
        setLoading(false);
        return;
    }
    
    try {
        await onSave({ service, username, password });
        onClose();
    } catch (error) {
        setMessage(error.message);
    } finally {
        setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 p-6 rounded-xl shadow-2xl max-w-md w-full">
        <h3 className="text-xl font-bold text-white mb-4">Add New Password</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300">Service/Website</label>
            <input type="text" value={service} onChange={e => setService(e.target.value)} 
              className="mt-1 block w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg shadow-sm text-white" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300">Username/Email</label>
            <input type="text" value={username} onChange={e => setUsername(e.target.value)} 
              className="mt-1 block w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg shadow-sm text-white" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300">Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} 
              className="mt-1 block w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg shadow-sm text-white" required />
          </div>
          <Message message={message} type="error" />
          <div className="flex justify-end space-x-3 pt-2">
            <button type="button" onClick={onClose}
              className="py-2 px-4 border border-gray-600 rounded-lg text-sm font-medium text-gray-300 hover:bg-gray-700 transition duration-150">
              Cancel
            </button>
            <button type="submit" disabled={loading}
              className="py-2 px-4 rounded-lg text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 transition duration-150">
              {loading ? 'Saving...' : 'Save Password'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};


const Dashboard = ({ userEmail, userName, onAnalyzeClick }) => {
  const [passwords, setPasswords] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchPasswords = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await apiFetch('/api/passwords', { method: 'GET' });
      setPasswords(data);
    } catch (e) {
      setError(`Failed to fetch passwords: ${e.message}`);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPasswords();
  }, [fetchPasswords]);

  const handleSavePassword = async (entry) => {
    try {
      await apiFetch('/api/passwords', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(entry),
      });
      fetchPasswords(); // Refresh list
    } catch (e) {
      throw new Error(`Failed to save: ${e.message}`);
    }
  };

  const handleDeletePassword = async (id) => {
    if (window.confirm("Are you sure you want to delete this password?")) {
      try {
        await apiFetch(`/api/passwords/${id}`, { method: 'DELETE' });
        fetchPasswords(); // Refresh list
      } catch (e) {
        setError(`Failed to delete: ${e.message}`);
      }
    }
  };

  return (
    <div className="p-4 sm:p-8 max-w-4xl w-full">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-white">Welcome, {userName || userEmail}!</h2>
        <div className='flex space-x-3'>
          <button onClick={onAnalyzeClick}
            className="flex items-center px-4 py-2 border border-yellow-500 rounded-lg text-sm font-medium text-yellow-400 hover:bg-gray-700 transition duration-150 shadow-md">
            <Zap size={18} className="mr-2" /> Analyze
          </button>
          <button onClick={() => setIsModalOpen(true)}
            className="flex items-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 transition duration-150 shadow-lg">
            <PlusCircle size={18} className="mr-2" /> Add New
          </button>
        </div>
      </div>

      <Message message={error} type="error" />

      <div className="bg-gray-900 p-4 rounded-xl shadow-inner min-h-[200px]">
        <h3 className="text-xl font-semibold text-gray-300 mb-4 border-b border-gray-700 pb-2">Your Saved Passwords ({passwords.length})</h3>
        
        {loading && <p className="text-gray-400 text-center py-8">Loading passwords...</p>}
        
        {!loading && passwords.length === 0 && (
          <p className="text-gray-400 text-center py-8">You have no saved passwords. Click "Add New" to get started.</p>
        )}

        {!loading && passwords.length > 0 && (
          <div className="space-y-4">
            {passwords.map(entry => (
              <PasswordEntry key={entry._id} entry={entry} onDelete={handleDeletePassword} />
            ))}
          </div>
        )}
      </div>

      {isModalOpen && (
        <AddPasswordModal 
          onClose={() => setIsModalOpen(false)} 
          onSave={handleSavePassword}
        />
      )}
    </div>
  );
};

// --- Header Component ---

const Header = ({ userEmail, onLogout, isAuthenticated }) => (
  <header className="bg-gray-800 shadow-lg fixed top-0 w-full z-10">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex justify-between items-center">
      <div className="text-xl font-bold text-white flex items-center">
        <Key size={24} className="text-indigo-400 mr-2" />
        Health Tracker
      </div>
      {isAuthenticated ? (
        <div className="flex items-center space-x-4">
          <span className="text-sm text-gray-300 hidden sm:block truncate max-w-[150px]">{userEmail}</span>
          <button onClick={onLogout}
            className="flex items-center px-3 py-1 border border-red-500 rounded-lg text-sm font-medium text-red-400 hover:bg-gray-700 transition duration-150">
            <LogIn size={16} className="mr-1" /> Logout
          </button>
        </div>
      ) : (
        <span className="text-sm text-gray-400">Secure Authentication</span>
      )}
    </div>
  </header>
);

// --- Main App Component ---

const App = () => {
  const [mode, setMode] = useState('login'); // 'login', 'signup', 'dashboard', 'analyze'
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userEmail, setUserEmail] = useState('');
  const [userName, setUserName] = useState('');
  const [inactivityTimer, setInactivityTimer] = useState(null);

  // Function to set up the inactivity timer
  const startInactivityTimer = useCallback(() => {
    // Clear any existing timer
    if (inactivityTimer) {
      clearTimeout(inactivityTimer);
    }
    // Set a new timer
    const timer = setTimeout(() => {
      alert("You have been logged out due to inactivity.");
      handleLogout();
    }, INACTIVITY_TIMEOUT_MS);
    setInactivityTimer(timer);
  }, [inactivityTimer]);

  // Function to reset the timer on user activity
  const resetInactivityTimer = useCallback(() => {
    if (isAuthenticated) {
      startInactivityTimer();
    }
  }, [isAuthenticated, startInactivityTimer]);

  // Initial load and setup of event listeners for activity tracking
  useEffect(() => {
    const handleActivity = () => resetInactivityTimer();

    // Attach listeners for user activity
    window.addEventListener('mousemove', handleActivity);
    window.addEventListener('keypress', handleActivity);
    window.addEventListener('scroll', handleActivity);
    window.addEventListener('touchstart', handleActivity);

    // Initial check for session (on page load)
    const checkSession = async () => {
      try {
        const data = await apiFetch('/api/session_status', { method: 'GET' });
        if (data.is_authenticated) {
          handleAuthSuccess(data.email, data.user_name);
        }
      } catch (e) {
        // Assume session check failure means not logged in
        console.log('No active session found.');
      }
    };

    checkSession();

    // Cleanup: remove listeners when component unmounts
    return () => {
      window.removeEventListener('mousemove', handleActivity);
      window.removeEventListener('keypress', handleActivity);
      window.removeEventListener('scroll', handleActivity);
      window.removeEventListener('touchstart', handleActivity);
      if (inactivityTimer) {
        clearTimeout(inactivityTimer);
      }
    };
  }, [resetInactivityTimer, inactivityTimer]);


  // Handle successful login or signup
  const handleAuthSuccess = (email, name) => {
    setIsAuthenticated(true);
    setUserEmail(email);
    setUserName(name);
    setMode('dashboard');
    startInactivityTimer(); // Start timer on successful login
  };

  // Handle logout
  const handleLogout = useCallback(async () => {
    try {
      // Clear session on the backend
      await apiFetch('/api/logout', { method: 'POST' });
    } catch (e) {
      console.error("Logout failed on server, but client session will be cleared.", e);
    } finally {
      // Clear client state
      setIsAuthenticated(false);
      setUserEmail('');
      setUserName('');
      setMode('login');
      if (inactivityTimer) {
        clearTimeout(inactivityTimer);
        setInactivityTimer(null);
      }
    }
  }, [inactivityTimer]);

  // Use effect to handle the cleanup logout event when the user navigates away or closes the tab.
  useEffect(() => {
    const handleUnload = () => {
      // Send a synchronous request or use navigator.sendBeacon
      // For simplicity in a single-file environment, we rely on the backend session timeout.
      // In a multi-file setup, a proper sendBeacon call would be used here.
      console.log("Attempting to signal logout on unload (relying on session timeout).");
    };

    window.addEventListener('unload', handleUnload);

    return () => {
      window.removeEventListener('unload', handleUnload);
    };
  }, [handleLogout]);
  

  // Rendering based on mode
  return (
    <div className="min-h-screen bg-gray-950 flex flex-col font-sans">
      <Header 
        userEmail={userEmail} 
        onLogout={handleLogout} 
        isAuthenticated={isAuthenticated} 
      />
      
      <main className={`flex-grow flex items-center justify-center ${mode !== 'dashboard' ? 'pt-24 pb-10' : 'pt-20'}`}>
        
        {mode === 'login' && <LoginForm onAuthSuccess={handleAuthSuccess} onSwitchMode={setMode} />}
        {mode === 'signup' && <SignupForm onAuthSuccess={handleAuthSuccess} onSwitchMode={setMode} />}
        
        {mode === 'dashboard' && isAuthenticated && (
          <Dashboard 
            userEmail={userEmail} 
            userName={userName} // Pass userName to Dashboard
            onAnalyzeClick={() => setMode('analyze')}
          />
        )}
        
        {mode === 'analyze' && isAuthenticated && (
            <PasswordAnalyzer onBackToDashboard={() => setMode('dashboard')} />
        )}

        {/* Fallback/Loading Screen */}
        {mode === 'dashboard' && !isAuthenticated && (
          <div className="text-white text-xl p-8 max-w-lg w-full bg-gray-800 rounded-xl shadow-2xl text-center">
              Redirecting to login...
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
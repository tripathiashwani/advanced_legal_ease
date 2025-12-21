import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Signup from './pages/Signup.jsx';
import CommonLanding from './pages/common/landing.js';

// You can add more pages here later
const Home = () => (
  <div className="h-screen flex items-center justify-center bg-gray-100">
    <div className="text-center">
      <h1 className="text-4xl font-bold text-blue-600 mb-4">
        🚀 Welcome to LegalEase
      </h1>
      <p className="text-gray-600 mb-6">Streamline your legal practice</p>
      <div className="space-x-4">
        <a 
          href="/signup" 
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Sign Up
        </a>
        <a 
          href="/login" 
          className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700 transition-colors"
        >
          Login
        </a>
      </div>
    </div>
  </div>
);

// Placeholder for Login page
const Login = () => (
  <div className="h-screen flex items-center justify-center bg-gray-100">
    <div className="text-center">
      <h1 className="text-2xl font-bold text-gray-800 mb-4">Login Page</h1>
      <p className="text-gray-600">Login page coming soon...</p>
      <a href="/signup" className="text-blue-600 hover:underline">
        Don't have an account? Sign up
      </a>
    </div>
  </div>
);

// Placeholder for Terms page
const Terms = () => (
  <div className="min-h-screen bg-gray-50 py-12 px-4">
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Terms of Service</h1>
      <div className="bg-white p-8 rounded-lg shadow">
        <p className="text-gray-600 mb-4">Terms of Service content will be added here...</p>
        <a href="/signup" className="text-blue-600 hover:underline">← Back to Signup</a>
      </div>
    </div>
  </div>
);

// Placeholder for Privacy page
const Privacy = () => (
  <div className="min-h-screen bg-gray-50 py-12 px-4">
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Privacy Policy</h1>
      <div className="bg-white p-8 rounded-lg shadow">
        <p className="text-gray-600 mb-4">Privacy Policy content will be added here...</p>
        <a href="/signup" className="text-blue-600 hover:underline">← Back to Signup</a>
      </div>
    </div>
  </div>
);

export default function App() {
  return (
    <Router>
      <Routes>
        {/* Home page */}
        <Route path="/" element={<Home />} />
        
        {/* Signup page */}
        <Route path="/signup" element={<Signup />} />
        <Route path="/register" element={<Signup />} /> {/* Alternative route */}
        
        {/* Login page */}
        <Route path="/login" element={<Login />} />

        <Route path="/common-landing" element={<CommonLanding/>} />
        
        {/* Terms and Privacy pages */}
        <Route path="/terms" element={<Terms />} />
        <Route path="/privacy" element={<Privacy />} />
        
        {/* Redirect any unknown routes to home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

import { useState, useEffect } from 'react';
import { Menu, X, Home } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Navigation = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${
      isScrolled ? 'bg-slate-900/95 backdrop-blur-md shadow-lg' : 'bg-transparent'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-2">
            <Home className="h-8 w-8 text-blue-400" />
            <span className="text-xl font-bold text-white">Home Pulse AI</span>
          </div>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-8">
            <a href="#home" className="text-white hover:text-blue-400 transition-colors">Home</a>
            <a href="#features" className="text-white hover:text-blue-400 transition-colors">Features</a>
            <a href="#search" className="text-white hover:text-blue-400 transition-colors">Search</a>
            <a href="#testimonials" className="text-white hover:text-blue-400 transition-colors">Reviews</a>
            <button
              onClick={() => navigate('/login')}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
            >
              Login
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden text-white"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden bg-slate-900/95 backdrop-blur-md">
            <div className="px-2 pt-2 pb-3 space-y-1">
              <a href="#home" className="block px-3 py-2 text-white hover:text-blue-400">Home</a>
              <a href="#features" className="block px-3 py-2 text-white hover:text-blue-400">Features</a>
              <a href="#search" className="block px-3 py-2 text-white hover:text-blue-400">Search</a>
              <a href="#testimonials" className="block px-3 py-2 text-white hover:text-blue-400">Reviews</a>
              <button
                onClick={() => navigate('/login')}
                className="w-full text-left px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg mt-2"
              >
                Get Started
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navigation;

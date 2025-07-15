import { useEffect, useState } from 'react';
import Navigation from '../components/Navigation';
import Footer from '../components/Footer';

const NotFound = () => {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 relative overflow-hidden text-white">
      {/* Dynamic Background */}
      <div
        className="fixed inset-0 opacity-20 transition-transform duration-1000 ease-out"
        style={{
          backgroundImage: `linear-gradient(45deg, hsl(220, 70%, ${20 + scrollY * 0.01}%), hsl(240, 80%, ${15 + scrollY * 0.005}%))`,
          transform: `translateY(${scrollY * 0.3}px) scale(${1 + scrollY * 0.0005})`,
        }}
      />

      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div
          className="absolute w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"
          style={{
            top: `${20 + scrollY * 0.1}%`,
            left: `${10 + scrollY * 0.05}%`,
            transform: `rotate(${scrollY * 0.1}deg)`,
          }}
        />
        <div
          className="absolute w-80 h-80 bg-purple-500/10 rounded-full blur-3xl"
          style={{
            top: `${60 + scrollY * 0.08}%`,
            right: `${15 + scrollY * 0.07}%`,
            transform: `rotate(${-scrollY * 0.08}deg)`,
          }}
        />
      </div>

      <Navigation />

      {/* Main Message */}
      <div className="flex flex-col items-center justify-center text-center px-4 py-32">
        <h1 className="text-5xl md:text-7xl font-bold mb-6">404</h1>
        <p className="text-2xl md:text-3xl font-medium mb-4">Page Not Found</p>
        <p className="text-base md:text-lg text-gray-300 max-w-xl">
          Sorry, the page you’re looking for doesn’t exist or has been moved. Please check the URL or return to the homepage.
        </p>
        <a
          href="/"
          className="mt-6 inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-2xl transition"
        >
          Go Back Home
        </a>
      </div>

      <Footer />
    </div>
  );
};

export default NotFound;

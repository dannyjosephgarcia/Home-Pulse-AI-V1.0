import React from 'react';
import { ArrowDown } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface HeroProps {
  scrollY: number;
}

const Hero: React.FC<HeroProps> = ({ scrollY }) => {
    const navigate = useNavigate();

  const handleStartSearching = () => {
    navigate('/login');
  };

  const handleLearnMore = () => {
    const productSection = document.getElementById('product');
    if (productSection) {
      productSection.scrollIntoView({ behavior: 'smooth' });
    }
  };
  return (
    <section id="home" className="relative min-h-screen flex items-center justify-center px-4 overflow-visible pt-20 pb-20">
      <div
        className="text-center max-w-4xl mx-auto transform transition-transform duration-1000"
        style={{ transform: `translateY(${scrollY * 0.2}px)` }}
      >
        <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
          One Dashboard
          <span className="block bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent pb-4">
            Every Property Decision
          </span>
        </h1>

        <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-2xl mx-auto">
          See upcoming repairs, plan budgets, and get instant answers from our built-in AI assistant—without juggling multiple tools.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <button
            onClick={handleStartSearching}
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-all transform hover:scale-105 shadow-lg"
          >
            Start Searching
          </button>
          <button
            onClick={handleLearnMore}
            className="border-2 border-white text-white hover:bg-white hover:text-slate-900 px-8 py-4 rounded-lg text-lg font-semibold transition-all transform hover:scale-105"
          >
            Learn More
          </button>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <ArrowDown className="text-white opacity-70" size={32} />
      </div>
    </section>
  );
};

export default Hero;

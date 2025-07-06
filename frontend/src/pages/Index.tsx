
import React, { useEffect, useState } from 'react';
import Hero from '../components/Hero';
import Features from '../components/Features';
import SearchForm from '../components/SearchForm';
import Testimonials from '../components/Testimonials';
import Footer from '../components/Footer';
import Navigation from '../components/Navigation';

const Index = () => {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 relative overflow-hidden">
      {/* Dynamic Background */}
      <div
        className="fixed inset-0 opacity-20 transition-transform duration-1000 ease-out"
        style={{
          backgroundImage: `linear-gradient(45deg, hsl(220, 70%, ${20 + scrollY * 0.01}%), hsl(240, 80%, ${15 + scrollY * 0.005}%))`,
          transform: `translateY(${scrollY * 0.3}px) scale(${1 + scrollY * 0.0005})`
        }}
      />

      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">-
        <div
          className="absolute w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"
          style={{
            top: `${20 + scrollY * 0.1}%`,
            left: `${10 + scrollY * 0.05}%`,
            transform: `rotate(${scrollY * 0.1}deg)`
          }}
        />
        <div
          className="absolute w-80 h-80 bg-purple-500/10 rounded-full blur-3xl"
          style={{
            top: `${60 + scrollY * 0.08}%`,
            right: `${15 + scrollY * 0.07}%`,
            transform: `rotate(${-scrollY * 0.08}deg)`
          }}
        />
      </div>

      <Navigation />
      <Hero scrollY={scrollY} />
      <Features />
      <SearchForm />
      <Testimonials />
      <Footer />
    </div>
  );
};

export default Index;

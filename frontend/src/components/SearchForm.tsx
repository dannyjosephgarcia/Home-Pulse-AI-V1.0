import React, { useState } from 'react';
import { Search, MapPin, Loader2 } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const SearchForm = () => {
  const [zipcode, setZipcode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!zipcode.trim()) {
      toast({
        title: "Error",
        description: "Please enter a valid zipcode",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`http://localhost:5000/v1/fetch_houses?postalCode=${zipcode}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch data');
      }

      const data = await response.json();

      console.log('API Response:', data);

      toast({
        title: "Search Successful",
        description: `Found properties for zipcode: ${zipcode}`,
      });

      // Here you would typically handle the response data
      // For example, navigate to results page or update state

    } catch (error) {
      console.error('API Error:', error);
      toast({
        title: "Search Failed",
        description: "Unable to connect to the search service. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section id="search" className="py-20 px-4 relative z-10">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 md:p-12 shadow-2xl">
          <div className="text-center mb-8">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Start Your Property Search
            </h2>
            <p className="text-xl text-gray-300">
              Enter your zipcode to discover available properties in your area
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <MapPin className="h-5 w-5 text-gray-400" />
              </div>

              <input
                type="text"
                value={zipcode}
                onChange={(e) => setZipcode(e.target.value)}
                placeholder="Enter zipcode (e.g., 90210)"
                className="w-full pl-12 pr-4 py-4 bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all text-lg"
                maxLength={10}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white py-4 px-8 rounded-lg text-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center space-x-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <Search className="h-5 w-5" />
                  <span>Search Properties</span>
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-400">
              We'll search our database of thousands of properties to find the perfect matches for your area
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SearchForm;

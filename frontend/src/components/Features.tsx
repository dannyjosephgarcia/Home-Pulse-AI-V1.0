import React from 'react';
import { Search, MapPin, TrendingUp, Shield } from 'lucide-react';

const Features = () => {
  const features = [
    {
      icon: <Search className="h-12 w-12 text-blue-400" />,
      title: "Advanced Search",
      description: "Find properties with our powerful filtering system and detailed search criteria."
    },
    {
      icon: <MapPin className="h-12 w-12 text-green-400" />,
      title: "Location Insights",
      description: "Get detailed neighborhood information, schools, and local amenities data."
    },
    {
      icon: <TrendingUp className="h-12 w-12 text-purple-400" />,
      title: "Market Analytics",
      description: "Access real-time market trends and property value predictions."
    },
    {
      icon: <Shield className="h-12 w-12 text-yellow-400" />,
      title: "Secure Transactions",
      description: "Protected deals with verified listings and secure payment processing."
    }
  ];

  return (
    <section id="features" className="py-20 px-4 relative z-10">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Why Choose Us
          </h2>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            We provide the most comprehensive real estate tools to help you make informed decisions
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white/10 backdrop-blur-md rounded-xl p-6 text-center hover:bg-white/20 transition-all duration-300 transform hover:scale-105 hover:shadow-xl"
            >
              <div className="flex justify-center mb-4">
                {feature.icon}
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">
                {feature.title}
              </h3>
              <p className="text-gray-300">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;

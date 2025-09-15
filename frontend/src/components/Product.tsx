import React from 'react';
import { Brain, Home, Clock, TrendingUp } from 'lucide-react';

const Product = () => {
  return (
    <section id="product" className="py-20 px-4 relative z-10">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Meet HomePulseAI
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            The intelligent home management system that predicts maintenance needs,
            optimizes costs, and keeps your property in perfect condition
          </p>
        </div>

        <div className="space-y-20">
          {/* Feature 1 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="order-2 lg:order-1">
              <div className="bg-gradient-to-br from-blue-600/20 to-purple-600/20 rounded-2xl p-8 backdrop-blur-md border border-white/10">
                <Brain className="w-16 h-16 text-blue-400 mb-6" />
                <h3 className="text-3xl font-bold text-white mb-4">
                  Predictive Analytics
                </h3>
                <p className="text-gray-300 text-lg leading-relaxed">
                  Our AI analyzes your home's appliances, systems, and structures to predict
                  maintenance needs before they become costly problems. Get personalized
                  timelines and budget forecasts tailored to your specific property.
                </p>
              </div>
            </div>
            <div className="order-1 lg:order-2 flex justify-center">
              <div className="w-80 h-80 bg-gradient-to-br from-blue-500/30 to-purple-500/30 rounded-full flex items-center justify-center backdrop-blur-sm border border-white/20">
                <TrendingUp className="w-32 h-32 text-white/80" />
              </div>
            </div>
          </div>

          {/* Feature 2 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="flex justify-center">
              <div className="w-80 h-80 bg-gradient-to-br from-green-500/30 to-blue-500/30 rounded-full flex items-center justify-center backdrop-blur-sm border border-white/20">
                <Home className="w-32 h-32 text-white/80" />
              </div>
            </div>
            <div>
              <div className="bg-gradient-to-br from-green-600/20 to-blue-600/20 rounded-2xl p-8 backdrop-blur-md border border-white/10">
                <Home className="w-16 h-16 text-green-400 mb-6" />
                <h3 className="text-3xl font-bold text-white mb-4">
                  Complete Home Management
                </h3>
                <p className="text-gray-300 text-lg leading-relaxed">
                  Track everything from HVAC systems and appliances to roofing and flooring.
                  Get maintenance schedules, replacement timelines, and cost estimates
                  all in one intelligent dashboard.
                </p>
              </div>
            </div>
          </div>

          {/* Feature 3 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="order-2 lg:order-1">
              <div className="bg-gradient-to-br from-purple-600/20 to-pink-600/20 rounded-2xl p-8 backdrop-blur-md border border-white/10">
                <Clock className="w-16 h-16 text-purple-400 mb-6" />
                <h3 className="text-3xl font-bold text-white mb-4">
                  Smart Scheduling
                </h3>
                <p className="text-gray-300 text-lg leading-relaxed">
                  Never miss important maintenance again. HomePulseAI creates
                  personalized schedules and sends timely reminders, helping you
                  maintain your home's value and avoid emergency repairs.
                </p>
              </div>
            </div>
            <div className="order-1 lg:order-2 flex justify-center">
              <div className="w-80 h-80 bg-gradient-to-br from-purple-500/30 to-pink-500/30 rounded-full flex items-center justify-center backdrop-blur-sm border border-white/20">
                <Clock className="w-32 h-32 text-white/80" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Product;

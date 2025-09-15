import { Check, Users, Building } from 'lucide-react';
import { Button } from '../components/ui/button';

const Pricing = () => {
  return (
    <section id="pricing" className="py-20 px-4 relative z-10">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Choose the plan that works best for you
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {/* Individual Plan */}
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20 hover:bg-white/15 transition-all duration-300">
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-blue-400" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">Individual</h3>
              <p className="text-gray-300 mb-6">Perfect for homeowners who want to stay on top of maintenance</p>
              <div className="text-center">
                <span className="text-5xl font-bold text-white">$99</span>
                <span className="text-gray-300 text-xl">/month</span>
              </div>
            </div>

            <ul className="space-y-4 mb-8">
              <li className="flex items-center text-gray-300">
                <Check className="w-5 h-5 text-green-400 mr-3 flex-shrink-0" />
                Complete home asset tracking
              </li>
              <li className="flex items-center text-gray-300">
                <Check className="w-5 h-5 text-green-400 mr-3 flex-shrink-0" />
                AI-powered maintenance predictions
              </li>
              <li className="flex items-center text-gray-300">
                <Check className="w-5 h-5 text-green-400 mr-3 flex-shrink-0" />
                Personalized replacement timelines
              </li>
              <li className="flex items-center text-gray-300">
                <Check className="w-5 h-5 text-green-400 mr-3 flex-shrink-0" />
                Cost forecasting and budgeting
              </li>
              <li className="flex items-center text-gray-300">
                <Check className="w-5 h-5 text-green-400 mr-3 flex-shrink-0" />
                Smart maintenance reminders
              </li>
              <li className="flex items-center text-gray-300">
                <Check className="w-5 h-5 text-green-400 mr-3 flex-shrink-0" />
                24/7 support
              </li>
            </ul>

            <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 text-lg">
              Get Started
            </Button>
          </div>

          {/* Enterprise Plan */}
          <div className="bg-gradient-to-b from-purple-600/20 to-blue-600/20 backdrop-blur-md rounded-2xl p-8 border-2 border-purple-400/30 hover:border-purple-400/50 transition-all duration-300 relative">
            <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
              <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-2 rounded-full text-sm font-semibold">
                Most Popular
              </div>
            </div>

            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Building className="w-8 h-8 text-purple-400" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">Real Estate Brokers</h3>
              <p className="text-gray-300 mb-6">License HomePulseAI to offer as a free service to your clients</p>
              <div className="text-center">
                <span className="text-3xl font-bold text-white">Custom Pricing</span>
              </div>
            </div>

            <ul className="space-y-4 mb-8">
              <li className="flex items-center text-gray-300">
                <Check className="w-5 h-5 text-green-400 mr-3 flex-shrink-0" />
                White-label solution
              </li>
              <li className="flex items-center text-gray-300">
                <Check className="w-5 h-5 text-green-400 mr-3 flex-shrink-0" />
                Unlimited client accounts
              </li>
              <li className="flex items-center text-gray-300">
                <Check className="w-5 h-5 text-green-400 mr-3 flex-shrink-0" />
                Branded mobile app
              </li>
              <li className="flex items-center text-gray-300">
                <Check className="w-5 h-5 text-green-400 mr-3 flex-shrink-0" />
                Custom reporting dashboard
              </li>
              <li className="flex items-center text-gray-300">
                <Check className="w-5 h-5 text-green-400 mr-3 flex-shrink-0" />
                Priority support
              </li>
              <li className="flex items-center text-gray-300">
                <Check className="w-5 h-5 text-green-400 mr-3 flex-shrink-0" />
                Training and onboarding
              </li>
            </ul>

            <Button className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white py-3 text-lg">
              Contact Sales
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Pricing;
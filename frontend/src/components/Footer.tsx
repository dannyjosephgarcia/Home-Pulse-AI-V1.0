import { Home, Mail, Phone, MapPin } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-slate-900/50 backdrop-blur-md border-t border-white/10 py-12 px-4 relative z-10">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Home className="h-8 w-8 text-blue-400" />
              <span className="text-xl font-bold text-white">Home Pulse AI</span>
            </div>
            <p className="text-gray-300">
              Your trusted partner in budgeting for the perfect property. We make investments simple, transparent,
              and accessible.
            </p>
          </div>

          {/* Quick Links */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Quick Links</h3>
            <ul className="space-y-2">
              <li><a href="#home" className="text-gray-300 hover:text-blue-400 transition-colors">Home</a></li>
              <li><a href="#features" className="text-gray-300 hover:text-blue-400 transition-colors">Features</a></li>
              <li><a href="#search" className="text-gray-300 hover:text-blue-400 transition-colors">Search</a></li>
              <li><a href="#testimonials" className="text-gray-300 hover:text-blue-400 transition-colors">Reviews</a></li>
            </ul>
          </div>

          {/* Services */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Services</h3>
            <ul className="space-y-2">
              <li><span className="text-gray-300">Property Search</span></li>
              <li><span className="text-gray-300">Market Analysis</span></li>
              <li><span className="text-gray-300">Investment Advice</span></li>
              <li><span className="text-gray-300">Property Management</span></li>
            </ul>
          </div>

          {/* Contact */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Contact Us</h3>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Mail className="h-4 w-4 text-blue-400" />
                <span className="text-gray-300">homepulseai@gmail.com.com</span>
              </div>
              <div className="flex items-center space-x-2">
                <Phone className="h-4 w-4 text-blue-400" />
                <span className="text-gray-300">(708) 673-2131</span>
              </div>
              <div className="flex items-center space-x-2">
                <MapPin className="h-4 w-4 text-blue-400" />
                <span className="text-gray-300">123 Real Estate Ave, Suite 100</span>
              </div>
            </div>
          </div>
        </div>

        <div className="border-t border-white/10 mt-8 pt-8 text-center">
          <p className="text-gray-400">
            © 2025 Next Level Coding, LLC. All rights reserved. Built with modern technology for the modern investor.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

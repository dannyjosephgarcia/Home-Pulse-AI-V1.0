import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { XCircle, Mail, Phone } from 'lucide-react';

const PaymentCancel = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 relative overflow-hidden">
      {/* Dynamic Background */}
      <div className="fixed inset-0 opacity-20">
        <div className="absolute w-96 h-96 bg-blue-500/10 rounded-full blur-3xl top-20 left-10 animate-pulse" />
        <div className="absolute w-80 h-80 bg-purple-500/10 rounded-full blur-3xl top-60 right-15 animate-pulse" />
      </div>

      {/* Content */}
      <div className="relative z-10 min-h-screen flex items-center justify-center p-4">
        <Card className="w-full max-w-md bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-8 text-center">
            <div className="space-y-6">
              <div className="flex justify-center">
                <XCircle className="h-16 w-16 text-red-400" />
              </div>

              <div className="space-y-2">
                <h1 className="text-2xl font-bold text-white">Payment Cancelled</h1>
                <p className="text-white/70">
                  Your payment was cancelled or encountered an issue. No charges have been made to your account.
                </p>
              </div>

              <div className="space-y-4">
                <Button
                  onClick={() => navigate('/')}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3"
                >
                  Try Again
                </Button>

                <Button
                  onClick={() => navigate('/')}
                  variant="outline"
                  className="w-full bg-white/10 hover:bg-white/20 text-white border-white/20"
                >
                  Return Home
                </Button>
              </div>

              <div className="mt-8 pt-6 border-t border-white/20">
                <h3 className="text-white font-semibold mb-4">Need Help?</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex items-center justify-center space-x-2 text-white/70">
                    <Mail className="h-4 w-4" />
                    <span>nextlevelcodingacademy@gmail.com</span>
                  </div>
                  <div className="flex items-center justify-center space-x-2 text-white/70">
                    <Phone className="h-4 w-4" />
                    <span>1-708-673-2131</span>
                  </div>
                  <p className="text-white/60 text-xs mt-4">
                    Our customer support team is available 24/7 to assist you with any payment issues.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PaymentCancel;
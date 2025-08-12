import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { toast } from 'sonner';
import { CheckCircle, Loader2, AlertTriangle } from 'lucide-react';

const PaymentSuccess = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [isProcessing, setIsProcessing] = useState(true);

  useEffect(() => {
    const checkPaymentStatus = async () => {
      try {
        // Extract session_id from URL parameters
        const sessionId = searchParams.get('session_id');

        const response = await fetch('https://home-pulse-api.onrender.com/v1/customers/post-payment-login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            sessionId: sessionId
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to check payment status');
        }

        const data = await response.json();

        if (data.paidStatus === true) {
          // Payment confirmed, store JWT and redirect
          if (data.jwt || data.token) {
            localStorage.setItem('authToken', data.jwt || data.token);
            toast.success('Payment confirmed! Redirecting to dashboard...');
            navigate('/dashboard');
          } else {
            throw new Error('No authentication token received');
          }
        }
        // If paidStatus is not true, continue polling
      } catch (error) {
        console.error('Error checking payment status:', error);
        // Continue polling even on error
      }
    };

    // Initial check
    checkPaymentStatus();

    // Set up polling every 3 seconds
    const interval = setInterval(checkPaymentStatus, 3000);

    // Cleanup interval on component unmount
    return () => clearInterval(interval);
  }, [navigate]);

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
                <Loader2 className="h-16 w-16 text-blue-400 animate-spin" />
              </div>
              <div className="space-y-2">
                <h1 className="text-2xl font-bold text-white">Verifying Payment</h1>
                <p className="text-white/70">
                  Please wait while we confirm your payment status...
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PaymentSuccess;
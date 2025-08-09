import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { toast } from 'sonner';
import { CheckCircle, Loader2, AlertTriangle } from 'lucide-react';

const PaymentSuccess = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(true);
  const [jwt, setJwt] = useState<string | null>(null);
  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    const updatePaymentStatus = async () => {
      if (!sessionId) {
        toast.error('Invalid payment session');
        setIsProcessing(false);
        return;
      }

      try {
        const response = await fetch('https://home-pulse-api.onrender.com/v1/payment/update-payment-status', {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ sessionId: sessionId }),
        });

        if (!response.ok) {
          throw new Error('Failed to update payment status');
        }

        const data = await response.json();

        if (data.jwt) {
          setJwt(data.jwt);
          // Store JWT in localStorage for authentication
          localStorage.setItem('authToken', data.jwt);
          toast.success('Payment processed successfully!');
        } else {
          throw new Error('No JWT received from server');
        }
      } catch (error) {
        console.error('Error updating payment status:', error);
        toast.error('Failed to process payment confirmation');
      } finally {
        setIsProcessing(false);
      }
    };

    updatePaymentStatus();
  }, [sessionId]);

  const handleGoToDashboard = () => {
    if (jwt) {
      // The JWT is already stored in localStorage, navigate to dashboard
      navigate('/dashboard');
    } else {
      toast.error('Authentication token not available');
    }
  };

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
            {isProcessing ? (
              <div className="space-y-6">
                <div className="flex justify-center">
                  <Loader2 className="h-16 w-16 text-blue-400 animate-spin" />
                </div>
                <div className="space-y-2">
                  <h1 className="text-2xl font-bold text-white">Processing Payment</h1>
                  <p className="text-white/70">
                    Please wait while we confirm your payment...
                  </p>
                </div>
              </div>
            ) : jwt ? (
              <div className="space-y-6">
                <div className="flex justify-center">
                  <CheckCircle className="h-16 w-16 text-green-400" />
                </div>
                <div className="space-y-2">
                  <h1 className="text-2xl font-bold text-white">Payment Successful!</h1>
                  <p className="text-white/70">
                    Thank you for your purchase. Your payment has been processed successfully.
                  </p>
                </div>
                <Button
                  onClick={handleGoToDashboard}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3"
                >
                  Access Your Dashboard
                </Button>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="flex justify-center">
                  <AlertTriangle className="h-16 w-16 text-amber-400" />
                </div>
                <div className="space-y-2">
                  <h1 className="text-2xl font-bold text-white">Payment Error</h1>
                  <p className="text-white/70">
                    There was an issue processing your payment confirmation. Please contact customer support.
                  </p>
                </div>
                <Button
                  onClick={() => navigate('/')}
                  className="w-full bg-white/20 hover:bg-white/30 text-white border-white/20"
                >
                  Return Home
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PaymentSuccess;
import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../lib/api';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { LogOut, Home, MapPin, Plus } from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

interface Property {
  id: number;
  postal_code: string;
  address: string;
  age: number;
  created_at: string;
  user_id: number;
}

const Dashboard = () => {
  const { user, signOut } = useAuth();
  const [properties, setProperties] = useState<Property[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchProperties();
  }, []);

  const fetchProperties = async () => {
    try {
      const { data, error } = await apiClient.getProperties();

      if (error) {
        console.error('Error fetching properties:', error);
        toast.error('Failed to load properties');
      } else {
        setProperties(data || []);
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('Network error while loading properties');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignOut = async () => {
    const { error } = await signOut();
    if (error) {
      toast.error('Error signing out');
    } else {
      toast.success('Signed out successfully');
      navigate('/');
    }
  };

  const handlePropertyClick = (propertyId: number) => {
    navigate(`/property/${propertyId}`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary to-primary-dark">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white"></div>
      </div>
    );
  }

  return (
  <div className="min-h-screen bg-gradient-to-br from-primary to-primary-dark">
    {/* Header */}
    <header className="bg-white/10 backdrop-blur-md border-b border-white/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <Home className="h-8 w-8 text-white" />
            <h1 className="text-xl font-bold text-white">Home Pulse AI Dashboard</h1>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-white/80">Welcome, {user?.email}</span>
            <Button
              variant="outline"
              onClick={handleSignOut}
              className="bg-white/20 border-white/30 text-white hover:bg-white/30"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </div>
    </header>

    {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">Your Properties</h2>
          <p className="text-white/80">Click on any property to view detailed information and location.</p>
        </div>
      {properties.length === 0 ? (
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardContent className="p-8 text-center">
              <Home className="h-16 w-16 text-white/50 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">No Properties Found</h3>
              <p className="text-white/70 mb-4">You haven't added any properties yet.</p>
              <Button
                onClick={() => navigate('/properties')}
                className="bg-white text-primary hover:bg-white/90"
              >
                Add Your First Property
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {properties.map((property) => (
              <Card
                key={property.id}
                className="bg-white/10 backdrop-blur-md border-white/20 hover:bg-white/20 transition-all duration-200 cursor-pointer group"
                onClick={() => handlePropertyClick(property.id)}
              >
                <CardHeader>
                  <CardTitle className="text-white flex items-center space-x-2">
                    <MapPin className="h-5 w-5" />
                    <span>Property Location: {property.address}</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-white/70">Postal Code:</span>
                      <span className="text-white font-medium">{property.postal_code || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/70">Address:</span>
                      <span className="text-white font-medium">{property.address || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/70">Home Age:</span>
                      <span className="text-white font-medium">{property.age ? `${property.age} years` : 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/70">Added:</span>
                      <span className="text-white font-medium">
                        {new Date(property.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <div className="mt-8 text-center">
                    <span className="text-white/60 group-hover:text-white/80 transition-colors">
                      Click to view details →
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}

            {/* Add Property Card */}
            <Card
              className="rounded-xl bg-white/5 hover:bg-white/10 border border-white/20 shadow-sm backdrop-blur-md transition-all duration-200 cursor-pointer group"
              onClick={() => navigate('/properties')}
            >
              <CardContent className="p-6 flex flex-col items-center justify-center">
                <div className="w-24 h-24 rounded-full bg-white/5 hover:scale-105 border border-white/20 shadow-sm backdrop-blur-md transition-all duration-200 cursor-pointer group flex items-center justify-center p-0">
                  <Plus className="h-10 w-10 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Add Property</h3>
                <p className="text-white/70 text-center text-sm">
                  Click to add a new property to your portfolio
                </p>
              </CardContent>
            </Card>
          </div>
      )}
      </main>
  </div>
);
};

export default Dashboard;

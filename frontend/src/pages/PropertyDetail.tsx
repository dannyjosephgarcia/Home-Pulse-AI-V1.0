import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiClient } from '../lib/api';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { ArrowLeft, Home, Wrench, Building } from 'lucide-react';
import { toast } from 'sonner';

interface Property {
  id: number;
  postal_code: string;
  address: string;
  age: number;
  user_id: number;
  created_at: string;
}

interface Appliance {
  id: number;
  appliance_type: string;
  age_in_years: number;
  estimated_replacement_cost: number;
  property_id: number;
  forecasted_replacement_date: string;
}

interface Structure {
  id: number;
  structure_type: string;
  age_in_years: number;
  estimated_replacement_cost: number;
  property_id: number;
  forecasted_replacement_date: string;
}

const PropertyDetail = () => {
  const { propertyId } = useParams<{ propertyId: string }>();
  const navigate = useNavigate();
  const [property, setProperty] = useState<Property | null>(null);
  const [appliances, setAppliances] = useState<Appliance[]>([]);
  const [structures, setStructures] = useState<Structure[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (propertyId) {
      fetchPropertyData();
    }
  }, [propertyId]);

  const fetchPropertyData = async () => {
    try {
      const id = parseInt(propertyId!);

      // Fetch property details
      const { data: propertyData, error: propertyError } = await apiClient.getProperty(id);

      if (propertyError) {
        console.error('Error fetching property:', propertyError);
        toast.error('Failed to load property details');
        return;
      }

      // Fetch appliances
      const { data: appliancesData, error: appliancesError } = await apiClient.getPropertyAppliances(id);

      if (appliancesError) {
        console.error('Error fetching appliances:', appliancesError);
        toast.error('Failed to load appliances');
      }

      // Fetch structures
      const { data: structuresData, error: structuresError } = await apiClient.getPropertyStructures(id);

      if (structuresError) {
        console.error('Error fetching structures:', structuresError);
        toast.error('Failed to load structures');
      }

      setProperty(propertyData);
      setAppliances(appliancesData || []);
      setStructures(structuresData || []);
    } catch (error) {
      console.error('Error:', error);
      toast.error('Network error while loading property data');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary to-primary-dark">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white"></div>
      </div>
    );
  }

  if (!property) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center">
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-8 text-center">
            <h3 className="text-xl font-semibold text-white mb-2">Property Not Found</h3>
            <p className="text-white/70 mb-4">The requested property could not be found.</p>
            <Button
              onClick={() => navigate('/dashboard')}
              className="bg-white text-primary hover:bg-white/90"
            >
              Back to Dashboard
            </Button>
          </CardContent>
        </Card>
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
              <Button
                variant="ghost"
                onClick={() => navigate('/dashboard')}
                className="text-white hover:bg-white/20"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
              <div className="h-6 w-px bg-white/30" />
              <Home className="h-6 w-6 text-white" />
              <h1 className="text-xl font-bold text-white">Property: {property.address}</h1>
            </div>
          </div>
        </div>
      </header>

      <div className="flex h-[calc(100vh-4rem)]">
        {/* Left Panel - Property Details */}
        <div className="w-1/2 p-6 overflow-y-auto">
          <div className="space-y-6">
            {/* Property Information */}
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <Home className="h-5 w-5" />
                  <span>Property Information</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-white/70">Address:</span>
                  <span className="text-white font-medium">{property.address || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/70">Postal Code:</span>
                  <span className="text-white font-medium">{property.postal_code || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/70">Home Age:</span>
                  <span className="text-white font-medium">{property.age ? `${property.age} years` : 'N/A'}</span>
                </div>
              </CardContent>
            </Card>

            {/* Appliances */}
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <Wrench className="h-5 w-5" />
                  <span>Appliances ({appliances.length})</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {appliances.length === 0 ? (
                  <p className="text-white/70 text-center py-4">No appliances recorded</p>
                ) : (
                  <div className="space-y-3">
                    {appliances.map((appliance) => (
                      <div key={appliance.id} className="bg-white/5 rounded-lg p-3">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="text-white font-medium capitalize">{appliance.appliance_type}</h4>
                          <span className="text-white/70 text-sm">{appliance.age_in_years} years old</span>
                        </div>
                        <div className="space-y-1">
                          <p className="text-white/60 text-sm">
                              Estimated replacement cost:{' '}
                              {appliance.estimated_replacement_cost != null
                                ? `$${appliance.estimated_replacement_cost.toLocaleString()}`
                                : 'N/A'}
                            </p>
                          {appliance.forecasted_replacement_date && (
                            <p className="text-white/60 text-sm">
                              Forecasted replacement:{' '}
                              {appliance.forecasted_replacement_date === 'TBD'
                                ? 'TBD'
                                : new Date(appliance.forecasted_replacement_date).toLocaleDateString()}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Structures */}
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <Building className="h-5 w-5" />
                  <span>Structures ({structures.length})</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {structures.length === 0 ? (
                  <p className="text-white/70 text-center py-4">No structures recorded</p>
                ) : (
                  <div className="space-y-3">
                    {structures.map((structure) => (
                      <div key={structure.id} className="bg-white/5 rounded-lg p-3">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="text-white font-medium capitalize">{structure.structure_type}</h4>
                          <span className="text-white/70 text-sm">{structure.age_in_years} years old</span>
                        </div>
                        <div className="space-y-1">
                          <p className="text-white/60 text-sm">
                              Estimated replacement cost:{' '}
                              {structure.estimated_replacement_cost != null
                                ? `$${structure.estimated_replacement_cost.toLocaleString()}`
                                : 'N/A'}
                            </p>
                          {structure.forecasted_replacement_date && (
                            <p className="text-white/60 text-sm">
                              Forecasted replacement:{' '}
                              {structure.forecasted_replacement_date === 'TBD'
                                ? 'TBD'
                                : new Date(structure.forecasted_replacement_date).toLocaleDateString()}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Right Panel - Map */}
        <div className="w-1/2 bg-white/5 backdrop-blur-sm border-l border-white/20">
          <div className="h-full flex items-center justify-center">
            <Card className="bg-white/10 backdrop-blur-md border-white/20 m-6">
              <CardContent className="p-8 text-center">
                <div className="text-white/50 mb-4">
                  <svg className="w-16 h-16 mx-auto" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">Map Integration</h3>
                <p className="text-white/70 mb-4">
                  Map functionality will be implemented here to show the property location based on the address.
                </p>
                <p className="text-white/60 text-sm">
                  Address: {property.address || 'No address available'}
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PropertyDetail;

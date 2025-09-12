import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiClient } from '../lib/api';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { Button } from '../components/ui/button';
import { useAuth } from '../contexts/AuthContext';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { ArrowLeft, Home, Wrench, Building, MapPin, Image, Upload, Edit, Save, X, ChevronDown, ChevronRight } from 'lucide-react';
import { toast } from 'sonner';
import { HomeBot } from '../components/HomeBot';
import 'leaflet/dist/leaflet.css';

// Type declaration for MapContainer props
declare module 'react-leaflet' {
  interface MapContainerProps {
    center: [number, number];
    zoom: number;
    scrollWheelZoom?: boolean;
    style?: React.CSSProperties;
    children?: React.ReactNode;
  }
}

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
  const { user } = useAuth();
  const [property, setProperty] = useState<Property | null>(null);
  const [appliances, setAppliances] = useState<Appliance[]>([]);
  const [structures, setStructures] = useState<Structure[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [coordinates, setCoordinates] = useState<{ lat: number; lng: number } | null>(null);
  const [isGeocodingLoading, setIsGeocodingLoading] = useState(false);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isImageLoading, setIsImageLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [expandedAppliances, setExpandedAppliances] = useState<Set<number>>(new Set());
  const [expandedStructures, setExpandedStructures] = useState<Set<number>>(new Set());
  const [editingAppliances, setEditingAppliances] = useState<{ [key: number]: Appliance }>({});
  const [editingStructures, setEditingStructures] = useState<{ [key: number]: Structure }>({});
  const [isUpdatingAppliances, setIsUpdatingAppliances] = useState(false);
  const [isUpdatingStructures, setIsUpdatingStructures] = useState(false);

  // Fix for default marker icons in react-leaflet
  delete (L.Icon.Default.prototype as any)._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  });

  useEffect(() => {
    if (propertyId) {
      fetchPropertyData();
      fetchPropertyImage();
    }
  }, [propertyId]);

  const geocodeAddress = async (address: string) => {
    const apiKey = import.meta.env.VITE_OPENCAGE_API_KEY;
    if (!apiKey) {
      toast.error('OpenCage API key not configured');
      return;
    }

    setIsGeocodingLoading(true);
    try {
      const response = await fetch(
        `https://api.opencagedata.com/geocode/v1/json?q=${encodeURIComponent(address)}&key=${apiKey}&limit=4`
      );
      const data = await response.json();

      if (data.results && data.results.length > 0) {
        const { lat, lng } = data.results[0].geometry;
        setCoordinates({ lat, lng });
        toast.success('Location found successfully');
      } else {
        toast.error('Address not found');
        setCoordinates(null);
      }
    } catch (error) {
      console.error('Geocoding error:', error);
      toast.error('Failed to geocode address');
      setCoordinates(null);
    } finally {
      setIsGeocodingLoading(false);
    }
  };

  const fetchPropertyImage = async () => {
    if (!user || !propertyId) return;

    setIsImageLoading(true);
    try {
      const id = parseInt(propertyId);
      const { data: imageData, error: imageError } = await apiClient.getPropertyImageSignedUrl(id, user.user_id);

      if (imageError) {
        console.error('Error fetching property image:', imageError);
        // Don't show error toast for missing images as it's expected
        setImageUrl(null);
        return;
      }

      if (imageData?.signedURL) {
        setImageUrl(imageData.signedURL);
      }
    } catch (error) {
      console.error('Error fetching property image:', error);
      setImageUrl(null);
    } finally {
      setIsImageLoading(false);
    }
  };

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !user || !propertyId) return;

    setIsUploading(true);
    try {
      const id = parseInt(propertyId);
      const fileName = file.name;

      // Get signed URL for upload
      const { data: uploadData, error: uploadError } = await apiClient.uploadPropertyImage(id, user.user_id, fileName);

      if (uploadError) {
        console.error('Error getting upload URL:', uploadError);
        toast.error('Failed to prepare image upload');
        return;
      }

      if (!uploadData?.imageUrl) {
        toast.error('No upload URL received');
        return;
      }

      // Upload file to S3 using signed URL
      const uploadResponse = await fetch(uploadData.imageUrl, {
        method: 'PUT',
        body: file,
        headers: {
          'Content-Type': file.type,
        },
      });

      if (!uploadResponse.ok) {
        throw new Error('Failed to upload to S3');
      }

      toast.success('Image uploaded successfully');

      // Refresh the image display
      await fetchPropertyImage();

    } catch (error) {
      console.error('Error uploading image:', error);
      toast.error('Failed to upload image');
    } finally {
      setIsUploading(false);
      // Reset file input
      event.target.value = '';
    }
  };

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

  const toggleApplianceExpansion = (applianceId: number) => {
    const newExpanded = new Set(expandedAppliances);
    if (newExpanded.has(applianceId)) {
      newExpanded.delete(applianceId);
      // Clear editing state when collapsing
      const newEditing = { ...editingAppliances };
      delete newEditing[applianceId];
      setEditingAppliances(newEditing);
    } else {
      newExpanded.add(applianceId);
    }
    setExpandedAppliances(newExpanded);
  };

  const toggleStructureExpansion = (structureId: number) => {
    const newExpanded = new Set(expandedStructures);
    if (newExpanded.has(structureId)) {
      newExpanded.delete(structureId);
      // Clear editing state when collapsing
      const newEditing = { ...editingStructures };
      delete newEditing[structureId];
      setEditingStructures(newEditing);
    } else {
      newExpanded.add(structureId);
    }
    setExpandedStructures(newExpanded);
  };

  const startEditingAppliance = (appliance: Appliance) => {
    setEditingAppliances({
      ...editingAppliances,
      [appliance.id]: { ...appliance }
    });
  };

  const startEditingStructure = (structure: Structure) => {
    setEditingStructures({
      ...editingStructures,
      [structure.id]: { ...structure }
    });
  };

  const cancelEditingAppliance = (applianceId: number) => {
    const newEditing = { ...editingAppliances };
    delete newEditing[applianceId];
    setEditingAppliances(newEditing);
  };

  const cancelEditingStructure = (structureId: number) => {
    const newEditing = { ...editingStructures };
    delete newEditing[structureId];
    setEditingStructures(newEditing);
  };

  const updateApplianceField = (applianceId: number, field: keyof Appliance, value: any) => {
    if (editingAppliances[applianceId]) {
      setEditingAppliances({
        ...editingAppliances,
        [applianceId]: {
          ...editingAppliances[applianceId],
          [field]: value
        }
      });
    }
  };

  const updateStructureField = (structureId: number, field: keyof Structure, value: any) => {
    if (editingStructures[structureId]) {
      setEditingStructures({
        ...editingStructures,
        [structureId]: {
          ...editingStructures[structureId],
          [field]: value
        }
      });
    }
  };

  const saveAppliances = async () => {
    if (!propertyId || Object.keys(editingAppliances).length === 0) return;

    setIsUpdatingAppliances(true);
    try {
      const updates = Object.values(editingAppliances).map(appliance => ({
        appliance_type: appliance.appliance_type,
        age_in_years: Number(appliance.age_in_years),
        estimated_replacement_cost: Number(appliance.estimated_replacement_cost),
        forecasted_replacement_date: appliance.forecasted_replacement_date
      }));

      const { error } = await apiClient.updatePropertyAppliances(parseInt(propertyId), updates);

      if (error) {
        console.error('Error updating appliances:', error);
        toast.error('Failed to update appliances');
        return;
      }

      // Update the local state with the new values
      const newAppliances = appliances.map(appliance => {
        const edited = editingAppliances[appliance.id];
        return edited ? edited : appliance;
      });
      setAppliances(newAppliances);

      // Clear editing state
      setEditingAppliances({});
      toast.success('Appliances updated successfully');
    } catch (error) {
      console.error('Error updating appliances:', error);
      toast.error('Network error while updating appliances');
    } finally {
      setIsUpdatingAppliances(false);
    }
  };

  const saveStructures = async () => {
    if (!propertyId || Object.keys(editingStructures).length === 0) return;

    setIsUpdatingStructures(true);
    try {
      const updates = Object.values(editingStructures).map(structure => ({
        structure_type: structure.structure_type,
        age_in_years: Number(structure.age_in_years),
        estimated_replacement_cost: Number(structure.estimated_replacement_cost),
        forecasted_replacement_date: structure.forecasted_replacement_date
      }));

      const { error } = await apiClient.updatePropertyStructures(parseInt(propertyId), updates);

      if (error) {
        console.error('Error updating structures:', error);
        toast.error('Failed to update structures');
        return;
      }

      // Update the local state with the new values
      const newStructures = structures.map(structure => {
        const edited = editingStructures[structure.id];
        return edited ? edited : structure;
      });
      setStructures(newStructures);

      // Clear editing state
      setEditingStructures({});
      toast.success('Structures updated successfully');
    } catch (error) {
      console.error('Error updating structures:', error);
      toast.error('Network error while updating structures');
    } finally {
      setIsUpdatingStructures(false);
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
                <CardTitle className="text-white flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Wrench className="h-5 w-5" />
                    <span>Appliances ({appliances.length})</span>
                  </div>
                  {Object.keys(editingAppliances).length > 0 && (
                    <Button
                      onClick={saveAppliances}
                      disabled={isUpdatingAppliances}
                      size="sm"
                      className="bg-green-600 hover:bg-green-700 text-white"
                    >
                      <Save className="h-4 w-4 mr-2" />
                      {isUpdatingAppliances ? 'Saving...' : 'Apply Changes'}
                    </Button>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {appliances.length === 0 ? (
                  <p className="text-white/70 text-center py-4">No appliances recorded</p>
                ) : (
                  <div className="space-y-3">
                    {appliances.map((appliance) => {
                      const isExpanded = expandedAppliances.has(appliance.id);
                      const isEditing = editingAppliances[appliance.id];
                      const currentData = isEditing || appliance;
                      const rawDate = currentData.forecasted_replacement_date;
                      let formattedDate = '';

                      if (rawDate) {
                          const d = new Date(rawDate);
                          if (!isNaN(d.getTime())) {
                            formattedDate = d.toISOString().split('T')[0];
                          }
                        }

                      return (
                        <div key={appliance.id} className="bg-white/5 rounded-lg">
                          <div
                            className="p-3 cursor-pointer hover:bg-white/10 transition-colors"
                            onClick={() => toggleApplianceExpansion(appliance.id)}
                          >
                            <div className="flex justify-between items-start">
                              <div className="flex items-center space-x-2">
                                {isExpanded ? (
                                  <ChevronDown className="h-4 w-4 text-white/70" />
                                ) : (
                                  <ChevronRight className="h-4 w-4 text-white/70" />
                                )}
                                <h4 className="text-white font-medium capitalize">{appliance.appliance_type}</h4>
                              </div>
                              <span className="text-white/70 text-sm">{appliance.age_in_years} years old</span>
                            </div>
                            <div className="ml-6 space-y-1">
                              {appliance.estimated_replacement_cost && (
                                <p className="text-white/60 text-sm">
                                  Estimated replacement: ${appliance.estimated_replacement_cost.toLocaleString()}
                                </p>
                              )}
                              {appliance.forecasted_replacement_date && (
                                <p className="text-white/60 text-sm">
                                  Forecasted replacement: {new Date(appliance.forecasted_replacement_date).toLocaleDateString()}
                                </p>
                              )}
                            </div>
                          </div>

                          {isExpanded && (
                            <div className="px-3 pb-3 ml-6 space-y-3 border-t border-white/10 pt-3">
                              {!isEditing ? (
                                <Button
                                  onClick={() => startEditingAppliance(appliance)}
                                  size="sm"
                                  variant="outline"
                                  className="bg-white/10 hover:bg-white/20 text-white border-white/30"
                                >
                                  <Edit className="h-4 w-4 mr-2" />
                                  Update
                                </Button>
                              ) : (
                                <div className="space-y-3">
                                  <div>
                                    <Label className="text-white/70 text-sm">Type</Label>
                                    <Input
                                      value={currentData.appliance_type}
                                      onChange={(e) => updateApplianceField(appliance.id, 'appliance_type', e.target.value)}
                                      className="bg-white/10 border-white/20 text-white"
                                    />
                                  </div>
                                  <div>
                                    <Label className="text-white/70 text-sm">Age (years)</Label>
                                    <Input
                                      type="number"
                                      value={currentData.age_in_years}
                                      onChange={(e) => updateApplianceField(appliance.id, 'age_in_years', parseInt(e.target.value) || 0)}
                                      className="bg-white/10 border-white/20 text-white"
                                    />
                                  </div>
                                  <div>
                                    <Label className="text-white/70 text-sm">Estimated Replacement Cost</Label>
                                    <Input
                                      type="number"
                                      value={currentData.estimated_replacement_cost || ''}
                                      onChange={(e) => updateApplianceField(appliance.id, 'estimated_replacement_cost', parseFloat(e.target.value) || 0)}
                                      className="bg-white/10 border-white/20 text-white"
                                    />
                                  </div>
                                  <div>
                                    <Label className="text-white/70 text-sm">Forecasted Replacement Date</Label>
                                    <Input
                                      type="date"
                                      value={formattedDate}
                                      onChange={(e) =>
                                        updateApplianceField(
                                          appliance.id,
                                          'forecasted_replacement_date',
                                          e.target.value
                                        )
                                      }
                                      className="bg-white/10 border-white/20 text-white"
                                    />
                                  </div>
                                  <div className="flex space-x-2">
                                    <Button
                                      onClick={() => cancelEditingAppliance(appliance.id)}
                                      size="sm"
                                      variant="outline"
                                      className="bg-white/10 hover:bg-white/20 text-white border-white/30"
                                    >
                                      <X className="h-4 w-4 mr-2" />
                                      Cancel
                                    </Button>
                                  </div>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Structures */}
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardHeader>
                <CardTitle className="text-white flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Building className="h-5 w-5" />
                    <span>Structures ({structures.length})</span>
                  </div>
                  {Object.keys(editingStructures).length > 0 && (
                    <Button
                      onClick={saveStructures}
                      disabled={isUpdatingStructures}
                      size="sm"
                      className="bg-green-600 hover:bg-green-700 text-white"
                    >
                      <Save className="h-4 w-4 mr-2" />
                      {isUpdatingStructures ? 'Saving...' : 'Apply Changes'}
                    </Button>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {structures.length === 0 ? (
                  <p className="text-white/70 text-center py-4">No structures recorded</p>
                ) : (
                  <div className="space-y-3">
                    {structures.map((structure) => {
                      const isExpanded = expandedStructures.has(structure.id);
                      const isEditing = editingStructures[structure.id];
                      const currentData = isEditing || structure;
                      const rawDate = currentData.forecasted_replacement_date;
                      const typeDisplayMap: Record<string, string> = {
                          ac_unit: 'Air Conditioner',
                          water_heater: 'Water Heater',
                        };
                      let formattedDate = '';

                      if (rawDate) {
                          const d = new Date(rawDate);
                          if (!isNaN(d.getTime())) {
                            formattedDate = d.toISOString().split('T')[0];
                          }
                        }

                      return (
                        <div key={structure.id} className="bg-white/5 rounded-lg">
                          <div
                            className="p-3 cursor-pointer hover:bg-white/10 transition-colors"
                            onClick={() => toggleStructureExpansion(structure.id)}
                          >
                            <div className="flex justify-between items-start">
                              <div className="flex items-center space-x-2">
                                {isExpanded ? (
                                  <ChevronDown className="h-4 w-4 text-white/70" />
                                ) : (
                                  <ChevronRight className="h-4 w-4 text-white/70" />
                                )}
                                <h4 className="text-white font-medium capitalize">
                                  {typeDisplayMap[structure.structure_type] ?? structure.structure_type}
                                </h4>
                              </div>
                              <span className="text-white/70 text-sm">{structure.age_in_years} years old</span>
                            </div>
                            <div className="ml-6 space-y-1">
                              {structure.estimated_replacement_cost && (
                                <p className="text-white/60 text-sm">
                                  Estimated replacement: ${structure.estimated_replacement_cost.toLocaleString()}
                                </p>
                              )}
                              {structure.forecasted_replacement_date && (
                                <p className="text-white/60 text-sm">
                                  Forecasted replacement: {new Date(structure.forecasted_replacement_date).toLocaleDateString()}
                                </p>
                              )}
                            </div>
                          </div>

                          {isExpanded && (
                            <div className="px-3 pb-3 ml-6 space-y-3 border-t border-white/10 pt-3">
                              {!isEditing ? (
                                <Button
                                  onClick={() => startEditingStructure(structure)}
                                  size="sm"
                                  variant="outline"
                                  className="bg-white/10 hover:bg-white/20 text-white border-white/30"
                                >
                                  <Edit className="h-4 w-4 mr-2" />
                                  Update
                                </Button>
                              ) : (
                                <div className="space-y-3">
                                  <div>
                                    <Label className="text-white/70 text-sm">Type</Label>
                                    <Input
                                      value={currentData.structure_type}
                                      onChange={(e) => updateStructureField(structure.id, 'structure_type', e.target.value)}
                                      className="bg-white/10 border-white/20 text-white"
                                    />
                                  </div>
                                  <div>
                                    <Label className="text-white/70 text-sm">Age (years)</Label>
                                    <Input
                                      type="number"
                                      value={currentData.age_in_years}
                                      onChange={(e) => updateStructureField(structure.id, 'age_in_years', parseInt(e.target.value) || 0)}
                                      className="bg-white/10 border-white/20 text-white"
                                    />
                                  </div>
                                  <div>
                                    <Label className="text-white/70 text-sm">Estimated Replacement Cost</Label>
                                    <Input
                                      type="number"
                                      value={currentData.estimated_replacement_cost || ''}
                                      onChange={(e) => updateStructureField(structure.id, 'estimated_replacement_cost', parseFloat(e.target.value) || 0)}
                                      className="bg-white/10 border-white/20 text-white"
                                    />
                                  </div>
                                  <div>
                                    <Label className="text-white/70 text-sm">Forecasted Replacement Date</Label>
                                    <Input
                                      type="date"
                                      value={formattedDate}
                                      onChange={(e) =>
                                        updateStructureField(
                                          structure.id,
                                          'forecasted_replacement_date',
                                          e.target.value
                                        )
                                      }
                                      className="bg-white/10 border-white/20 text-white"
                                    />
                                  </div>
                                  <div className="flex space-x-2">
                                    <Button
                                      onClick={() => cancelEditingStructure(structure.id)}
                                      size="sm"
                                      variant="outline"
                                      className="bg-white/10 hover:bg-white/20 text-white border-white/30"
                                    >
                                      <X className="h-4 w-4 mr-2" />
                                      Cancel
                                    </Button>
                                  </div>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Right Panel - Photo and Map */}
        <div className="w-1/2 bg-white/5 backdrop-blur-sm border-l border-white/20 flex flex-col">
          {/* Property Photo */}
          <div className="h-1/2 p-4">
            <Card className="bg-white/10 backdrop-blur-md border-white/20 h-full">
              <CardHeader>
                <CardTitle className="text-white flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Image className="h-5 w-5" />
                    <span>Property Photo</span>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    className="bg-white/10 hover:bg-white/20 text-white border-white/30"
                    onClick={() => {
                      const input = document.createElement('input');
                      input.type = 'file';
                      input.accept = 'image/*';
                      input.onchange = (event) => {
                        const target = event.target as HTMLInputElement;
                        const syntheticEvent = {
                          target,
                          currentTarget: target,
                        } as React.ChangeEvent<HTMLInputElement>;
                        handleImageUpload(syntheticEvent);
                      };
                      input.click();
                    }}
                    disabled={isUploading}
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    {isUploading ? 'Uploading...' : 'Upload'}
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent className="h-[calc(100%-4rem)] flex items-center justify-center">
                {isImageLoading ? (
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-2"></div>
                    <p className="text-white/70 text-sm">Loading image...</p>
                  </div>
                ) : imageUrl ? (
                  <div className="w-full h-full">
                    <img
                      src={imageUrl}
                      alt="Property"
                      className="w-full h-full object-cover rounded-lg"
                      onError={(e) => {
                          const target = e.target as HTMLImageElement;
                          console.error('Failed to load image', target.src);
                          setImageUrl(null);
                      }}
                    />
                  </div>
                ) : (
                  <div className="text-center">
                    <Image className="h-24 w-32 text-white/50 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-white mb-2">No Photo Available</h3>
                    <p className="text-white/70 text-sm">
                      Click "Upload" to add a property photo
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Map Section */}
          <div className="h-2/3 flex flex-col">
            {/* Auto-locate Button */}
            <div className="p-4 pb-2">
              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardContent className="p-4 mt-4">
                  <Button
                    onClick={() => property?.address && geocodeAddress(property.address)}
                    disabled={!property?.address || isGeocodingLoading}
                    className="w-full bg-white/20 hover:bg-white/30 text-white border-white/20"
                  >
                    {isGeocodingLoading ? 'Locating...' : 'Locate on Map'}
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Map Container */}
            <div className="flex-1 p-4 pt-2">
              <Card className="bg-white/10 backdrop-blur-md border-white/20 h-full">
                <CardHeader>
                  <CardTitle className="text-white flex items-center space-x-2">
                    <MapPin className="h-5 w-5" />
                    <span>Property Location</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="h-[calc(100%-4rem)]">
                  {coordinates ? (
                    <div className="h-full rounded-lg overflow-hidden">
                      <MapContainer
                        center={[coordinates.lat, coordinates.lng] as [number, number]}
                        zoom={15}
                        scrollWheelZoom={false}
                        style={{ height: '100%', width: '100%' }}
                      >
                        <TileLayer
                          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />
                        <Marker position={[coordinates.lat, coordinates.lng] as [number, number]}>
                          <Popup>
                            <div className="text-center">
                              <strong>{property.address}</strong>
                              <br />
                              Property #{property.id}
                            </div>
                          </Popup>
                        </Marker>
                      </MapContainer>
                    </div>
                  ) : (
                    <div className="h-full flex items-center justify-center text-center">
                      <div>
                        <MapPin className="h-16 w-16 text-white/50 mx-auto mb-4" />
                        <h3 className="text-lg font-semibold text-white mb-2">Find Property</h3>
                        <p className="text-white/70 text-sm mb-4">
                          Search for the geographic location of your property.
                        </p>
                        <p className="text-white/60 text-xs">
                          Address: {property.address || 'No address available'}
                        </p>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>

        {/* Right Panel - HomeBot Chat */}
        <div className="w-1/3 bg-white/5 backdrop-blur-sm border-l border-white/20 p-6">
          <HomeBot
            appliances={appliances}
            propertyId={property.id}
            onApplianceUpdate={(applianceType, newDate) => {
              // Update the appliances state with the new forecasted date
              setAppliances(prev => prev.map(appliance =>
                appliance.appliance_type === applianceType
                  ? { ...appliance, forecasted_replacement_date: newDate }
                  : appliance
              ));
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default PropertyDetail;

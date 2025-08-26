import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../lib/api';
import { Button } from '../components/ui/button';
import { Tabs, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Home, MapPin, Plus, Users, Calendar, DollarSign, AlertCircle, Edit3, Save, X, Eye, UserPlus, PhoneCall } from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import UserProfile from '../components/UserProfile';

interface Property {
  id: number;
  postal_code: string;
  address: string;
  age: number;
  created_at: string;
  user_id: number;
}

interface Tenant {
  id: number;
  first_name: string;
  last_name: string;
  phone_number?: string;
  current_rent: number;
  contract_duration_months: number;
  contract_start_date: string;
  contract_end_date: string;
  is_current: boolean;
  property_id: number;
  recommended_improvement_dates: string[];
}

interface Address {
  property_id: number;
  address: string;
}

const Dashboard = () => {
  const { user } = useAuth();
  const [properties, setProperties] = useState<Property[]>([]);
  const [tenants, setTenants] = useState<{ [propertyId: number]: Tenant[] }>({});
  const [addresses, setAddresses] = useState<Address[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingTenants, setIsLoadingTenants] = useState(false);
  const [activeTab, setActiveTab] = useState('properties');
  const [editingTenant, setEditingTenant] = useState<number | null>(null);
  const [editForm, setEditForm] = useState<Partial<Tenant>>({});
  const [showAddTenant, setShowAddTenant] = useState<number | null>(null);
  const [newTenantForm, setNewTenantForm] = useState<Partial<Tenant>>({});
  const navigate = useNavigate();

  useEffect(() => {
    fetchProperties();
  }, []);

  useEffect(() => {
    if (activeTab === 'tenants' && properties.length > 0) {
      fetchAllTenants();
      fetchAddresses();
    }
  }, [activeTab, properties]);

  const fetchAddresses = async () => {
    if (!user) return;

    try {
      const { data, error } = await apiClient.getPropertyAddresses(user.user_id);
      if (error) {
        console.error('Failed to fetch addresses:', error);
        toast.error('Failed to fetch addresses');
      } else {
        setAddresses(data || []);
      }
    } catch (error) {
      console.error('Error fetching addresses:', error);
      toast.error('Error fetching addresses');
    }
  };

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

  const fetchAllTenants = async () => {
    setIsLoadingTenants(true);
    const tenantData: { [propertyId: number]: Tenant[] } = {};

    try {
      await Promise.all(
        properties.map(async (property) => {
          try {
            const { data, error } = await apiClient.getPropertyTenants(property.id);
            if (error) {
              console.error(`Failed to fetch tenants for property ${property.id}:`, error);
              tenantData[property.id] = [];
            } else {
              tenantData[property.id] = data || [];
            }
          } catch (error) {
            console.error(`Error fetching tenants for property ${property.id}:`, error);
            tenantData[property.id] = [];
          }
        })
      );
      setTenants(tenantData);
    } catch (error) {
      console.error('Error fetching tenant data:', error);
      toast.error('Failed to load tenant information');
    } finally {
      setIsLoadingTenants(false);
    }
  };

  const updateTenant = async (tenantId: number, propertyId: number, updatedData: Partial<Tenant>) => {
    try {
      const { error } = await apiClient.updateTenant(propertyId, tenantId, updatedData);

      if (error) {
        console.error('Failed to update tenant:', error);
        toast.error('Failed to update tenant information');
      } else {
        toast.success('Tenant information updated successfully');
        // Refresh tenant data
        await fetchAllTenants();
        setEditingTenant(null);
        setEditForm({});
      }
    } catch (error) {
      console.error('Error updating tenant:', error);
      toast.error('Network error while updating tenant');
    }
  };

  const handleEditClick = (tenant: Tenant) => {
    setEditingTenant(tenant.id);
    setEditForm(tenant);
  };

  const handleSaveClick = () => {
    if (editingTenant && editForm.property_id) {
      updateTenant(editingTenant, editForm.property_id, editForm);
    }
  };

  const handleCancelEdit = () => {
    setEditingTenant(null);
    setEditForm({});
  };

  const handlePropertyClick = (propertyId: number) => {
    navigate(`/property/${propertyId}`);
  };

  const addTenant = async (propertyId: number, tenantData: Partial<Tenant>) => {
    try {
      const { error } = await apiClient.addTenant(propertyId, tenantData);

      if (error) {
        console.error('Failed to add tenant:', error);
        toast.error('Failed to add tenant');
      } else {
        toast.success('Tenant added successfully');
        await fetchAllTenants();
        setShowAddTenant(null);
        setNewTenantForm({});
      }
    } catch (error) {
      console.error('Error adding tenant:', error);
      toast.error('Network error while adding tenant');
    }
  };

  const handleAddTenant = (propertyId: number) => {
    const propertyTenants = tenants[propertyId] || [];
    const currentTenant = propertyTenants.find(t => t.is_current);

    if (currentTenant) {
      // If there's a current tenant, edit them instead
      setEditingTenant(currentTenant.id);
      setEditForm(currentTenant);
    } else {
      // If no current tenant, add a new one
      setShowAddTenant(propertyId);
      setNewTenantForm({ property_id: propertyId, is_current: true });
    }
  };

  const handleSaveNewTenant = () => {
    if (showAddTenant && newTenantForm.property_id) {
      addTenant(showAddTenant, newTenantForm);
    }
  };

  const handleCancelAddTenant = () => {
    setShowAddTenant(null);
    setNewTenantForm({});
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
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-3">
                <Home className="h-8 w-8 text-white" />
                <h1 className="text-xl font-bold text-white">Home Pulse AI Dashboard</h1>
              </div>

              {/* Tabs in Header */}
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="bg-white/10 backdrop-blur-md border-white/20">
                  <TabsTrigger
                    value="properties"
                    className="data-[state=active]:bg-white/20 data-[state=active]:text-white text-white/70 text-sm"
                  >
                    Properties
                  </TabsTrigger>
                  <TabsTrigger
                    value="tenants"
                    className="data-[state=active]:bg-white/20 data-[state=active]:text-white text-white/70 text-sm"
                  >
                    Tenants
                  </TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-white/80">
                Welcome, {user?.first_name || user?.email}
              </span>
              <UserProfile />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">Your Dashboard</h2>
          <p className="text-white/80">Manage your properties and tenant information.</p>
        </div>

        <div className="w-full">
          {activeTab === 'properties' && renderPropertyTab()}
          {activeTab === 'tenants' && renderTenantTab()}
        </div>
      </main>
    </div>
  );

  function renderPropertyTab() {
    return (
      <div>

      {properties.length === 0 ? (
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-8 text-center">
            <Home className="h-16 w-16 text-white/50 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">No Properties Found</h3>
            <p className="text-white/70 mb-4">You haven't added any properties yet.</p>
            <Button
              onClick={() => navigate('/properties')}
              className="bg-purple-800 text-primary hover:bg-purple/90"
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
                  <span>{property.address}</span>
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
                <div className="mt-4 text-center">
                  <span className="text-white/60 group-hover:text-white/80 transition-colors">
                    Click to view details →
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}

          {/* Add Property Card */}
          <Card
            className="bg-white/10 backdrop-blur-md border-white/20 hover:bg-white/20 transition-all duration-200 cursor-pointer group border-dashed"
            onClick={() => navigate('/properties')}
          >
            <CardContent className="p-6 flex flex-col items-center justify-center h-full min-h-[280px]">
              <div className="w-20 h-20 rounded-full bg-white/20 flex items-center justify-center mb-4 group-hover:bg-white/30 transition-colors">
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
      </div>
    );
  }

  function renderTenantTab() {
    if (isLoadingTenants) {
      return (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
        </div>
      );
    }

    if (properties.length === 0) {
      return (
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-8 text-center">
            <Users className="h-16 w-16 text-white/50 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">No Properties Found</h3>
            <p className="text-white/70 mb-4">Add properties first to view tenant information.</p>
            <Button
              onClick={() => navigate('/properties')}
              className="bg-white text-primary hover:bg-white/90"
            >
              Add Your First Property
            </Button>
          </CardContent>
        </Card>
      );
    }

    return (
      <div className="space-y-6">
        {/* Add Tenant for Properties without Tenants */}
        {addresses.filter(address => {
          // Only show properties where all tenants have is_current = false or no tenants exist
          const propertyTenants = tenants[address.property_id] || [];
          return propertyTenants.length === 0 || !propertyTenants.some(tenant => tenant.is_current);
        }).length > 0 && (
          <Card className="bg-white/10 backdrop-blur-md border-white/20 border-dashed">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <UserPlus className="h-5 w-5" />
                <span>Add Tenant to Property</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="property_select" className="text-white/70">Select Property Address</Label>
                  <Select onValueChange={(value) => setNewTenantForm({...newTenantForm, property_id: Number(value)})}>
                    <SelectTrigger className="bg-white/10 border-white/20 text-white">
                      <SelectValue placeholder="Choose a property address" />
                    </SelectTrigger>
                    <SelectContent className="bg-background border-border">
                      {addresses.filter(address => {
                        // Only show properties where all tenants have is_current = false or no tenants exist
                        const propertyTenants = tenants[address.property_id] || [];
                        return propertyTenants.length === 0 || !propertyTenants.some(tenant => tenant.is_current);
                      }).map((address) => (
                        <SelectItem key={address.property_id} value={address.property_id.toString()}>
                          {address.address}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {newTenantForm.property_id && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="new_first_name" className="text-white/70">First Name</Label>
                      <Input
                        id="new_first_name"
                        value={newTenantForm.first_name || ''}
                        onChange={(e) => setNewTenantForm({...newTenantForm, first_name: e.target.value})}
                        className="bg-white/10 border-white/20 text-white"
                      />
                    </div>
                      <div>
                        <Label htmlFor="new_last_name" className="text-white/70">Last Name</Label>
                        <Input
                          id="new_last_name"
                          value={newTenantForm.last_name || ''}
                          onChange={(e) => setNewTenantForm({...newTenantForm, last_name: e.target.value})}
                          className="bg-white/10 border-white/20 text-white"
                        />
                      </div>
                      <div>
                        <Label htmlFor="new_phone_number" className="text-white/70">Phone Number</Label>
                        <Input
                          id="new_phone_number"
                          value={newTenantForm.phone_number || ''}
                          onChange={(e) => setNewTenantForm({...newTenantForm, phone_number: e.target.value})}
                          className="bg-white/10 border-white/20 text-white"
                        />
                      </div>
                    <div>
                      <Label htmlFor="new_rent" className="text-white/70">Monthly Rent</Label>
                      <Input
                        id="new_rent"
                        type="number"
                        value={newTenantForm.current_rent || ''}
                        onChange={(e) => setNewTenantForm({...newTenantForm, current_rent: Number(e.target.value)})}
                        className="bg-white/10 border-white/20 text-white"
                      />
                    </div>
                    <div>
                      <Label htmlFor="new_duration" className="text-white/70">Contract Duration (months)</Label>
                      <Input
                        id="new_duration"
                        type="number"
                        value={newTenantForm.contract_duration_months || ''}
                        onChange={(e) => setNewTenantForm({...newTenantForm, contract_duration_months: Number(e.target.value)})}
                        className="bg-white/10 border-white/20 text-white"
                      />
                    </div>
                    <div>
                      <Label htmlFor="new_start_date" className="text-white/70">Contract Start Date</Label>
                      <Input
                        id="new_start_date"
                        type="date"
                        value={newTenantForm.contract_start_date?.split('T')[0] || ''}
                        onChange={(e) => setNewTenantForm({...newTenantForm, contract_start_date: e.target.value})}
                        className="bg-white/10 border-white/20 text-white"
                      />
                    </div>
                    <div>
                      <Label htmlFor="new_end_date" className="text-white/70">Contract End Date</Label>
                      <Input
                        id="new_end_date"
                        type="date"
                        value={newTenantForm.contract_end_date?.split('T')[0] || ''}
                        onChange={(e) => setNewTenantForm({...newTenantForm, contract_end_date: e.target.value})}
                        className="bg-white/10 border-white/20 text-white"
                      />
                    </div>
                  </div>
                )}

                {newTenantForm.property_id && (
                  <div className="flex space-x-2">
                    <Button
                      onClick={() => addTenant(newTenantForm.property_id!, newTenantForm)}
                      className="bg-green-600 hover:bg-green-700 text-white"
                    >
                      <Save className="h-4 w-4 mr-1" />
                      Add Tenant
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => setNewTenantForm({})}
                      className="bg-white/10 border-white/20 text-white hover:bg-white/20"
                    >
                      <X className="h-4 w-4 mr-1" />
                      Clear
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {properties
          .sort((a, b) => {
            // Sort properties by tenant contract end date
            const aTenantsWithCurrent = tenants[a.id] || [];
            const bTenantsWithCurrent = tenants[b.id] || [];
            const aCurrentTenant = aTenantsWithCurrent.find(t => t.is_current);
            const bCurrentTenant = bTenantsWithCurrent.find(t => t.is_current);

            // Properties with tenants with end dates first, then those without
            if (aCurrentTenant && aCurrentTenant.contract_end_date && bCurrentTenant && bCurrentTenant.contract_end_date) {
              return new Date(aCurrentTenant.contract_end_date).getTime() - new Date(bCurrentTenant.contract_end_date).getTime();
            }
            if (aCurrentTenant && aCurrentTenant.contract_end_date && (!bCurrentTenant || !bCurrentTenant.contract_end_date)) {
              return -1;
            }
            if ((!aCurrentTenant || !aCurrentTenant.contract_end_date) && bCurrentTenant && bCurrentTenant.contract_end_date) {
              return 1;
            }
            return 0;
          })
          .map((property) => {
          const propertyTenants = tenants[property.id] || [];
          const currentTenant = propertyTenants.find(t => t.is_current);
          const previousTenants = propertyTenants.filter(t => !t.is_current);

          return (
            <Card key={property.id} className="bg-white/10 backdrop-blur-md border-white/20">
              <CardHeader>
                <CardTitle className="text-white flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <MapPin className="h-5 w-5" />
                    <span>{property.address}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleAddTenant(property.id)}
                      className="bg-white/10 border-white/20 text-white hover:bg-white/20"
                    >
                      <UserPlus className="h-4 w-4 mr-1" />
                      {currentTenant ? 'Update Tenant' : 'Add Tenant'}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handlePropertyClick(property.id)}
                      className="bg-white/10 border-white/20 text-white hover:bg-white/20"
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      View Property
                    </Button>
                    {!currentTenant && (
                      <div className="flex items-center space-x-2 text-orange-400">
                        <AlertCircle className="h-5 w-5" />
                        <span className="text-sm">Vacant</span>
                      </div>
                    )}
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {showAddTenant === property.id && (
                  <div className="mb-6 p-4 bg-white/5 rounded-lg border border-white/10">
                    <h4 className="text-white font-medium mb-4">Add New Tenant</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="add_first_name" className="text-white/70">First Name</Label>
                        <Input
                          id="add_first_name"
                          value={newTenantForm.first_name || ''}
                          onChange={(e) => setNewTenantForm({...newTenantForm, first_name: e.target.value})}
                          className="bg-white/10 border-white/20 text-white"
                        />
                      </div>
                        <div>
                          <Label htmlFor="add_last_name" className="text-white/70">Last Name</Label>
                          <Input
                            id="add_last_name"
                            value={newTenantForm.last_name || ''}
                            onChange={(e) => setNewTenantForm({...newTenantForm, last_name: e.target.value})}
                            className="bg-white/10 border-white/20 text-white"
                          />
                        </div>
                        <div>
                          <Label htmlFor="add_phone_number" className="text-white/70">Phone Number</Label>
                          <Input
                            id="add_phone_number"
                            value={newTenantForm.phone_number || ''}
                            onChange={(e) => setNewTenantForm({...newTenantForm, phone_number: e.target.value})}
                            className="bg-white/10 border-white/20 text-white"
                          />
                        </div>
                      <div>
                        <Label htmlFor="add_rent" className="text-white/70">Monthly Rent</Label>
                        <Input
                          id="add_rent"
                          type="number"
                          value={newTenantForm.current_rent || ''}
                          onChange={(e) => setNewTenantForm({...newTenantForm, current_rent: Number(e.target.value)})}
                          className="bg-white/10 border-white/20 text-white"
                        />
                      </div>
                      <div>
                        <Label htmlFor="add_duration" className="text-white/70">Contract Duration (months)</Label>
                        <Input
                          id="add_duration"
                          type="number"
                          value={newTenantForm.contract_duration_months || ''}
                          onChange={(e) => setNewTenantForm({...newTenantForm, contract_duration_months: Number(e.target.value)})}
                          className="bg-white/10 border-white/20 text-white"
                        />
                      </div>
                      <div>
                        <Label htmlFor="add_start_date" className="text-white/70">Contract Start Date</Label>
                        <Input
                          id="add_start_date"
                          type="date"
                          value={newTenantForm.contract_start_date?.split('T')[0] || ''}
                          onChange={(e) => setNewTenantForm({...newTenantForm, contract_start_date: e.target.value})}
                          className="bg-white/10 border-white/20 text-white"
                        />
                      </div>
                      <div>
                        <Label htmlFor="add_end_date" className="text-white/70">Contract End Date</Label>
                        <Input
                          id="add_end_date"
                          type="date"
                          value={newTenantForm.contract_end_date?.split('T')[0] || ''}
                          onChange={(e) => setNewTenantForm({...newTenantForm, contract_end_date: e.target.value})}
                          className="bg-white/10 border-white/20 text-white"
                        />
                      </div>
                    </div>
                    <div className="flex space-x-2 mt-4">
                      <Button
                        onClick={handleSaveNewTenant}
                        className="bg-green-600 hover:bg-green-700 text-white"
                      >
                        <Save className="h-4 w-4 mr-1" />
                        Save Tenant
                      </Button>
                      <Button
                        variant="outline"
                        onClick={handleCancelAddTenant}
                        className="bg-white/10 border-white/20 text-white hover:bg-white/20"
                      >
                        <X className="h-4 w-4 mr-1" />
                        Cancel
                      </Button>
                    </div>
                  </div>
                )}

                {currentTenant ? (
                  <div className="space-y-4">
                    <div className="flex justify-end mb-4">
                      {editingTenant === currentTenant.id ? (
                        <div className="flex space-x-2">
                          <Button
                            size="sm"
                            onClick={handleSaveClick}
                            className="bg-green-600 hover:bg-green-700 text-white"
                          >
                            <Save className="h-4 w-4 mr-1" />
                            Save
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={handleCancelEdit}
                            className="bg-white/10 border-white/20 text-white hover:bg-white/20"
                          >
                            <X className="h-4 w-4 mr-1" />
                            Cancel
                          </Button>
                        </div>
                      ) : (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleEditClick(currentTenant)}
                          className="bg-white/10 border-white/20 text-white hover:bg-white/20"
                        >
                          <Edit3 className="h-4 w-4 mr-1" />
                          Edit
                        </Button>
                      )}
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2 text-white/70">
                          <Users className="h-4 w-4" />
                          <span className="text-sm">Current Tenant</span>
                        </div>
                        {editingTenant === currentTenant.id ? (
                          <div className="grid grid-cols-2 gap-2">
                            <div>
                              <Label htmlFor="first_name" className="text-white/70 text-xs">First Name</Label>
                              <Input
                                id="first_name"
                                value={editForm.first_name || ''}
                                onChange={(e) => setEditForm({...editForm, first_name: e.target.value})}
                                className="bg-white/10 border-white/20 text-white text-sm h-8"
                              />
                            </div>
                            <div>
                              <Label htmlFor="last_name" className="text-white/70 text-xs">Last Name</Label>
                              <Input
                                id="last_name"
                                value={editForm.last_name || ''}
                                onChange={(e) => setEditForm({...editForm, last_name: e.target.value})}
                                className="bg-white/10 border-white/20 text-white text-sm h-8"
                              />
                            </div>
                          </div>
                        ) : (
                          <p className="text-white font-medium">
                            {currentTenant.first_name} {currentTenant.last_name}
                          </p>
                        )}
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2 text-white/70">
                          <PhoneCall className="h-4 w-4" />
                          <span className="text-sm">Phone Number</span>
                        </div>
                        {editingTenant === currentTenant.id ? (
                          <div>
                            <Label htmlFor="phone_number" className="text-white/70 text-xs">Phone Number</Label>
                            <Input
                              id="phone_number"
                              value={editForm.phone_number || ''}
                              onChange={(e) => setEditForm({...editForm, phone_number: e.target.value})}
                              className="bg-white/10 border-white/20 text-white text-sm h-8"
                            />
                          </div>
                        ) : (
                          <p className="text-white font-medium">
                            {currentTenant.phone_number || 'N/A'}
                          </p>
                        )}
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2 text-white/70">
                          <DollarSign className="h-4 w-4" />
                          <span className="text-sm">Monthly Rent</span>
                        </div>
                        {editingTenant === currentTenant.id ? (
                          <div>
                            <Label htmlFor="current_rent" className="text-white/70 text-xs">Monthly Rent</Label>
                            <Input
                              id="current_rent"
                              type="number"
                              value={editForm.current_rent || ''}
                              onChange={(e) => setEditForm({...editForm, current_rent: Number(e.target.value)})}
                              className="bg-white/10 border-white/20 text-white text-sm h-8"
                            />
                          </div>
                        ) : (
                          <p className="text-white font-medium">
                            ${currentTenant.current_rent?.toLocaleString() || 'N/A'}
                          </p>
                        )}
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2 text-white/70">
                          <Calendar className="h-4 w-4" />
                          <span className="text-sm">Contract Duration</span>
                        </div>
                        {editingTenant === currentTenant.id ? (
                          <div>
                            <Label htmlFor="contract_duration" className="text-white/70 text-xs">Contract Duration (months)</Label>
                            <Input
                              id="contract_duration"
                              type="number"
                              value={editForm.contract_duration_months || ''}
                              onChange={(e) => setEditForm({...editForm, contract_duration_months: Number(e.target.value)})}
                              className="bg-white/10 border-white/20 text-white text-sm h-8"
                            />
                          </div>
                        ) : (
                          <p className="text-white font-medium">
                            {currentTenant.contract_duration_months} months
                          </p>
                        )}
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2 text-white/70">
                          <Calendar className="h-4 w-4" />
                          <span className="text-sm">Contract Ends</span>
                        </div>
                        {editingTenant === currentTenant.id ? (
                          <div>
                            <Label htmlFor="contract_end_date" className="text-white/70 text-xs">Contract End Date</Label>
                            <Input
                              id="contract_end_date"
                              type="date"
                              value={editForm.contract_end_date?.split('T')[0] || ''}
                              onChange={(e) => setEditForm({...editForm, contract_end_date: e.target.value})}
                              className="bg-white/10 border-white/20 text-white text-sm h-8"
                            />
                          </div>
                        ) : (
                          <p className="text-white font-medium">
                            {new Date(currentTenant.contract_end_date).toLocaleDateString()}
                          </p>
                        )}
                      </div>
                    </div>

                    {currentTenant.recommended_improvement_dates && currentTenant.recommended_improvement_dates.length > 0 && (
                      <div className="mt-4 p-4 bg-white/5 rounded-lg">
                        <h4 className="text-white font-medium mb-2">Recommended Improvement Dates</h4>
                        <div className="space-y-1">
                          {currentTenant.recommended_improvement_dates.map((date, index) => (
                            <p key={index} className="text-white/70 text-sm">
                              • {new Date(date).toLocaleDateString()}
                            </p>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="bg-orange-400/10 border border-orange-400/20 rounded-lg p-4">
                      <div className="flex items-center space-x-2 mb-2">
                        <AlertCircle className="h-5 w-5 text-orange-400" />
                        <span className="text-orange-400 font-medium">Property Currently Vacant</span>
                      </div>
                      <p className="text-white/70 text-sm">This property does not have a current tenant.</p>
                    </div>

                    {previousTenants.length > 0 && (
                      <div className="space-y-2">
                        <h4 className="text-white font-medium">Previous Tenants</h4>
                        <div className="space-y-2">
                          {previousTenants.map((tenant) => (
                            <div key={tenant.id} className="bg-white/5 rounded-lg p-3">
                              <div className="flex justify-between items-center">
                                <span className="text-white">
                                  {tenant.first_name} {tenant.last_name}
                                </span>
                                <span className="text-white/70 text-sm">
                                  Ended: {new Date(tenant.contract_end_date).toLocaleDateString()}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
    );
  }
};

export default Dashboard;

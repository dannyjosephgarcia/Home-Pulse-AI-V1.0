import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, Plus, Trash2, ArrowLeft, Loader2, Calendar } from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../lib/api';

interface Appliance {
  name: string;
  age: number;
}

interface Structure {
  name: string;
  age: number;
}

interface Property {
  postalCode: string;
  homeAge: number;
  homeAddress: string;
  appliances: Appliance[];
  structures: Structure[];
}

const Properties = () => {
  const [properties, setProperties] = useState<Property[]>([
    {
      postalCode: '',
      homeAge: 0,
      homeAddress: '',
      appliances: [
        { name: 'Stove', age: 0 },
        { name: 'Dishwasher', age: 0 },
        { name: 'Dryer', age: 0 },
        { name: 'Refrigerator', age: 0 },
        { name: 'Washer', age: 0 },
      ],
      structures: [
        { name: 'Roof', age: 0 },
        { name: 'Driveway', age: 0 },
        { name: 'Water Heater', age: 0 },
        { name: 'Furnace', age: 0 },
        { name: 'A/C Unit', age: 0 },
      ]
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();

  const addProperty = () => {
    setProperties([...properties, {
      postalCode: '',
      homeAge: 0,
      homeAddress: '',
      appliances: [
        { name: 'Stove', age: 0 },
        { name: 'Dishwasher', age: 0 },
        { name: 'Dryer', age: 0 },
        { name: 'Refrigerator', age: 0 },
        { name: 'Washer', age: 0 },
      ],
      structures: [
        { name: 'Roof', age: 0 },
        { name: 'Driveway', age: 0 },
        { name: 'Water Heater', age: 0 },
        { name: 'Furnace', age: 0 },
        { name: 'A/C Unit', age: 0 },
      ]
    }]);
  };

  const removeProperty = (index: number) => {
    if (properties.length > 1) {
      setProperties(properties.filter((_, i) => i !== index));
    }
  };

  const updateProperty = (index: number, field: keyof Property, value: any) => {
    const updated = [...properties];
    updated[index] = { ...updated[index], [field]: value };
    setProperties(updated);
  };

  const updateAppliance = (propertyIndex: number, applianceIndex: number, age: number) => {
    const updated = [...properties];
    updated[propertyIndex].appliances[applianceIndex].age = age;
    setProperties(updated);
  };

  const updateStructure = (propertyIndex: number, structureIndex: number, age: number) => {
    const updated = [...properties];
    updated[propertyIndex].structures[structureIndex].age = age;
    setProperties(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate all properties
    for (let i = 0; i < properties.length; i++) {
      const property = properties[i];
      if (!property.postalCode.trim()) {
        toast({
          title: "Error",
          description: `Please fill in postal code for property ${i + 1}`,
          variant: "destructive",
        });
        return;
      }
      if (property.homeAge <= 0) {
        toast({
          title: "Error",
          description: `Please enter a valid home age for property ${i + 1}`,
          variant: "destructive",
        });
        return;
      }
    }

    setIsLoading(true);

    try {
      // Format as array of property hashmaps
      const payload = properties.map(property => ({
        postalCode: property.postalCode.trim(),
        homeAge: property.homeAge,
        homeAddress: property.homeAddress,
        appliances: property.appliances.reduce((acc, appliance) => {
          acc[appliance.name.toLowerCase()] = appliance.age;
          return acc;
        }, {} as Record<string, number>),
        structures: property.structures.reduce((acc, structure) => {
            acc[structure.name.toLowerCase()] = structure.age;
            return acc;
        }, {} as Record<string, number>)
      }));

      const { data, error } = await apiClient.submitProperties(payload);

      if (!error) {
        toast({
          title: "Properties Submitted Successfully!",
          description: `${properties.length} property(ies) have been added to your portfolio.`,
        });
        navigate('/dashboard');
      } else {
        const errorData = await response.text();
        toast({
          title: "Submission Failed",
          description: error.message || 'Please try again later',
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Network Error",
        description: "Unable to connect to the server. Please try again later.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 relative overflow-hidden">
      {/* Background Elements */}
      <div className="fixed inset-0 opacity-20">
        <div className="absolute w-96 h-96 bg-blue-500/10 rounded-full blur-3xl top-20 left-10" />
        <div className="absolute w-80 h-80 bg-purple-500/10 rounded-full blur-3xl bottom-20 right-15" />
      </div>

      {/* Navigation */}
      <nav className="relative z-10 flex items-center justify-between p-6">
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 text-white/80 hover:text-white transition-colors"
        >
          <ArrowLeft size={20} />
          Back to Dashboard
        </button>
      </nav>

      {/* Main Content */}
      <div className="relative z-10 px-4 pb-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-white mb-2">
              Property Portfolio
            </h1>
            <p className="text-white/80 text-lg">
              Add your investment properties along with appliance and structure details
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-8">
            {properties.map((property, propertyIndex) => (
              <div key={propertyIndex} className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
                {/* Property Header */}
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <Home className="text-white/80" size={24} />
                    <h2 className="text-xl font-semibold text-white">
                      Property {propertyIndex + 1}
                    </h2>
                  </div>
                  {properties.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeProperty(propertyIndex)}
                      className="text-red-400 hover:text-red-300 transition-colors p-2"
                    >
                      <Trash2 size={20} />
                    </button>
                  )}
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  {/* Postal Code */}
                  <div className="space-y-2">
                    <label className="text-white/90 text-sm font-medium">
                      Postal Code
                    </label>
                    <input
                      type="text"
                      value={property.postalCode}
                      onChange={(e) => updateProperty(propertyIndex, 'postalCode', e.target.value)}
                      className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                      placeholder="Enter postal code"
                      disabled={isLoading}
                    />
                  </div>

                  {/* Home Age */}
                  <div className="space-y-2">
                    <label className="text-white/90 text-sm font-medium">
                      Home Age (years)
                    </label>
                    <div className="relative">
                      <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/60" size={20} />
                      <input
                        type="number"
                        min="0"
                        value={property.homeAge || ''}
                        onChange={(e) => updateProperty(propertyIndex, 'homeAge', parseInt(e.target.value) || 0)}
                        className="w-full pl-12 pr-4 py-3 bg-white/10 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                        placeholder="Age in years"
                        disabled={isLoading}
                      />
                    </div>
                  </div>

                  {/* Home Address */}
                    <div className="space-y-2 md:col-span-2">
                      <label className="text-white/90 text-sm font-medium">
                        Home Address
                      </label>
                      <input
                        type="text"
                        value={property.homeAddress || ""}
                        onChange={(e) => updateProperty(propertyIndex, 'homeAddress', e.target.value)}
                        className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                        placeholder="123 Main St, City, State"
                        disabled={isLoading}
                      />
                    </div>
                </div>

                {/* Appliances */}
                <div className="mt-6">
                  <h3 className="text-lg font-medium text-white mb-4">Appliances</h3>
                  <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {property.appliances.map((appliance, applianceIndex) => (
                      <div key={applianceIndex} className="space-y-2">
                        <label className="text-white/90 text-sm font-medium">
                          {appliance.name} Age (years)
                        </label>
                        <input
                          type="number"
                          min="0"
                          value={appliance.age || ''}
                          onChange={(e) => updateAppliance(propertyIndex, applianceIndex, parseInt(e.target.value) || 0)}
                          className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                          placeholder="Age in years"
                          disabled={isLoading}
                        />
                      </div>
                    ))}
                  </div>
                </div>

                {/* Structure */}
                <div className="mt-6">
                  <h3 className="text-lg font-medium text-white mb-4">Structures</h3>
                  <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {property.structures.map((structure, structureIndex) => (
                      <div key={structureIndex} className="space-y-2">
                        <label className="text-white/90 text-sm font-medium">
                          {structure.name} Age (years)
                        </label>
                        <input
                          type="number"
                          min="0"
                          value={structure.age || ''}
                          onChange={(e) => updateStructure(propertyIndex, structureIndex, parseInt(e.target.value) || 0)}
                          className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                          placeholder="Age in years"
                          disabled={isLoading}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}

            {/* Add Property Button */}
            <div className="text-center">
              <button
                type="button"
                onClick={addProperty}
                className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-md text-white px-6 py-3 rounded-xl border border-white/30 hover:bg-white/20 transition-all duration-200"
                disabled={isLoading}
              >
                <Plus size={20} />
                Add Another Property
              </button>
            </div>

            {/* Submit Button */}
            <div className="text-center">
              <button
                type="submit"
                disabled={isLoading}
                className="bg-gradient-to-r from-blue-500 to-purple-600 text-white py-4 px-8 rounded-xl font-semibold hover:from-blue-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 focus:ring-offset-transparent transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mx-auto"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="animate-spin" size={20} />
                    Submitting Properties...
                  </>
                ) : (
                  `Submit ${properties.length} Homes`
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Properties;

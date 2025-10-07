import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, Plus, Trash2, ArrowLeft, Loader2, Calendar, Upload, FileText } from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import { apiClient } from '../lib/api';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';

interface Appliance {
  name: string;
  age: number;
  brand?: string;
  model?: string;
}

interface Structure {
  name: string;
  age: number;
}

interface Unit {
  unitNumber: string;
  appliances: Appliance[];
}

interface Property {
  street: string;
  city: string;
  state: string;
  zip: string;
  homeAge: number;
  isMultifamily: boolean;
  structures: Structure[];
  units?: Unit[];
  appliances?: Appliance[];
}

const AVAILABLE_APPLIANCES = ['Stove', 'Dishwasher', 'Dryer', 'Refrigerator', 'Washer', 'A/C Unit', 'Water Heater'];
const AVAILABLE_STRUCTURES = ['Roof', 'Driveway', 'Furnace'];

const US_STATES = [
  { value: 'AL', label: 'AL' }, { value: 'AK', label: 'AK' }, { value: 'AZ', label: 'AZ' }, { value: 'AR', label: 'AR' },
  { value: 'CA', label: 'CA' }, { value: 'CO', label: 'CO' }, { value: 'CT', label: 'CT' }, { value: 'DE', label: 'DE' },
  { value: 'FL', label: 'FL' }, { value: 'GA', label: 'GA' }, { value: 'HI', label: 'HI' }, { value: 'ID', label: 'ID' },
  { value: 'IL', label: 'IL' }, { value: 'IN', label: 'IN' }, { value: 'IA', label: 'IA' }, { value: 'KS', label: 'KS' },
  { value: 'KY', label: 'KY' }, { value: 'LA', label: 'LA' }, { value: 'ME', label: 'ME' }, { value: 'MD', label: 'MD' },
  { value: 'MA', label: 'MA' }, { value: 'MI', label: 'MI' }, { value: 'MN', label: 'MN' }, { value: 'MS', label: 'MS' },
  { value: 'MO', label: 'MO' }, { value: 'MT', label: 'MT' }, { value: 'NE', label: 'NE' }, { value: 'NV', label: 'NV' },
  { value: 'NH', label: 'NH' }, { value: 'NJ', label: 'NJ' }, { value: 'NM', label: 'NM' }, { value: 'NY', label: 'NY' },
  { value: 'NC', label: 'NC' }, { value: 'ND', label: 'ND' }, { value: 'OH', label: 'OH' }, { value: 'OK', label: 'OK' },
  { value: 'OR', label: 'OR' }, { value: 'PA', label: 'PA' }, { value: 'RI', label: 'RI' }, { value: 'SC', label: 'SC' },
  { value: 'SD', label: 'SD' }, { value: 'TN', label: 'TN' }, { value: 'TX', label: 'TX' }, { value: 'UT', label: 'UT' },
  { value: 'VT', label: 'VT' }, { value: 'VA', label: 'VA' }, { value: 'WA', label: 'WA' }, { value: 'WV', label: 'WV' },
  { value: 'WI', label: 'WI' }, { value: 'WY', label: 'WY' }
];

const Properties = () => {
  const [properties, setProperties] = useState<Property[]>([
    {
      street: '',
      city: '',
      state: '',
      zip: '',
      homeAge: 0,
      isMultifamily: false,
      appliances: [],
      structures: []
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadMode, setUploadMode] = useState<'form' | 'csv'>('form');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const { toast } = useToast();

  const addProperty = () => {
    setProperties([...properties, {
      street: '',
      city: '',
      state: '',
      zip: '',
      homeAge: 0,
      isMultifamily: false,
      appliances: [],
      structures: []
    }]);
  };

  const removeProperty = (index: number) => {
    if (properties.length > 1) {
      setProperties(properties.filter((_, i) => i !== index));
    }
  };

  const updateProperty = (index: number, field: keyof Property, value: any) => {
    const updated = [...properties];

    // Handle multifamily toggle
    if (field === 'isMultifamily') {
      if (value) {
        // Switching to multifamily: move appliances to first unit
        updated[index] = {
          ...updated[index],
          isMultifamily: true,
          units: [{
            unitNumber: '',
            appliances: updated[index].appliances || []
          }],
          appliances: undefined
        };
      } else {
        // Switching to single-family: move first unit's appliances to property level
        const firstUnitAppliances = updated[index].units?.[0]?.appliances || [];
        updated[index] = {
          ...updated[index],
          isMultifamily: false,
          appliances: firstUnitAppliances,
          units: undefined
        };
      }
    } else {
      updated[index] = { ...updated[index], [field]: value };
    }

    setProperties(updated);
  };

  const addAppliance = (propertyIndex: number) => {
    const updated = [...properties];
    if (!updated[propertyIndex].appliances) {
      updated[propertyIndex].appliances = [];
    }
    updated[propertyIndex].appliances!.push({ name: '', age: 0, brand: '', model: '' });
    setProperties(updated);
  };

  const removeAppliance = (propertyIndex: number, applianceIndex: number) => {
    const updated = [...properties];
    if (updated[propertyIndex].appliances) {
      updated[propertyIndex].appliances = updated[propertyIndex].appliances!.filter((_, i) => i !== applianceIndex);
    }
    setProperties(updated);
  };

  const updateApplianceName = (propertyIndex: number, applianceIndex: number, name: string) => {
    const updated = [...properties];
    if (updated[propertyIndex].appliances) {
      updated[propertyIndex].appliances![applianceIndex].name = name;
    }
    setProperties(updated);
  };

  const updateApplianceAge = (propertyIndex: number, applianceIndex: number, age: number) => {
    const updated = [...properties];
    if (updated[propertyIndex].appliances) {
      updated[propertyIndex].appliances![applianceIndex].age = age;
    }
    setProperties(updated);
  };

  const updateApplianceBrand = (propertyIndex: number, applianceIndex: number, brand: string) => {
    const updated = [...properties];
    if (updated[propertyIndex].appliances) {
      updated[propertyIndex].appliances![applianceIndex].brand = brand;
    }
    setProperties(updated);
  };

  const updateApplianceModel = (propertyIndex: number, applianceIndex: number, model: string) => {
    const updated = [...properties];
    if (updated[propertyIndex].appliances) {
      updated[propertyIndex].appliances![applianceIndex].model = model;
    }
    setProperties(updated);
  };

  const addStructure = (propertyIndex: number) => {
    const updated = [...properties];
    updated[propertyIndex].structures.push({ name: '', age: 0 });
    setProperties(updated);
  };

  const removeStructure = (propertyIndex: number, structureIndex: number) => {
    const updated = [...properties];
    updated[propertyIndex].structures = updated[propertyIndex].structures.filter((_, i) => i !== structureIndex);
    setProperties(updated);
  };

  const updateStructureName = (propertyIndex: number, structureIndex: number, name: string) => {
    const updated = [...properties];
    updated[propertyIndex].structures[structureIndex].name = name;
    setProperties(updated);
  };

  const updateStructureAge = (propertyIndex: number, structureIndex: number, age: number) => {
    const updated = [...properties];
    updated[propertyIndex].structures[structureIndex].age = age;
    setProperties(updated);
  };

  // Unit management functions
  const addUnit = (propertyIndex: number) => {
    const updated = [...properties];
    if (!updated[propertyIndex].units) {
      updated[propertyIndex].units = [];
    }
    updated[propertyIndex].units!.push({ unitNumber: '', appliances: [] });
    setProperties(updated);
  };

  const removeUnit = (propertyIndex: number, unitIndex: number) => {
    const updated = [...properties];
    if (updated[propertyIndex].units && updated[propertyIndex].units!.length > 1) {
      updated[propertyIndex].units = updated[propertyIndex].units!.filter((_, i) => i !== unitIndex);
      setProperties(updated);
    }
  };

  const updateUnitNumber = (propertyIndex: number, unitIndex: number, unitNumber: string) => {
    const updated = [...properties];
    if (updated[propertyIndex].units) {
      updated[propertyIndex].units![unitIndex].unitNumber = unitNumber;
      setProperties(updated);
    }
  };

  const addUnitAppliance = (propertyIndex: number, unitIndex: number) => {
    const updated = [...properties];
    if (updated[propertyIndex].units) {
      updated[propertyIndex].units![unitIndex].appliances.push({ name: '', age: 0, brand: '', model: '' });
      setProperties(updated);
    }
  };

  const removeUnitAppliance = (propertyIndex: number, unitIndex: number, applianceIndex: number) => {
    const updated = [...properties];
    if (updated[propertyIndex].units) {
      updated[propertyIndex].units![unitIndex].appliances = updated[propertyIndex].units![unitIndex].appliances.filter((_, i) => i !== applianceIndex);
      setProperties(updated);
    }
  };

  const updateUnitApplianceName = (propertyIndex: number, unitIndex: number, applianceIndex: number, name: string) => {
    const updated = [...properties];
    if (updated[propertyIndex].units) {
      updated[propertyIndex].units![unitIndex].appliances[applianceIndex].name = name;
      setProperties(updated);
    }
  };

  const updateUnitApplianceAge = (propertyIndex: number, unitIndex: number, applianceIndex: number, age: number) => {
    const updated = [...properties];
    if (updated[propertyIndex].units) {
      updated[propertyIndex].units![unitIndex].appliances[applianceIndex].age = age;
      setProperties(updated);
    }
  };

  const updateUnitApplianceBrand = (propertyIndex: number, unitIndex: number, applianceIndex: number, brand: string) => {
    const updated = [...properties];
    if (updated[propertyIndex].units) {
      updated[propertyIndex].units![unitIndex].appliances[applianceIndex].brand = brand;
      setProperties(updated);
    }
  };

  const updateUnitApplianceModel = (propertyIndex: number, unitIndex: number, applianceIndex: number, model: string) => {
    const updated = [...properties];
    if (updated[propertyIndex].units) {
      updated[propertyIndex].units![unitIndex].appliances[applianceIndex].model = model;
      setProperties(updated);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate all properties
    for (let i = 0; i < properties.length; i++) {
      const property = properties[i];
      if (!property.street.trim() || !property.city.trim() || !property.state.trim() || !property.zip.trim()) {
        toast({
          title: "Error",
          description: `Please fill in all address fields for property ${i + 1}`,
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

      // Validate multifamily properties have at least one unit with a unit number
      if (property.isMultifamily) {
        if (!property.units || property.units.length === 0) {
          toast({
            title: "Error",
            description: `Multifamily property ${i + 1} must have at least one unit`,
            variant: "destructive",
          });
          return;
        }

        const hasValidUnit = property.units.some(unit => unit.unitNumber.trim());
        if (!hasValidUnit) {
          toast({
            title: "Error",
            description: `Please provide at least one unit number for property ${i + 1}`,
            variant: "destructive",
          });
          return;
        }
      }
    }

    setIsLoading(true);

    try {
      // Format as array of property hashmaps
      const payload = properties.map(property => {
        const basePayload = {
          street: property.street.trim(),
          city: property.city.trim(),
          state: property.state.trim(),
          zip: property.zip.trim(),
          homeAge: property.homeAge,
          isMultifamily: property.isMultifamily,
          structures: property.structures.reduce((acc, structure) => {
            if (structure.name) {
              acc[structure.name.toLowerCase()] = structure.age;
            }
            return acc;
          }, {} as Record<string, number>)
        };

        if (property.isMultifamily && property.units) {
          // Multifamily: include units array with appliances per unit
          return {
            ...basePayload,
            units: property.units
              .filter(unit => unit.unitNumber.trim())
              .map(unit => ({
                unitNumber: unit.unitNumber.trim(),
                appliances: unit.appliances.reduce((acc, appliance) => {
                  if (appliance.name) {
                    acc[appliance.name.toLowerCase()] = {
                      age: appliance.age,
                      ...(appliance.brand && { brand: appliance.brand.trim() }),
                      ...(appliance.model && { model: appliance.model.trim() })
                    };
                  }
                  return acc;
                }, {} as Record<string, any>)
              }))
          };
        } else {
          // Single-family: appliances at property level
          return {
            ...basePayload,
            appliances: (property.appliances || []).reduce((acc, appliance) => {
              if (appliance.name) {
                acc[appliance.name.toLowerCase()] = {
                  age: appliance.age,
                  ...(appliance.brand && { brand: appliance.brand.trim() }),
                  ...(appliance.model && { model: appliance.model.trim() })
                };
              }
              return acc;
            }, {} as Record<string, any>)
          };
        }
      });

      const {  data: _data, error } = await apiClient.submitProperties(payload);

      if (!error) {
        toast({
          title: "Properties Submitted Successfully!",
          description: `${properties.length} property(ies) have been added to your portfolio.`,
        });
        navigate('/dashboard');
      } else {
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

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.csv')) {
      toast({
        title: "Invalid File Type",
        description: "Please select a CSV file (.csv)",
        variant: "destructive",
      });
      return;
    }

    // Validate file size (under 2MB)
    const MAX_SIZE = 2 * 1024 * 1024; // 2MB in bytes
    if (file.size > MAX_SIZE) {
      toast({
        title: "File Too Large",
        description: "Please select a file smaller than 2MB",
        variant: "destructive",
      });
      return;
    }

    setSelectedFile(file);
  };

  const handleCsvUpload = async () => {
    if (!selectedFile) {
      toast({
        title: "No File Selected",
        description: "Please select a CSV file to upload",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      const { error } = await apiClient.csvBulkUpload(selectedFile);

      if (!error) {
        toast({
          title: "CSV Upload Successful!",
          description: "Your properties have been imported successfully.",
        });
        navigate('/dashboard');
      } else {
        toast({
          title: "CSV Upload Failed",
          description: "There was an issue with your CSV file upload. Please check the template and try again.",
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

          {/* Upload Mode Toggle */}
          <div className="flex justify-center mb-8">
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-1 border border-white/20">
              <button
                onClick={() => setUploadMode('form')}
                className={`px-6 py-2 rounded-lg transition-all duration-200 ${
                  uploadMode === 'form'
                    ? 'bg-white/20 text-white shadow-lg'
                    : 'text-white/70 hover:text-white'
                }`}
              >
                Manual Entry
              </button>
              <button
                onClick={() => setUploadMode('csv')}
                className={`px-6 py-2 rounded-lg transition-all duration-200 ${
                  uploadMode === 'csv'
                    ? 'bg-white/20 text-white shadow-lg'
                    : 'text-white/70 hover:text-white'
                }`}
              >
                CSV Upload
              </button>
            </div>
          </div>

          {uploadMode === 'csv' ? (
            /* CSV Upload Section */
            <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
              <div className="text-center">
                <Upload className="mx-auto text-white/80 mb-4" size={48} />
                <h2 className="text-2xl font-semibold text-white mb-2">
                  Upload CSV File
                </h2>
                <p className="text-white/70 mb-6">
                  Upload a CSV file with your property and appliance information
                </p>

                <div className="space-y-4">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv"
                    onChange={handleFileSelect}
                    className="hidden"
                  />

                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-md text-white px-6 py-3 rounded-xl border border-white/30 hover:bg-white/20 transition-all duration-200"
                    disabled={isLoading}
                  >
                    <FileText size={20} />
                    Choose CSV File
                  </button>

                  {selectedFile && (
                    <div className="bg-white/5 backdrop-blur-md rounded-xl p-4 border border-white/10">
                      <div className="flex items-center justify-center gap-2 text-white/90">
                        <FileText size={16} />
                        <span className="text-sm">{selectedFile.name}</span>
                        <span className="text-xs text-white/60">
                          ({(selectedFile.size / 1024).toFixed(1)} KB)
                        </span>
                      </div>
                    </div>
                  )}

                  <div className="text-center">
                    <button
                      type="button"
                      onClick={handleCsvUpload}
                      disabled={isLoading || !selectedFile}
                      className="bg-gradient-to-r from-blue-500 to-purple-600 text-white py-4 px-8 rounded-xl font-semibold hover:from-blue-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 focus:ring-offset-transparent transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mx-auto"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="animate-spin" size={20} />
                          Uploading CSV...
                        </>
                      ) : (
                        <>
                          <Upload size={20} />
                          Upload CSV File
                        </>
                      )}
                    </button>
                  </div>

                  <div className="text-xs text-white/60 text-center max-w-md mx-auto">
                    <p>File requirements:</p>
                    <ul className="list-disc list-inside mt-1 space-y-1">
                      <li>CSV format (.csv)</li>
                      <li>Maximum file size: 2MB</li>
                      <li>Follow the provided template structure</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          ) : (
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

                <div className="grid gap-6">
                  {/* Address Fields */}
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-white/90 text-sm font-medium">
                        Street Address
                      </label>
                      <input
                        type="text"
                        value={property.street}
                        onChange={(e) => updateProperty(propertyIndex, 'street', e.target.value)}
                        className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                        placeholder="Enter street address"
                        disabled={isLoading}
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="text-white/90 text-sm font-medium">
                        City
                      </label>
                      <input
                        type="text"
                        value={property.city}
                        onChange={(e) => updateProperty(propertyIndex, 'city', e.target.value)}
                        className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                        placeholder="Enter city"
                        disabled={isLoading}
                      />
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-white/90 text-sm font-medium">
                        State
                      </label>
                      <Select
                        value={property.state}
                        onValueChange={(value) => updateProperty(propertyIndex, 'state', value)}
                        disabled={isLoading}
                      >
                        <SelectTrigger className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all">
                          <SelectValue placeholder="Select state" />
                        </SelectTrigger>
                        <SelectContent className="bg-white/95 backdrop-blur-md border border-white/30 rounded-xl max-h-48 overflow-y-auto">
                          {US_STATES.map((state) => (
                            <SelectItem
                              key={state.value}
                              value={state.value}
                              className="text-gray-800 hover:bg-blue-50 focus:bg-blue-50"
                            >
                              {state.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <label className="text-white/90 text-sm font-medium">
                        ZIP Code
                      </label>
                      <input
                        type="text"
                        value={property.zip}
                        onChange={(e) => updateProperty(propertyIndex, 'zip', e.target.value)}
                        className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                        placeholder="Enter ZIP code"
                        disabled={isLoading}
                      />
                    </div>
                  </div>

                  {/* Home Age */}
                  <div className="grid md:grid-cols-2 gap-4">
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
                  </div>

                  {/* Multifamily Property Section */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        id={`multifamily-${propertyIndex}`}
                        checked={property.isMultifamily}
                        onChange={(e) => updateProperty(propertyIndex, 'isMultifamily', e.target.checked)}
                        className="w-5 h-5 bg-white/10 border-2 border-white/30 rounded cursor-pointer focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 focus:ring-offset-transparent"
                        disabled={isLoading}
                      />
                      <label htmlFor={`multifamily-${propertyIndex}`} className="text-white/90 text-sm font-medium cursor-pointer">
                        This is a multifamily property
                      </label>
                    </div>
                  </div>
                </div>

                {property.isMultifamily ? (
                  <>
                    {/* Structures Section - Property Level for Multifamily */}
                    <div className="mt-8">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-medium text-white">Property Structures (Optional)</h3>
                        <button
                          type="button"
                          onClick={() => addStructure(propertyIndex)}
                          className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-md text-white px-4 py-2 rounded-lg border border-white/30 hover:bg-white/20 transition-all duration-200 text-sm"
                          disabled={isLoading}
                        >
                          <Plus size={16} />
                          Add Structure
                        </button>
                      </div>

                      {property.structures.length === 0 ? (
                        <p className="text-white/60 text-sm italic">No structures added yet. Click "Add Structure" to get started.</p>
                      ) : (
                        <div className="space-y-4">
                          {property.structures.map((structure, structureIndex) => (
                            <div key={structureIndex} className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="space-y-2 w-full">
                                  <label className="text-white/90 text-sm font-medium">
                                    Structure Type
                                  </label>
                                  <Select
                                    value={structure.name}
                                    onValueChange={(value) => updateStructureName(propertyIndex, structureIndex, value)}
                                    disabled={isLoading}
                                  >
                                    <SelectTrigger className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all">
                                      <SelectValue placeholder="Select structure" />
                                    </SelectTrigger>
                                    <SelectContent className="bg-white/95 backdrop-blur-md border border-white/30 rounded-xl">
                                      {AVAILABLE_STRUCTURES.map((structureType) => (
                                        <SelectItem
                                          key={structureType}
                                          value={structureType}
                                          className="text-gray-800 hover:bg-blue-50 focus:bg-blue-50"
                                        >
                                          {structureType}
                                        </SelectItem>
                                      ))}
                                    </SelectContent>
                                  </Select>
                                </div>

                                <div className="space-y-2 w-full">
                                  <label className="text-white/90 text-sm font-medium">
                                    Age (years)
                                  </label>
                                  <input
                                    type="number"
                                    min="0"
                                    value={structure.age || ''}
                                    onChange={(e) => updateStructureAge(propertyIndex, structureIndex, parseInt(e.target.value) || 0)}
                                    className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                                    placeholder="Age in years"
                                    disabled={isLoading}
                                  />
                                </div>
                              </div>

                              <div className="mt-4 flex justify-end">
                                <button
                                  type="button"
                                  onClick={() => removeStructure(propertyIndex, structureIndex)}
                                  className="text-red-400 hover:text-red-300 transition-colors px-4 py-2 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 flex items-center gap-2"
                                  disabled={isLoading}
                                >
                                  <Trash2 size={20} />
                                  <span className="text-sm">Remove Structure</span>
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Units Section */}
                    <div className="mt-8">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-medium text-white">Units</h3>
                        <button
                          type="button"
                          onClick={() => addUnit(propertyIndex)}
                          className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-md text-white px-4 py-2 rounded-lg border border-white/30 hover:bg-white/20 transition-all duration-200 text-sm"
                          disabled={isLoading}
                        >
                          <Plus size={16} />
                          Add Unit
                        </button>
                      </div>

                      {property.units && property.units.length > 0 ? (
                        <div className="space-y-6">
                          {property.units.map((unit, unitIndex) => (
                            <div key={unitIndex} className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
                              <div className="flex items-center justify-between mb-4">
                                <h4 className="text-md font-medium text-white">Unit {unitIndex + 1}</h4>
                                {property.units && property.units.length > 1 && (
                                  <button
                                    type="button"
                                    onClick={() => removeUnit(propertyIndex, unitIndex)}
                                    className="text-red-400 hover:text-red-300 transition-colors p-2"
                                  >
                                    <Trash2 size={18} />
                                  </button>
                                )}
                              </div>

                              {/* Unit Number */}
                              <div className="mb-4">
                                <div className="space-y-2">
                                  <label className="text-white/90 text-sm font-medium">
                                    Unit Number
                                  </label>
                                  <input
                                    type="text"
                                    value={unit.unitNumber}
                                    onChange={(e) => updateUnitNumber(propertyIndex, unitIndex, e.target.value)}
                                    className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                                    placeholder="e.g., Unit 101, Apt A"
                                    disabled={isLoading}
                                  />
                                </div>
                              </div>

                              {/* Unit Appliances */}
                              <div>
                                <div className="flex items-center justify-between mb-3">
                                  <h5 className="text-sm font-medium text-white/90">Appliances (Optional)</h5>
                                  <button
                                    type="button"
                                    onClick={() => addUnitAppliance(propertyIndex, unitIndex)}
                                    className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-md text-white px-3 py-1.5 rounded-lg border border-white/30 hover:bg-white/20 transition-all duration-200 text-xs"
                                    disabled={isLoading}
                                  >
                                    <Plus size={14} />
                                    Add Appliance
                                  </button>
                                </div>

                                {unit.appliances.length === 0 ? (
                                  <p className="text-white/60 text-xs italic">No appliances added for this unit.</p>
                                ) : (
                                  <div className="space-y-3">
                                    {unit.appliances.map((appliance, applianceIndex) => (
                                      <div key={applianceIndex} className="bg-white/5 backdrop-blur-sm rounded-lg p-3 border border-white/10">
                                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                                          <div className="space-y-2 w-full">
                                            <label className="text-white/90 text-xs font-medium">
                                              Appliance Type
                                            </label>
                                            <Select
                                              value={appliance.name}
                                              onValueChange={(value) => updateUnitApplianceName(propertyIndex, unitIndex, applianceIndex, value)}
                                              disabled={isLoading}
                                            >
                                              <SelectTrigger className="w-full px-3 py-2 bg-white/10 border border-white/30 rounded-lg text-white text-sm placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all">
                                                <SelectValue placeholder="Select appliance" />
                                              </SelectTrigger>
                                              <SelectContent className="bg-white/95 backdrop-blur-md border border-white/30 rounded-lg">
                                                {AVAILABLE_APPLIANCES.map((applianceType) => (
                                                  <SelectItem
                                                    key={applianceType}
                                                    value={applianceType}
                                                    className="text-gray-800 hover:bg-blue-50 focus:bg-blue-50"
                                                  >
                                                    {applianceType}
                                                  </SelectItem>
                                                ))}
                                              </SelectContent>
                                            </Select>
                                          </div>

                                          <div className="space-y-2 w-full">
                                            <label className="text-white/90 text-xs font-medium">
                                              Age (years)
                                            </label>
                                            <input
                                              type="number"
                                              min="0"
                                              value={appliance.age || ''}
                                              onChange={(e) => updateUnitApplianceAge(propertyIndex, unitIndex, applianceIndex, parseInt(e.target.value) || 0)}
                                              className="w-full px-3 py-2 bg-white/10 border border-white/30 rounded-lg text-white text-sm placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                                              placeholder="Age in years"
                                              disabled={isLoading}
                                            />
                                          </div>

                                          <div className="space-y-2 w-full">
                                            <label className="text-white/90 text-xs font-medium">
                                              Brand (Optional)
                                            </label>
                                            <input
                                              type="text"
                                              value={appliance.brand || ''}
                                              onChange={(e) => updateUnitApplianceBrand(propertyIndex, unitIndex, applianceIndex, e.target.value)}
                                              className="w-full px-3 py-2 bg-white/10 border border-white/30 rounded-lg text-white text-sm placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                                              placeholder="e.g., LG, Samsung"
                                              disabled={isLoading}
                                            />
                                          </div>

                                          <div className="space-y-2 w-full">
                                            <label className="text-white/90 text-xs font-medium">
                                              Model (Optional)
                                            </label>
                                            <input
                                              type="text"
                                              value={appliance.model || ''}
                                              onChange={(e) => updateUnitApplianceModel(propertyIndex, unitIndex, applianceIndex, e.target.value)}
                                              className="w-full px-3 py-2 bg-white/10 border border-white/30 rounded-lg text-white text-sm placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                                              placeholder="e.g., Model XYZ"
                                              disabled={isLoading}
                                            />
                                          </div>
                                        </div>

                                        <div className="mt-3 flex justify-end">
                                          <button
                                            type="button"
                                            onClick={() => removeUnitAppliance(propertyIndex, unitIndex, applianceIndex)}
                                            className="text-red-400 hover:text-red-300 transition-colors px-3 py-1.5 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 flex items-center gap-2 text-xs"
                                            disabled={isLoading}
                                          >
                                            <Trash2 size={16} />
                                            <span>Remove</span>
                                          </button>
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-white/60 text-sm italic">No units added yet. Click "Add Unit" to get started.</p>
                      )}
                    </div>
                  </>
                ) : (
                  <>
                    {/* Appliances Section - Property Level for Single-Family */}
                    <div className="mt-8">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-medium text-white">Appliances (Optional)</h3>
                        <button
                          type="button"
                          onClick={() => addAppliance(propertyIndex)}
                          className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-md text-white px-4 py-2 rounded-lg border border-white/30 hover:bg-white/20 transition-all duration-200 text-sm"
                          disabled={isLoading}
                        >
                          <Plus size={16} />
                          Add Appliance
                        </button>
                      </div>

                      {!property.appliances || property.appliances.length === 0 ? (
                        <p className="text-white/60 text-sm italic">No appliances added yet. Click "Add Appliance" to get started.</p>
                      ) : (
                        <div className="space-y-4">
                          {property.appliances.map((appliance, applianceIndex) => (
                            <div key={applianceIndex} className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                <div className="space-y-2 w-full">
                                  <label className="text-white/90 text-sm font-medium">
                                    Appliance Type
                                  </label>
                                  <Select
                                    value={appliance.name}
                                    onValueChange={(value) => updateApplianceName(propertyIndex, applianceIndex, value)}
                                    disabled={isLoading}
                                  >
                                    <SelectTrigger className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all">
                                      <SelectValue placeholder="Select appliance" />
                                    </SelectTrigger>
                                    <SelectContent className="bg-white/95 backdrop-blur-md border border-white/30 rounded-xl">
                                      {AVAILABLE_APPLIANCES.map((applianceType) => (
                                        <SelectItem
                                          key={applianceType}
                                          value={applianceType}
                                          className="text-gray-800 hover:bg-blue-50 focus:bg-blue-50"
                                        >
                                          {applianceType}
                                        </SelectItem>
                                      ))}
                                    </SelectContent>
                                  </Select>
                                </div>

                                <div className="space-y-2 w-full">
                                  <label className="text-white/90 text-sm font-medium">
                                    Age (years)
                                  </label>
                                  <input
                                    type="number"
                                    min="0"
                                    value={appliance.age || ''}
                                    onChange={(e) => updateApplianceAge(propertyIndex, applianceIndex, parseInt(e.target.value) || 0)}
                                    className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                                    placeholder="Age in years"
                                    disabled={isLoading}
                                  />
                                </div>

                                <div className="space-y-2 w-full">
                                  <label className="text-white/90 text-sm font-medium">
                                    Brand (Optional)
                                  </label>
                                  <input
                                    type="text"
                                    value={appliance.brand || ''}
                                    onChange={(e) => updateApplianceBrand(propertyIndex, applianceIndex, e.target.value)}
                                    className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                                    placeholder="e.g., LG, Samsung"
                                    disabled={isLoading}
                                  />
                                </div>

                                <div className="space-y-2 w-full">
                                  <label className="text-white/90 text-sm font-medium">
                                    Model (Optional)
                                  </label>
                                  <input
                                    type="text"
                                    value={appliance.model || ''}
                                    onChange={(e) => updateApplianceModel(propertyIndex, applianceIndex, e.target.value)}
                                    className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                                    placeholder="e.g., Model XYZ"
                                    disabled={isLoading}
                                  />
                                </div>
                              </div>

                              <div className="mt-4 flex justify-end">
                                <button
                                  type="button"
                                  onClick={() => removeAppliance(propertyIndex, applianceIndex)}
                                  className="text-red-400 hover:text-red-300 transition-colors px-4 py-2 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 flex items-center gap-2"
                                  disabled={isLoading}
                                >
                                  <Trash2 size={20} />
                                  <span className="text-sm">Remove Appliance</span>
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Structures Section - Property Level for Single-Family */}
                    <div className="mt-8">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-medium text-white">Structures (Optional)</h3>
                        <button
                          type="button"
                          onClick={() => addStructure(propertyIndex)}
                          className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-md text-white px-4 py-2 rounded-lg border border-white/30 hover:bg-white/20 transition-all duration-200 text-sm"
                          disabled={isLoading}
                        >
                          <Plus size={16} />
                          Add Structure
                        </button>
                      </div>

                      {property.structures.length === 0 ? (
                        <p className="text-white/60 text-sm italic">No structures added yet. Click "Add Structure" to get started.</p>
                      ) : (
                        <div className="space-y-4">
                          {property.structures.map((structure, structureIndex) => (
                            <div key={structureIndex} className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="space-y-2 w-full">
                                  <label className="text-white/90 text-sm font-medium">
                                    Structure Type
                                  </label>
                                  <Select
                                    value={structure.name}
                                    onValueChange={(value) => updateStructureName(propertyIndex, structureIndex, value)}
                                    disabled={isLoading}
                                  >
                                    <SelectTrigger className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all">
                                      <SelectValue placeholder="Select structure" />
                                    </SelectTrigger>
                                    <SelectContent className="bg-white/95 backdrop-blur-md border border-white/30 rounded-xl">
                                      {AVAILABLE_STRUCTURES.map((structureType) => (
                                        <SelectItem
                                          key={structureType}
                                          value={structureType}
                                          className="text-gray-800 hover:bg-blue-50 focus:bg-blue-50"
                                        >
                                          {structureType}
                                        </SelectItem>
                                      ))}
                                    </SelectContent>
                                  </Select>
                                </div>

                                <div className="space-y-2 w-full">
                                  <label className="text-white/90 text-sm font-medium">
                                    Age (years)
                                  </label>
                                  <input
                                    type="number"
                                    min="0"
                                    value={structure.age || ''}
                                    onChange={(e) => updateStructureAge(propertyIndex, structureIndex, parseInt(e.target.value) || 0)}
                                    className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                                    placeholder="Age in years"
                                    disabled={isLoading}
                                  />
                                </div>
                              </div>

                              <div className="mt-4 flex justify-end">
                                <button
                                  type="button"
                                  onClick={() => removeStructure(propertyIndex, structureIndex)}
                                  className="text-red-400 hover:text-red-300 transition-colors px-4 py-2 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 flex items-center gap-2"
                                  disabled={isLoading}
                                >
                                  <Trash2 size={20} />
                                  <span className="text-sm">Remove Structure</span>
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </>
                )}
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
          )}
        </div>
      </div>
    </div>
  );
};

export default Properties;

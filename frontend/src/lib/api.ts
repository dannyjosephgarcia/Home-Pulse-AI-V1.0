// const API_BASE_URL = 'https://home-pulse-api.onrender.com';

const API_BASE_URL = 'http://localhost:5000';


// Token management
export const getAuthToken = (): string | null => {
  return localStorage.getItem('auth_token');
};

export const setAuthToken = (token: string): void => {
  localStorage.setItem('auth_token', token);
};

export const removeAuthToken = (): void => {
  localStorage.removeItem('auth_token');
};

export const isTokenExpired = (token: string): boolean => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Date.now() / 1000;
    return payload.exp < currentTime;
  } catch {
    return true;
  }
};

export const getUserFromToken = (token: string): { user_id: number; email: string; first_name?: string; last_name?: string } | null => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return {
      user_id: payload.user_id,
      email: payload.email,
      first_name: payload.first_name,
      last_name: payload.last_name
    };
  } catch {
    return null;
  }
};

// API client
class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<{ data: T | null; error: any }> {
    try {
      const token = getAuthToken();
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      // Add existing headers
      if (options.headers) {
        Object.entries(options.headers as Record<string, string>).forEach(([key, value]) => {
          headers[key] = value;
        });
      }

      if (token && !isTokenExpired(token)) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
      });

      const data = await response.json();

      if (!response.ok) {
        return { data: null, error: data };
      }

      return { data, error: null };
    } catch (error) {
      return { data: null, error: { message: 'Network error' } };
    }
  }

  // Auth endpoints
  async signUp(email: string, password: string): Promise<{ data: any; error: any }> {
    return this.request('/v1/customers/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async signIn(email: string, password: string): Promise<{ data: any; error: any }> {
    return this.request('/v1/customers/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  // Property endpoints
  async getProperties(): Promise<{ data: any[] | null; error: any }> {
    return this.request('/v1/properties', {
      method: 'GET',
    });
  }

  async getProperty(propertyId: number): Promise<{ data: any | null; error: any }> {
    return this.request(`/v1/properties/${propertyId}`, {
      method: 'GET',
    });
  }

  async getPropertyAppliances(propertyId: number): Promise<{ data: any[] | null; error: any }> {
    return this.request(`/v1/properties/${propertyId}/appliances`, {
      method: 'GET',
    });
  }

  async getPropertyStructures(propertyId: number): Promise<{ data: any[] | null; error: any }> {
    return this.request(`/v1/properties/${propertyId}/structures`, {
      method: 'GET',
    });
  }

  async submitProperties(properties: any[]): Promise<{ data: any | null; error: any }> {
    return this.request('/v1/properties', {
      method: 'POST',
      body: JSON.stringify(properties),
    });
  }

  async updateProfile(firstName: string, lastName: string): Promise<{ data: any | null; error: any }> {
    return this.request('/v1/customers/profile', {
      method: 'PUT',
      body: JSON.stringify({ firstName, lastName }),
    });
  }

  async getPropertyAddresses(userId: number): Promise<{ data: any[] | null; error: any }> {
    return this.request(`/v1/properties/${userId}/addresses`, {
      method: 'GET',
    });
  }

  async getPropertyTenants(propertyId: number): Promise<{ data: any[] | null; error: any }> {
    return this.request(`/v1/properties/${propertyId}/tenants`, {
      method: 'GET',
    });
  }

  async updateTenant(propertyId: number, tenantId: number, tenantData: any): Promise<{ data: any | null; error: any }> {
    return this.request(`/v1/properties/${propertyId}/tenants/${tenantId}`, {
      method: 'PUT',
      body: JSON.stringify(tenantData),
    });
  }

  async addTenant(propertyId: number, tenantData: any): Promise<{ data: any | null; error: any }> {
    return this.request(`/v1/properties/${propertyId}/tenants`, {
      method: 'POST',
      body: JSON.stringify(tenantData),
    });
  }

  async getPropertyImageSignedUrl(propertyId: number, userId: number): Promise<{ data: any | null; error: any }> {
    return this.request(`/v1/properties/${propertyId}/customers/${userId}/image`, {
      method: 'GET',
    });
  }

  async uploadPropertyImage(propertyId: number, userId: number, fileName: string): Promise<{ data: any | null; error: any }> {
    return this.request(`/v1/properties/${propertyId}/customers/${userId}/image`, {
      method: 'POST',
      body: JSON.stringify({ fileName }),
    });
  }

    async cancelSubscription(userId: number): Promise<{ data: any | null; error: any }> {
    return this.request(`/v1/customers/${userId}/cancel-subscription`, {
      method: 'DELETE',
    });
  }

    async getSubscriptionInformation(userId: number): Promise<{ data: any | null; error: any }> {
    return this.request(`/v1/customers/${userId}/retrieve-subscription-information`, {
      method: 'GET',
    });
  }

  async askLifecycleQuestion(question: string, applianceAge: number): Promise<{ data: any | null; error: any }> {
    return this.request('/v1/home-bot/ask-lifecycle-question', {
      method: 'POST',
      body: JSON.stringify({ question, applianceAge }),
    });
  }

    async updateApplianceForecastedDate(propertyId: number, applianceType: string, forecastedDate: string): Promise<{ data: any | null; error: any }> {
    return this.request(`/v1/properties/${propertyId}/appliances/forecasted-date`, {
      method: 'PUT',
      body: JSON.stringify({
        propertyId: propertyId,
        applianceType: applianceType,
        forecastedReplacementDate: forecastedDate
      }),
    });
  }

  // Appliances update endpoints
  async updatePropertyAppliances(propertyId: number, applianceUpdates: any[]): Promise<{ data: any | null; error: any }> {
    return this.request(`/v1/properties/${propertyId}/appliances`, {
      method: 'PUT',
      body: JSON.stringify({ applianceUpdates }),
    });
  }

  // Structures update endpoints
  async updatePropertyStructures(propertyId: number, structureUpdates: any[]): Promise<{ data: any | null; error: any }> {
    return this.request(`/v1/properties/${propertyId}/structures`, {
      method: 'PUT',
      body: JSON.stringify({ structureUpdates: structureUpdates }),
    });
  }

  // CSV bulk upload endpoint
  async csvBulkUpload(csvFile: File): Promise<{ data: any | null; error: any }> {
    try {
        const token = getAuthToken();
        const formData = new FormData();
        formData.append("file", csvFile);

        const headers: Record<string, string> = {};

        if (token && !isTokenExpired(token)) {
          headers['Authorization'] = `Bearer ${token}`;
        }

      const response = await fetch(`${API_BASE_URL}/v1/properties/csv-bulk-upload`, {
          method: 'POST',
          headers,
          body: formData,
        });

      const data = await response.json();

      if (!response.ok) {
        return { data: null, error: data };
      }

      return { data, error: null };
    } catch (error) {
      return { data: null, error: { message: 'Network error' } };
    }
  }

  // Properties needs attention endpoint
  async getPropertiesNeedsAttention(userId: number): Promise<{ data: any | null; error: any }> {
    return this.request(`/v1/properties/${userId}/needs-attention`, {
      method: 'GET',
    });
  }

  // Units endpoints
  async getPropertyUnits(propertyId: number): Promise<{ data: any[] | null; error: any }> {
    return this.request(`/v1/properties/${propertyId}/units`, {
      method: 'GET',
    });
  }

  async getUnitAppliances(unitId: number): Promise<{ data: any[] | null; error: any }> {
    return this.request(`/v1/units/${unitId}/appliances`, {
      method: 'GET',
    });
  }
}

export const apiClient = new ApiClient();
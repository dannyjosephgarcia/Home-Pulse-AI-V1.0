
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar';
import { Sidebar, SidebarContent, SidebarGroup, SidebarGroupContent, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarProvider} from '../components/ui/sidebar';
import { User, CreditCard, Upload, Settings } from 'lucide-react';
import { apiClient, setAuthToken, getUserFromToken } from '../lib/api';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

const Profile = () => {
  const { user, setUser } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [scrollY, setScrollY] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleSubmitProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const { data, error } = await apiClient.updateProfile(firstName, lastName);

      if (error) {
        toast.error('Failed to update profile');
      } else {
        if (data?.token) {
          setAuthToken(data.token);
          const updatedUser = getUserFromToken(data.token);
          if (updatedUser) {
            setUser(updatedUser);
            toast.success('Profile updated successfully');
          }
        }
        setFirstName('');
        setLastName('');
      }
    } catch (error) {
      toast.error('Network error while updating profile');
    } finally {
      setIsLoading(false);
    }
  };

  const handleProfilePictureUpload = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = () => {
      toast.info('Profile picture upload functionality coming soon');
    };
    input.click();
  };

  const sidebarItems = [
    { id: 'profile', title: 'Update Profile', icon: User },
    { id: 'subscription', title: 'Manage Subscription', icon: CreditCard },
    { id: 'picture', title: 'Profile Picture', icon: Upload }
  ];

  const ProfileSidebar = () => (
    <Sidebar className="w-64">
      <SidebarContent className="bg-gradient-to-b from-blue-800/80 via-purple-800/40 to-blue-900/90 backdrop-blur-sm border-r border-blue-500/40">
        {/* Logo and Back Button */}
        <div className="p-4 border-b border-blue-300/20">
          <Button
            variant="ghost"
            onClick={() => navigate('/dashboard')}
            className="text-blue-100 hover:bg-blue-500/20 mb-3 w-full justify-start"
          >
            ← Back to Dashboard
          </Button>
          <div className="text-center">
              <h2 className="text-xl font-bold text-white mb-1">HomePulse AI</h2>
              <p className="text-blue-200 text-sm flex items-center justify-center gap-1">
                <Settings className="h-4 w-4" />
                Account Settings
              </p>
            </div>
        </div>

        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {sidebarItems.map((item) => (
                <SidebarMenuItem key={item.id}>
                  <SidebarMenuButton
                    onClick={() => setActiveTab(item.id)}
                    className={`text-blue-100/80 hover:text-white hover:bg-blue-500/20 transition-all duration-200 ${
                      activeTab === item.id ? 'bg-blue-500/50 text-white shadow-lg' : ''
                    }`}
                  >
                    <item.icon className="h-4 w-4 mr-2" />
                    <span>{item.title}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'profile':
        return (
          <Card className="bg-white/10 backdrop-blur-sm border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Update Profile</CardTitle>
              <CardDescription className="text-white/70">
                Update your personal information
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-white/70 mb-4">
                Email: {user?.email}
              </div>

              <form onSubmit={handleSubmitProfile} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="firstName" className="text-white">First Name</Label>
                  <Input
                    id="firstName"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    placeholder="Enter your first name"
                    required
                    className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="lastName" className="text-white">Last Name</Label>
                  <Input
                    id="lastName"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    placeholder="Enter your last name"
                    required
                    className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
                  />
                </div>

                <Button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-white/20 hover:bg-white/30 text-white border border-white/30"
                >
                  {isLoading ? 'Updating...' : 'Update Profile'}
                </Button>
              </form>
            </CardContent>
          </Card>
        );

      case 'subscription':
        return (
          <Card className="bg-white/10 backdrop-blur-sm border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Manage Subscription</CardTitle>
              <CardDescription className="text-white/70">
                View and manage your subscription plan
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-center h-32">
                <div className="text-center text-white/70">
                  <CreditCard className="h-8 w-8 mx-auto mb-2" />
                  <p>Subscription management coming soon</p>
                </div>
              </div>
            </CardContent>
          </Card>
        );

      case 'picture':
        return (
          <Card className="bg-white/10 backdrop-blur-sm border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Profile Picture</CardTitle>
              <CardDescription className="text-white/70">
                Upload and manage your profile picture
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center space-y-4">
                <Avatar className="h-24 w-24">
                  <AvatarImage src="" />
                  <AvatarFallback className="bg-white/20 text-white text-lg">
                    {user?.first_name?.[0] || user?.email?.[0]?.toUpperCase()}
                  </AvatarFallback>
                </Avatar>

                <Button
                  onClick={handleProfilePictureUpload}
                  className="bg-white/20 hover:bg-white/30 text-white border border-white/30"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Upload Picture
                </Button>
              </div>
            </CardContent>
          </Card>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 relative overflow-hidden">
      {/* Dynamic Background */}
      <div
        className="fixed inset-0 opacity-20 transition-transform duration-1000 ease-out"
        style={{
          backgroundImage: `linear-gradient(45deg, hsl(220, 70%, ${20 + scrollY * 0.01}%), hsl(240, 80%, ${15 + scrollY * 0.005}%))`,
          transform: `translateY(${scrollY * 0.3}px) scale(${1 + scrollY * 0.0005})`
        }}
      />

      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div
          className="absolute w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"
          style={{
            top: `${20 + scrollY * 0.1}%`,
            left: `${10 + scrollY * 0.05}%`,
            transform: `rotate(${scrollY * 0.1}deg)`
          }}
        />
        <div
          className="absolute w-80 h-80 bg-purple-500/10 rounded-full blur-3xl"
          style={{
            top: `${60 + scrollY * 0.08}%`,
            right: `${15 + scrollY * 0.07}%`,
            transform: `rotate(${-scrollY * 0.08}deg)`
          }}
        />
      </div>

      <SidebarProvider>
        <div className="min-h-screen flex w-full">
          <ProfileSidebar />

          <main className="flex-1 p-6">
            <div className="max-w-2xl mx-auto">
              {renderContent()}
            </div>
          </main>
        </div>
      </SidebarProvider>
    </div>
  );
};

export default Profile;
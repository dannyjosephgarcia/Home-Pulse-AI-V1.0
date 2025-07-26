import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { User, CreditCard, LogOut } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { apiClient, setAuthToken, getUserFromToken } from '../lib/api';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

interface UserProfileProps {
  onProfileUpdate?: () => void;
}

const UserProfile = ({ onProfileUpdate }: UserProfileProps) => {
  const { user, signOut, setUser } = useAuth();
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();

  const handleSubmitProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const { data, error } = await apiClient.updateProfile(firstName, lastName);

      if (error) {
        toast.error('Failed to update profile');
      } else {
        // Update token and user with response from PUT request
        if (data?.token) {
          setAuthToken(data.token);
          const updatedUser = getUserFromToken(data.token);
          if (updatedUser) {
            setUser(updatedUser);
            toast.success('Profile updated successfully');
          }
        }
        setIsOpen(false);
        setFirstName('');
        setLastName('');
        // Call the refresh function passed from parent if needed
        if (onProfileUpdate) {
          onProfileUpdate();
        }
      }
    } catch (error) {
      toast.error('Network error while updating profile');
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

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          className="bg-white/20 border-white/30 text-white hover:bg-white/30"
        >
          <User className="h-4 w-4 mr-2" />
          Profile
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>User Profile</DialogTitle>
        </DialogHeader>
        <Tabs defaultValue="profile" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="profile">Profile</TabsTrigger>
            <TabsTrigger value="payment" disabled>Payment</TabsTrigger>
          </TabsList>

          <TabsContent value="profile" className="space-y-4">
            <div className="text-sm text-muted-foreground mb-4">
              Email: {user?.email}
            </div>

            <form onSubmit={handleSubmitProfile} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="firstName">First Name</Label>
                <Input
                  id="firstName"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  placeholder="Enter your first name"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="lastName">Last Name</Label>
                <Input
                  id="lastName"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  placeholder="Enter your last name"
                  required
                />
              </div>

              <Button type="submit" disabled={isLoading} className="w-full">
                {isLoading ? 'Updating...' : 'Update Profile'}
              </Button>
            </form>

            <div className="pt-4 border-t">
              <Button
                variant="outline"
                onClick={handleSignOut}
                className="w-full"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Sign Out
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="payment" className="space-y-4">
            <div className="flex items-center justify-center h-32">
              <div className="text-center text-muted-foreground">
                <CreditCard className="h-8 w-8 mx-auto mb-2" />
                <p>Payment management coming soon</p>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

export default UserProfile;
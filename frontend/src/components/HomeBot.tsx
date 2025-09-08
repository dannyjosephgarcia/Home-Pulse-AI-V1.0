import { useState, useRef, useEffect } from 'react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { ScrollArea } from '../components/ui/scroll-area';
import { apiClient } from '../lib/api';
import { toast } from 'sonner';
import { MessageCircle, Send, Bot, User } from 'lucide-react';

interface Appliance {
  id: number;
  appliance_type: string;
  age_in_years: number;
}

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  applianceType?: string;
  forecastedDate?: string;
  showUpdateOption?: boolean;
}

interface HomeBotProps {
  appliances: Appliance[];
  propertyId?: number;
  onApplianceUpdate?: (applianceType: string, newDate: string) => void;
}

export const HomeBot = ({ appliances, propertyId, onApplianceUpdate }: HomeBotProps) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'bot',
      content: "Hello! I'm HomeBot, your AI assistant for home maintenance questions. Select an appliance and ask me anything about its lifecycle, maintenance, or replacement!",
      timestamp: new Date(),
    }
  ]);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [selectedApplianceId, setSelectedApplianceId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Scroll to bottom when new messages are added
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = async () => {
    if (!currentQuestion.trim() || !selectedApplianceId) {
      toast.error('Please select an appliance and enter a question');
      return;
    }

    const selectedAppliance = appliances.find(a => a.id.toString() === selectedApplianceId);
    if (!selectedAppliance) {
      toast.error('Please select a valid appliance');
      return;
    }

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: currentQuestion,
      timestamp: new Date(),
      applianceType: selectedAppliance.appliance_type,
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentQuestion('');
    setIsLoading(true);

    try {
      const { data, error } = await apiClient.askLifecycleQuestion(
        currentQuestion,
        selectedAppliance.age_in_years
      );

      if (error) {
        console.error('HomeBot API error:', error);
        toast.error('Failed to get response from HomeBot');

        // Add error message
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'bot',
          content: "I'm sorry, I'm having trouble processing your request right now. Please try again later.",
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, errorMessage]);
        return;
      }

      // Add bot response
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: data?.response || data?.answer || 'I received your question but couldn\'t generate a proper response.',
        timestamp: new Date(),
        forecastedDate: data?.forecasted_replacement_date,
        showUpdateOption: !!data?.forecasted_replacement_date && !!propertyId,
        applianceType: selectedAppliance.appliance_type,
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message to HomeBot:', error);
      toast.error('Network error while contacting HomeBot');

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: "I'm experiencing network issues. Please check your connection and try again.",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

    const handleUpdateForecastedDate = async (messageId: string, applianceType: string, forecastedDate: string) => {
    if (!propertyId) {
      toast.error('Property ID not available');
      return;
    }

    try {
      const { data, error } = await apiClient.updateApplianceForecastedDate(
        propertyId,
        applianceType,
        forecastedDate
      );

      if (error) {
        console.error('Error updating forecasted date:', error);
        toast.error('Failed to update forecasted date');
        return;
      }

      if (data?.putRecordStatus === 200) {
        toast.success('Forecasted date updated successfully');

        // Remove the update option from the message
        setMessages(prev => prev.map(msg =>
          msg.id === messageId ? { ...msg, showUpdateOption: false } : msg
        ));

        // Call the callback to update the parent component
        if (onApplianceUpdate) {
          onApplianceUpdate(applianceType, forecastedDate);
        }
      } else {
        toast.error('Failed to update forecasted date');
      }
    } catch (error) {
      console.error('Error updating forecasted date:', error);
      toast.error('Network error while updating forecasted date');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Card className="bg-white/10 backdrop-blur-md border-white/20 h-full flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="text-white flex items-center space-x-2">
          <MessageCircle className="h-5 w-5" />
          <span>HomeBot Assistant</span>
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col space-y-4 p-4">
        {/* Messages Area */}
        <ScrollArea className="flex-1 pr-3" ref={scrollAreaRef}>
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.type === 'user'
                      ? 'bg-primary text-white'
                      : 'bg-white/20 text-white'
                  }`}
                >
                  <div className="flex items-start space-x-2">
                    {message.type === 'bot' ? (
                      <Bot className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    ) : (
                      <User className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    )}
                    <div className="flex-1">
                      {message.applianceType && (
                        <div className="text-xs opacity-75 mb-1">
                          About: {message.applianceType}
                        </div>
                      )}
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      {message.showUpdateOption && message.forecastedDate && message.applianceType && (
                        <div className="mt-3 p-2 bg-white/10 rounded-lg border border-white/20">
                          <p className="text-xs text-white/80 mb-2">
                            New forecasted replacement date: {new Date(message.forecastedDate).toLocaleDateString()}
                          </p>
                          <Button
                            size="sm"
                            onClick={() => handleUpdateForecastedDate(message.id, message.applianceType!, message.forecastedDate!)}
                            className="bg-primary hover:bg-primary/90 text-white text-xs px-3 py-1"
                          >
                            Select to update replacement date
                          </Button>
                        </div>
                      )}
                      <div className="text-xs opacity-60 mt-1">
                        {message.timestamp.toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white/20 text-white rounded-lg p-3 max-w-[80%]">
                  <div className="flex items-center space-x-2">
                    <Bot className="h-4 w-4" />
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        {/* Input Area */}
        <div className="space-y-3 border-t border-white/20 pt-4">
          {/* Appliance Selection */}
          <Select value={selectedApplianceId} onValueChange={setSelectedApplianceId}>
            <SelectTrigger className="bg-white/10 border-white/20 text-white">
              <SelectValue placeholder="Select an appliance..." />
            </SelectTrigger>
            <SelectContent>
              {appliances.map((appliance) => (
                <SelectItem key={appliance.id} value={appliance.id.toString()}>
                  {appliance.appliance_type} ({appliance.age_in_years} years old)
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Message Input */}
          <div className="flex space-x-2">
            <Input
              value={currentQuestion}
              onChange={(e) => setCurrentQuestion(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about maintenance, replacement, or lifecycle..."
              className="flex-1 bg-white/10 border-white/20 text-white placeholder:text-white/50"
              disabled={isLoading || !selectedApplianceId}
            />
            <Button
              onClick={handleSendMessage}
              disabled={!currentQuestion.trim() || !selectedApplianceId || isLoading}
              className="bg-primary hover:bg-primary/90 text-white px-3"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

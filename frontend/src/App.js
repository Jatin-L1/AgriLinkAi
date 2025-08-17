import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Textarea } from './components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Badge } from './components/ui/badge';
import { Separator } from './components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Progress } from './components/ui/progress';
import { Alert, AlertDescription } from './components/ui/alert';
import { 
  Leaf, MapPin, MessageCircle, Clock, Sparkles, Camera, 
  TrendingUp, CloudRain, Thermometer, Droplets, Wind,
  BarChart3, Users, Globe, Zap, Upload, Brain, Target
} from 'lucide-react';

const BACKEND_URL = 'http://localhost:8001';

function App() {
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('');
  const [language, setLanguage] = useState('hindi');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [recentQueries, setRecentQueries] = useState([]);
  const [weatherData, setWeatherData] = useState(null);
  const [cropRecommendations, setCropRecommendations] = useState(null);
  const [marketPrices, setMarketPrices] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [diseaseDetection, setDiseaseDetection] = useState(null);
  const [activeTab, setActiveTab] = useState('chat');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const result = await axios.post(`${BACKEND_URL}/api/query`, {
        query: query.trim(),
        location: location.trim(),
        language: language
      });
      
      setResponse(result.data);
      loadRecentQueries();
      
      // Load weather data if location is provided
      if (location.trim()) {
        loadWeatherData(location.trim());
      }
    } catch (error) {
      console.error('Error:', error);
      setResponse({
        response: 'सिस्टम में कोई समस्या है। कृपया बाद में कोशिश करें।',
        language: language,
        query_id: 'error',
        timestamp: new Date().toISOString(),
        confidence: 0,
        suggestions: []
      });
    }
    setLoading(false);
  };

  const loadRecentQueries = async () => {
    try {
      const result = await axios.get(`${BACKEND_URL}/api/queries?limit=5`);
      setRecentQueries(result.data.queries || []);
    } catch (error) {
      console.error('Failed to load recent queries:', error);
    }
  };

  const loadWeatherData = async (loc) => {
    try {
      const result = await axios.get(`${BACKEND_URL}/api/weather/${encodeURIComponent(loc)}`);
      setWeatherData(result.data);
    } catch (error) {
      console.error('Failed to load weather data:', error);
    }
  };

  const loadCropRecommendations = async () => {
    if (!location.trim()) return;
    
    try {
      const result = await axios.post(`${BACKEND_URL}/api/crop-recommendation`, {
        location: location.trim()
      });
      setCropRecommendations(result.data);
    } catch (error) {
      console.error('Failed to load crop recommendations:', error);
    }
  };

  const loadMarketPrices = async () => {
    try {
      const result = await axios.get(`${BACKEND_URL}/api/market-prices`);
      setMarketPrices(result.data);
    } catch (error) {
      console.error('Failed to load market prices:', error);
    }
  };

  const checkSystemHealth = async () => {
    try {
      const result = await axios.get(`${BACKEND_URL}/api/health`);
      setSystemHealth(result.data);
    } catch (error) {
      console.error('Failed to check system health:', error);
    }
  };

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setSelectedImage(file);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('image', file);

      const result = await axios.post(`${BACKEND_URL}/api/disease-detection`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setDiseaseDetection(result.data);
    } catch (error) {
      console.error('Disease detection error:', error);
      setDiseaseDetection({
        disease_name: 'पहचान में त्रुटि',
        confidence: 0,
        symptoms: ['इमेज प्रोसेसिंग में समस्या'],
        treatment: ['कृपया दोबारा कोशिश करें'],
        prevention: [],
        severity: 'अज्ञात'
      });
    }
    setLoading(false);
  };

  useEffect(() => {
    loadRecentQueries();
    loadMarketPrices();
    checkSystemHealth();
  }, []);

  useEffect(() => {
    if (location.trim()) {
      loadWeatherData(location.trim());
    }
  }, [location]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50">
      {/* Header */}
      <header className="bg-white/90 backdrop-blur-md border-b border-green-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-green-400 to-emerald-500 rounded-xl shadow-lg">
                <Brain className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-green-700 to-emerald-600 bg-clip-text text-transparent">
                  एग्रीलिंक AI सलाहकार
                </h1>
                <p className="text-green-600 text-sm flex items-center gap-2">
                  <Zap className="h-3 w-3" />
                  Advanced Agricultural Intelligence Platform
                </p>
              </div>
            </div>
            
            {/* System Status */}
            <div className="flex items-center gap-4">
              {systemHealth && (
                <div className="flex items-center gap-2 text-sm">
                  <div className={`w-2 h-2 rounded-full ${
                    systemHealth.ollama === 'connected' ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                  <span className="text-gray-600">
                    {systemHealth.ollama === 'connected' ? 'AI Online' : 'AI Offline'}
                  </span>
                </div>
              )}
              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                v2.0 Enhanced
              </Badge>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Enhanced Tabs Navigation */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5 bg-white/80 backdrop-blur-sm">
            <TabsTrigger value="chat" className="flex items-center gap-2">
              <MessageCircle className="h-4 w-4" />
              AI Chat
            </TabsTrigger>
            <TabsTrigger value="crops" className="flex items-center gap-2">
              <Target className="h-4 w-4" />
              Crop Advisor
            </TabsTrigger>
            <TabsTrigger value="disease" className="flex items-center gap-2">
              <Camera className="h-4 w-4" />
              Disease Detection
            </TabsTrigger>
            <TabsTrigger value="weather" className="flex items-center gap-2">
              <CloudRain className="h-4 w-4" />
              Weather
            </TabsTrigger>
            <TabsTrigger value="market" className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Market
            </TabsTrigger>
          </TabsList>

          {/* Chat Tab */}
          <TabsContent value="chat" className="space-y-6">
            <div className="grid lg:grid-cols-3 gap-8">
              {/* Enhanced Query Input Section */}
              <div className="lg:col-span-2 space-y-6">
                <Card className="border-green-200 shadow-xl bg-white/80 backdrop-blur-sm">
                  <CardHeader className="bg-gradient-to-r from-green-50 to-emerald-50 border-b border-green-100">
                    <CardTitle className="flex items-center gap-2 text-green-800">
                      <Brain className="h-5 w-5" />
                      AI-Powered Agricultural Assistant
                    </CardTitle>
                    <CardDescription>
                      फसल, मौसम, रोग, नीति, या वित्त संबंधी कोई भी प्रश्न पूछें - अब Ollama AI के साथ
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4 pt-6">
                    <form onSubmit={handleSubmit} className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                          <MessageCircle className="h-4 w-4" />
                          आपका प्रश्न / Your Question
                        </label>
                        <Textarea
                          value={query}
                          onChange={(e) => setQuery(e.target.value)}
                          placeholder="उदाहरण: इस मौसम में कौन सी फसल उगानी चाहिए? मेरी फसल में कीड़े लग गए हैं, क्या करूं?"
                          className="min-h-[120px] border-green-200 focus:border-green-400 focus:ring-green-400 resize-none"
                          required
                        />
                      </div>

                      <div className="grid md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                            <MapPin className="h-4 w-4" />
                            स्थान / Location
                          </label>
                          <Input
                            value={location}
                            onChange={(e) => setLocation(e.target.value)}
                            placeholder="जैसे: पंजाब, हरियाणा, उत्तर प्रदेश"
                            className="border-green-200 focus:border-green-400 focus:ring-green-400"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                            <Globe className="h-4 w-4" />
                            भाषा / Language
                          </label>
                          <Select value={language} onValueChange={setLanguage}>
                            <SelectTrigger className="border-green-200 focus:border-green-400 focus:ring-green-400">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="hindi">हिंदी (Hindi)</SelectItem>
                              <SelectItem value="punjabi">ਪੰਜਾਬੀ (Punjabi)</SelectItem>
                              <SelectItem value="english">English</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>

                      <Button 
                        type="submit" 
                        disabled={loading || !query.trim()}
                        className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-lg"
                        size="lg"
                      >
                        {loading ? (
                          <div className="flex items-center gap-2">
                            <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
                            AI विश्लेषण कर रहा है...
                          </div>
                        ) : (
                          <>
                            <Brain className="h-5 w-5 mr-2" />
                            AI सलाह प्राप्त करें
                          </>
                        )}
                      </Button>
                    </form>
                  </CardContent>
                </Card>

                {/* Enhanced Response Section */}
                {response && (
                  <Card className="border-green-200 shadow-xl bg-white/80 backdrop-blur-sm">
                    <CardHeader className="bg-gradient-to-r from-green-50 to-emerald-50 border-b border-green-100">
                      <CardTitle className="flex items-center gap-2 text-green-800">
                        <Brain className="h-5 w-5" />
                        AI सलाहकार का उत्तर
                      </CardTitle>
                      <div className="flex items-center gap-4 text-sm text-gray-600 flex-wrap">
                        <div className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          {new Date(response.timestamp).toLocaleString('hi-IN')}
                        </div>
                        <Badge variant="secondary" className="bg-green-100 text-green-800">
                          {response.language}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          ID: {response.query_id.slice(0, 8)}
                        </Badge>
                        {response.confidence > 0 && (
                          <div className="flex items-center gap-2">
                            <span className="text-xs">Confidence:</span>
                            <Progress value={response.confidence * 100} className="w-16 h-2" />
                            <span className="text-xs">{Math.round(response.confidence * 100)}%</span>
                          </div>
                        )}
                      </div>
                    </CardHeader>
                    <CardContent className="pt-6 space-y-4">
                      <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-xl border-l-4 border-green-500 shadow-sm">
                        <p className="text-gray-800 leading-relaxed whitespace-pre-wrap text-lg">
                          {response.response}
                        </p>
                      </div>
                      
                      {/* AI Suggestions */}
                      {response.suggestions && response.suggestions.length > 0 && (
                        <div className="mt-4">
                          <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                            <Target className="h-4 w-4" />
                            सुझाव / Suggestions
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {response.suggestions.map((suggestion, index) => (
                              <Badge key={index} variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                                {suggestion}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}
              </div>

              {/* Enhanced Sidebar */}
              <div className="space-y-6">
                {/* Enhanced System Info */}
                <Card className="border-green-200 shadow-xl bg-white/80 backdrop-blur-sm">
                  <CardHeader className="bg-gradient-to-r from-green-50 to-emerald-50 border-b border-green-100">
                    <CardTitle className="text-green-800 text-lg flex items-center gap-2">
                      <Zap className="h-5 w-5" />
                      सिस्टम स्थिति
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-6 space-y-3">
                    <div className="flex items-center gap-2 text-sm">
                      <div className={`w-2 h-2 rounded-full ${
                        systemHealth?.ollama === 'connected' ? 'bg-green-500' : 'bg-red-500'
                      }`}></div>
                      <span>Ollama AI {systemHealth?.model || 'llama3.2:3b'}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <div className={`w-2 h-2 rounded-full ${
                        systemHealth?.mongodb === 'connected' ? 'bg-green-500' : 'bg-orange-500'
                      }`}></div>
                      <span>Database Connection</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <div className={`w-2 h-2 rounded-full ${
                        systemHealth?.weather_api === 'configured' ? 'bg-green-500' : 'bg-yellow-500'
                      }`}></div>
                      <span>Weather API</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <div className={`w-2 h-2 rounded-full ${
                        systemHealth?.twilio === 'configured' ? 'bg-green-500' : 'bg-orange-500'
                      }`}></div>
                      <span>SMS Integration</span>
                    </div>
                  </CardContent>
                </Card>

                {/* Weather Widget */}
                {weatherData && (
                  <Card className="border-blue-200 shadow-xl bg-white/80 backdrop-blur-sm">
                    <CardHeader className="bg-gradient-to-r from-blue-50 to-sky-50 border-b border-blue-100">
                      <CardTitle className="text-blue-800 text-lg flex items-center gap-2">
                        <CloudRain className="h-5 w-5" />
                        मौसम जानकारी
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-6 space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Thermometer className="h-4 w-4 text-red-500" />
                          <span className="text-sm">तापमान</span>
                        </div>
                        <span className="font-semibold">{weatherData.temperature}°C</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Droplets className="h-4 w-4 text-blue-500" />
                          <span className="text-sm">आर्द्रता</span>
                        </div>
                        <span className="font-semibold">{weatherData.humidity}%</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Wind className="h-4 w-4 text-gray-500" />
                          <span className="text-sm">हवा</span>
                        </div>
                        <span className="font-semibold">{weatherData.wind_speed} km/h</span>
                      </div>
                      <div className="mt-3 p-2 bg-blue-50 rounded-lg">
                        <p className="text-sm text-blue-800">{weatherData.description}</p>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Recent Queries */}
                <Card className="border-green-200 shadow-xl bg-white/80 backdrop-blur-sm">
                  <CardHeader className="bg-gradient-to-r from-green-50 to-emerald-50 border-b border-green-100">
                    <CardTitle className="text-green-800 text-lg flex items-center gap-2">
                      <Clock className="h-5 w-5" />
                      हाल की क्वेरी
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-6">
                    {recentQueries.length > 0 ? (
                      <div className="space-y-3 max-h-64 overflow-y-auto">
                        {recentQueries.map((q, index) => (
                          <div key={index} className="p-3 bg-green-50 rounded-lg border border-green-200 hover:bg-green-100 transition-colors cursor-pointer"
                               onClick={() => setQuery(q.query)}>
                            <p className="text-sm text-gray-800 mb-1 line-clamp-2">
                              {q.query}
                            </p>
                            <div className="flex items-center gap-2 text-xs text-gray-500">
                              <MapPin className="h-3 w-3" />
                              <span>{q.location}</span>
                              <Badge variant="outline" className="text-xs">
                                {q.language}
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-sm">कोई क्वेरी नहीं मिली</p>
                    )}
                  </CardContent>
                </Card>

                {/* Enhanced Sample Queries */}
                <Card className="border-green-200 shadow-xl bg-white/80 backdrop-blur-sm">
                  <CardHeader className="bg-gradient-to-r from-green-50 to-emerald-50 border-b border-green-100">
                    <CardTitle className="text-green-800 text-lg flex items-center gap-2">
                      <MessageCircle className="h-5 w-5" />
                      उदाहरण प्रश्न
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-6">
                    <div className="space-y-2">
                      {[
                        "इस मौसम में कौन सी फसल उगानी चाहिए?",
                        "गेहूं की बुआई का सही समय क्या है?",
                        "PM-KISAN योजना की पूरी जानकारी दें",
                        "कपास में कीड़े का जैविक इलाज?",
                        "मिट्टी की जांच कैसे कराएं?",
                        "What are the best crops for Punjab?",
                        "Organic farming techniques in Hindi"
                      ].map((sample, index) => (
                        <button
                          key={index}
                          onClick={() => setQuery(sample)}
                          className="w-full text-left p-3 text-sm bg-green-50 hover:bg-green-100 rounded-lg border border-green-200 transition-all duration-200 hover:shadow-md"
                        >
                          {sample}
                        </button>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Crop Recommendation Tab */}
          <TabsContent value="crops" className="space-y-6">
            <Card className="border-green-200 shadow-xl bg-white/80 backdrop-blur-sm">
              <CardHeader className="bg-gradient-to-r from-green-50 to-emerald-50 border-b border-green-100">
                <CardTitle className="flex items-center gap-2 text-green-800">
                  <Target className="h-5 w-5" />
                  AI-Powered Crop Recommendation
                </CardTitle>
                <CardDescription>
                  मिट्टी और मौसम के आधार पर सबसे उपयुक्त फसलों की सिफारिश प्राप्त करें
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="space-y-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    <Input
                      value={location}
                      onChange={(e) => setLocation(e.target.value)}
                      placeholder="स्थान दर्ज करें"
                      className="border-green-200 focus:border-green-400"
                    />
                    <Button 
                      onClick={loadCropRecommendations}
                      disabled={!location.trim() || loading}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <Target className="h-4 w-4 mr-2" />
                      फसल सुझाव प्राप्त करें
                    </Button>
                  </div>
                  
                  {cropRecommendations && (
                    <div className="mt-6 space-y-4">
                      <div className="grid md:grid-cols-2 gap-4">
                        <Card className="border-green-200">
                          <CardHeader className="pb-3">
                            <CardTitle className="text-lg text-green-800">मुख्य सिफारिश</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-2">
                              {cropRecommendations.primary_crops.map((crop, index) => (
                                <Badge key={index} variant="default" className="bg-green-600 mr-2">
                                  {crop}
                                </Badge>
                              ))}
                            </div>
                          </CardContent>
                        </Card>
                        
                        <Card className="border-blue-200">
                          <CardHeader className="pb-3">
                            <CardTitle className="text-lg text-blue-800">वैकल्पिक विकल्प</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-2">
                              {cropRecommendations.alternative_crops.map((crop, index) => (
                                <Badge key={index} variant="outline" className="border-blue-600 text-blue-600 mr-2">
                                  {crop}
                                </Badge>
                              ))}
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                      
                      <div className="grid md:grid-cols-3 gap-4">
                        <Card className="border-orange-200">
                          <CardContent className="pt-4">
                            <div className="text-center">
                              <p className="text-sm text-gray-600">बुआई का समय</p>
                              <p className="font-semibold text-orange-800">{cropRecommendations.planting_time}</p>
                            </div>
                          </CardContent>
                        </Card>
                        
                        <Card className="border-purple-200">
                          <CardContent className="pt-4">
                            <div className="text-center">
                              <p className="text-sm text-gray-600">अपेक्षित उत्पादन</p>
                              <p className="font-semibold text-purple-800">{cropRecommendations.expected_yield}</p>
                            </div>
                          </CardContent>
                        </Card>
                        
                        <Card className="border-indigo-200">
                          <CardContent className="pt-4">
                            <div className="text-center">
                              <p className="text-sm text-gray-600">बाजार मूल्य</p>
                              <p className="font-semibold text-indigo-800">{cropRecommendations.market_price}</p>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Disease Detection Tab */}
          <TabsContent value="disease" className="space-y-6">
            <Card className="border-red-200 shadow-xl bg-white/80 backdrop-blur-sm">
              <CardHeader className="bg-gradient-to-r from-red-50 to-pink-50 border-b border-red-100">
                <CardTitle className="flex items-center gap-2 text-red-800">
                  <Camera className="h-5 w-5" />
                  Plant Disease Detection
                </CardTitle>
                <CardDescription>
                  पौधों की बीमारी पहचानने के लिए पत्तियों की फोटो अपलोड करें
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="space-y-4">
                  <div className="border-2 border-dashed border-red-200 rounded-lg p-8 text-center">
                    <Upload className="h-12 w-12 text-red-400 mx-auto mb-4" />
                    <p className="text-gray-600 mb-4">पत्तियों की स्पष्ट फोटो अपलोड करें</p>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleImageUpload}
                      className="hidden"
                      id="image-upload"
                    />
                    <label htmlFor="image-upload">
                      <Button variant="outline" className="border-red-600 text-red-600 hover:bg-red-50" asChild>
                        <span>
                          <Camera className="h-4 w-4 mr-2" />
                          फोटो चुनें
                        </span>
                      </Button>
                    </label>
                  </div>
                  
                  {selectedImage && (
                    <div className="mt-4">
                      <p className="text-sm text-gray-600 mb-2">अपलोड की गई फोटो:</p>
                      <img 
                        src={URL.createObjectURL(selectedImage)} 
                        alt="Uploaded plant" 
                        className="max-w-xs rounded-lg shadow-md"
                      />
                    </div>
                  )}
                  
                  {diseaseDetection && (
                    <Card className="border-red-200 mt-6">
                      <CardHeader className="bg-red-50">
                        <CardTitle className="text-red-800 flex items-center gap-2">
                          <Target className="h-5 w-5" />
                          रोग पहचान परिणाम
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="pt-4 space-y-4">
                        <div className="flex items-center justify-between">
                          <span className="font-semibold">रोग का नाम:</span>
                          <Badge variant="destructive">{diseaseDetection.disease_name}</Badge>
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <span className="font-semibold">विश्वसनीयता:</span>
                          <div className="flex items-center gap-2">
                            <Progress value={diseaseDetection.confidence * 100} className="w-20" />
                            <span>{Math.round(diseaseDetection.confidence * 100)}%</span>
                          </div>
                        </div>
                        
                        <div>
                          <h4 className="font-semibold mb-2">लक्षण:</h4>
                          <ul className="list-disc list-inside space-y-1">
                            {diseaseDetection.symptoms.map((symptom, index) => (
                              <li key={index} className="text-sm text-gray-700">{symptom}</li>
                            ))}
                          </ul>
                        </div>
                        
                        <div>
                          <h4 className="font-semibold mb-2">उपचार:</h4>
                          <ul className="list-disc list-inside space-y-1">
                            {diseaseDetection.treatment.map((treatment, index) => (
                              <li key={index} className="text-sm text-gray-700">{treatment}</li>
                            ))}
                          </ul>
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Weather Tab */}
          <TabsContent value="weather" className="space-y-6">
            <Card className="border-blue-200 shadow-xl bg-white/80 backdrop-blur-sm">
              <CardHeader className="bg-gradient-to-r from-blue-50 to-sky-50 border-b border-blue-100">
                <CardTitle className="flex items-center gap-2 text-blue-800">
                  <CloudRain className="h-5 w-5" />
                  Comprehensive Weather Analysis
                </CardTitle>
                <CardDescription>
                  एग्रीलिंक के लिए विस्तृत मौसम जानकारी और पूर्वानुमान
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="grid md:grid-cols-2 gap-4 mb-6">
                  <Input
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="स्थान दर्ज करें"
                    className="border-blue-200 focus:border-blue-400"
                  />
                  <Button 
                    onClick={() => loadWeatherData(location)}
                    disabled={!location.trim() || loading}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    <CloudRain className="h-4 w-4 mr-2" />
                    मौसम डेटा लोड करें
                  </Button>
                </div>
                
                {weatherData && (
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <Card className="border-red-200">
                      <CardContent className="pt-4 text-center">
                        <Thermometer className="h-8 w-8 text-red-500 mx-auto mb-2" />
                        <p className="text-sm text-gray-600">तापमान</p>
                        <p className="text-2xl font-bold text-red-600">{weatherData.temperature}°C</p>
                      </CardContent>
                    </Card>
                    
                    <Card className="border-blue-200">
                      <CardContent className="pt-4 text-center">
                        <Droplets className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                        <p className="text-sm text-gray-600">आर्द्रता</p>
                        <p className="text-2xl font-bold text-blue-600">{weatherData.humidity}%</p>
                      </CardContent>
                    </Card>
                    
                    <Card className="border-gray-200">
                      <CardContent className="pt-4 text-center">
                        <Wind className="h-8 w-8 text-gray-500 mx-auto mb-2" />
                        <p className="text-sm text-gray-600">हवा की गति</p>
                        <p className="text-2xl font-bold text-gray-600">{weatherData.wind_speed} km/h</p>
                      </CardContent>
                    </Card>
                    
                    {weatherData.rainfall !== undefined && (
                      <Card className="border-indigo-200">
                        <CardContent className="pt-4 text-center">
                          <CloudRain className="h-8 w-8 text-indigo-500 mx-auto mb-2" />
                          <p className="text-sm text-gray-600">वर्षा</p>
                          <p className="text-2xl font-bold text-indigo-600">{weatherData.rainfall} mm</p>
                        </CardContent>
                      </Card>
                    )}
                    
                    {weatherData.pressure && (
                      <Card className="border-purple-200">
                        <CardContent className="pt-4 text-center">
                          <BarChart3 className="h-8 w-8 text-purple-500 mx-auto mb-2" />
                          <p className="text-sm text-gray-600">दबाव</p>
                          <p className="text-2xl font-bold text-purple-600">{weatherData.pressure} hPa</p>
                        </CardContent>
                      </Card>
                    )}
                    
                    {weatherData.visibility && (
                      <Card className="border-green-200">
                        <CardContent className="pt-4 text-center">
                          <Globe className="h-8 w-8 text-green-500 mx-auto mb-2" />
                          <p className="text-sm text-gray-600">दृश्यता</p>
                          <p className="text-2xl font-bold text-green-600">{weatherData.visibility} km</p>
                        </CardContent>
                      </Card>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Market Tab */}
          <TabsContent value="market" className="space-y-6">
            <Card className="border-yellow-200 shadow-xl bg-white/80 backdrop-blur-sm">
              <CardHeader className="bg-gradient-to-r from-yellow-50 to-orange-50 border-b border-yellow-100">
                <CardTitle className="flex items-center gap-2 text-yellow-800">
                  <TrendingUp className="h-5 w-5" />
                  Market Intelligence & Prices
                </CardTitle>
                <CardDescription>
                  वर्तमान बाजार मूल्य और ट्रेंड्स की जानकारी
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                {marketPrices && (
                  <div className="space-y-4">
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {Object.entries(marketPrices.prices).map(([crop, data]) => (
                        <Card key={crop} className="border-yellow-200">
                          <CardContent className="pt-4">
                            <div className="flex items-center justify-between mb-2">
                              <h3 className="font-semibold text-gray-800">{crop}</h3>
                              <Badge 
                                variant={data.trend === 'up' ? 'default' : data.trend === 'down' ? 'destructive' : 'secondary'}
                                className={
                                  data.trend === 'up' ? 'bg-green-600' : 
                                  data.trend === 'down' ? 'bg-red-600' : 
                                  'bg-gray-600'
                                }
                              >
                                {data.trend === 'up' ? '↗' : data.trend === 'down' ? '↘' : '→'}
                              </Badge>
                            </div>
                            <p className="text-2xl font-bold text-yellow-600">₹{data.price}</p>
                            <p className="text-sm text-gray-600">प्रति {data.unit}</p>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                    
                    <div className="mt-6 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                      <p className="text-sm text-yellow-800">
                        <Clock className="h-4 w-4 inline mr-1" />
                        अंतिम अपडेट: {new Date(marketPrices.last_updated).toLocaleString('hi-IN')}
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Enhanced Footer */}
      <footer className="bg-white/90 backdrop-blur-md border-t border-green-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Brain className="h-6 w-6 text-green-600" />
                <h3 className="font-bold text-green-800">एग्रीलिंक AI सलाहकार</h3>
              </div>
              <p className="text-sm text-gray-600">
                भारतीय किसानों के लिए AI-powered स्मार्ट एग्रीलिंक समाधान। 
                Ollama AI के साथ उन्नत तकनीक।
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold text-gray-800 mb-3">Features</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center gap-2">
                  <Brain className="h-3 w-3" />
                  AI-Powered Advice
                </li>
                <li className="flex items-center gap-2">
                  <Target className="h-3 w-3" />
                  Crop Recommendations
                </li>
                <li className="flex items-center gap-2">
                  <Camera className="h-3 w-3" />
                  Disease Detection
                </li>
                <li className="flex items-center gap-2">
                  <CloudRain className="h-3 w-3" />
                  Weather Analysis
                </li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-gray-800 mb-3">Technology</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• Ollama AI Integration</li>
                <li>• Real-time Weather Data</li>
                <li>• Multi-language Support</li>
                <li>• SMS Integration</li>
                <li>• Market Intelligence</li>
              </ul>
            </div>
          </div>
          
          <Separator className="my-6" />
          
          <div className="text-center text-gray-600">
            <p className="text-sm">
              Enhanced Agricultural AI Platform • Built for Capital One Launchpad 2025 Hackathon
            </p>
            <p className="text-xs mt-1 flex items-center justify-center gap-2">
              <Zap className="h-3 w-3" />
              Powered by Ollama AI • Real-time Intelligence • Multi-modal Support
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;

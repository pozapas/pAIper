'use client';

import React, { useState, useEffect } from 'react';
import { Settings, Eye, EyeOff, AlertCircle, CheckCircle, RefreshCw } from 'lucide-react';
import { APIConfig } from '@/types';
import { validateApiKey, isValidUrl } from '@/lib/utils';
import { cn } from '@/lib/utils';

interface APIConfigurationProps {
  config: APIConfig;
  onConfigUpdate: (config: APIConfig) => void;
  onContinue: () => void;
}

interface OllamaModel {
  name: string;
  size: number;
  modified_at: string;
  digest: string;
}

const OPENROUTER_MODELS = [
  { id: 'google/gemini-2.5-flash', name: 'Gemini 2.5 Flash (Default)', provider: 'Google' },
  { id: 'custom', name: 'Custom Model...', provider: 'Custom' },
];

export default function APIConfiguration({ config, onConfigUpdate, onContinue }: APIConfigurationProps) {
  const [showKeys, setShowKeys] = useState({
    openRouterKey: false,
    googleScholarKey: false,
    scopusKey: false,
  });

  const [validationStatus, setValidationStatus] = useState({
    openRouterKey: null as boolean | null,
    ollamaEndpoint: null as boolean | null,
    googleScholarKey: null as boolean | null,
    scopusKey: null as boolean | null,
  });

  const [ollamaModels, setOllamaModels] = useState<OllamaModel[]>([]);
  const [ollamaLoading, setOllamaLoading] = useState(false);
  const [ollamaError, setOllamaError] = useState<string | null>(null);
  const [customModelName, setCustomModelName] = useState('');

  const handleInputChange = (key: keyof APIConfig, value: string) => {
    const newConfig = { ...config, [key]: value };
    
    // Set default OpenRouter model when API key is first entered
    if (key === 'openRouterKey' && value && !config.openRouterKey && !config.openRouterModel) {
      newConfig.openRouterModel = 'google/gemini-2.5-flash';
    }
    
    onConfigUpdate(newConfig);

    // Validate input
    let isValid = null;
    switch (key) {
      case 'openRouterKey':
        isValid = value ? validateApiKey(value, 'openrouter') : null;
        break;
      case 'ollamaEndpoint':
        isValid = value ? isValidUrl(value) : null;
        if (isValid && value !== config.ollamaEndpoint) {
          // Clear selected model when endpoint changes
          onConfigUpdate({ ...newConfig, ollamaModel: undefined });
          setOllamaModels([]);
          setOllamaError(null);
        }
        break;
      case 'googleScholarKey':
        isValid = value ? validateApiKey(value, 'google-scholar') : null;
        break;
      case 'scopusKey':
        isValid = value ? validateApiKey(value, 'scopus') : null;
        break;
    }

    setValidationStatus(prev => ({ ...prev, [key]: isValid }));
  };

  const handleModelSelection = (modelId: string) => {
    if (modelId === 'custom') {
      // Set to custom mode and trigger input display
      setCustomModelName(''); // Clear any previous custom input
      handleInputChange('openRouterModel', 'custom'); // Set to 'custom' to trigger display
      return;
    }
    // Set predefined model
    handleInputChange('openRouterModel', modelId);
    setCustomModelName(''); // Clear custom input when selecting predefined model
  };

  const handleCustomModelSubmit = () => {
    if (customModelName.trim()) {
      handleInputChange('openRouterModel', customModelName.trim());
      setCustomModelName(''); // Clear after setting
    }
  };

  const isCustomModel = () => {
    if (!config.openRouterModel) return false;
    // Check if it's the 'custom' placeholder or a custom model not in predefined list
    return config.openRouterModel === 'custom' || !OPENROUTER_MODELS.find(m => m.id === config.openRouterModel);
  };

  const fetchOllamaModels = async () => {
    if (!config.ollamaEndpoint || !validationStatus.ollamaEndpoint) return;

    setOllamaLoading(true);
    setOllamaError(null);

    try {
      const response = await fetch('/api/check-ollama', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ollamaEndpoint: config.ollamaEndpoint })
      });

      const data = await response.json();

      if (data.available) {
        setOllamaModels(data.models);
        if (data.models.length === 0) {
          setOllamaError('No models found. Run "ollama pull <model-name>" to install models.');
        }
      } else {
        setOllamaError(data.error || 'Cannot connect to Ollama');
        setOllamaModels([]);
      }
    } catch (error) {
      setOllamaError('Failed to fetch Ollama models');
      setOllamaModels([]);
    } finally {
      setOllamaLoading(false);
    }
  };

  // Auto-fetch models when endpoint is validated
  useEffect(() => {
    if (validationStatus.ollamaEndpoint === true && config.ollamaEndpoint) {
      fetchOllamaModels();
    }
  }, [validationStatus.ollamaEndpoint, config.ollamaEndpoint]);

  const toggleShowKey = (key: keyof typeof showKeys) => {
    setShowKeys(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const isConfigValid = () => {
    // At least one AI provider should be configured
    const hasOpenRouter = config.openRouterKey && validationStatus.openRouterKey && config.openRouterModel;
    const hasOllama = config.ollamaEndpoint && validationStatus.ollamaEndpoint && config.ollamaModel;
    const hasAI = hasOpenRouter || hasOllama;
    
    // At least one search provider should be configured
    const hasSearch = (config.googleScholarKey && validationStatus.googleScholarKey) || 
                     (config.scopusKey && validationStatus.scopusKey);
    
    return hasAI && hasSearch;
  };

  const ValidationIcon = ({ status }: { status: boolean | null }) => {
    if (status === null) return null;
    return status ? (
      <CheckCircle className="w-4 h-4 text-green-500" />
    ) : (
      <AlertCircle className="w-4 h-4 text-red-500" />
    );
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="flex items-center gap-3 mb-6">
        <Settings className="w-6 h-6 text-blue-600" />
        <h2 className="text-2xl font-bold text-gray-900">API Configuration</h2>
      </div>

      <p className="text-gray-600 mb-6">
        Configure your API keys and endpoints to get started with pAIper. You need at least one AI provider 
        and one academic database provider to proceed.
      </p>

      <div className="space-y-6">
        {/* AI Providers Section */}
        <div className="bg-blue-50 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            🤖 AI Providers
            <span className="text-sm text-gray-500">(Choose at least one)</span>
          </h3>
          
          <div className="space-y-4">
            {/* OpenRouter API Key */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                OpenRouter API Key
                <span className="text-xs text-gray-500 ml-1">(Recommended)</span>
              </label>
              <div className="relative">
                <input
                  type={showKeys.openRouterKey ? 'text' : 'password'}
                  value={config.openRouterKey || ''}
                  onChange={(e) => handleInputChange('openRouterKey', e.target.value)}
                  placeholder="sk-or-v1-..."
                  className={cn(
                    "w-full px-3 py-2 pr-20 border rounded-md focus:outline-none focus:ring-2 text-gray-900 placeholder-gray-500",
                    validationStatus.openRouterKey === false 
                      ? "border-red-300 focus:ring-red-500" 
                      : validationStatus.openRouterKey === true
                      ? "border-green-300 focus:ring-green-500"
                      : "border-gray-300 focus:ring-blue-500"
                  )}
                />
                <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
                  <ValidationIcon status={validationStatus.openRouterKey} />
                  <button
                    type="button"
                    onClick={() => toggleShowKey('openRouterKey')}
                    className="p-1 text-gray-400 hover:text-gray-600"
                  >
                    {showKeys.openRouterKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Get your API key from <a href="https://openrouter.ai" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">openrouter.ai</a>
              </p>

              {/* OpenRouter Model Selection */}
              {config.openRouterKey && validationStatus.openRouterKey && (
                <div className="mt-3">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select OpenRouter Model
                  </label>
                  <select
                    value={isCustomModel() ? 'custom' : (config.openRouterModel || '')}
                    onChange={(e) => handleModelSelection(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
                  >
                    <option value="">Choose a model...</option>
                    {OPENROUTER_MODELS.map((model) => (
                      <option key={model.id} value={model.id}>
                        {model.name} ({model.provider})
                      </option>
                    ))}
                  </select>

                  {/* Custom Model Input - Show when custom is selected */}
                  {(config.openRouterModel === 'custom' || customModelName !== '' || isCustomModel()) && (
                    <div className="mt-3">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Custom Model Name
                      </label>
                      <div className="flex gap-2">
                        <input
                          type="text"
                          value={config.openRouterModel === 'custom' ? customModelName : (isCustomModel() ? config.openRouterModel : customModelName)}
                          onChange={(e) => {
                            setCustomModelName(e.target.value);
                          }}
                          placeholder="e.g., openai/gpt-4-turbo, anthropic/claude-3-opus"
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 placeholder-gray-500"
                        />
                        {(config.openRouterModel === 'custom' || !isCustomModel()) && (
                          <button
                            type="button"
                            onClick={handleCustomModelSubmit}
                            disabled={!customModelName.trim()}
                            className="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-sm"
                          >
                            Set
                          </button>
                        )}
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        Enter any OpenRouter model ID. Check <a href="https://openrouter.ai/models" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">available models</a>
                      </p>
                    </div>
                  )}

                  {/* Current Model Display */}
                  {config.openRouterModel && isCustomModel() && (
                    <div className="mt-2 text-sm text-gray-600 bg-gray-50 p-2 rounded">
                      <span className="font-medium">Current model:</span> {config.openRouterModel}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Ollama Endpoint */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ollama Endpoint
                <span className="text-xs text-gray-500 ml-1">(Local AI)</span>
              </label>
              <div className="relative">
                <input
                  type="url"
                  value={config.ollamaEndpoint || ''}
                  onChange={(e) => handleInputChange('ollamaEndpoint', e.target.value)}
                  placeholder="http://localhost:11434"
                  className={cn(
                    "w-full px-3 py-2 pr-10 border rounded-md focus:outline-none focus:ring-2 text-gray-900 placeholder-gray-500",
                    validationStatus.ollamaEndpoint === false 
                      ? "border-red-300 focus:ring-red-500" 
                      : validationStatus.ollamaEndpoint === true
                      ? "border-green-300 focus:ring-green-500"
                      : "border-gray-300 focus:ring-blue-500"
                  )}
                />
                <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
                  <ValidationIcon status={validationStatus.ollamaEndpoint} />
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Make sure Ollama is running locally. Default: http://localhost:11434
              </p>

              {/* Ollama Model Selection */}
              {config.ollamaEndpoint && validationStatus.ollamaEndpoint && (
                <div className="mt-3">
                  <div className="flex items-center justify-between mb-2">
                    <label className="block text-sm font-medium text-gray-700">
                      Select Ollama Model
                    </label>
                    <button
                      type="button"
                      onClick={fetchOllamaModels}
                      disabled={ollamaLoading}
                      className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 disabled:opacity-50"
                    >
                      <RefreshCw className={cn("w-3 h-3", ollamaLoading && "animate-spin")} />
                      Refresh
                    </button>
                  </div>

                  {ollamaLoading && (
                    <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                      <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                      Checking available models...
                    </div>
                  )}

                  {ollamaError && (
                    <div className="text-sm text-red-600 mb-2 p-2 bg-red-50 rounded">
                      {ollamaError}
                    </div>
                  )}

                  {ollamaModels.length > 0 && (
                    <select
                      value={config.ollamaModel || ''}
                      onChange={(e) => handleInputChange('ollamaModel', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
                    >
                      <option value="">Choose a model...</option>
                      {ollamaModels.map((model) => (
                        <option key={model.name} value={model.name}>
                          {model.name} ({(model.size / (1024 ** 3)).toFixed(1)} GB)
                        </option>
                      ))}
                    </select>
                  )}

                  {!ollamaLoading && !ollamaError && ollamaModels.length === 0 && config.ollamaEndpoint && validationStatus.ollamaEndpoint && (
                    <div className="text-sm text-gray-600 p-2 bg-gray-50 rounded">
                      No models found. Install models with: <code className="bg-gray-200 px-1 rounded">ollama pull llama3.1</code>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Academic Databases Section */}
        <div className="bg-green-50 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            📚 Academic Databases
            <span className="text-sm text-gray-500">(Choose at least one)</span>
          </h3>
          
          <div className="space-y-4">
            {/* Google Scholar API Key */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Google Scholar API Key
                <span className="text-xs text-gray-500 ml-1">(Serpapi or similar)</span>
              </label>
              <div className="relative">
                <input
                  type={showKeys.googleScholarKey ? 'text' : 'password'}
                  value={config.googleScholarKey || ''}
                  onChange={(e) => handleInputChange('googleScholarKey', e.target.value)}
                  placeholder="Your Google Scholar API key..."
                  className={cn(
                    "w-full px-3 py-2 pr-20 border rounded-md focus:outline-none focus:ring-2 text-gray-900 placeholder-gray-500",
                    validationStatus.googleScholarKey === false 
                      ? "border-red-300 focus:ring-red-500" 
                      : validationStatus.googleScholarKey === true
                      ? "border-green-300 focus:ring-green-500"
                      : "border-gray-300 focus:ring-blue-500"
                  )}
                />
                <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
                  <ValidationIcon status={validationStatus.googleScholarKey} />
                  <button
                    type="button"
                    onClick={() => toggleShowKey('googleScholarKey')}
                    className="p-1 text-gray-400 hover:text-gray-600"
                  >
                    {showKeys.googleScholarKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Get API access from <a href="https://serpapi.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">SerpApi</a> or similar services
              </p>
            </div>

            {/* Scopus API Key */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Scopus API Key
                <span className="text-xs text-gray-500 ml-1">(Elsevier)</span>
              </label>
              <div className="relative">
                <input
                  type={showKeys.scopusKey ? 'text' : 'password'}
                  value={config.scopusKey || ''}
                  onChange={(e) => handleInputChange('scopusKey', e.target.value)}
                  placeholder="Your Scopus API key..."
                  className={cn(
                    "w-full px-3 py-2 pr-20 border rounded-md focus:outline-none focus:ring-2 text-gray-900 placeholder-gray-500",
                    validationStatus.scopusKey === false 
                      ? "border-red-300 focus:ring-red-500" 
                      : validationStatus.scopusKey === true
                      ? "border-green-300 focus:ring-green-500"
                      : "border-gray-300 focus:ring-blue-500"
                  )}
                />
                <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
                  <ValidationIcon status={validationStatus.scopusKey} />
                  <button
                    type="button"
                    onClick={() => toggleShowKey('scopusKey')}
                    className="p-1 text-gray-400 hover:text-gray-600"
                  >
                    {showKeys.scopusKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Get your API key from <a href="https://dev.elsevier.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Elsevier Developer Portal</a>
              </p>
            </div>
          </div>
        </div>

        {/* Configuration Status */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-2">Configuration Status</h3>
          <div className="text-sm space-y-1">
            <div className="flex items-center gap-2">
              {((config.openRouterKey && validationStatus.openRouterKey && config.openRouterModel) || 
                (config.ollamaEndpoint && validationStatus.ollamaEndpoint && config.ollamaModel)) ? (
                <CheckCircle className="w-4 h-4 text-green-500" />
              ) : (
                <AlertCircle className="w-4 h-4 text-red-500" />
              )}
              <span>AI Provider: {
                (config.openRouterKey && validationStatus.openRouterKey && config.openRouterModel) 
                  ? `OpenRouter (${OPENROUTER_MODELS.find(m => m.id === config.openRouterModel)?.name || config.openRouterModel})` :
                (config.ollamaEndpoint && validationStatus.ollamaEndpoint && config.ollamaModel) 
                  ? `Ollama (${config.ollamaModel})` :
                'Not configured'
              }</span>
            </div>
            <div className="flex items-center gap-2">
              {((config.googleScholarKey && validationStatus.googleScholarKey) || 
                (config.scopusKey && validationStatus.scopusKey)) ? (
                <CheckCircle className="w-4 h-4 text-green-500" />
              ) : (
                <AlertCircle className="w-4 h-4 text-red-500" />
              )}
              <span>Search Provider: {
                (config.googleScholarKey && validationStatus.googleScholarKey) ? 'Google Scholar configured' :
                (config.scopusKey && validationStatus.scopusKey) ? 'Scopus configured' :
                'Not configured'
              }</span>
            </div>
          </div>
        </div>

        {/* Continue Button */}
        <button
          onClick={onContinue}
          disabled={!isConfigValid()}
          className={cn(
            "w-full py-3 px-4 rounded-md font-medium transition-colors",
            isConfigValid()
              ? "bg-blue-600 text-white hover:bg-blue-700"
              : "bg-gray-300 text-gray-500 cursor-not-allowed"
          )}
        >
          {isConfigValid() ? "Continue to Query Generation" : "Complete Configuration to Continue"}
        </button>
      </div>
    </div>
  );
}
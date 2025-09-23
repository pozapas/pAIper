import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';

export async function POST(request: NextRequest) {
  try {
    const { ollamaEndpoint } = await request.json();

    if (!ollamaEndpoint) {
      return NextResponse.json({ error: 'Ollama endpoint is required' }, { status: 400 });
    }

    // Test connection and get available models
    const response = await axios.get(`${ollamaEndpoint}/api/tags`, {
      timeout: 5000
    });

    const models = response.data.models?.map((model: any) => ({
      name: model.name,
      size: model.size,
      modified_at: model.modified_at,
      digest: model.digest
    })) || [];

    return NextResponse.json({ 
      available: true,
      models
    });
  } catch (error) {
    console.error('Ollama connection error:', error);
    
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
        return NextResponse.json({ 
          error: 'Cannot connect to Ollama. Make sure Ollama is running.',
          available: false,
          models: []
        }, { status: 200 }); // Return 200 so UI can handle gracefully
      }
      
      if (error.response?.status === 404) {
        return NextResponse.json({ 
          error: 'Ollama API endpoint not found. Check your endpoint URL.',
          available: false,
          models: []
        }, { status: 200 });
      }
    }

    return NextResponse.json({
      error: 'Failed to connect to Ollama',
      available: false,
      models: []
    }, { status: 200 });
  }
}
import PaiperApp from '@/components/PaiperApp';
import NoSSR from '@/components/NoSSR';

export default function Home() {
  return (
    <NoSSR fallback={
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mx-auto mb-4">
            <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9.5 2A1.5 1.5 0 008 3.5v1A1.5 1.5 0 009.5 6h5A1.5 1.5 0 0016 4.5v-1A1.5 1.5 0 0014.5 2h-5zM11 8v6l1.5-1.5L14 14V8h-3z"/>
            </svg>
          </div>
          <div className="text-xl font-bold text-gray-900 mb-2">pAIper</div>
          <div className="text-sm text-gray-600">AI-Powered Research Discovery</div>
          <div className="text-xs text-gray-500 mt-2">Loading...</div>
        </div>
      </div>
    }>
      <PaiperApp />
    </NoSSR>
  );
}

import { useState } from 'react';
import { Button } from './ui/button';
import { EmptyState } from './EmptyState';
import { ErrorState } from './ErrorState';
import { LoadingSkeleton, CompactLoadingSkeleton } from './LoadingSkeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';

export function StatesDemoPanel() {
  const [showError, setShowError] = useState(false);

  return (
    <div className="min-h-screen bg-[#f8f9fa] p-8">
      <div className="max-w-[1200px] mx-auto">
        <h1 className="mb-2">UI States Demo</h1>
        <p className="text-[#6c757d] mb-8">
          Demonstration of empty states, error states, and loading skeletons
        </p>

        <Tabs defaultValue="empty" className="w-full">
          <TabsList className="mb-6">
            <TabsTrigger value="empty">Empty State</TabsTrigger>
            <TabsTrigger value="error">Error State</TabsTrigger>
            <TabsTrigger value="loading">Loading Skeleton</TabsTrigger>
          </TabsList>

          <TabsContent value="empty">
            <div className="bg-white rounded-lg shadow-md p-8">
              <h3 className="mb-4">Empty State Example</h3>
              <EmptyState
                title="No Triggers Available"
                description="There are currently no news triggers set up in the system. Contact your administrator to create triggers."
                actionLabel="Contact Administrator"
                onAction={() => alert('Contact administrator clicked')}
              />
            </div>
          </TabsContent>

          <TabsContent value="error">
            <div className="bg-white rounded-lg shadow-md p-8">
              <h3 className="mb-6">Error State Examples</h3>
              
              <div className="space-y-6">
                <div>
                  <h4 className="mb-3 text-sm text-[#6c757d]">API Timeout Error</h4>
                  <ErrorState
                    title="Failed to Load Data"
                    message="Unable to fetch data from Earnings API. The request timed out after 5 seconds."
                    technicalDetails="Error code: ETIMEDOUT
Endpoint: /api/earnings/AAPL
Timestamp: 2025-10-28T10:34:22Z"
                    onRetry={() => alert('Retry clicked')}
                    onDismiss={() => setShowError(false)}
                  />
                </div>

                <div>
                  <h4 className="mb-3 text-sm text-[#6c757d]">Simple Error (No Actions)</h4>
                  <ErrorState
                    title="Configuration Error"
                    message="The selected model is not available in your subscription plan."
                  />
                </div>

                <div>
                  <h4 className="mb-3 text-sm text-[#6c757d]">Network Error</h4>
                  <ErrorState
                    title="Network Connection Lost"
                    message="Unable to reach the server. Please check your internet connection and try again."
                    technicalDetails="Error: Network request failed
Status: 0
URL: https://api.newscms.com/v1/triggers"
                    onRetry={() => alert('Retry clicked')}
                  />
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="loading">
            <div className="space-y-6">
              <div className="bg-white rounded-lg shadow-md p-8">
                <h3 className="mb-4">Full Page Loading Skeleton</h3>
                <div className="border border-[#dee2e6] rounded-lg overflow-hidden">
                  <LoadingSkeleton />
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-md p-8">
                <h3 className="mb-4">Compact Loading Skeleton</h3>
                <div className="border border-[#dee2e6] rounded-lg overflow-hidden">
                  <CompactLoadingSkeleton />
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>

        <div className="mt-8 p-4 bg-[#e7f1ff] border border-[#0d6efd] rounded-lg">
          <p className="text-sm text-[#212529]">
            <strong>Note:</strong> These components can be used throughout the application to handle various UI states consistently.
          </p>
        </div>
      </div>
    </div>
  );
}

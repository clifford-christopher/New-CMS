export function LoadingSkeleton() {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar Skeleton */}
      <div className="w-[280px] bg-white border-r border-[#dee2e6] p-4 space-y-4">
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className="h-12 bg-gradient-to-r from-[#f8f9fa] via-[#e9ecef] to-[#f8f9fa] rounded animate-pulse"
            style={{
              backgroundSize: '200% 100%',
              animation: 'shimmer 1.5s linear infinite'
            }}
          />
        ))}
      </div>

      {/* Main Content Skeleton */}
      <div className="flex-1 bg-[#f8f9fa] p-8">
        {/* Header Skeleton */}
        <div
          className="w-[300px] h-8 bg-gradient-to-r from-[#f8f9fa] via-[#e9ecef] to-[#f8f9fa] rounded mb-6 animate-pulse"
          style={{
            backgroundSize: '200% 100%',
            animation: 'shimmer 1.5s linear infinite'
          }}
        />

        {/* Panel Skeletons */}
        <div className="space-y-6">
          {/* Panel 1 */}
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div
              className="w-[200px] h-5 bg-gradient-to-r from-[#f8f9fa] via-[#e9ecef] to-[#f8f9fa] rounded mb-4 animate-pulse"
              style={{
                backgroundSize: '200% 100%',
                animation: 'shimmer 1.5s linear infinite'
              }}
            />
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div
                  key={i}
                  className="h-4 bg-gradient-to-r from-[#f8f9fa] via-[#e9ecef] to-[#f8f9fa] rounded animate-pulse"
                  style={{
                    width: i === 0 ? '100%' : i === 1 ? '80%' : '60%',
                    backgroundSize: '200% 100%',
                    animation: 'shimmer 1.5s linear infinite'
                  }}
                />
              ))}
            </div>
          </div>

          {/* Panel 2 */}
          <div className="bg-white rounded-lg p-6 shadow-sm h-[400px]">
            <div
              className="w-[200px] h-5 bg-gradient-to-r from-[#f8f9fa] via-[#e9ecef] to-[#f8f9fa] rounded mb-4 animate-pulse"
              style={{
                backgroundSize: '200% 100%',
                animation: 'shimmer 1.5s linear infinite'
              }}
            />
            <div className="space-y-3">
              {[...Array(8)].map((_, i) => (
                <div
                  key={i}
                  className="h-4 bg-gradient-to-r from-[#f8f9fa] via-[#e9ecef] to-[#f8f9fa] rounded animate-pulse"
                  style={{
                    width: Math.random() * 40 + 60 + '%',
                    backgroundSize: '200% 100%',
                    animation: 'shimmer 1.5s linear infinite'
                  }}
                />
              ))}
            </div>
          </div>

          {/* Panel 3 */}
          <div className="bg-white rounded-lg p-6 shadow-sm h-[300px]">
            <div
              className="w-[200px] h-5 bg-gradient-to-r from-[#f8f9fa] via-[#e9ecef] to-[#f8f9fa] rounded mb-4 animate-pulse"
              style={{
                backgroundSize: '200% 100%',
                animation: 'shimmer 1.5s linear infinite'
              }}
            />
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div
                  key={i}
                  className="h-4 bg-gradient-to-r from-[#f8f9fa] via-[#e9ecef] to-[#f8f9fa] rounded animate-pulse"
                  style={{
                    width: Math.random() * 30 + 70 + '%',
                    backgroundSize: '200% 100%',
                    animation: 'shimmer 1.5s linear infinite'
                  }}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes shimmer {
          0% {
            background-position: -200% 0;
          }
          100% {
            background-position: 200% 0;
          }
        }
      `}</style>
    </div>
  );
}

// Compact loading skeleton for smaller components
export function CompactLoadingSkeleton() {
  return (
    <div className="space-y-3 p-4">
      {[...Array(4)].map((_, i) => (
        <div
          key={i}
          className="h-10 bg-gradient-to-r from-[#f8f9fa] via-[#e9ecef] to-[#f8f9fa] rounded animate-pulse"
          style={{
            backgroundSize: '200% 100%',
            animation: 'shimmer 1.5s linear infinite'
          }}
        />
      ))}
    </div>
  );
}

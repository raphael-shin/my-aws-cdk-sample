import React from 'react';
import { Amplify } from 'aws-amplify';
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import PhotoStart from './PhotoStart';
import PhotoTake from './PhotoTake';
import ImageDisplay from './ImageDisplay';
import { Authenticator } from '@aws-amplify/ui-react';
import { QueryCache, QueryClient, QueryClientProvider } from "@tanstack/react-query";
import '@aws-amplify/ui-react/styles.css';

Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: 'us-west-2_j4di9vdEv',
      userPoolClientId: '53krpd79r9qdnigc6754j00do9',
    }
  }
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: Infinity,
    },
  },
  queryCache: new QueryCache({
    onError: (error) => {
      console.error(error);
    },
  }),
});

const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
        <Router>
          <Routes>
            <Route path="/" element={<Navigate to="/photo/start" replace />} />
            <Route path="/photo/start" element={<PhotoStart />} />
            <Route path="/photo/take" element={<PhotoTake />} />
            <Route path="/image/:uuid" element={<ImageDisplay />}/>
          </Routes>
        </Router>
    </QueryClientProvider>

  );
};

export default App;

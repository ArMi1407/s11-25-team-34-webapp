// routes/SignupRoute.jsx
import { useLocation, Navigate } from 'react-router-dom';

export const SignupRoute = ({ children }) => {
  const location = useLocation();

  const hasValidPersonId = location.state?.personId;

  if (!hasValidPersonId) {
    return <Navigate to="/register" replace />;
  }

  return children;
};

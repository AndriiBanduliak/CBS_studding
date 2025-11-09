import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../store/useAuth'

export default function PrivateRoute({ children }) {
  const { user } = useAuth()
  const location = useLocation()
  if (!user) return <Navigate to="/auth" replace state={{ from: location }} />
  return children
}

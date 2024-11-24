
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { RegisterForm } from './components/RegisterForm/RegisterForm'
import { AuthLayout } from './components/AuthLayout/AuthLayout'
import { Home } from './components/Home/Home'
import { LoginForm } from './components/LoginForm/LoginForm'
import { ProtectedRoute } from './components/ProtectedRoute/ProtectedRoute'
import { DashboardLayout } from './components/DashboardLayout/DashboardLayout'
import { Projects } from './components/Project/Project'
import { ProjectDetails } from './components/Project/ProjectDetails'
import { SubscriptionPlans } from './components/Subscriptions/SubscriptionPlans'

function App() {


  return (
    <BrowserRouter>
    <Routes>
      <Route path='/' element={<Home/>}/>
      <Route path='/register' element={
        <AuthLayout title='Register'>
          <RegisterForm />
        </AuthLayout>
      } />
      <Route path='/login' element={
        <AuthLayout title='Login'>
          <LoginForm />
        </AuthLayout>
      } />
      <Route path="/dashboard/subscription" element={
          <ProtectedRoute>
            <DashboardLayout>
              <SubscriptionPlans />
            </DashboardLayout>
          </ProtectedRoute>
        } />
        <Route path="/dashboard/projects" element={
          <ProtectedRoute>
            <DashboardLayout>
              <Projects />
            </DashboardLayout>
          </ProtectedRoute>
        } />
        <Route path="/dashboard/projects/:id" element={
          <ProtectedRoute>
            <DashboardLayout>
              <ProjectDetails />
            </DashboardLayout>
          </ProtectedRoute>
        } />

    </Routes>
    </BrowserRouter>
  )
}

export default App

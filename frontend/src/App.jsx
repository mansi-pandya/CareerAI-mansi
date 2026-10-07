import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { Suspense, lazy } from 'react'

import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import MainLayout from './layouts/MainLayout'
import AuthLayout from './layouts/AuthLayout'
import DashboardLayout from './layouts/DashboardLayout'

// Lazy-loaded pages
const Landing = lazy(() => import('./pages/Landing'))
const Login = lazy(() => import('./pages/auth/Login'))
const Register = lazy(() => import('./pages/auth/Register'))
const ForgotPassword = lazy(() => import('./pages/auth/ForgotPassword'))
const ResetPassword = lazy(() => import('./pages/auth/ResetPassword'))
const Dashboard = lazy(() => import('./pages/dashboard/Dashboard'))
const Profile = lazy(() => import('./pages/profile/Profile'))
const NotFound = lazy(() => import('./pages/NotFound'))

// Stage 2 — Resume & ATS
const ResumeList = lazy(() => import('./pages/resume/ResumeList'))
const ResumeUpload = lazy(() => import('./pages/resume/ResumeUpload'))
const ResumeBuilder = lazy(() => import('./pages/resume/ResumeBuilder'))
const ResumePreview = lazy(() => import('./pages/resume/ResumePreview'))
const ATSAnalyzer = lazy(() => import('./pages/ats/ATSAnalyzer'))
const ATSJobSpecific = lazy(() => import('./pages/ats/ATSJobSpecific'))

// Stage 3 — Career Recommendation, Skill Gap, Learning Roadmap
const CareerRecommendations = lazy(() => import('./pages/career/CareerRecommendations'))
const CareerDetail = lazy(() => import('./pages/career/CareerDetail'))
const SkillGap = lazy(() => import('./pages/career/SkillGap'))
const ImprovementCenter = lazy(() => import('./pages/career/ImprovementCenter'))
const LearningResources = lazy(() => import('./pages/learning/LearningResources'))
const LearningRoadmap = lazy(() => import('./pages/learning/LearningRoadmap'))

// Stage 4 — Job Discovery
const JobSearch = lazy(() => import('./pages/jobs/JobSearch'))
const JobDetail = lazy(() => import('./pages/jobs/JobDetail'))
const SavedJobs = lazy(() => import('./pages/jobs/SavedJobs'))
const MarketAnalysis = lazy(() => import('./pages/jobs/MarketAnalysis'))

// Stage 5 — Opportunity Checker
const OpportunityChecker = lazy(() => import('./pages/opportunities/OpportunityChecker'))
const OpportunityHistory = lazy(() => import('./pages/opportunities/OpportunityHistory'))
const InterviewSetup = lazy(() => import('./pages/interviews/InterviewSetup'))
const InterviewSession = lazy(() => import('./pages/interviews/InterviewSession'))
const InterviewResults = lazy(() => import('./pages/interviews/InterviewResults'))

function PageLoader() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950">
      <div className="w-10 h-10 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#1f2937',
              color: '#f9fafb',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '10px',
            },
            success: { iconTheme: { primary: '#10b981', secondary: '#f9fafb' } },
            error: { iconTheme: { primary: '#ef4444', secondary: '#f9fafb' } },
          }}
        />

        <Suspense fallback={<PageLoader />}>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Landing />} />

            {/* Auth routes */}
            <Route element={<AuthLayout />}>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />
            </Route>

            {/* Protected dashboard routes */}
            <Route
              element={
                <ProtectedRoute>
                  <DashboardLayout />
                </ProtectedRoute>
              }
            >
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/resume" element={<ResumeList />} />
              <Route path="/resume/upload" element={<ResumeUpload />} />
              <Route path="/resume/create" element={<ResumeBuilder />} />
              <Route path="/resume/:resumeId/builder" element={<ResumeBuilder />} />
              <Route path="/resume/:resumeId/preview" element={<ResumePreview />} />
              <Route path="/ats" element={<ATSAnalyzer />} />
              <Route path="/ats/job-specific" element={<ATSJobSpecific />} />

              {/* Stage 3 — Career & Learning */}
              <Route path="/careers" element={<CareerRecommendations />} />
              <Route path="/careers/:slug" element={<CareerDetail />} />
              <Route path="/skill-gap" element={<SkillGap />} />
              <Route path="/improvement" element={<ImprovementCenter />} />
              <Route path="/learning" element={<LearningResources />} />
              <Route path="/learning/roadmap" element={<LearningRoadmap />} />

              {/* Stage 4 — Job Discovery */}
              <Route path="/jobs" element={<JobSearch />} />
              <Route path="/jobs/saved" element={<SavedJobs />} />
              <Route path="/jobs/market" element={<MarketAnalysis />} />
              <Route path="/jobs/:jobId" element={<JobDetail />} />
              <Route path="/opportunity" element={<OpportunityChecker />} />
              <Route path="/opportunity/history" element={<OpportunityHistory />} />
              <Route path="/interview" element={<InterviewSetup />} />
              <Route path="/interview/:id" element={<InterviewSession />} />
              <Route path="/interview/:id/results" element={<InterviewResults />} />
            </Route>

            {/* Fallbacks */}
            <Route path="/404" element={<NotFound />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </AuthProvider>
    </BrowserRouter>
  )
}

import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  DocumentTextIcon,
  BriefcaseIcon,
  AcademicCapIcon,
  ChartBarIcon,
  ShieldCheckIcon,
  VideoCameraIcon,
  SparklesIcon,
  CheckCircleIcon,
  StarIcon,
  LockClosedIcon,
  GlobeAltIcon,
  UserGroupIcon,
  ArrowRightIcon,
  ChevronDownIcon,
  MagnifyingGlassIcon,
  LightBulbIcon,
  TrophyIcon,
} from '@heroicons/react/24/outline'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Navbar from '../components/Navbar'
import Footer from '../components/Footer'

// ─── Data ────────────────────────────────────────────────────────────────────

const HOW_IT_WORKS = [
  { step: '01', title: 'Create Your Profile', desc: 'Sign up and complete your student profile with education, skills, and career goals.', icon: UserGroupIcon, color: 'text-blue-400' },
  { step: '02', title: 'Upload Your Resume', desc: 'Upload an existing resume or build one with our AI-powered resume builder.', icon: DocumentTextIcon, color: 'text-indigo-400' },
  { step: '03', title: 'AI Analyzes Everything', desc: 'Our AI evaluates your resume, skills, and goals against thousands of job profiles.', icon: SparklesIcon, color: 'text-purple-400' },
  { step: '04', title: 'Get Personalized Insights', desc: 'Receive your Career Readiness Score, skill gaps, job matches, and learning paths.', icon: ChartBarIcon, color: 'text-teal-400' },
  { step: '05', title: 'Practice & Apply', desc: 'Do mock AI interviews, close skill gaps, and apply to verified opportunities.', icon: TrophyIcon, color: 'text-emerald-400' },
]

const FEATURES = [
  {
    id: 'ats',
    title: 'Resume & ATS Optimization',
    badge: 'ATS Score',
    badgeColor: 'blue',
    icon: DocumentTextIcon,
    iconBg: 'from-blue-600 to-blue-800',
    desc: 'Our AI parses your resume and scores it against real ATS algorithms used by Fortune 500 companies. Get instant feedback on formatting, keywords, and content gaps — before employers ever see it.',
    bullets: ['Keyword density analysis', 'ATS-friendly format check', 'Section completeness score', 'Industry-specific keyword suggestions'],
  },
  {
    id: 'career',
    title: 'AI Career Matching',
    badge: 'Career Match',
    badgeColor: 'purple',
    icon: SparklesIcon,
    iconBg: 'from-purple-600 to-indigo-700',
    desc: 'Using ML models trained on millions of career trajectories, CareerAI matches your unique skills, education, and aspirations to the best-fit career paths with salary data included.',
    bullets: ['Top 10 career matches with % fit', 'Salary range benchmarks', 'Growth trajectory insights', 'Required vs. your skill comparison'],
  },
  {
    id: 'jobs',
    title: 'Real Job Discovery',
    badge: 'Live Jobs',
    badgeColor: 'green',
    icon: BriefcaseIcon,
    iconBg: 'from-emerald-600 to-teal-700',
    desc: 'CareerAI aggregates live job postings from LinkedIn, Indeed, Glassdoor, and company career pages, ranking them by your personal career readiness match.',
    bullets: ['Real-time job aggregation', 'Match score per listing', 'Application tracking', 'Internship & entry-level filter'],
  },
  {
    id: 'verify',
    title: 'Opportunity Verification',
    badge: 'Safe Apply',
    badgeColor: 'teal',
    icon: ShieldCheckIcon,
    iconBg: 'from-teal-600 to-cyan-700',
    desc: 'Not every job posting is legitimate. CareerAI\'s verification engine flags scam postings, ghost jobs, and misleading listings so you spend time only on real opportunities.',
    bullets: ['Scam detection AI', 'Company legitimacy check', 'Job posting freshness score', 'Red flag alerts'],
  },
  {
    id: 'skills',
    title: 'Skill Gap Analysis',
    badge: 'Skill Map',
    badgeColor: 'orange',
    icon: AcademicCapIcon,
    iconBg: 'from-orange-600 to-amber-700',
    desc: 'Know exactly which skills stand between you and your dream job. CareerAI maps your current skills against your target role requirements and surfaces the highest-priority gaps.',
    bullets: ['Per-role skill gap heatmap', 'Priority ranking by impact', 'Free & paid learning resources', 'Progress tracking'],
  },
  {
    id: 'learning',
    title: 'Personalized Learning Paths',
    badge: 'Learning',
    badgeColor: 'indigo',
    icon: LightBulbIcon,
    iconBg: 'from-indigo-600 to-violet-700',
    desc: 'Curated learning journeys built around your skill gaps, learning pace, and career timeline. From free YouTube tutorials to paid Coursera courses — all prioritized for maximum ROI.',
    bullets: ['Curated course recommendations', 'Free & premium resources', 'Estimated time to competency', 'Skill mastery tracking'],
  },
  {
    id: 'interview',
    title: 'Virtual AI Interview',
    badge: 'AI Prep',
    badgeColor: 'red',
    icon: VideoCameraIcon,
    iconBg: 'from-red-600 to-rose-700',
    desc: 'Practice unlimited AI-powered mock interviews tailored to your target role. Get scored on content, communication, and confidence with actionable feedback after each session.',
    bullets: ['Role-specific question bank', 'Answer scoring & feedback', 'Behavioral & technical modes', 'Confidence & clarity metrics'],
  },
  {
    id: 'score',
    title: 'Career Readiness Score',
    badge: 'Readiness',
    badgeColor: 'yellow',
    icon: TrophyIcon,
    iconBg: 'from-yellow-600 to-orange-600',
    desc: 'Your single unified metric that aggregates ATS score, skill match, career match, job match, and interview readiness into one actionable Career Readiness Score (0–100).',
    bullets: ['6-factor composite score', 'Week-over-week trend', 'Industry percentile ranking', 'Improvement roadmap'],
  },
]

const SDG_POINTS = [
  'Bridges the employability gap for students from all backgrounds',
  'Provides equal access to AI career tools regardless of location',
  'Reduces unemployment by matching students to appropriate roles',
  'Promotes skills-based hiring over nepotism and connections',
]

const SECURITY_POINTS = [
  { icon: LockClosedIcon, title: 'End-to-End Encryption', desc: 'All data in transit and at rest is encrypted with AES-256.' },
  { icon: ShieldCheckIcon, title: 'GDPR Compliant', desc: 'You own your data. Export or delete it at any time.' },
  { icon: GlobeAltIcon, title: 'No Data Selling', desc: 'We never sell your personal data to employers or third parties.' },
  { icon: CheckCircleIcon, title: 'SOC 2 Aligned', desc: 'Security controls aligned with SOC 2 Type II standards.' },
]

const FAQS = [
  { q: 'Is CareerAI free to use?', a: 'CareerAI offers a generous free tier covering profile creation, ATS scoring, career matching, and basic job discovery. Premium features like unlimited AI interviews and advanced analytics are available on paid plans.' },
  { q: 'How accurate is the ATS scoring?', a: 'Our ATS engine is trained on data from actual ATS systems used by top employers. Scores correlate strongly with real interview rates. Accuracy improves as you provide more profile data.' },
  { q: 'Does CareerAI store my resume?', a: 'Yes, your resume is securely stored and encrypted. You can delete it at any time from your profile settings. We never share it with employers without your explicit permission.' },
  { q: 'How does Opportunity Verification work?', a: 'Our verification engine cross-references job postings against known company databases, checks posting age and consistency, analyzes language patterns associated with scams, and assigns a legitimacy confidence score.' },
  { q: 'Can I use CareerAI for any career field?', a: 'CareerAI covers 200+ career paths across technology, business, healthcare, design, engineering, finance, marketing, and more. Our models are continuously trained on new job data.' },
  { q: 'How is CareerAI aligned with SDG 8?', a: 'UN SDG 8 calls for promoting sustained, inclusive economic growth and full, productive employment. CareerAI directly supports this by providing free AI career tools to students globally, with particular focus on underserved communities.' },
]

// ─── Section Components ────────────────────────────────────────────────────────

function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-950 via-navy-950 to-gray-950" />
      <div className="absolute inset-0 hero-glow" />
      {/* Grid pattern */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `linear-gradient(rgba(255,255,255,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.5) 1px, transparent 1px)`,
          backgroundSize: '50px 50px',
        }}
      />

      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 text-center pt-24 pb-20">
        <Badge variant="blue" className="mb-6 text-sm px-4 py-1.5">
          🚀 AI-Powered Career Readiness Platform
        </Badge>

        <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-extrabold text-white leading-tight mb-6 tracking-tight">
          Build Skills.{' '}
          <span className="gradient-text">Find Opportunities.</span>
          <br />
          Get Career-Ready.
        </h1>

        <p className="text-lg sm:text-xl text-gray-400 max-w-3xl mx-auto mb-10 leading-relaxed">
          CareerAI combines resume analysis, AI career matching, live job discovery, opportunity verification, skill gap analysis, and virtual interview prep — all in one platform designed for students.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
          <Link to="/register">
            <Button size="xl" variant="primary" className="gap-3 min-w-[200px]">
              <SparklesIcon className="w-5 h-5" />
              Get Started Free
            </Button>
          </Link>
          <a href="#ats">
            <Button size="xl" variant="outline" className="gap-3 min-w-[200px]">
              <DocumentTextIcon className="w-5 h-5" />
              Analyze My Resume
            </Button>
          </a>
          <a href="#features">
            <Button size="xl" variant="ghost" className="gap-3">
              Explore CareerAI
              <ArrowRightIcon className="w-4 h-4" />
            </Button>
          </a>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-3xl mx-auto">
          {[
            { value: '50K+', label: 'Students Helped' },
            { value: '200+', label: 'Career Paths' },
            { value: '95%', label: 'ATS Accuracy' },
            { value: 'SDG 8', label: 'UN Aligned' },
          ].map((stat) => (
            <div key={stat.label} className="glass rounded-xl p-4">
              <p className="text-2xl font-bold gradient-text">{stat.value}</p>
              <p className="text-sm text-gray-500 mt-1">{stat.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Scroll cue */}
      <a href="#how-it-works" className="absolute bottom-8 left-1/2 -translate-x-1/2 text-gray-600 hover:text-gray-400 transition-colors animate-bounce">
        <ChevronDownIcon className="w-6 h-6" />
      </a>
    </section>
  )
}

function HowItWorksSection() {
  return (
    <section id="how-it-works" className="py-24 bg-gray-900/30">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-16">
          <Badge variant="indigo" className="mb-4">Step-by-Step</Badge>
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">How CareerAI Works</h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            From profile creation to job offer — a clear, AI-guided journey in five steps.
          </p>
        </div>

        <div className="relative">
          {/* Connector line */}
          <div className="hidden lg:block absolute top-16 left-[10%] right-[10%] h-0.5 bg-gradient-to-r from-blue-600/0 via-indigo-500/40 to-blue-600/0" />

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
            {HOW_IT_WORKS.map((step) => {
              const Icon = step.icon
              return (
                <div key={step.step} className="flex flex-col items-center text-center group">
                  <div className="relative mb-4">
                    <div className="w-16 h-16 rounded-2xl glass border border-white/10 flex items-center justify-center group-hover:border-blue-500/40 transition-all">
                      <Icon className={`w-7 h-7 ${step.color}`} />
                    </div>
                    <span className="absolute -top-2 -right-2 text-xs font-bold text-gray-600 bg-gray-950 rounded-full w-6 h-6 flex items-center justify-center border border-white/5">
                      {step.step}
                    </span>
                  </div>
                  <h3 className="text-sm font-semibold text-white mb-2">{step.title}</h3>
                  <p className="text-xs text-gray-500 leading-relaxed">{step.desc}</p>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}

function FeatureSection({ feature, index }) {
  const Icon = feature.icon
  const isEven = index % 2 === 0

  return (
    <section id={feature.id} className="py-20 section-divider">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className={`flex flex-col lg:flex-row items-center gap-12 ${!isEven ? 'lg:flex-row-reverse' : ''}`}>
          {/* Text */}
          <div className="flex-1">
            <Badge variant={feature.badgeColor} className="mb-4">{feature.badge}</Badge>
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4 leading-tight">{feature.title}</h2>
            <p className="text-gray-400 text-lg leading-relaxed mb-8">{feature.desc}</p>
            <ul className="space-y-3">
              {feature.bullets.map((b) => (
                <li key={b} className="flex items-center gap-3 text-gray-300">
                  <CheckCircleIcon className="w-5 h-5 text-emerald-400 shrink-0" />
                  <span>{b}</span>
                </li>
              ))}
            </ul>
            <div className="mt-8">
              <Link to="/register">
                <Button variant="primary" size="lg">
                  Try {feature.badge} Free
                  <ArrowRightIcon className="w-4 h-4" />
                </Button>
              </Link>
            </div>
          </div>

          {/* Visual */}
          <div className="flex-1 flex items-center justify-center">
            <div className="relative w-full max-w-sm">
              <div className="absolute inset-0 rounded-3xl bg-gradient-to-br opacity-20 blur-3xl"
                style={{ background: `linear-gradient(135deg, ${feature.iconBg.includes('blue') ? '#3b82f6' : feature.iconBg.includes('purple') ? '#8b5cf6' : feature.iconBg.includes('emerald') ? '#10b981' : feature.iconBg.includes('teal') ? '#14b8a6' : feature.iconBg.includes('orange') ? '#f59e0b' : feature.iconBg.includes('indigo') ? '#6366f1' : feature.iconBg.includes('red') ? '#ef4444' : '#eab308'}, transparent)` }}
              />
              <div className="relative glass rounded-3xl p-8 flex flex-col items-center gap-6 border border-white/8">
                <div className={`w-20 h-20 rounded-2xl bg-gradient-to-br ${feature.iconBg} flex items-center justify-center shadow-2xl`}>
                  <Icon className="w-10 h-10 text-white" />
                </div>
                <div className="w-full space-y-3">
                  {feature.bullets.map((b, i) => (
                    <div key={i} className="flex items-center gap-3 bg-white/4 rounded-lg px-4 py-2.5">
                      <div className="w-2 h-2 rounded-full bg-blue-400 shrink-0" />
                      <span className="text-sm text-gray-300">{b}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

function CareerReadinessScoreSection() {
  const scores = [
    { label: 'ATS Readiness', value: 78, color: '#3b82f6' },
    { label: 'Skill Match', value: 65, color: '#8b5cf6' },
    { label: 'Career Match', value: 82, color: '#10b981' },
    { label: 'Job Match', value: 71, color: '#f59e0b' },
    { label: 'Interview Ready', value: 55, color: '#ef4444' },
  ]
  const overall = Math.round(scores.reduce((s, x) => s + x.value, 0) / scores.length)
  const circumference = 2 * Math.PI * 70
  const offset = circumference - (overall / 100) * circumference

  return (
    <section id="score" className="py-24 bg-gray-900/20 section-divider">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-16">
          <Badge variant="yellow" className="mb-4">Career Readiness Score</Badge>
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">Your Single Source of Career Truth</h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Six factors combined into one powerful score — so you always know exactly where you stand.
          </p>
        </div>

        <div className="flex flex-col lg:flex-row items-center justify-center gap-12">
          {/* Big circle */}
          <div className="relative flex items-center justify-center">
            <svg width="200" height="200" className="-rotate-90">
              <circle cx="100" cy="100" r="70" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="12" />
              <circle cx="100" cy="100" r="70" fill="none" stroke="#3b82f6" strokeWidth="12"
                strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round"
                style={{ transition: 'stroke-dashoffset 1s ease' }} />
            </svg>
            <div className="absolute flex flex-col items-center">
              <span className="text-5xl font-extrabold gradient-text">{overall}</span>
              <span className="text-sm text-gray-400">/ 100</span>
              <span className="text-xs text-gray-500 mt-1">Overall</span>
            </div>
          </div>

          {/* Factor bars */}
          <div className="w-full max-w-md space-y-4">
            {scores.map((s) => {
              const c = 2 * Math.PI * 16
              const o = c - (s.value / 100) * c
              return (
                <div key={s.label} className="flex items-center gap-4">
                  <svg width="40" height="40" className="-rotate-90 shrink-0">
                    <circle cx="20" cy="20" r="16" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="4" />
                    <circle cx="20" cy="20" r="16" fill="none" stroke={s.color} strokeWidth="4"
                      strokeDasharray={c} strokeDashoffset={o} strokeLinecap="round" />
                  </svg>
                  <div className="flex-1">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-300">{s.label}</span>
                      <span className="font-medium" style={{ color: s.color }}>{s.value}</span>
                    </div>
                    <div className="h-1.5 rounded-full bg-white/6 overflow-hidden">
                      <div className="h-full rounded-full" style={{ width: `${s.value}%`, backgroundColor: s.color, transition: 'width 0.8s ease' }} />
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        <div className="mt-12 text-center">
          <Link to="/register">
            <Button size="lg" variant="primary">
              <TrophyIcon className="w-5 h-5" />
              Check My Career Readiness Score
            </Button>
          </Link>
        </div>
      </div>
    </section>
  )
}

function Sdg8Section() {
  return (
    <section id="sdg" className="py-20 section-divider">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="glass-navy rounded-3xl p-8 md:p-12">
          <div className="flex flex-col md:flex-row items-start gap-8">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shrink-0">
              <GlobeAltIcon className="w-10 h-10 text-white" />
            </div>
            <div>
              <Badge variant="yellow" className="mb-3">UN SDG 8</Badge>
              <h2 className="text-3xl font-bold text-white mb-4">Decent Work &amp; Economic Growth</h2>
              <p className="text-gray-300 text-lg leading-relaxed mb-6">
                CareerAI is proudly aligned with United Nations Sustainable Development Goal 8 — promoting sustained, inclusive and sustainable economic growth, full and productive employment and decent work for all.
              </p>
              <ul className="space-y-3">
                {SDG_POINTS.map((p) => (
                  <li key={p} className="flex items-start gap-3 text-gray-300">
                    <CheckCircleIcon className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                    <span>{p}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

function SecuritySection() {
  return (
    <section id="security" className="py-20 bg-gray-900/30 section-divider">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-12">
          <Badge variant="green" className="mb-4">Security &amp; Privacy</Badge>
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">Your Data is Safe With Us</h2>
          <p className="text-gray-400 max-w-xl mx-auto">Enterprise-grade security so you can focus on your career, not your privacy.</p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {SECURITY_POINTS.map((p) => {
            const Icon = p.icon
            return (
              <div key={p.title} className="glass rounded-2xl p-6 flex flex-col gap-4 hover:border-green-500/30 transition-all">
                <div className="w-12 h-12 rounded-xl bg-emerald-900/30 border border-emerald-500/20 flex items-center justify-center">
                  <Icon className="w-6 h-6 text-emerald-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-white mb-1">{p.title}</h3>
                  <p className="text-sm text-gray-500">{p.desc}</p>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

function FaqSection() {
  const [open, setOpen] = useState(null)

  return (
    <section id="faq" className="py-24 section-divider">
      <div className="max-w-3xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-12">
          <Badge variant="indigo" className="mb-4">FAQ</Badge>
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">Frequently Asked Questions</h2>
          <p className="text-gray-400">Everything you need to know about CareerAI.</p>
        </div>
        <div className="space-y-3">
          {FAQS.map((faq, i) => (
            <div
              key={i}
              className={`glass rounded-xl overflow-hidden border transition-all duration-200 ${open === i ? 'border-blue-500/30' : 'border-white/6'}`}
            >
              <button
                className="w-full flex items-center justify-between px-6 py-4 text-left"
                onClick={() => setOpen(open === i ? null : i)}
              >
                <span className="font-medium text-white pr-4">{faq.q}</span>
                <ChevronDownIcon
                  className={`w-5 h-5 text-gray-400 shrink-0 transition-transform duration-200 ${open === i ? 'rotate-180' : ''}`}
                />
              </button>
              {open === i && (
                <div className="px-6 pb-5">
                  <p className="text-gray-400 leading-relaxed">{faq.a}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function CtaSection() {
  return (
    <section className="py-24 section-divider">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 text-center">
        <div className="glass-navy rounded-3xl p-10 md:p-16">
          <Badge variant="blue" className="mb-6">Start Today</Badge>
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            Ready to Launch Your Career?
          </h2>
          <p className="text-gray-400 text-lg mb-10 max-w-2xl mx-auto">
            Join thousands of students using CareerAI to get job-ready faster. Free to start, no credit card required.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/register">
              <Button size="xl" variant="primary" className="min-w-[200px]">
                <SparklesIcon className="w-5 h-5" />
                Create Free Account
              </Button>
            </Link>
            <Link to="/login">
              <Button size="xl" variant="outline" className="min-w-[180px]">
                Sign In
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </section>
  )
}

// ─── Main Landing Component ───────────────────────────────────────────────────

export default function Landing() {
  return (
    <div className="min-h-screen bg-gray-950">
      <Navbar />
      <HeroSection />
      <HowItWorksSection />

      <div id="features">
        {FEATURES.map((feature, i) => (
          <FeatureSection key={feature.id} feature={feature} index={i} />
        ))}
      </div>

      <CareerReadinessScoreSection />
      <Sdg8Section />
      <SecuritySection />
      <FaqSection />
      <CtaSection />
      <Footer />
    </div>
  )
}
